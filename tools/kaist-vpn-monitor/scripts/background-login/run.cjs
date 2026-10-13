#!/usr/bin/env node
'use strict';
// No credentials, OTPs, session URLs, page snapshots or browser logs are emitted.
delete process.env.DEBUG;
delete process.env.PWDEBUG;
const fs = require('node:fs/promises');
const net = require('node:net');
const os = require('node:os');
const path = require('node:path');
const {execFile, spawn} = require('node:child_process');
const {promisify} = require('node:util');
const {randomUUID} = require('node:crypto');
const run = promisify(execFile);
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const {loadSettings} = require('./settings.cjs');
const {ORIGIN, OTP_ORIGIN, originIs, allowedRequest, allowedLauncher, emailFrame, portalReady} = require('./browser-policy.cjs');
const {startVpnProxy} = require('./vpn-proxy.cjs');
const scriptRoot = path.resolve(__dirname, '..');
const runtime = path.join(os.homedir(), 'Library', 'Caches', 'kaist-vpn-monitor');
const healthCheckOnly = process.argv.includes('--health-check');
const emit = result => process.stdout.write(JSON.stringify(result) + '\n');
let stage = 'prerequisites', attempts = 0, context, proxy, lock;
function stop(reason) {const error = new Error(reason);error.safeReason = reason;throw error;}
async function helper(name) {
  const bundled = path.resolve(scriptRoot, '..', 'bin', name);
  if (await fs.stat(bundled).catch(() => null)) return bundled;
  const source = path.join(scriptRoot, name + '.swift');
  const binary = path.join(runtime, name);
  const src = await fs.stat(source);
  const compiled = await fs.stat(binary).catch(() => null);
  if (!compiled || compiled.mtimeMs < src.mtimeMs) await run('/usr/bin/swiftc', [source, '-o', binary], {timeout:60000});
  return binary;
}
async function removePrivatePath(target) {
  try {await fs.unlink(target);}
  catch (error) {if (error.code !== 'ENOENT') throw error;}
}
async function waitConnectorOtp(scope) {
  const socketPath = path.join(runtime, 'connector-otp.sock');
  const requestPath = path.join(runtime, 'connector-otp-request.json');
  const expiresAtMs = Date.now() + 90000;
  const requestId = randomUUID();
  await removePrivatePath(socketPath);
  await removePrivatePath(requestPath);
  let server;
  try {
    return await new Promise((resolve, reject) => {
      let settled = false, timer;
      const finish = (error, code) => {
        if (settled) return;
        settled = true;
        if (timer) clearTimeout(timer);
        if (server?.listening) server.close(() => {});
        error ? reject(error) : resolve(code);
      };
      server = net.createServer(client => {
        let input = '', handled = false;
        client.setEncoding('utf8');
        client.setTimeout(2000,()=>client.destroy());
        client.on('error', () => {});
        client.on('data', chunk => {
          if (handled) return;
          input += chunk;
          if (input.length > 256) {handled = true;client.end('rejected\n');return;}
          const newline = input.indexOf('\n');
          if (newline < 0) return;
          handled = true;
          let message;
          try {message=JSON.parse(input.slice(0,newline));} catch {client.end('rejected\n');return;}
          if(!message||message.requestId!==requestId||Date.now()>=expiresAtMs){client.end('rejected\n');return;}
          const code = message.code;
          if (code === 'abort') {
            client.end('aborted\n');
            const error = new Error('connector_email_unavailable');
            error.safeReason = 'connector_email_unavailable';
            finish(error);
            return;
          }
          if (typeof code!=='string'||!/^\d{6}$/.test(code) || input.slice(newline + 1).trim()) {client.end('rejected\n');return;}
          client.end('accepted\n');
          finish(null,code);
        });
      });
      server.once('error', error => finish(error));
      server.listen(socketPath, async () => {
        try {
          await fs.chmod(socketPath,0o600);
          await fs.writeFile(requestPath,JSON.stringify({requestId,capturedAtMs:scope.capturedAtMs,expiresAtMs,otpSender:scope.otpSender}),{mode:0o600});
          await fs.chmod(requestPath,0o600);
          timer = setTimeout(() => {
            const error = new Error('connector_email_timeout');
            error.safeReason = 'connector_email_timeout';
            finish(error);
          },90000);
        } catch (error) {finish(error);}
      });
    });
  } finally {
    if (server?.listening) await new Promise(resolve => server.close(() => resolve()));
    await removePrivatePath(socketPath);
    await removePrivatePath(requestPath);
  }
}
async function nativeState(preflight) {return JSON.parse((await run(preflight, [], {timeout:10000})).stdout);}
async function launchIvanti(launcher) {
  try {
    const result = JSON.parse((await run(launcher, [], {timeout:10000,maxBuffer:8192})).stdout);
    return result.status === 'started';
  } catch {return false;}
}
async function restartIvanti(restart) {
  try {
    const result = JSON.parse((await run(restart, [], {timeout:15000,maxBuffer:8192})).stdout);
    return ['exited','already_exited'].includes(result.status);
  } catch {return false;}
}
async function exitIvanti(menuExit) {
  try {
    const result = JSON.parse((await run(menuExit, [], {timeout:20000,maxBuffer:8192})).stdout);
    return ['exited','already_exited'].includes(result.status);
  } catch {return false;}
}
async function readyNativeState(preflight, launcher) {
  let state = await nativeState(preflight);
  if (!state.axTrusted || state.ivantiRunning) return state;
  if (!await launchIvanti(launcher)) return state;
  for (let i = 0; i < 20; i++) {
    await delay(500);
    state = await nativeState(preflight);
    if (state.ivantiRunning && state.trayObserved && state.exactProfile) return state;
  }
  return state;
}
async function recoverNativeState(preflight, restart, menuExit, launcher) {
  // Preserve normal app termination as the first choice.  If it does not
  // complete, use the Ivanti status menu's exact Exit action once; the helper
  // never force-quits, touches services, activates a window, or emits input.
  if (!await restartIvanti(restart) && !await exitIvanti(menuExit)) return null;
  await delay(2000);
  return readyNativeState(preflight, launcher);
}
async function hideIvanti(hider) {
  // Window suppression is intentionally best-effort: it must never interrupt
  // authentication or change the connection outcome.
  await run(hider, [], {timeout:10000,maxBuffer:8192}).catch(() => {});
}
async function dismissNativeTimeout(dismissTimeout) {
  try {
    const result = JSON.parse((await run(dismissTimeout, [], {timeout:10000,maxBuffer:8192})).stdout);
    return ['dismissed','absent'].includes(result.status) ? result.status : 'unavailable';
  } catch {return 'unavailable';}
}
function nativeConnected(state) {
  return state.trayObserved && state.exactProfile && state.profileDisconnectAvailable && !state.profileConnectAvailable && !state.noActiveConnections;
}
function nativeInactive(state) {
  return state.trayObserved && state.exactProfile && state.noActiveConnections && state.profileConnectAvailable && !state.profileDisconnectAvailable;
}
async function verifySsh() {
  stage = 'ssh';
  try {await run('/usr/bin/ssh', ['-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ConnectionAttempts=1',loadSettings().sshTarget,'hostname'], {timeout:15000});}
  catch {stop('ssh_check_failed');}
}
async function authState(page) {
  return page.evaluate(() => {
    if (location.origin !== 'https://kvpn.kaist.ac.kr') return 'unexpected_origin';
    if (document.body.innerText.includes('Invalid username or password.')) return 'credentials_rejected';
    if (document.title === 'Confirmation') return 'confirmation';
    if (location.pathname === '/download/') return 'download';
    if (location.pathname.startsWith('/dana/user/')) return 'portal';
    return 'authentication';
  });
}
async function waitAuthentication(page) {
  await page.waitForFunction(() => document.title === 'Confirmation' || location.pathname === '/download/' || location.pathname.startsWith('/dana/user/') || document.body.innerText.includes('Invalid username or password.'), {}, {timeout:30000});
  let state = await authState(page);
  if (state === 'confirmation') {
    const message = await page.locator('body').innerText();
    if (!message.includes('Continue will result in termination of the other session.')) stop('unexpected_session_confirmation');
    // The user authorized reconnecting this account. Native preflight was inactive.
    // Handle the continuation immediately; do not leave the OTP challenge waiting.
    await page.getByRole('button', {name:'Continue the session',exact:true}).click();
    await page.waitForFunction(() => location.pathname === '/download/' || location.pathname.startsWith('/dana/user/') || document.body.innerText.includes('Invalid username or password.'), {}, {timeout:30000});
    state = await authState(page);
  }
  if (state === 'credentials_rejected') stop('credentials_rejected');
  if (!['portal','download'].includes(state)) stop('authentication_not_completed');
  await page.waitForFunction(() => location.pathname === '/download/' || !!document.getElementById('1-header'), {}, {timeout:15000});
}
async function authenticate(page) {
  for (const wait of [0,10000,30000]) {
    if (wait) await delay(wait);
    await page.goto(ORIGIN + '/', {waitUntil:'domcontentloaded'});
    if (new URL(page.url()).origin !== ORIGIN) stop('unexpected_login_origin');
    if (['portal','download'].includes(await authState(page))) return;
    if (await page.getByPlaceholder('User name',{exact:true}).count() !== 1 || await page.getByPlaceholder('Password',{exact:true}).count() !== 1) stop('unexpected_login_form');
    let secret = '', receipt;
    try {
      for (const [service,placeholder] of [['username','User name'],['password','Password']]) {
        if (!originIs(page.url(), ORIGIN)) stop('unexpected_login_origin');
        secret = (await run('/usr/bin/security', ['find-generic-password','-s','kaist-vpn-monitor.' + service,'-w'])).stdout.replace(/\n$/,'');
        if (!originIs(page.url(), ORIGIN)) stop('unexpected_login_origin');
        await page.getByPlaceholder(placeholder,{exact:true}).fill(secret);secret = '';
      }
      const realm = await page.locator('select').evaluateAll(es => es.map(e => e.selectedOptions[0]?.textContent.trim()));
      if (!realm.includes('KAIST Members')) stop('unexpected_realm');
      if (!originIs(page.url(), ORIGIN)) stop('unexpected_login_origin');
      const login = page.getByRole('button',{name:'LOGIN',exact:true});
      const destination = await login.evaluate(button => button.hasAttribute('formaction') ? button.formAction : button.form?.action || location.href);
      if (!originIs(destination, ORIGIN)) stop('unexpected_login_action');
      attempts++;
      await login.click();
      const frame = await emailFrame(page);
      const emailMethod = frame.locator('.email .title');
      if (await emailMethod.count() !== 1) stop('email_method_unavailable');
      if (!originIs(page.url(), ORIGIN) || !originIs(frame.url(), OTP_ORIGIN)) stop('unexpected_otp_origin');
      const scope = {capturedAtMs:Date.now(), otpSender:loadSettings().otpSender};
      await emailMethod.click();
      emit({status:'authenticating',stage:'email',attempts});
      try {
        receipt = {status:'received',code:await waitConnectorOtp(scope)};
      } catch (error) {
        const timedOut = error.safeReason === 'connector_email_timeout';
        if (timedOut && attempts < 3) continue;
        stop(timedOut ? 'connector_email_timeout' : 'connector_email_unavailable');
      }
      if (receipt.status !== 'received') stop('fresh_email_unavailable');
      if (!originIs(page.url(), ORIGIN) || frame.isDetached() || !originIs(frame.url(), OTP_ORIGIN)) stop('unexpected_otp_origin');
      try {await frame.getByRole('textbox').fill(receipt.code);} finally {receipt.code = '';}
      await frame.getByRole('button',{name:'Login',exact:true}).click();
      await waitAuthentication(page);
      return;
    } finally {secret = '';if (receipt) receipt.code = '';}
  }
  stop('authentication_attempts_exhausted');
}
async function handoff(page, launcher) {
  stage = 'launcher';
  const step = async (name, action) => {
    try {return await action();}
    catch {stop('launcher_' + name + '_failed');}
  };
  const seen = new Set();
  let delivered = false, deliveryFailed = false;
  const deliver = url => {
    if (!url.startsWith('pulsesecure:') || seen.has(url)) return;
    if (seen.size >= 3) {deliveryFailed = true;return;}
    seen.add(url);
    const child = spawn(launcher, [], {env:{KVPN_PRIVATE_PIPE:'1'},stdio:['pipe','pipe','ignore']});
    let output = '';
    child.stdout.on('data', chunk => output += chunk.toString());
    child.on('error', () => {deliveryFailed = true;});
    child.stdin.on('error', () => {deliveryFailed = true;});
    child.on('close', code => {
      try {delivered ||= code === 0 && JSON.parse(output).status === 'launcher_request_delivered';}
      catch {deliveryFailed = true;}
    });
    child.stdin.end(url);
  };
  const observe = async target => {
    const cdp = await context.newCDPSession(target);
    await cdp.send('Page.enable');
    const {frameTree} = await cdp.send('Page.getFrameTree');
    cdp.on('Page.frameRequestedNavigation', event => {
      if (allowedLauncher(event.url,target.url(),event.frameId,frameTree.frame.id)) deliver(event.url);
    });
  };
  await step('observe', () => observe(page));
  const awaitDelivery = async seconds => {
    for (let i=0;i<seconds && !delivered && !deliveryFailed;i++) await delay(1000);
    return delivered;
  };
  let portalLoadFailed = false;
  try {if(!await portalReady(page))await page.goto(ORIGIN + '/dana/user/', {waitUntil:'domcontentloaded'});}
  catch {portalLoadFailed = true;}
  // The portal can launch PulseApplicationLauncher immediately during this
  // navigation, which aborts Chromium's page load. Observe and hand off that
  // private URI before deciding the portal load failed.
  if (portalLoadFailed || seen.size) {
    if (await awaitDelivery(30)) return;
    stop(deliveryFailed ? 'launcher_delivery_failed' : 'launcher_portal_load_failed');
  }
  await step('client_section', () => page.locator('[id="1-header"]').waitFor({state:'visible',timeout:15000}));
  if (new URL(page.url()).origin !== ORIGIN) stop('unexpected_portal_origin');
  await step('client_section_validate', () => page.locator('[id="1-header"]').evaluate(h => {
    if (!/Client Application Sessions|클라이언트 응용프로그램 세션/.test(h.textContent)) throw new Error('Unexpected client section');
    if (h.nextElementSibling.classList.contains('collapsed')) h.click();
  }));
  await step('start_control', () => page.locator('#client_card_start_button').waitFor({state:'visible'}));
  await step('start_click', () => page.locator('#client_card_start_button').evaluate(e => e.click()));
  await awaitDelivery(30);
  if (!delivered) stop(deliveryFailed ? 'launcher_delivery_failed' : 'launcher_request_missing');
}
async function main() {
  loadSettings();
  if (!healthCheckOnly && !process.argv.includes('--connector-otp')) stop('use_monitor_for_recovery');
  await fs.mkdir(runtime,{recursive:true,mode:0o700});
  await fs.chmod(runtime,0o700);
  const lockPath = path.join(runtime,'run.lock');
  try {lock = await fs.open(lockPath,'wx',0o600);}
  catch (error) {
    if (error.code !== 'EEXIST') throw error;
    const owner = Number((await fs.readFile(lockPath,'utf8')).trim());
    if (!Number.isSafeInteger(owner) || owner <= 0) stop('lock_owner_unavailable');
    let ownerMissing = false;
    try {process.kill(owner,0);} catch (probe) {ownerMissing = probe.code === 'ESRCH';}
    if (!ownerMissing) stop('existing_run_lock');
    await fs.unlink(lockPath);
    lock = await fs.open(lockPath,'wx',0o600);
  }
  await lock.writeFile(String(process.pid));
  const preflight = await helper('preflight');
  if (healthCheckOnly) {
    stage = 'native';
    const state = await nativeState(preflight);
    if (!state.axTrusted) stop('accessibility_unavailable');
    if (nativeConnected(state)) {
      await verifySsh();
      emit({status:'connected',native:'SA',ssh:'ok',attempts:0,reusedConnection:true});
    } else {
      emit({status:'needs_recovery',stage:'native',reason:nativeInactive(state) ? 'native_inactive' : 'native_state_unavailable',attempts:0});
      process.exitCode = 2;
    }
    return;
  }
  const ivantiLauncher = await helper('launch-ivanti');
  const ivantiRestarter = await helper('restart-ivanti');
  const ivantiMenuExit = await helper('exit-ivanti');
  const ivantiHider = await helper('hide-ivanti');
  let initial = await readyNativeState(preflight,ivantiLauncher);
  if (!nativeConnected(initial)) await hideIvanti(ivantiHider);
  if (!nativeConnected(initial) && !nativeInactive(initial) && initial.axTrusted && initial.ivantiRunning) {
    const recovered = await recoverNativeState(preflight,ivantiRestarter,ivantiMenuExit,ivantiLauncher);
    if (!recovered) stop('native_restart_failed');
    initial = recovered;
  }
  if (!nativeConnected(initial)) await hideIvanti(ivantiHider);
  if (!initial.axTrusted || !initial.trayObserved || !initial.exactProfile) stop('native_state_unavailable');
  if (nativeConnected(initial)) {
    await verifySsh();emit({status:'connected',native:'SA',ssh:'ok',attempts:0,reusedConnection:true});return;
  }
  if (!nativeInactive(initial)) stop('native_state_indeterminate');
  const launcher = await helper('open-launcher');
  const dismissTimeout = await helper('dismiss-timeout');
  stage = 'browser';
  const {chromium} = require('playwright-core');
  proxy = await startVpnProxy();
  context = await chromium.launchPersistentContext(path.join(runtime,'chrome-profile'),{channel:'chrome',headless:true,chromiumSandbox:true,serviceWorkers:'block',proxy:{server:proxy.url,bypass:'<-loopback>'},args:['--disable-quic'],viewport:{width:1280,height:900}});
  await context.route('**/*', route => {
    const request = route.request();
    let mainNavigation;
    try {mainNavigation = request.isNavigationRequest() && !request.frame().parentFrame();}
    catch {return route.abort();}
    return allowedRequest(request.url(),mainNavigation) ? route.continue() : route.abort();
  });
  const page = context.pages()[0] || await context.newPage();page.setDefaultTimeout(15000);
  page.on('dialog', dialog => dialog.dismiss().catch(() => {}));
  stage = 'authentication';
  await authenticate(page);
  await handoff(page,launcher);
  await delay(1000);
  await hideIvanti(ivantiHider);
  stage = 'native';
  let connected = false;
  const nativeDeadline = Date.now() + 180000;
  while (Date.now() < nativeDeadline) {
    if (nativeConnected(await nativeState(preflight))) {connected = true;break;}
    // A post-launch 1382 sheet can mask the tray's Disconnect item even when
    // the native SA connection has succeeded.  Dismiss only that exact sheet;
    // never press Retry or interact with any credential/OTP UI.
    if (await dismissNativeTimeout(dismissTimeout) === 'dismissed') {
      await delay(250);
      continue;
    }
    await delay(1000);
  }
  if (!connected) stop('native_connection_not_verified');
  await verifySsh();
  emit({status:'connected',native:'SA',ssh:'ok',attempts,reusedConnection:false});
}
main().catch(error => {
  emit({status:'blocked',stage,reason:error.safeReason || 'operation_failed',attempts});process.exitCode = 1;
}).finally(async () => {
  if (context) await context.close().catch(() => {});
  if (proxy) await proxy.close().catch(() => {});
  if (lock) {await lock.close();await fs.unlink(path.join(runtime,'run.lock'));}
});

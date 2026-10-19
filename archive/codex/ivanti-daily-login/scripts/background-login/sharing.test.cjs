'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {execFileSync} = require('node:child_process');
const {validateSettings} = require('./settings.cjs');
const {allowedRequest, allowedLauncher} = require('./browser-policy.cjs');

test('SSH settings reject options, shell text and missing values', () => {
  for (const sshTarget of ['', '-oProxyCommand=anything', 'lab host', 'lab;whoami', 'lab\nother', undefined]) {
    assert.throws(() => validateSettings({sshTarget, codexBinary:'/usr/local/bin/codex', otpSender:'vpn@example.invalid'}));
  }
  assert.equal(validateSettings({sshTarget:'lab-vpn-check', codexBinary:'/usr/local/bin/codex', otpSender:'vpn@example.invalid'}).sshTarget, 'lab-vpn-check');
  assert.throws(() => validateSettings({sshTarget:'lab', codexBinary:'codex'}));
});

test('--status is read-only and works before setup', () => {
  const home = fs.mkdtempSync(path.join(os.tmpdir(), 'vpn-status-test-'));
  try {
    const output = execFileSync(process.execPath, [path.join(__dirname, 'monitor.cjs'), '--status'], {env:{...process.env, HOME:home}, encoding:'utf8'});
    assert.deepEqual(JSON.parse(output), {});
    assert.deepEqual(fs.readdirSync(home), []);
  } finally {fs.rmSync(home, {recursive:true, force:true});}
});

test('missing configuration stops before native access or authentication', () => {
  const home = fs.mkdtempSync(path.join(os.tmpdir(), 'vpn-config-test-'));
  try {
    assert.throws(() => execFileSync(process.execPath, [path.join(__dirname, 'run.cjs')], {env:{...process.env, HOME:home}, encoding:'utf8'}), error => {
      const result = JSON.parse(error.stdout);
      assert.equal(result.reason, 'settings_unavailable');
      assert.equal(result.attempts, 0);
      return error.status === 1;
    });
    assert.deepEqual(fs.readdirSync(home), []);
  } finally {fs.rmSync(home, {recursive:true, force:true});}
});

test('agent setup writes only nonsecret local configuration with private permissions', () => {
  const home = fs.mkdtempSync(path.join(os.tmpdir(), 'vpn-setup-test-'));
  try {
    execFileSync(process.execPath, [path.resolve(__dirname, '../../setup.cjs'), '--ssh-target', 'lab-vpn-check', '--codex', process.execPath, '--otp-sender', 'vpn@example.invalid'], {env:{...process.env, HOME:home}, encoding:'utf8'});
    const config = path.join(home, '.config/kaist-vpn-monitor/config.json');
    assert.deepEqual(JSON.parse(fs.readFileSync(config)), {sshTarget:'lab-vpn-check', codexBinary:process.execPath, otpSender:'vpn@example.invalid'});
    assert.equal(fs.statSync(config).mode & 0o777, 0o600);
    assert.equal(fs.statSync(path.dirname(config)).mode & 0o777, 0o700);
    assert.equal(fs.existsSync(path.join(home, 'Applications')), false);
  } finally {fs.rmSync(home, {recursive:true, force:true});}
});


test('browser policy rejects outside origins and untrusted native initiators', () => {
  assert.equal(allowedRequest('https://kvpn.kaist.ac.kr/login', true), true);
  assert.equal(allowedRequest('https://kvpnportal.kaist.ac.kr:8443/otp', false), true);
  for (const url of ['https://kvpn.kaist.ac.kr.evil.invalid/', 'https://kvpn.kaist.ac.kr@evil.invalid/', 'http://kvpn.kaist.ac.kr/', 'https://evil.invalid/']) {
    assert.equal(allowedRequest(url, false), false);
  }
  assert.equal(allowedRequest('https://kvpnportal.kaist.ac.kr:8443/otp', true), false);
  assert.equal(allowedLauncher('pulsesecure:synthetic', 'https://kvpn.kaist.ac.kr/dana/user/', 'main', 'main'), true);
  assert.equal(allowedLauncher('pulsesecure:synthetic', 'https://kvpn.kaist.ac.kr/dana/user/', 'child', 'main'), false);
  assert.equal(allowedLauncher('pulsesecure:synthetic', 'https://evil.invalid/', 'main', 'main'), false);
});

test('a submission bound to an old request cannot use the current request file', () => {
  const home = fs.mkdtempSync(path.join(os.tmpdir(), 'vpn-request-test-'));
  try {
    const runtime = path.join(home,'Library/Caches/kaist-vpn-monitor');
    fs.mkdirSync(runtime,{recursive:true});
    fs.writeFileSync(path.join(runtime,'connector-otp-request.json'),JSON.stringify({requestId:'new',capturedAtMs:Date.now(),expiresAtMs:Date.now()+90000,otpSender:'vpn@example.invalid'}));
    assert.throws(()=>execFileSync(process.execPath,[path.join(__dirname,'submit-connector-gmail-otp.cjs'),'--request-id','old','--received-at-ms',String(Date.now())],{env:{...process.env,HOME:home},encoding:'utf8'}),error=>{
      assert.equal(JSON.parse(error.stdout).status,'stale_request');
      return error.status===1;
    });
  } finally {fs.rmSync(home,{recursive:true,force:true});}
});

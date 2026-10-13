#!/usr/bin/env node
'use strict';
const fs = require('node:fs/promises');
const path = require('node:path');
const os = require('node:os');
const {execFileSync} = require('node:child_process');
const {loadSettings} = require('./scripts/background-login/settings.cjs');
const identifier = 'local.kaist.vpn-monitor.community';
const app = path.join(os.homedir(), 'Applications', 'KAIST VPN Monitor Community.app');
const binary = path.join(app, 'Contents', 'MacOS', 'kaist-vpn-monitor');
const plist = path.join(os.homedir(), 'Library', 'LaunchAgents', identifier+'.plist');
const domain = 'gui/'+process.getuid();
const state = path.join(os.homedir(), '.local', 'state', 'kaist-vpn-monitor');
function run(command, args) {return execFileSync(command, args, {stdio:'pipe'});}
async function writePlist(destination, value) {
  await fs.writeFile(destination, JSON.stringify(value));
  run('/usr/bin/plutil', ['-convert', 'xml1', destination]);
}
async function build(destination) {
  try {await fs.access(destination); throw new Error('Destination already exists; no files replaced.');}
  catch (error) {if (error.code !== 'ENOENT') throw error;}
  const dependency = path.join(__dirname, 'scripts', 'background-login', 'node_modules', 'playwright-core', 'package.json');
  await fs.access(dependency);
  const contents = path.join(destination, 'Contents');
  await fs.mkdir(path.join(contents, 'MacOS'), {recursive:true});
  await fs.mkdir(path.join(contents, 'Resources'), {recursive:true});
  // npm bin symlinks must not point back outside the installed app bundle.
  await fs.cp(path.join(__dirname, 'scripts'), path.join(contents, 'Resources', 'scripts'), {recursive:true, dereference:true});
  run('/usr/bin/swiftc', [path.join(__dirname, 'scripts/background-login/monitor-launcher.swift'), '-o', path.join(contents, 'MacOS/kaist-vpn-monitor')]);
  // Compile helpers before enabling the schedule, so recovery needs no compiler.
  const bin = path.join(contents, 'Resources', 'bin');
  await fs.mkdir(bin);
  for (const file of await fs.readdir(path.join(__dirname, 'scripts'))) {
    if (file.endsWith('.swift')) run('/usr/bin/swiftc', [path.join(__dirname, 'scripts', file), '-o', path.join(bin, file.slice(0,-6))]);
  }
  await writePlist(path.join(contents, 'Info.plist'), {
    CFBundleIdentifier:identifier, CFBundleName:'KAIST VPN Monitor Community',
    CFBundleDisplayName:'KAIST VPN Monitor Community', CFBundleExecutable:'kaist-vpn-monitor',
    CFBundlePackageType:'APPL', CFBundleVersion:'1', LSUIElement:true,
    MonitorNodePath:process.execPath,
  });
  run('/usr/bin/codesign', ['--force', '--deep', '--sign', '-', destination]);
}
async function main() {
  if (process.platform !== 'darwin') throw new Error('macOS is required.');
  const [major,minor] = process.versions.node.split('.').map(Number);
  if(major<22||(major===22&&minor<19))throw new Error('Node.js 22.19 or newer is required.');
  const args = process.argv.slice(2);
  if (args.length === 2 && args[0] === '--build') {
    await build(path.resolve(args[1]));
    console.log('Build complete. Nothing installed or scheduled.');
    return;
  }
  if (args.length !== 1 || !['--install','--enable','--disable'].includes(args[0])) {
    throw new Error('Usage: node install.cjs --install | --enable | --disable | --build OUTPUT.app');
  }
  if (args[0] === '--disable') {
    run('/bin/launchctl', ['disable', domain+'/'+identifier]);
    try {run('/bin/launchctl', ['bootout', domain+'/'+identifier]);}
    catch {
      // An already-unloaded job is also stopped. Verify instead of hiding errors.
      let loaded = false;
      try {run('/bin/launchctl', ['print', domain+'/'+identifier]); loaded = true;} catch {}
      if (loaded) throw new Error('The job is still loaded; stop was not confirmed.');
    }
    console.log('Schedule stopped. The current VPN connection is unchanged.');
    return;
  }
  if (args[0] === '--install') {
    await build(app);
    console.log('App installed, schedule OFF. Grant Accessibility, configure local settings and Keychain, then verify --check-only.');
    return;
  }
  loadSettings();
  await fs.access(binary, fs.constants.X_OK);
  await fs.mkdir(state, {recursive:true, mode:0o700});
  await fs.chmod(state, 0o700);
  await fs.mkdir(path.dirname(plist), {recursive:true});
  await writePlist(plist, {
    Label:identifier, AssociatedBundleIdentifiers:[identifier], ProgramArguments:[binary,'--scheduled'],
    StartInterval:300, RunAtLoad:true, ProcessType:'Background', Nice:19,
    LowPriorityIO:true, LowPriorityBackgroundIO:true,
    EnvironmentVariables:{PATH:[path.dirname(process.execPath),path.dirname(loadSettings().codexBinary),'/opt/homebrew/bin','/usr/local/bin','/usr/bin','/bin','/usr/sbin','/sbin'].join(':')},
    StandardOutPath:'/dev/null', StandardErrorPath:path.join(state, 'launchd-error.log'),
  });
  run('/bin/launchctl', ['enable', domain+'/'+identifier]);
  run('/bin/launchctl', ['bootstrap', domain, plist]);
  console.log('5-minute schedule enabled, including at user login. Check --status after the first run.');
}
main().catch(error => {
  console.error(error.status !== undefined ? 'Build or launchctl failed; schedule success is not confirmed.' : error.message);
  process.exitCode=1;
});

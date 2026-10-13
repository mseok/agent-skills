#!/usr/bin/env node
'use strict';
const fs = require('node:fs/promises');
const path = require('node:path');
const readline = require('node:readline/promises');
const {execFileSync} = require('node:child_process');
const {settingsPath, validateSettings} = require('./scripts/background-login/settings.cjs');

async function main() {
  if (process.platform !== 'darwin') throw new Error('macOS is required.');
  const prompt = readline.createInterface({input:process.stdin, output:process.stdout});
  try {
    let codex = '';
    try {codex = execFileSync('/usr/bin/which', ['codex'], {encoding:'utf8'}).trim();} catch {}
    const sshTarget = (await prompt.question('VPN으로 접근할 SSH 별칭 (예: lab-vpn-check): ')).trim();
    const codexBinary = (await prompt.question(`Codex 실행 파일 절대 경로${codex ? ` [${codex}]` : ''}: `)).trim() || codex;
    const settings = validateSettings({sshTarget, codexBinary});
    await fs.access(settings.codexBinary, fs.constants.X_OK);
    await fs.mkdir(path.dirname(settingsPath), {recursive:true, mode:0o700});
    await fs.chmod(path.dirname(settingsPath), 0o700);
    await fs.writeFile(settingsPath, JSON.stringify(settings, null, 2)+'\n', {mode:0o600});
    await fs.chmod(settingsPath, 0o600);
    console.log('로컬 설정을 저장했습니다. VPN 로그인이나 자동 실행은 시작하지 않았습니다.');
  } finally {prompt.close();}
}
main().catch(error => {console.error(error.message); process.exitCode=1;});

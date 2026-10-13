'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {execFileSync} = require('node:child_process');
const {validateSettings} = require('./settings.cjs');
const {validateMessage, fnv1a} = require('./submit-connector-gmail-otp.cjs');

test('SSH settings reject options, shell text and missing values', () => {
  for (const sshTarget of ['', '-oProxyCommand=anything', 'lab host', 'lab;whoami', 'lab\nother', undefined]) {
    assert.throws(() => validateSettings({sshTarget, codexBinary:'/usr/local/bin/codex'}));
  }
  assert.equal(validateSettings({sshTarget:'lab-vpn-check', codexBinary:'/usr/local/bin/codex'}).sshTarget, 'lab-vpn-check');
  assert.throws(() => validateSettings({sshTarget:'lab', codexBinary:'codex'}));
});

test('OTP bridge accepts only the pinned sender, time window and exact template', () => {
  // Synthetic test data only; no real sender or message is stored here.
  const scope = {senderHash:fnv1a('vpn@example.invalid'), capturedAtMs:100000, expiresAtMs:190000};
  const encode = value => Buffer.from(value).toString('base64url');
  const raw = encode('From: vpn@example.invalid\r\n\r\nKVPN OTP number: 123456');
  assert.equal(validateMessage(raw, 110000, scope), '123456');
  assert.throws(() => validateMessage(raw, 97000, scope), /stale_message/);
  assert.throws(() => validateMessage(raw, 190001, scope), /stale_message/);
  assert.throws(() => validateMessage(raw, 110000, {...scope, senderHash:fnv1a('other@example.invalid')}), /sender_mismatch/);
  assert.throws(() => validateMessage(encode('From: vpn@example.invalid\r\n\r\nOther number: 123456'), 110000, scope), /template_mismatch/);
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

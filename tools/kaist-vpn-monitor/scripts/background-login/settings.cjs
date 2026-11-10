'use strict';
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const settingsPath = path.join(os.homedir(), '.config', 'kaist-vpn-monitor', 'config.json');

function validateSettings(value) {
  if (!value || typeof value.sshTarget !== 'string' ||
      !/^[a-zA-Z0-9][a-zA-Z0-9_.@-]*$/.test(value.sshTarget)) {
    throw new Error('SSH target must be an existing SSH config alias or user@host, without options.');
  }
  if (typeof value.codexBinary !== 'string' || !path.isAbsolute(value.codexBinary)) {
    throw new Error('Codex executable must be an absolute path.');
  }
  if (typeof value.otpSender !== 'string' || !/^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}$/.test(value.otpSender)) {
    throw new Error('OTP sender must be the exact mailbox from a user-verified legitimate KVPN email.');
  }
  // Optional SMS OTP fallback: the phone forwards the KVPN SMS code to this host over Tailscale.
  let smsOtp = null;
  if (value.smsOtp !== undefined) {
    const {listen, port, phone} = value.smsOtp || {};
    const tailnet = address => typeof address === 'string' &&
      /^100\.(6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d{1,3}\.\d{1,3}$/.test(address) &&
      address.split('.').every(part => Number(part) <= 255);
    if (!tailnet(listen) || !tailnet(phone) || !Number.isInteger(port) || port < 1024 || port > 65535) {
      throw new Error('SMS OTP needs Tailscale listen and phone addresses and a port from 1024 to 65535.');
    }
    smsOtp = {listen, port, phone};
  }
  return {sshTarget:value.sshTarget, codexBinary:value.codexBinary, otpSender:value.otpSender.toLowerCase(), smsOtp};
}
function loadSettings() {
  try {return validateSettings(JSON.parse(fs.readFileSync(settingsPath, 'utf8')));}
  catch {
    const error = new Error('settings_unavailable');
    error.safeReason = 'settings_unavailable';
    throw error;
  }
}
module.exports = {settingsPath, validateSettings, loadSettings};

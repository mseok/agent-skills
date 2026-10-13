#!/usr/bin/env node
'use strict';
// Accept Gmail's raw message only through stdin, validate it locally, and
// forward its OTP over the task-owned Unix socket.  It never writes the raw
// message or OTP to stdout, stderr, command-line arguments, or disk.
const fs = require('node:fs/promises');
const net = require('node:net');
const os = require('node:os');
const path = require('node:path');

const runtime = path.join(os.homedir(), 'Library', 'Caches', 'kaist-vpn-monitor');
const requestPath = path.join(runtime, 'connector-otp-request.json');
const emit = value => process.stdout.write(JSON.stringify(value) + '\n');

function fnv1a(value) {
  let hash = 14695981039346656037n;
  for (const byte of Buffer.from(value,'utf8')) {
    hash ^= BigInt(byte);
    hash = BigInt.asUintN(64,hash * 1099511628211n);
  }
  return hash.toString(16);
}
function fail(reason) {
  emit({status:reason});
  process.exitCode = 1;
}
async function request() {
  try {
    const value = JSON.parse(await fs.readFile(requestPath,'utf8'));
    if (!Number.isSafeInteger(value.capturedAtMs) || !Number.isSafeInteger(value.expiresAtMs) || typeof value.senderHash !== 'string' || Date.now() > value.expiresAtMs) throw new Error('expired');
    return value;
  } catch {return null;}
}
async function readLine() {
  return new Promise((resolve,reject) => {
    let data = '';
    const isTTY = process.stdin.isTTY;
    if (isTTY) process.stdin.setRawMode(true);
    const cleanup = () => {
      process.stdin.off('data',onData);
      process.stdin.off('error',onError);
      if (isTTY) process.stdin.setRawMode(false);
    };
    const onError = error => {cleanup();reject(error);};
    const onData = chunk => {
      data += chunk.toString('utf8');
      if (data.length > 1048576) {cleanup();reject(new Error('input_too_large'));return;}
      const newline = data.indexOf('\n');
      if (newline < 0) return;
      const line = data.slice(0,newline).trim();
      cleanup();
      resolve(line);
    };
    process.stdin.on('data',onData);
    process.stdin.once('error',onError);
    process.stdin.resume();
  });
}
async function submit(socketPath, code) {
  return new Promise((resolve,reject) => {
    const socket = net.createConnection(socketPath);
    let response = '';
    socket.setTimeout(10000);
    socket.setEncoding('utf8');
    socket.on('connect', () => socket.end(code + '\n'));
    socket.on('data', chunk => response += chunk);
    socket.on('timeout', () => socket.destroy(new Error('timeout')));
    socket.on('error', reject);
    socket.on('close', () => response.trim() === 'accepted' ? resolve() : reject(new Error('rejected')));
  });
}
function validateMessage(encoded, receivedAtMs, current) {
  if (!Number.isSafeInteger(receivedAtMs) || receivedAtMs < current.capturedAtMs - 2000 || receivedAtMs > current.expiresAtMs) throw new Error('stale_message');
  let raw = Buffer.from(encoded,'base64url').toString('utf8');
  const from = raw.match(/^From:[ \t]*([^\r\n]*(?:\r?\n[ \t]+[^\r\n]*)*)/mi);
  if (!from || fnv1a(from[1].replace(/\s+/g,' ').trim().toLowerCase()) !== current.senderHash) throw new Error('sender_mismatch');
  const otp = raw.match(/KVPN\s+OTP\s+number[\s\S]{0,4096}?(?<![0-9])([0-9]{6})(?![0-9])/i)?.[1];
  raw = '';
  if (!otp) throw new Error('template_mismatch');
  return otp;
}
async function main() {
  const current = await request();
  if (!current) return fail('request_unavailable');
  if (process.argv.includes('--request')) {
    emit({status:'ready',capturedAtMs:current.capturedAtMs,expiresAtMs:current.expiresAtMs});
    return;
  }
  // Gmail's raw message date may be the sender's header time rather than the
  // connector's receipt time.  The caller supplies the connector search
  // result's received time, which is the timestamp used to select a fresh
  // candidate for this one-time request.
  const receivedAtMs = Number(process.argv[process.argv.indexOf('--received-at-ms') + 1]);
  if (!Number.isSafeInteger(receivedAtMs) || receivedAtMs < current.capturedAtMs - 2000 || receivedAtMs > current.expiresAtMs) return fail('stale_message');
  let encoded;
  try {encoded = await readLine();} catch {return fail('input_unavailable');}
  let otp;
  try {otp = validateMessage(encoded,receivedAtMs,current);}
  catch(error) {return fail(['stale_message','sender_mismatch','template_mismatch'].includes(error.message) ? error.message : 'message_unavailable');}
  finally {encoded = '';}
  try {await submit(path.join(runtime,'connector-otp.sock'),otp);}
  finally {otp = '';}
  emit({status:'submitted'});
}
if (require.main === module) main().catch(() => fail('submit_failed'));
module.exports = {validateMessage,fnv1a};

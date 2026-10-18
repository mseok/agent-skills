#!/usr/bin/env node
'use strict';
// Accept Gmail's raw message only through stdin, validate it locally, and
// forward its OTP over the task-owned Unix socket.  It never writes the raw
// message or OTP to stdout, stderr, command-line arguments, or disk.
const fs = require('node:fs/promises');
const net = require('node:net');
const os = require('node:os');
const path = require('node:path');

const {validateMessage} = require('./verify-email.cjs');
const runtime = path.join(os.homedir(), 'Library', 'Caches', 'codex-ivanti-background-secure-v021');
const requestPath = path.join(runtime, 'connector-otp-request.json');
const emit = value => process.stdout.write(JSON.stringify(value) + '\n');

function fail(reason) {
  emit({status:reason});
  process.exitCode = 1;
}
async function request() {
  try {
    const value = JSON.parse(await fs.readFile(requestPath,'utf8'));
    if (typeof value.requestId!=='string'||!Number.isSafeInteger(value.capturedAtMs) || !Number.isSafeInteger(value.expiresAtMs) || typeof value.otpSender !== 'string' || Date.now() > value.expiresAtMs) throw new Error('expired');
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
async function submit(socketPath, code, requestId) {
  return new Promise((resolve,reject) => {
    const socket = net.createConnection(socketPath);
    let response = '';
    socket.setTimeout(10000);
    socket.setEncoding('utf8');
    socket.on('connect', () => socket.end(JSON.stringify({requestId,code}) + '\n'));
    socket.on('data', chunk => response += chunk);
    socket.on('timeout', () => socket.destroy(new Error('timeout')));
    socket.on('error', reject);
    socket.on('close', () => response.trim() === 'accepted' ? resolve() : reject(new Error('rejected')));
  });
}
async function main() {
  const current = await request();
  if (!current) return fail('request_unavailable');
  if (process.argv.includes('--request')) {
    emit({status:'ready',capturedAtMs:current.capturedAtMs,expiresAtMs:current.expiresAtMs});
    return;
  }
  const expectedRequestId=process.argv[process.argv.indexOf('--request-id')+1];
  if(expectedRequestId!==current.requestId)return fail('stale_request');
  // Gmail's raw message date may be the sender's header time rather than the
  // connector's receipt time.  The caller supplies the connector search
  // result's received time, which is the timestamp used to select a fresh
  // candidate for this one-time request.
  const receivedAtMs = Number(process.argv[process.argv.indexOf('--received-at-ms') + 1]);
  if (!Number.isSafeInteger(receivedAtMs) || receivedAtMs < current.capturedAtMs - 2000 || receivedAtMs > current.expiresAtMs) return fail('stale_message');
  let encoded;
  try {encoded = await readLine();} catch(error) {return fail(error.message==='input_too_large'?'message_unavailable':'input_unavailable');}
  let otp;
  try {otp = await validateMessage(encoded,receivedAtMs,current);}
  catch(error) {return fail(['stale_message','sender_mismatch','template_mismatch','email_authentication_failed'].includes(error.message) ? error.message : 'message_unavailable');}
  finally {encoded = '';}
  try {
    if(Date.now()>=current.expiresAtMs)return fail('stale_request');
    await submit(path.join(runtime,'connector-otp.sock'),otp,current.requestId);
  }
  finally {otp = '';}
  emit({status:'submitted'});
}
if (require.main === module) main().catch(() => fail('submit_failed'));
module.exports = {validateMessage};

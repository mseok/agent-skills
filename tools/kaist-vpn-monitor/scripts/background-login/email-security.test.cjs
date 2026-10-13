'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const {generateKeyPairSync} = require('node:crypto');
const {dkimSign} = require('mailauth/lib/dkim/sign');
const {validateMessage} = require('./verify-email.cjs');
const {bridgeOtp,submit} = require('./monitor.cjs');

// Disposable keys and synthetic mail only. No private key is stored or printed.
const keys = generateKeyPairSync('rsa', {modulusLength:2048});
const privateKey = keys.privateKey.export({format:'pem',type:'pkcs8'});
const publicKey = keys.publicKey.export({format:'der',type:'spki'}).toString('base64');
const now = Date.now();
const scope = {otpSender:'vpn@example.invalid', capturedAtMs:now, expiresAtMs:now+90000};
const resolver = async (name,type) => {
  assert.equal(type,'TXT');
  assert.equal(name,'vpn._domainkey.example.invalid');
  return [['v=DKIM1; k=rsa; p='+publicKey]];
};
const encode = raw => Buffer.from(raw).toString('base64url');
async function fixture(options = {}) {
  const body = options.body || 'KVPN OTP number: 123456\r\n';
  const message = 'From: vpn@example.invalid\r\nDate: '+new Date(now).toUTCString()+'\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: base64\r\n\r\n'+Buffer.from(body).toString('base64')+'\r\n';
  const signature = await dkimSign(message, {
    signTime:new Date(options.signTime || now),
    headerList:options.headerList || 'from:date:mime-version:content-type:content-transfer-encoding',
    signatureData:[{signingDomain:options.domain || 'example.invalid', selector:'vpn', privateKey, ...options.signature}],
  });
  assert.equal(signature.errors.length,0);
  return signature.signatures+message;
}

test('fresh fully signed MIME mail validates using synthetic DNS keys', async () => {
  assert.equal(await validateMessage(encode(await fixture()),now,scope,{resolver}),'123456');
});

test('unsigned spoofing and forged authentication-result headers cannot choose an OTP', async () => {
  const raw = 'From: vpn@example.invalid\r\nAuthentication-Results: mx.google.com; dkim=pass\r\n\r\nKVPN OTP number: 654321';
  await assert.rejects(validateMessage(encode(raw),now,scope,{resolver}), /email_authentication_failed/);
});

test('stale signatures, l= body limits, unsigned MIME interpretation and wrong signer fail closed', async () => {
  for (const options of [
    {signTime:now-121000}, {signature:{maxBodyLength:4}},
    {headerList:'from:date'}, {domain:'attacker.invalid'},
  ]) await assert.rejects(validateMessage(encode(await fixture(options)),now,scope,{resolver}), /email_authentication_failed/);
});

test('duplicate sender or MIME headers and a modified signed body are rejected', async () => {
  const signed = await fixture();
  for (const header of ['From: attacker@example.invalid','Content-Type: text/html','Content-Transfer-Encoding: 7bit','MIME-Version: 1.0']) {
    await assert.rejects(validateMessage(encode(header+'\r\n'+signed),now,scope,{resolver}), /message_unavailable/);
  }
  for (const header of ['Content-Type : text/html','X-Extra: ok\nFrom: attacker@example.invalid','NoColon']) {
    await assert.rejects(validateMessage(encode(header+'\r\n'+signed),now,scope,{resolver}), /message_unavailable/);
  }
  await assert.rejects(validateMessage(encode(signed+'extra'),now,scope,{resolver}), /email_authentication_failed/);
});

test('time window, enrolled sender and body template remain required', async () => {
  const signed = encode(await fixture());
  await assert.rejects(validateMessage(signed,now-2001,scope,{resolver}), /stale_message/);
  await assert.rejects(validateMessage(signed,scope.expiresAtMs+1,scope,{resolver}), /stale_message/);
  await assert.rejects(validateMessage(signed,now,{...scope,otpSender:'other@example.invalid'},{resolver}), /sender_mismatch/);
  await assert.rejects(validateMessage(encode(await fixture({body:'Other number: 123456'})),now,scope,{resolver}), /template_mismatch/);
});

test('an invalid candidate is skipped so a later valid candidate can succeed', async () => {
  const seen = [];
  const client = {
    candidates:async () => [{id:'invalid',email_ts:String(now)},{id:'valid',email_ts:String(now)}],
    raw:async id => {seen.push(id);return id;},
  };
  await bridgeOtp(client, {request:async () => scope, submit:async raw => raw === 'valid'});
  assert.deepEqual(seen,['invalid','valid']);
});

test('an IPC failure still aborts rather than being treated as invalid mail', async () => {
  const client = {candidates:async () => [{id:'valid',email_ts:String(now)}],raw:async () => 'valid'};
  await assert.rejects(bridgeOtp(client, {request:async () => scope,submit:async () => {throw new Error('otp_submit_unavailable');}}), /otp_submit_unavailable/);
});

test('oversized candidates are skippable before IPC', async () => {
  assert.equal(await submit('A'.repeat(1048577),now,scope),false);
});

test('a candidate fetched after expiry is not submitted to a later challenge', async () => {
  let submitted = false;
  const request = {...scope};
  const client = {
    candidates:async () => [{id:'valid',email_ts:String(now)}],
    raw:async () => {request.expiresAtMs=Date.now()-1;return 'valid';},
  };
  await bridgeOtp(client,{request:async()=>request,submit:async()=>{submitted=true;return true;}});
  assert.equal(submitted,false);
});

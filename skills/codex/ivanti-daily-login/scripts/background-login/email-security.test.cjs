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
    raw:async id => {seen.push(id);return {raw:id,receivedAtMs:now};},
  };
  await bridgeOtp(client, {request:async () => scope, submit:async raw => raw === 'valid'});
  assert.deepEqual(seen,['invalid','valid']);
});

test('an IPC failure still aborts rather than being treated as invalid mail', async () => {
  const client = {candidates:async () => [{id:'valid',email_ts:String(now)}],raw:async () => ({raw:'valid',receivedAtMs:now})};
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
    raw:async () => {request.expiresAtMs=Date.now()-1;return {raw:'valid',receivedAtMs:now};},
  };
  await bridgeOtp(client,{request:async()=>request,submit:async()=>{submitted=true;return true;}});
  assert.equal(submitted,false);
});

async function kaistFixture(body = '<p>Authentication code: 123456</p>\r\n', headerList = 'from:subject:message-id') {
  const message = 'From: vpn@example.invalid\r\nSubject: Your KVPN OTP number\r\nMessage-ID: <fixture@example.invalid>\r\nDate: '+new Date(now).toUTCString()+'\r\nMIME-Version: 1.0\r\nContent-Type: text/html\r\nContent-Transfer-Encoding: 7bit\r\n\r\n'+body;
  // A negative signing date deliberately omits optional t= in mailauth.
  const signature = await dkimSign(message, {signTime:new Date(-1000),headerList,
    signatureData:[{signingDomain:'example.invalid',selector:'vpn',privateKey}]});
  assert.ok(signature.signatures);
  assert.ok(!/\bt=/.test(signature.signatures));
  return signature.signatures+message;
}

test('KVPN signed subject and ASCII body work without unsigned MIME or Date trust', async () => {
  const signed=await kaistFixture();
  assert.equal(await validateMessage(encode(signed),now,scope,{resolver}),'123456');
  const modified=signed.replace('Content-Type: text/html','Content-Type: multipart/mixed; boundary=attacker').replace('Content-Transfer-Encoding: 7bit','Content-Transfer-Encoding: base64').replace('Date: '+new Date(now).toUTCString(),'Date: Thu, 01 Jan 1970 00:00:00 GMT');
  assert.equal(await validateMessage(encode(modified),now,scope,{resolver}),'123456');
  await assert.rejects(validateMessage(encode(signed),NaN,scope,{resolver}),/stale_message/);
  await assert.rejects(validateMessage(encode(signed),now-2001,scope,{resolver}),/stale_message/);
});

test('KVPN fallback rejects unsigned subject, ambiguous or encoded body, and mutations', async () => {
  await assert.rejects(validateMessage(encode(await kaistFixture(undefined,'from:message-id')),now,scope,{resolver}),/email_authentication_failed/);
  for(const body of ['123456 654321\r\n','no code\r\n','é 123456\r\n',Buffer.from('123456').toString('base64')+'\r\n']) {
    await assert.rejects(validateMessage(encode(await kaistFixture(body)),now,scope,{resolver}),/template_mismatch/);
  }
  const signed=await kaistFixture();
  await assert.rejects(validateMessage(encode('Subject: Your KVPN OTP number\r\n'+signed),now,scope,{resolver}),/message_unavailable/);
  await assert.rejects(validateMessage(encode(signed.replace('code: 123456','code: 654321')),now,scope,{resolver}),/email_authentication_failed/);
});

test('bridge uses trusted internal receipt and ignores forged search dates', async () => {
  const seen=[];
  const client={candidates:async()=>[{id:'stale',email_ts:String(now)},{id:'fresh',email_ts:'1970-01-01'}],raw:async id=>({raw:id,receivedAtMs:id==='stale'?now-10000:now})};
  await bridgeOtp(client,{request:async()=>scope,submit:async raw=>{seen.push(raw);return true;}});
  assert.deepEqual(seen,['fresh']);
});

test('connector binds raw and trusted receipt to the same Gmail message ID', async () => {
  const {GmailClient}=require('./connector-client.cjs');
  for(const metadata of [
    {id:'same',internal_date:String(now)}, {id:'other',internal_date:String(now)},
    {id:'same',internal_date:null}, {id:'same',internal_date:'2026-10-13'},
    {id:'same',internal_date:'1e12'}, {id:'same',internal_date:'1.5'},
    {id:'same',internal_date:'9007199254740992'},
  ]) {
    const client=new GmailClient();
    client.tool=async(_tool,args)=>args.format==='raw'?{id:'same',raw:'encoded'}:metadata;
    const result=await client.raw('same');
    assert.equal(Number.isSafeInteger(result.receivedAtMs),metadata.id==='same'&&metadata.internal_date===String(now));
  }
  const client=new GmailClient();
  client.tool=async(_tool,args)=>args.format==='raw'?{id:'other',raw:'encoded'}:{id:'same',internal_date:String(now)};
  assert.ok(Number.isNaN((await client.raw('same')).receivedAtMs));
});

test('KVPN raw selection is whitespace invariant and rejects controls or longer numbers', async () => {
  const signed=await kaistFixture('Authentication\t\tcode:  123456 \t\r\n');
  const changed=signed.replace('Authentication\t\tcode:  123456 \t\r\n','Authentication code: 123456\r\n');
  assert.equal(await validateMessage(encode(changed),now,scope,{resolver}),'123456');
  for(const body of ['0123456\r\n','123456\x01\r\n']) {
    await assert.rejects(validateMessage(encode(await kaistFixture(body)),now,scope,{resolver}),/template_mismatch/);
  }
});

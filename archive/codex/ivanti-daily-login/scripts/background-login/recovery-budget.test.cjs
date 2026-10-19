'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const source=fs.readFileSync(path.join(__dirname,'run.cjs'),'utf8');
const authenticateSource=source.slice(source.indexOf('async function authenticate(page)'),source.indexOf('async function handoff(page,'));

test('a resumed incident can submit only the remaining credential attempt',async()=>{
 let submissions=0;
 const origin='https://kvpn.kaist.ac.kr';
 const otpOrigin='https://kvpnportal.kaist.ac.kr:8443';
 const context=vm.createContext({
  attempts:2,URL,ORIGIN:origin,OTP_ORIGIN:otpOrigin,
  delay:async()=>{},originIs:(url,expected)=>new URL(url).origin===expected,
  stop:reason=>{throw new Error(reason);},authState:async()=> 'login',
  run:async()=>({stdout:'fixture'}),
  loadSettings:()=>({otpSender:'vpn@example.invalid'}),emit:()=>{},
  emailFrame:async()=>({url:()=>otpOrigin,locator:()=>({count:async()=>1,click:async()=>{}})}),
  waitConnectorOtp:async()=>{const error=new Error('timeout');error.safeReason='connector_email_timeout';throw error;}
 });
 vm.runInContext(authenticateSource,context);
 const page={
  goto:async()=>{},url:()=>origin,
  getByPlaceholder:()=>({count:async()=>1,fill:async()=>{}}),
  locator:()=>({evaluateAll:async()=>['KAIST Members']}),
  getByRole:()=>({evaluate:async()=>origin,click:async()=>{submissions++;}})
 };
 await assert.rejects(context.authenticate(page),/connector_email_timeout/);
 assert.equal(submissions,1);
 assert.equal(context.attempts,3);
 await assert.rejects(context.authenticate(page),/authentication_attempts_exhausted/);
 assert.equal(submissions,1);
});

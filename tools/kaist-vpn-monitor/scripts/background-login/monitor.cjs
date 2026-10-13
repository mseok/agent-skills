#!/usr/bin/env node
'use strict';
// Scheduled entrypoint. Normal checks and known recovery use no model.
const fs = require('node:fs/promises');
const path = require('node:path');
const os = require('node:os');
const net = require('node:net');
const readline = require('node:readline');
const {spawn,execFile} = require('node:child_process');
const {promisify} = require('node:util');
const {GmailClient,receivedAtMs} = require('./connector-client.cjs');
const run = promisify(execFile);
const delay = ms => new Promise(resolve => setTimeout(resolve,ms));
const runtime = path.join(os.homedir(),'Library','Caches','kaist-vpn-monitor');
const stateRoot = path.join(os.homedir(),'.local','state','kaist-vpn-monitor');
const statePath = path.join(stateRoot,'state.json');
const node = process.execPath;
const runner = path.join(__dirname,'run.cjs');
const now = () => new Date().toISOString();
const emit = value => process.stdout.write(JSON.stringify(value)+'\n');
let lock;

function safeResult(value) {
  return Object.fromEntries(['status','stage','reason','attempts','native','ssh','reusedConnection'].filter(k=>value[k]!==undefined).map(k=>[k,value[k]]));
}
function canRetryConnector(previous, health) {
  // A connector preflight outage submits no credentials. Recheck readiness on
  // the next scheduled run, including after login, without retrying auth failures.
  return previous.needsAttention===true && health.status==='needs_recovery' &&
    previous.result?.status==='blocked' && previous.result.stage==='connector' &&
    previous.result.reason==='gmail_connector_unavailable' && previous.result.attempts===0;
}
async function readState() {
  try {return JSON.parse(await fs.readFile(statePath,'utf8'));}
  catch(error) {if(error.code==='ENOENT')return {};throw error;}
}
async function save(state) {
  const temporary = statePath+'.'+process.pid+'.tmp';
  await fs.writeFile(temporary,JSON.stringify(state,null,2)+'\n',{mode:0o600});
  await fs.rename(temporary,statePath);
}
async function acquire() {
  const name = path.join(stateRoot,'monitor.lock');
  try {lock = await fs.open(name,'wx',0o600);}
  catch(error) {
    if(error.code!=='EEXIST')throw error;
    const owner = Number((await fs.readFile(name,'utf8')).trim());
    if(!Number.isSafeInteger(owner)||owner<=0)throw new Error('monitor_lock_unavailable');
    try {process.kill(owner,0);return false;}
    catch(probe) {if(probe.code!=='ESRCH')return false;}
    await fs.unlink(name);lock = await fs.open(name,'wx',0o600);
  }
  await lock.writeFile(String(process.pid));return true;
}
async function check() {
  let output;
  try {output = (await run(node,[runner,'--health-check'],{timeout:90000,maxBuffer:16384})).stdout;}
  catch(error) {output = error.stdout;}
  try {return safeResult(JSON.parse(output.trim().split('\n').at(-1)));}
  catch {return {status:'blocked',reason:'health_check_unavailable',attempts:0};}
}
async function notify(message) {
  await run('/usr/bin/osascript',['-e','on run argv\ndisplay notification (item 1 of argv) with title "KAIST VPN"\nend run',message],{timeout:10000}).catch(()=>{});
}
async function abortOtp() {
  await new Promise(resolve=>{
    const socket = net.createConnection(path.join(runtime,'connector-otp.sock'));
    socket.setTimeout(2000);
    socket.on('connect',()=>socket.end('abort\n'));
    socket.on('data',()=>{});
    socket.on('timeout',()=>socket.destroy());
    socket.on('error',()=>{});socket.on('close',resolve);
  });
}
async function otpRequest() {
  const deadline = Date.now()+4000;
  while(Date.now()<deadline) {
    try {
      const value = JSON.parse(await fs.readFile(path.join(runtime,'connector-otp-request.json'),'utf8'));
      if(Number.isSafeInteger(value.capturedAtMs)&&Number.isSafeInteger(value.expiresAtMs)&&value.expiresAtMs>Date.now())return value;
    } catch(error) {if(error.code!=='ENOENT')throw new Error('otp_request_unavailable');}
    await delay(100);
  }
  throw new Error('otp_request_unavailable');
}
async function submit(raw,received) {
  return new Promise((resolve,reject)=>{
    const child = spawn(node,[path.join(__dirname,'submit-connector-gmail-otp.cjs'),'--received-at-ms',String(received)],{stdio:['pipe','pipe','ignore']});
    let output='';
    child.stdout.on('data',chunk=>{if(output.length<4096)output+=chunk;});
    child.once('error',()=>reject(new Error('otp_submit_unavailable')));
    child.stdin.on('error',()=>{});
    child.once('close',code=>{
      let result;try{result=JSON.parse(output.trim());}catch{}
      code===0&&result?.status==='submitted' ? resolve() : reject(new Error('otp_validation_failed'));
    });
    child.stdin.end(raw+'\n');
  });
}
async function bridgeOtp(client) {
  const request = await otpRequest();
  const considered = new Set();
  while(Date.now()<request.expiresAtMs) {
    const messages = await client.candidates(request.capturedAtMs);
    for(const message of messages) {
      const received = receivedAtMs(message.email_ts);
      if(!Number.isSafeInteger(received)||received<request.capturedAtMs-2000||received>request.expiresAtMs||considered.has(message.id))continue;
      considered.add(message.id);
      let raw = await client.raw(message.id);
      try {await submit(raw,received);return;}
      finally {raw='';}
    }
    await delay(Math.min(5000,Math.max(0,request.expiresAtMs-Date.now())));
  }
  // The existing runner owns the three-attempt email-timeout contract.
}
async function recover() {
  const client = new GmailClient();
  try {
    await client.start();await client.ready();
    return await new Promise((resolve,reject)=>{
      const child = spawn(node,[runner,'--connector-otp'],{stdio:['ignore','pipe','ignore']});
      const lines = readline.createInterface({input:child.stdout});
      let final, bridge=Promise.resolve(), bridgeFailed=false;
      lines.on('line',line=>{
        let value;try{value=JSON.parse(line);}catch{return;}
        final=safeResult(value);
        if(value.status==='authenticating'&&value.stage==='email') {
          bridge=bridge.then(()=>bridgeOtp(client)).catch(async()=>{bridgeFailed=true;await abortOtp();});
        }
      });
      child.once('error',()=>reject(new Error('runner_unavailable')));
      child.once('close',async code=>{
        await bridge;lines.close();
        if(final?.status==='connected'&&code===0)resolve(final);
        else resolve(final?.status==='blocked' ? final : {status:'blocked',stage:'recovery',reason:bridgeFailed?'connector_email_unavailable':'runner_unavailable',attempts:final?.attempts||0});
      });
    });
  } catch {
    return {status:'blocked',stage:'connector',reason:'gmail_connector_unavailable',attempts:0};
  } finally {client.close();}
}
async function main() {
  if(process.argv.includes('--status')){emit(await readState());return;}
  await fs.mkdir(stateRoot,{recursive:true,mode:0o700});await fs.chmod(stateRoot,0o700);
  if(!await acquire()){emit({status:'busy'});return;}
  const previous=await readState();
  let result=await check();
  if(result.reason==='existing_run_lock'){emit({status:'busy'});return;}
  if(process.argv.includes('--check-only')){emit(result);return;}
  const connectorRetry=canRetryConnector(previous,result);
  if(result.status!=='connected'&&previous.needsAttention&&!process.argv.includes('--retry')&&!connectorRetry) {
    await save({...previous,lastCheckedAt:now(),lastHealth:result});emit({status:'attention_unchanged',reason:previous.result?.reason});return;
  }
  const health=result;
  if(result.status==='needs_recovery')result=await recover();
  if(connectorRetry&&canRetryConnector({needsAttention:true,result},health)) {
    await save({...previous,lastCheckedAt:now(),lastHealth:health});
    emit({status:'attention_unchanged',reason:result.reason});return;
  }
  const healthy=result.status==='connected';
  const state={version:1,lastCheckedAt:now(),lastHealthyAt:healthy?now():previous.lastHealthyAt||null,needsAttention:!healthy,result,modelCallsThisRun:0};
  if(healthy) {
    if(previous.needsAttention||result.reusedConnection===false)await notify('연결 복구를 확인했습니다.');
  } else {
    state.incidentAt=now();
    await save(state);
    await notify('자동 복구를 멈췄습니다. 확인이 필요합니다: '+(result.reason||'unknown'));
  }
  await save(state);emit(state);
}
if(require.main===module)main().catch(async()=>{
  const result={status:'blocked',reason:'monitor_unavailable'};
  if(process.argv.includes('--status')){emit(result);process.exitCode=1;return;}
  const previous=await readState().catch(()=>({}));
  await save({version:1,lastCheckedAt:now(),needsAttention:true,result,modelCallsThisRun:0}).catch(()=>{});
  if(previous.result?.reason!==result.reason)await notify('VPN 점검기 실행에 문제가 있습니다. 확인이 필요합니다.');
  emit(result);process.exitCode=1;
}).finally(async()=>{
  if(lock){await lock.close();await fs.unlink(path.join(stateRoot,'monitor.lock'));}
});
module.exports={safeResult,bridgeOtp,receivedAtMs,canRetryConnector};

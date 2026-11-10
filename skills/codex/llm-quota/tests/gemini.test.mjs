import assert from 'node:assert/strict';
import { test } from 'node:test';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { normalizeGemini, readGeminiQuota } from '../scripts/gemini-acp.mjs';

const quota='### Quota Limits\n- **Gemini Models**\n  - **Weekly Limit Remaining:** 100% remaining (resets Nov 09, 2026, 07:03 UTC)\n  - **Five Hour Limit Remaining:** 98% remaining (resets Nov 02, 2026, 12:03 UTC)\n- **Claude and GPT models**\n  - **Weekly Limit Remaining:** 40% remaining\n- **Gemini 4 Argon**\n  - **Gemini 4 Argon Weekly Limit:** 0% remaining (resets invalid)';
test('Gemini preserves provider groups, measured zero and unknown resets',()=>{
 const w=normalizeGemini(quota);
 assert.equal(w.length,4);assert.equal(w[0].remainingPercent,100);assert.equal(w[1].usedPercent,2);
 assert.equal(w[1].windowMinutes,300);assert.equal(w[1].resetsAt,'2026-11-02T12:03:00.000Z');
 assert.equal(w[2].scope,'Claude and GPT models');assert.equal(w[2].bucket,'gemini');assert.equal(w[2].resetsAt,null);
 assert.equal(w[3].remainingPercent,0);assert.equal(w[3].resetsAt,null);assert.deepEqual(normalizeGemini('unknown quota format'),[]);
});
function fake({advertise=true,tool=false}={}){
 return (_exe,_args,opts)=>{
  assert.equal(opts.env.AGY_ACP_FORCE_FILE_STORAGE,'1');assert.equal(opts.env.GEMINI_API_KEY,undefined);
  const code=`const rl=require('node:readline').createInterface({input:process.stdin});let stage=0;const send=x=>console.log(JSON.stringify({jsonrpc:'2.0',...x}));rl.on('line',line=>{const m=JSON.parse(line);if(m.method==='initialize'&&stage===0){stage++;send({id:m.id,result:{}});}else if(m.method==='session/new'&&stage===1){stage++;if(m.params.mcpServers.length)process.exit(91);send({id:m.id,result:{sessionId:'fixture'}});setTimeout(()=>send({method:'session/update',params:{sessionId:'fixture',update:{sessionUpdate:'available_commands_update',availableCommands:${advertise?'[{name:"usage"}]':'[]'}}}}),10);}else if(m.method==='session/prompt'&&stage===2&&m.params.prompt.length===1&&m.params.prompt[0].text==='/usage'){stage++;${tool?`send({method:'session/update',params:{update:{sessionUpdate:'tool_call'}}});`:`send({method:'session/update',params:{update:{sessionUpdate:'agent_message_chunk',content:{type:'text',text:${JSON.stringify(quota)}}}}});send({id:m.id,result:{stopReason:'end_turn'}});`}}else process.exit(92);});`;
  return spawn(process.execPath,['-e',code],opts);
 };
}
for(const [name,options,expected] of [['native local command',{advertise:true},'ok'],['unadvertised command',{advertise:false},'unavailable'],['unexpected tool activity',{tool:true},'error']]){
 test('Gemini: '+name,async()=>{
  const profileDir=fs.mkdtempSync(path.join(os.tmpdir(),'quota-acp-'));
  try{const r=await readGeminiQuota({executable:process.execPath,profileDir,spawnChild:fake(options),timeoutMs:3000});assert.equal(r.status,expected);if(expected==='ok')assert.equal(r.windows.length,4);else assert.equal(r.windows.length,0);}
  finally{fs.rmSync(profileDir,{recursive:true,force:true});}
 });
}
test('Gemini: a sign-in failure is auth_required, other rejections stay native_request_rejected',async()=>{
 const runtime=(code,message)=>(_exe,_args,opts)=>spawn(process.execPath,['-e',`require('node:readline').createInterface({input:process.stdin}).on('line',l=>{const m=JSON.parse(l);if(m.method==='initialize')console.log(JSON.stringify({jsonrpc:'2.0',id:m.id,result:{}}));else console.log(JSON.stringify({jsonrpc:'2.0',id:m.id,error:{code:${code},message:${JSON.stringify(message)}}}));});`],opts);
 const profileDir=fs.mkdtempSync(path.join(os.tmpdir(),'quota-acp-'));
 try{
  for(const [code,message,reason] of [[-32000,'Authentication required','auth_required'],[-32603,'Unauthenticated: sign in again','auth_required'],[-32603,'internal error','native_request_rejected']]){
   const r=await readGeminiQuota({executable:process.execPath,profileDir,spawnChild:runtime(code,message),timeoutMs:3000});
   assert.equal(r.status,'error');assert.equal(r.reason,reason);assert.equal(r.windows.length,0);
  }
 }finally{fs.rmSync(profileDir,{recursive:true,force:true});}
});

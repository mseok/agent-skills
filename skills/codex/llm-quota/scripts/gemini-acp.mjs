import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createInterface } from 'node:readline';

export function normalizeGemini(text) {
  let scope=null;
  const windows=[];
  for(const line of text.split('\n')) {
    const group=/^- \*\*([^*]+)\*\*\s*$/.exec(line);
    if(group){scope=group[1];continue;}
    const quota=/^\s+- \*\*([^*]+):\*\*\s*(\d+(?:\.\d+)?)% remaining(?: \(resets ([^)]+)\))?/.exec(line);
    if(!quota || !scope)continue;
    const remaining=Number(quota[2]);
    if(remaining<0 || remaining>100)continue;
    const date=quota[3]?new Date(quota[3]):null;
    windows.push({id:quota[1],bucket:'gemini',scope,
      windowMinutes:/weekly/i.test(quota[1])?10080:/five hour/i.test(quota[1])?300:null,
      usedPercent:100-remaining,remainingPercent:remaining,
      resetsAt:date&&!Number.isNaN(date.getTime())?date.toISOString():null});
  }
  return windows;
}

// A sign-in failure of the official ACP runtime: ACP's auth_required error code (-32000) or an
// authentication message. The quota reports it as `auth_required`; the bridge shows how to sign
// in again (renew-gemini-login). User decision 2026-11-09: "3번도 넣어주라."
export function isAcpAuthError(error) {
  if (!error) return false;
  return error.code === -32000 || /auth(entication)?[ _-]?required|unauthenticated|not (logged|signed) in|(log|sign)[ -]?in required|invalid_grant|reauth|credentials? (expired|invalid|missing)/i.test(String(error.message ?? ''));
}

export function readGeminiQuota({spawnChild=spawn,timeoutMs=25000,executable,profileDir}={}) {
  const state=process.env.BRIDGE_STATE_DIR??path.join(os.homedir(),process.platform==='darwin'?'Library/Application Support/chatgpt-claude-bridge':'.codex/claude-bridge/bridge');
  executable??=process.env.GEMINI_ACP_BIN??path.join(state,'acp/runtime/agy_acp_server.par');
  profileDir??=process.env.GEMINI_ACP_PROFILE??path.join(state,'acp/profile');
  const base={provider:'gemini',source:'official Antigravity ACP: advertised native /usage',accountScope:'dedicated ACP profile',checkedAt:new Date().toISOString(),windows:[]};
  if(!fs.existsSync(executable))return Promise.resolve({...base,status:'error',reason:'acp_runtime_missing'});
  if(!fs.existsSync(profileDir))return Promise.resolve({...base,status:'error',reason:'acp_profile_missing'});
  const home=path.join(profileDir,'.home'),tmp=path.join(profileDir,'.tmp'),cwd=path.join(profileDir,'.quota-workspace');
  for(const dir of [home,tmp,cwd])fs.mkdirSync(dir,{recursive:true,mode:0o700});
  const quote=s=>`'${s.replaceAll("'","'\\''")}'`;
  const env={HOME:home,GEMINI_HOME:profileDir,TMPDIR:tmp,AGY_ACP_FORCE_FILE_STORAGE:'1',PYTHONUNBUFFERED:'1',LANG:'en_US.UTF-8',PATH:'/usr/bin:/bin:/usr/sbin:/sbin',BROWSER:[process.execPath,'-e','process.exit(0)','--','%s'].map(quote).join(' ')};
  return new Promise(resolve=>{
    const child=spawnChild(executable,[],{stdio:['pipe','pipe','pipe'],env,cwd});
    const lines=createInterface({input:child.stdout});
    let settled=false,sessionId=null,commands=null,text='',quotaSent=false;
    const timer=setTimeout(()=>finish({status:'error',reason:'timeout'}),timeoutMs);
    function finish(result){
      if(settled)return;settled=true;clearTimeout(timer);lines.close();child.stdin.end();child.kill('SIGTERM');
      const killTimer=setTimeout(()=>child.kill('SIGKILL'),1000);killTimer.unref();child.once('close',()=>clearTimeout(killTimer));
      resolve({...base,checkedAt:new Date().toISOString(),...result});
    }
    const send=m=>child.stdin.write(JSON.stringify({jsonrpc:'2.0',...m})+'\n');
    function query(){
      if(quotaSent || !sessionId || commands===null)return;
      if(!commands.includes('usage'))return finish({status:'unavailable',reason:'native_usage_not_advertised'});
      quotaSent=true;
      // Exact built-in command only. Never replace this with natural language or a
      // model prompt. The runtime advertises and processes /usage locally.
      send({id:3,method:'session/prompt',params:{sessionId,prompt:[{type:'text',text:'/usage'}]}});
    }
    child.stderr.resume();
    child.on('error',()=>finish({status:'error',reason:'spawn_failed'}));
    child.stdin.on('error',()=>finish({status:'error',reason:'cli_input_closed'}));
    child.on('close',()=>finish({status:'error',reason:'cli_exited_before_response'}));
    lines.on('line',line=>{
      if(settled||!line.trim())return;
      let m;try{m=JSON.parse(line);}catch{return finish({status:'error',reason:'unexpected_native_output'});}
      if(m.method&&m.id!==undefined)return finish({status:'error',reason:'interaction_required'});
      if(m.method==='session/update'){
        const u=m.params?.update??{};
        if(u.sessionUpdate==='available_commands_update'){commands=(u.availableCommands??[]).map(c=>c.name);query();}
        if(u.sessionUpdate==='tool_call' || (u.sessionUpdate==='usage_update'&&u.used>0))return finish({status:'error',reason:'unexpected_model_activity'});
        if(quotaSent&&u.sessionUpdate==='agent_message_chunk'&&u.content?.type==='text')text+=u.content.text;
        return;
      }
      if(m.error)return finish({status:'error',reason:isAcpAuthError(m.error)?'auth_required':'native_request_rejected'});
      if(m.id===1)send({id:2,method:'session/new',params:{cwd,mcpServers:[]}});
      else if(m.id===2){sessionId=m.result?.sessionId;query();}
      else if(m.id===3){
        const windows=normalizeGemini(text);
        finish({status:windows.length?'ok':'unavailable',windows,...(!windows.length?{reason:'quota_format_unavailable'}:{})});
      }
    });
    send({id:1,method:'initialize',params:{protocolVersion:1,clientInfo:{name:'llm-quota',version:'1.1.0'},clientCapabilities:{fs:{readTextFile:false,writeTextFile:false},terminal:false}}});
  });
}

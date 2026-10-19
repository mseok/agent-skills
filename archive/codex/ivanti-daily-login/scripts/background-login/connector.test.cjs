'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {GmailClient}=require('./connector-client.cjs');
const searchError={isError:true,content:[{type:'text',text:'GmailApiError: Failed to search emails'}]};

test('transient Gmail search error retries the same read without restarting authentication',async()=>{
 const client=new GmailClient();let calls=0;
 client.call=async(method,params,timeout)=>{
  assert.equal(method,'mcpServer/tool/call');assert.equal(params.tool,'gmail.search_emails');
  assert.ok(timeout>0&&timeout<=30000);calls++;
  return calls===1?searchError:{structuredContent:{emails:[]}};
 };
 assert.deepEqual(await client.tool('gmail.search_emails',{query:'synthetic'},Date.now()+10000),{emails:[]});
 assert.equal(calls,2);
});

test('permission errors are not retried and their private message is not exposed',async()=>{
 const client=new GmailClient();let calls=0;
 client.call=async()=>{calls++;return {isError:true,content:[{type:'text',text:'Permission denied for private@example.invalid'}]};};
 await assert.rejects(client.tool('gmail.search_emails',{},Date.now()+10000),error=>error.message==='gmail_tool_failed');
 assert.equal(calls,1);
});

test('an expired OTP deadline prevents calls and a near deadline prevents another retry',async()=>{
 const client=new GmailClient();let calls=0;
 client.call=async()=>{calls++;return searchError;};
 await assert.rejects(client.tool('gmail.search_emails',{},Date.now()-1),/connector_timeout/);
 assert.equal(calls,0);
 await assert.rejects(client.tool('gmail.search_emails',{},Date.now()+500),/gmail_search_temporarily_unavailable/);
 assert.equal(calls,1);
});

test('candidate and same-ID raw metadata reads retain the OTP request deadline',async()=>{
 const client=new GmailClient();const deadline=Date.now()+80000;const seen=[];
 client.tool=async(tool,args,until)=>{
  seen.push(until);
  if(tool==='gmail.search_emails')return {emails:[]};
  return args.format==='raw'?{id:'same',raw:'encoded'}:{id:'same',internal_date:'1791880000000'};
 };
 await client.candidates(Date.now(),'vpn@example.invalid',deadline);
 await client.raw('same',deadline);
 assert.deepEqual(seen,[deadline,deadline,deadline]);
});

test('persistent Gmail backend failure stops after three read calls',async()=>{
 const client=new GmailClient();let calls=0;
 client.call=async()=>{calls++;return searchError;};
 await assert.rejects(client.tool('gmail.search_emails',{},Date.now()+15000),/gmail_search_temporarily_unavailable/);
 assert.equal(calls,3);
});

test('readiness checks search, raw and same-ID metadata before any new OTP',async()=>{
 const client=new GmailClient();const calls=[];
 client.tool=async(tool,args,deadline)=>{
  calls.push({tool,args,deadline});
  if(tool==='gmail.search_emails')return {emails:[{id:'existing'}]};
  return args.format==='raw'?{id:'existing',raw:'encoded'}:{id:'existing',internal_date:'1791880000000'};
 };
 await client.ready();
 assert.deepEqual(calls.map(call=>call.args.format),[undefined,'raw','metadata']);
 assert.equal(new Set(calls.map(call=>call.deadline)).size,1);
 client.tool=async(tool)=>{
  if(tool==='gmail.search_emails')return {emails:[{id:'existing'}]};
  throw new Error('gmail_tool_failed');
 };
 await assert.rejects(client.ready(),/gmail_tool_failed/);
});

test('readiness rejects malformed responses without accepting an unusable mail bridge',async()=>{
 const client=new GmailClient();
 client.tool=async()=>({});
 await assert.rejects(client.ready(),/gmail_response_unavailable/);
 client.tool=async(tool)=>tool==='gmail.search_emails'?{emails:[{id:'existing'}]}:{id:'wrong'};
 await assert.rejects(client.ready(),/gmail_response_unavailable/);
 client.tool=async()=>({emails:[]});
 await client.ready();
});

'use strict';
// Read-only Gmail access through the installed Codex protocol. No turn/start,
// model inference, persisted thread, message output or credential extraction.
const {loadSettings} = require('./settings.cjs');
const {spawn} = require('node:child_process');
const readline = require('node:readline');
const os = require('node:os');
const path = require('node:path');
const delay = ms => new Promise(resolve => setTimeout(resolve,ms));

function unwrap(value) {
  if (value?.result) return unwrap(value.result);
  if (value?.isError) {
    const temporarySearchFailure = value.content?.some(item => item.type === 'text' && item.text.trim() === 'GmailApiError: Failed to search emails');
    throw new Error(temporarySearchFailure ? 'gmail_search_temporarily_unavailable' : 'gmail_tool_failed');
  }
  if (value?.structuredContent) return value.structuredContent;
  for (const item of value?.content || []) {
    if (item.type !== 'text') continue;
    try {return JSON.parse(item.text);} catch { /* MCP may include a text notice. */ }
  }
  throw new Error('gmail_response_unavailable');
}

class GmailClient {
  constructor() {this.pending = new Map();this.nextId = 1;}
  async start() {
    this.process = spawn(loadSettings().codexBinary, ['app-server','--stdio'], {
      stdio:['pipe','pipe','ignore'], env:{...process.env,RUST_LOG:'error'}
    });
    this.lines = readline.createInterface({input:this.process.stdout});
    this.lines.on('line', line => {
      let message;
      try {message = JSON.parse(line);} catch {return;}
      const request = this.pending.get(message.id);
      if (request) {
        this.pending.delete(message.id);clearTimeout(request.timer);
        message.error ? request.reject(new Error('connector_request_failed')) : request.resolve(message.result);
      } else if (message.id !== undefined) {
        this.send({id:message.id,error:{code:-32601,message:'Interactive requests are unavailable in the VPN monitor'}});
      }
    });
    const ended = () => this.rejectPending('connector_unavailable');
    this.process.once('error', ended);this.process.once('exit', ended);
    this.process.stdin.on('error', ended);
    await this.call('initialize', {clientInfo:{name:'ivanti_monitor',version:'1.0'},capabilities:{experimentalApi:true}});
    this.send({method:'initialized'});
    const result = await this.call('thread/start', {
      ephemeral:true,cwd:path.join(os.homedir(),'Library','Caches','codex-ivanti-background-secure-v021'),approvalPolicy:'never'
    });
    this.threadId = result.thread.id;
    const inventory = await this.call('mcpServerStatus/list', {threadId:this.threadId,detail:'toolsAndAuthOnly',limit:50});
    const server = inventory.data?.find(item => item.name === 'codex_apps');
    if (!server?.tools?.['gmail.search_emails'] || !server?.tools?.['gmail.read_email']) throw new Error('gmail_tools_unavailable');
  }
  send(message) {this.process.stdin.write(JSON.stringify({jsonrpc:'2.0',...message})+'\n');}
  call(method, params, timeoutMs = 30000) {
    const id = this.nextId++;
    return new Promise((resolve,reject) => {
      const timer = setTimeout(() => {this.pending.delete(id);reject(new Error('connector_timeout'));},timeoutMs);
      this.pending.set(id,{resolve,reject,timer});this.send({id,method,params});
    });
  }
  async tool(tool, args, deadlineMs = Date.now()+30000) {
    if (!['gmail.search_emails','gmail.read_email'].includes(tool)) throw new Error('tool_not_allowed');
    let failure = new Error('connector_timeout');
    // Retry only the same read, within this challenge. Never request a new OTP
    // or hide a permission/authentication rejection behind a retry loop.
    for (const wait of [0,2000,5000]) {
      if (Date.now()+wait >= deadlineMs) throw failure;
      if (wait) await delay(wait);
      const remaining = deadlineMs-Date.now();
      if (remaining <= 0) throw failure;
      try {
        return unwrap(await this.call('mcpServer/tool/call', {threadId:this.threadId,server:'codex_apps',tool,arguments:args},Math.min(30000,remaining)));
      } catch(error) {
        if (error.message !== 'connector_timeout' && !(tool === 'gmail.search_emails' && error.message === 'gmail_search_temporarily_unavailable')) throw error;
        failure = error;
      }
    }
    throw failure;
  }
  async ready() {
    const deadline = Date.now()+30000;
    const value = await this.tool('gmail.search_emails', {query:'"KVPN OTP number" newer_than:1d -in:spam -in:trash',max_results:1},deadline);
    if (!Array.isArray(value.emails)) throw new Error('gmail_response_unavailable');
    if (value.emails[0]) {
      let receipt = await this.raw(value.emails[0].id,deadline);
      const valid = typeof receipt.raw==='string' && receipt.raw.length>0 && Number.isSafeInteger(receipt.receivedAtMs);
      receipt.raw='';
      if (!valid) throw new Error('gmail_response_unavailable');
    }
  }
  async candidates(capturedAtMs, otpSender, deadlineMs) {
    const after = Math.floor((capturedAtMs-2000)/1000);
    const value = await this.tool('gmail.search_emails', {query:`"KVPN OTP number" from:"${otpSender}" after:${after} -in:spam -in:trash`,max_results:50},deadlineMs);
    if (!Array.isArray(value.emails)) throw new Error('gmail_response_unavailable');
    return value.emails;
  }
  async raw(id, deadlineMs) {
    const value = await this.tool('gmail.read_email', {message_id:id,format:'raw'},deadlineMs);
    // Raw format omits internal_date on this connector. Read metadata for the
    // same immutable message; search email_ts is the unsigned sender Date.
    const metadata = await this.tool('gmail.read_email', {message_id:id,format:'metadata'},deadlineMs);
    const received = typeof metadata.internal_date === 'string' && /^[0-9]+$/.test(metadata.internal_date) ? Number(metadata.internal_date) : NaN;
    if (value.id !== id || metadata.id !== id || typeof value.raw !== 'string' || !Number.isSafeInteger(received) || received <= 0) return {raw:'',receivedAtMs:NaN};
    return {raw:value.raw, receivedAtMs:received};
  }
  rejectPending(reason) {
    for (const request of this.pending.values()) {clearTimeout(request.timer);request.reject(new Error(reason));}
    this.pending.clear();
  }
  close() {
    this.rejectPending('connector_closed');this.lines?.close();
    this.process?.stdin.end();this.process?.kill('SIGTERM');
  }
}

function receivedAtMs(value) {
  if (typeof value !== 'string') return NaN;
  if (/^\d+(?:\.\d+)?$/.test(value)) {const n = Number(value);return Math.round(n < 1e12 ? n*1000 : n);}
  return Date.parse(value);
}
module.exports = {GmailClient,receivedAtMs};

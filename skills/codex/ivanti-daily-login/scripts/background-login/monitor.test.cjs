'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const {canRetryConnector,recoveryAttempts} = require('./monitor.cjs');

const inactive = {status:'needs_recovery',stage:'native',reason:'native_inactive',attempts:0};
const outage = {needsAttention:true,result:{status:'blocked',stage:'connector',reason:'gmail_connector_unavailable',attempts:0}};

test('temporary connector outage can resume when native recovery is needed', () => {
  assert.equal(canRetryConnector(outage,inactive),true);
});

test('authentication failures remain latched even if the connector is now ready', () => {
  for (const result of [
    {status:'blocked',stage:'authentication',reason:'credential_rejected',attempts:1},
    {status:'blocked',stage:'authentication',reason:'email_timeout',attempts:3},
    {...outage.result,attempts:1},
    {...outage.result,attempts:undefined},
    {...outage.result,stage:'authentication'},
    {...outage.result,reason:'connector_email_unavailable'}
  ]) assert.equal(canRetryConnector({needsAttention:true,result},inactive),false);
});

test('a connected profile, indeterminate native state, or live runner never triggers this retry', () => {
  for (const health of [
    {status:'connected',native:'SA',ssh:'ok'},
    {status:'blocked',stage:'ssh',reason:'ssh_unavailable'},
    {status:'blocked',stage:'native',reason:'native_indeterminate'},
    {status:'busy',reason:'existing_run_lock'}
  ]) assert.equal(canRetryConnector(outage,health),false);
});

test('an unlatched or absent incident uses the normal monitor path', () => {
  assert.equal(canRetryConnector({...outage,needsAttention:false},inactive),false);
  assert.equal(canRetryConnector({},inactive),false);
});

test('connector diagnostics expose only fixed error codes',()=>{
 const {connectorDetail}=require('./monitor.cjs');
 assert.equal(connectorDetail(new Error('gmail_search_temporarily_unavailable')),'gmail_search_temporarily_unavailable');
 assert.equal(connectorDetail(new Error('private@example.invalid 123456')),'connector_failure');
});

test('a failed email read resumes only with a remaining incident budget',()=>{
 const result={status:'blocked',stage:'authentication',reason:'connector_email_unavailable',detail:'gmail_tool_failed',attempts:1};
 assert.equal(canRetryConnector({needsAttention:true,result},inactive),true);
 assert.equal(canRetryConnector({needsAttention:true,result:{...result,attempts:2}},inactive),true);
 for(const attempts of [3,-1,undefined,'1']) {
  assert.equal(canRetryConnector({needsAttention:true,result:{...result,attempts}},inactive),false);
 }
 for(const detail of ['connector_failure','otp_submit_unavailable','permission_denied',undefined]) {
  assert.equal(canRetryConnector({needsAttention:true,result:{...result,detail}},inactive),false);
 }
});

test('connector readiness failures preserve authentication attempts across scheduled runs',()=>{
 const previous={...outage,authenticationAttempts:2};
 assert.equal(recoveryAttempts(previous),2);
 assert.equal(canRetryConnector(previous,inactive),true);
 assert.equal(canRetryConnector({...previous,authenticationAttempts:3},inactive),false);
 for(const authenticationAttempts of [-1,'1',4]) {
  assert.equal(recoveryAttempts({...previous,authenticationAttempts}),3);
 }
});

'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const {canRetryConnector,otpRoute} = require('./monitor.cjs');

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

test('an unreachable Gmail connector starts the login with SMS when the phone route is configured', () => {
  const phone = {listen:'100.64.0.1',port:40000,phone:'100.64.0.2'};
  assert.deepEqual(otpRoute(undefined,phone),{args:[]});
  assert.deepEqual(otpRoute(undefined,null),{args:[]});
  assert.deepEqual(otpRoute(new Error('connector_timeout'),phone),{args:['--sms-first'],detail:'connector_timeout'});
  assert.deepEqual(otpRoute(new Error('spawn ENOENT'),phone),{args:['--sms-first'],detail:'connector_failure'});
});

test('without the phone route an unreachable Gmail connector still stops before any login', () => {
  assert.deepEqual(otpRoute(new Error('connector_timeout'),null).blocked,{...outage.result,detail:'connector_timeout'});
});

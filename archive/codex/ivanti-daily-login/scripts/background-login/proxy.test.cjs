'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');
const {allowedTunnel,startVpnProxy} = require('./vpn-proxy.cjs');

test('proxy only allows the two exact TLS endpoints',()=>{
  assert.equal(allowedTunnel('kvpn.kaist.ac.kr:443'),true);
  assert.equal(allowedTunnel('kvpnportal.kaist.ac.kr:8443'),true);
  for(const target of ['evil.invalid:443','kvpn.kaist.ac.kr.evil.invalid:443','kvpn.kaist.ac.kr:80','127.0.0.1:443','kvpn.kaist.ac.kr:443@evil.invalid:443'])assert.equal(allowedTunnel(target),false);
});

test('actual loopback proxy rejects off-list CONNECT without an upstream connection',async()=>{
  const proxy = await startVpnProxy();
  try {
    const status = await new Promise((resolve,reject)=>{
      const request = http.request(proxy.url,{method:'CONNECT',path:'evil.invalid:443'});
      request.once('connect',(response,socket)=>{socket.destroy();resolve(response.statusCode);});
      request.once('error',reject);
      request.end();
    });
    assert.equal(status,403);
  } finally {await proxy.close();}
});

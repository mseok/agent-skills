'use strict';
const http = require('node:http');
const net = require('node:net');
const targets = new Map([
  ['kvpn.kaist.ac.kr:443', {host:'kvpn.kaist.ac.kr',port:443}],
  ['kvpnportal.kaist.ac.kr:8443', {host:'kvpnportal.kaist.ac.kr',port:8443}],
]);
function allowedTunnel(authority) {return targets.has(authority);}

async function startVpnProxy() {
  // HTTPS tunnels preserve end-to-end TLS. Unlike Playwright route(), this
  // connection boundary also covers automatic HTTP redirect hops.
  const sockets = new Set();
  const server = http.createServer((_request,response) => {response.writeHead(403);response.end();});
  server.maxConnections = 32;
  server.headersTimeout = 5000;
  server.requestTimeout = 5000;
  server.on('connection',socket => {
    sockets.add(socket);
    socket.once('close',()=>sockets.delete(socket));
    socket.on('error',()=>{});
  });
  server.on('connect',(request,client,head) => {
    const target = targets.get(request.url);
    if(!target){client.end('HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\n');return;}
    const upstream = net.connect(target);
    sockets.add(upstream);
    upstream.once('close',()=>{sockets.delete(upstream);client.destroy();});
    upstream.on('error',()=>client.destroy());
    client.once('close',()=>upstream.destroy());
    upstream.setTimeout(120000,()=>upstream.destroy());
    upstream.once('connect',()=>{
      client.write('HTTP/1.1 200 Connection Established\r\n\r\n');
      if(head.length)upstream.write(head);
      client.pipe(upstream);upstream.pipe(client);
    });
  });
  await new Promise((resolve,reject)=>{
    server.once('error',reject);
    server.listen({host:'127.0.0.1',port:0,exclusive:true},resolve);
  });
  return {
    url:'http://127.0.0.1:'+server.address().port,
    close:async()=>{
      for(const socket of sockets)socket.destroy();
      await new Promise(resolve=>server.close(resolve));
    },
  };
}
module.exports = {allowedTunnel,startVpnProxy};

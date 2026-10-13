'use strict';
const test=require('node:test');const assert=require('node:assert/strict');const http=require('node:http');const {chromium}=require('playwright-core');
const {emailFrame,portalReady}=require('./browser-policy.cjs');

test('replaced MFA iframe is resolved after readiness; live origin still enforced',async()=>{
 const proxy=http.createServer((_q,r)=>{r.writeHead(403);r.end();});proxy.on('connect',(_q,s)=>s.end('HTTP/1.1 403 Forbidden\r\n\r\n'));
 await new Promise(resolve=>proxy.listen(0,'127.0.0.1',resolve));let browser;
 try{
  browser=await chromium.launch({channel:'chrome',headless:true,chromiumSandbox:true,proxy:{server:'http://127.0.0.1:'+proxy.address().port,bypass:'<-loopback>'}});
  const context=await browser.newContext({serviceWorkers:'block'});
  await context.route('**/*',route=>{
   const u=new URL(route.request().url());
   let body;
   if(u.hostname==='kvpn.kaist.ac.kr')body='<iframe id="tp_frame" src="https://kvpnportal.kaist.ac.kr:8443/empty"></iframe>';
   else if(['kvpnportal.kaist.ac.kr','foreign.invalid'].includes(u.hostname))body=u.pathname==='/empty'?'waiting':'<div class="email"><span class="title">Email</span></div>';
   else return route.abort();
   return route.fulfill({status:200,contentType:'text/html',body});
  });
  const page=await context.newPage();await page.goto('https://kvpn.kaist.ac.kr/');
  const old=await (await page.locator('#tp_frame').elementHandle()).contentFrame();
  await page.evaluate(()=>setTimeout(()=>{document.querySelector('#tp_frame').outerHTML='<iframe id="tp_frame" src="https://kvpnportal.kaist.ac.kr:8443/ready"></iframe>';},100));
  await assert.rejects(old.locator('.email .title').waitFor({state:'visible',timeout:2000}));
  const current=await emailFrame(page);assert.notEqual(current,old);assert.equal(current.url(),'https://kvpnportal.kaist.ac.kr:8443/ready');
  await page.evaluate(()=>{document.querySelector('#tp_frame').outerHTML='<iframe id="tp_frame" src="https://foreign.invalid/ready"></iframe>';});
  await assert.rejects(emailFrame(page),/unexpected_otp_origin/);
 }finally{await browser?.close();await new Promise(resolve=>proxy.close(resolve));}
});

test('only the ready exact-origin portal may avoid a redundant navigation',async()=>{
 for(const [url,count,expected] of [
  ['https://kvpn.kaist.ac.kr/dana/user/',1,true],['https://kvpn.kaist.ac.kr/dana/user/',0,false],
  ['https://kvpn.kaist.ac.kr/dana/user/',2,false],['https://foreign.invalid/dana/user/',1,false],
  ['https://kvpn.kaist.ac.kr/download/',1,false],['http://kvpn.kaist.ac.kr/dana/user/',1,false],
 ])assert.equal(await portalReady({url:()=>url,locator:()=>({count:async()=>count})}),expected);
});

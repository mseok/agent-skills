'use strict';
const ORIGIN = 'https://kvpn.kaist.ac.kr';
const OTP_ORIGIN = 'https://kvpnportal.kaist.ac.kr:8443';
function originIs(url, expected) {
  try {return new URL(url).origin === expected;} catch {return false;}
}
function allowedRequest(url, mainNavigation) {
  return originIs(url, ORIGIN) || (!mainNavigation && originIs(url, OTP_ORIGIN));
}
function allowedLauncher(url, pageUrl, frameId, mainFrameId) {
  return url.startsWith('pulsesecure:') && originIs(pageUrl, ORIGIN) && frameId === mainFrameId;
}
async function emailFrame(page) {
  // Resolve after the email option appears: login can replace the old iframe.
  try {await page.frameLocator('#tp_frame').locator('.email .title').waitFor({state:'visible',timeout:15000});}
  catch {const error=new Error('email_method_unavailable');error.safeReason=error.message;throw error;}
  const element=await page.locator('#tp_frame').elementHandle();
  const frame=element && await element.contentFrame();
  if(!frame || !originIs(page.url(),ORIGIN) || !originIs(frame.url(),OTP_ORIGIN)) {
    const error=new Error('unexpected_otp_origin');error.safeReason=error.message;throw error;
  }
  return frame;
}
async function portalReady(page) {
  return originIs(page.url(),ORIGIN) && new URL(page.url()).pathname.startsWith('/dana/user/') &&
    await page.locator('[id="1-header"]').count()===1;
}
module.exports = {ORIGIN, OTP_ORIGIN, originIs, allowedRequest, allowedLauncher, emailFrame, portalReady};

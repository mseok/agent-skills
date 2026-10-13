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
module.exports = {ORIGIN, OTP_ORIGIN, originIs, allowedRequest, allowedLauncher};

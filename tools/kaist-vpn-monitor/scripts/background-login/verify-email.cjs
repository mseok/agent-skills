'use strict';
const {Resolver} = require('node:dns/promises');
const {dkimVerify} = require('mailauth/lib/dkim/verify');
const {simpleParser} = require('mailparser');

async function validateMessage(encoded, receivedAtMs, current, options = {}) {
  if (!Number.isSafeInteger(receivedAtMs) || receivedAtMs < current.capturedAtMs - 2000 || receivedAtMs > current.expiresAtMs) throw new Error('stale_message');
  if (typeof encoded !== 'string' || encoded.length > 1048576 || !/^[A-Za-z0-9_=-]+$/.test(encoded)) throw new Error('message_unavailable');
  const raw = Buffer.from(encoded, 'base64url');
  const boundary = raw.indexOf('\r\n\r\n');
  if (boundary < 0 || boundary > 65536) throw new Error('message_unavailable');
  const headers = raw.subarray(0,boundary).toString('latin1').split(/\r\n(?![ \t])/);
  if (headers.some(header => header.indexOf(':') < 1 ||
      !/^[\x21-\x39\x3b-\x7e]+$/.test(header.slice(0,header.indexOf(':'))) ||
      /[\r\n]/.test(header.replace(/\r\n[ \t]+/g,' ')))) throw new Error('message_unavailable');
  const count = name => headers.filter(header => header.slice(0,header.indexOf(':')).toLowerCase() === name).length;
  if (count('from') !== 1 || ['subject','content-type','content-transfer-encoding','mime-version'].some(name => count(name) > 1) || count('dkim-signature') > 8) throw new Error('message_unavailable');
  const domain = current.otpSender.split('@')[1];
  const dns = new Resolver({timeout:2000, tries:1});
  let lookups = 0;
  const resolver = async (name, type) => {
    // Only request DKIM TXT keys under the explicitly enrolled sender's domain.
    const suffix = '._domainkey.'+domain;
    const normalized = name.toLowerCase();
    const selector = normalized.endsWith(suffix) ? normalized.slice(0,-suffix.length) : '';
    if (++lookups > 8 || type !== 'TXT' || !/^[a-z0-9_-]+(?:\.[a-z0-9_-]+)*$/.test(selector)) throw new Error('unapproved_key_lookup');
    return options.resolver ? options.resolver(name,type) : dns.resolveTxt(name);
  };
  const verified = await dkimVerify(raw, {strict:true, minBitLength:2048, resolver});
  if (verified.headerFrom?.length !== 1 || verified.headerFrom[0].toLowerCase() !== current.otpSender) throw new Error('sender_mismatch');
  const required = ['from', ...['content-type','content-transfer-encoding','mime-version'].filter(name => count(name))];
  const authenticated = verified.results.filter(result => {
    const signed = (result.signingHeaders?.keys || '').split(':').map(name => name.trim().toLowerCase());
    const signedAt = Date.parse(result.signTime);
    return result.status.result === 'pass' && !result.status.testing &&
      result.signingDomain?.toLowerCase() === domain && result.canonBodyLengthLimit === undefined &&
      signed.includes('from') &&
      (result.signTime === undefined || result.signTime === null ||
        (Number.isFinite(signedAt) && signedAt >= current.capturedAtMs - 120000 && signedAt <= current.expiresAtMs));
  });
  if (!authenticated.length) throw new Error('email_authentication_failed');
  const signedKeys = result => (result.signingHeaders?.keys || '').split(':').map(name => name.trim().toLowerCase());
  if (!authenticated.some(result => Number.isFinite(Date.parse(result.signTime)) && required.every(name => signedKeys(result).includes(name)))) {
    // Actual KVPN signs Subject and the entire ASCII body, but not MIME or Date.
    // Ignore unsigned interpretation headers: extract exactly one literal code
    // from authenticated bytes. DKIM relaxed whitespace cannot change digits.
    if (count('subject') !== 1 || !authenticated.some(result => signedKeys(result).includes('subject'))) throw new Error('email_authentication_failed');
    const subjectHeader = headers.find(header => header.slice(0,header.indexOf(':')).toLowerCase() === 'subject');
    const parsedSubject = await simpleParser(Buffer.from(subjectHeader+'\r\n\r\n','latin1'));
    const body = raw.subarray(boundary+4).toString('latin1');
    if (!/KVPN\s+OTP\s+number/i.test(parsedSubject.subject || '') || !/^[\x09\x0a\x0d\x20-\x7e]*$/.test(body)) throw new Error('template_mismatch');
    const codes = body.match(/(?<![0-9])[0-9]{6}(?![0-9])/g) || [];
    if (codes.length !== 1) throw new Error('template_mismatch');
    return codes[0];
  }
  const parsed = await simpleParser(raw, {skipHtmlToText:true, skipTextToHtml:true, skipImageLinks:true});
  const body = parsed.text || parsed.html || '';
  const otp = body.match(/KVPN\s+OTP\s+number[\s\S]{0,4096}?(?<![0-9])([0-9]{6})(?![0-9])/i)?.[1];
  if (!otp) throw new Error('template_mismatch');
  return otp;
}
module.exports = {validateMessage};

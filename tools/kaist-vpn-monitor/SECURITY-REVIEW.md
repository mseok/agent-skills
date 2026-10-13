# Security review: Community 0.2.0

Review date: 2026-10-13. Reviewer: independent **GPT-6 Astra, High** agent.
Scope: source, installation skill, dependency manifests, and isolated synthetic tests.
The reviewer did not access real credentials, mail, VPN sessions, or macOS permissions.

## Findings in 0.1.0 and remediation

The reviewer demonstrated three Medium-severity mail issues. No High/Critical
exploit, account takeover, or credential theft was demonstrated. This does not
establish that none exists.

1. **Sender-baseline poisoning:** one unrelated OTP-template email could make the
   entire Mail-derived sender baseline ambiguous and permanently block recovery.
   Removed Mail enumeration and its Full Disk Access requirement. Sender enrollment
   is explicit local configuration from a user-verified legitimate message.
2. **Invalid candidate abort:** a rejected email candidate stopped recovery before
   a later valid candidate was considered. Validation rejections are now skipped
   within the existing deadline. IPC and transport failures still stop recovery.
   Gmail search narrows to the enrolled sender and retrieves up to 50 candidates.
3. **Forged From accepted:** matching From text did not authenticate an OTP email.
   Added pinned `mailauth` DKIM verification and `mailparser` MIME parsing. Require
   the exact enrolled mailbox, a valid full-body signature from its exact domain,
   signed From and present MIME interpretation headers, no duplicate From/MIME
   headers, no `l=` body truncation, a non-test key, and RSA keys of at least 2048 bits.
   The verified signature timestamp must be within 120 seconds before the request
   and the request expiry. Raw Authentication-Results headers are never trusted.

The reviewer also identified conditional origin/launcher weaknesses. The patch
checks the live OTP Frame URL, rechecks page origin around credential use, checks
the login action, restricts browser requests to the two configured HTTPS origins,
and filters native launch requests to observed main-frame navigations while the
trusted portal is open. The navigation target is not proof of the initiating
script; this distinction is retained as a residual. No vendor URI
format was invented; native URI payload validation remains a vendor trust boundary.

The second review also caught an oversized-candidate abort and Playwright's
redirect interception limitation. Oversized mail is now skipped before IPC.
A random request identifier binds both submission and abort messages to one
challenge, with expiry checks before each candidate and after mail retrieval.
A temporary loopback CONNECT proxy only permits the two exact VPN TLS endpoints;
this connection boundary also blocks off-list redirect hops. TLS is not decrypted
by the proxy, and the proxy closes with the owned browser.

## Residual risks and compatibility

- Actual KVPN messages may lack a compatible signature, timestamp, or signed MIME
  headers, or use a delegated signing domain. Such mail is rejected. No actual
  KVPN account login was used to prove compatibility of the new verifier.
- Freshness is not binding to a server-issued challenge. A genuine signed message
  replayed within the permitted window may still cause wrong-code rejection.
  The VPN server remains the final OTP authority. No bypass was demonstrated.
- Sustained mailbox flooding, DNS failure, connector changes and platform changes
  can still deny service. Candidate and signature work is bounded; availability
  under arbitrary flooding is not guaranteed.
- DNS key lookup trusts the local DNS environment. Only TXT selectors under the
  configured sender's domain are queried. This is not DNSSEC verification.
- Same-user malware can alter user-owned code or access its session profile.
  File modes and ad-hoc signing are not isolation from that attacker.
- The official portal, Ivanti client, launcher URI interpretation, OS privacy
  controls and SSH configuration remain trusted. Whole-system compromise and
  vendor binary auditing are outside this review.
- Scheduled process shutdown and real unattended recovery were not exercised.

## Evidence

Synthetic tests cover the fixed mail failures, real DKIM verification with
ephemeral test keys and fake DNS, MIME tampering, freshness, configuration and
browser-origin policy. A current npm audit reports zero known advisories for the
pinned dependency tree; that is not a claim of vulnerability-free dependencies.

The final independent re-review found no remaining release-blocking defect in the
reviewed source/synthetic scope. It reran all 21 tests and additional crypto fixtures.
A fresh headless Chrome integration check also rejected synthetic off-list 307 and
308 POST redirects with `ERR_TUNNEL_CONNECTION_FAILED` using the production proxy
settings. Approved-host speculative preconnections were absorbed by inert test
sockets; no real portal response or authentication was used. This verifies that
narrow HTTP(S) redirect boundary, not every browser transport or real KVPN flow.

App build, strict ad-hoc signature verification, and the read-only initial status
check passed. See [VALIDATION.md](VALIDATION.md) for the full scope and limits.

---
name: ivanti-daily-login
description: Authenticate the KAIST KVPN web portal in regular Google Chrome, hand off through its authorized Ivanti launcher, verify the native SA (kvpn.kaist.ac.kr) connection, and check the messi SSH path without exposing credentials or OTPs.
---

# Ivanti Daily Login

Use Computer Use with regular Google Chrome for web authentication. Use native Ivanti Secure Access Client only for the final connection-state check after the authenticated KVPN portal offers its Start control. Do not use the ChatGPT in-app browser for this workflow.

## Keychain prerequisite

Run `scripts/configure-keychain.zsh` interactively once before the first unattended run. It stores the username and password under:

- `codex.ivanti-daily-login.username`
- `codex.ivanti-daily-login.password`

The Chrome helper `scripts/type-keychain-chrome.zsh` reads those values only through a private pipe and assigns them to the already focused field. Never read, print, log, copy, OCR, transcribe, or report either value or an OTP.

## Workflow

1. In regular Google Chrome, require an HTTPS page whose host is exactly `kvpn.kaist.ac.kr`. Reuse the existing KVPN tab when possible. If it is already at `/dana/user/` with the authenticated welcome/client-session content, continue; otherwise require the expected `VPN Login`, `User name`, `Password`, `KAIST Members`, and `LOGIN` controls.
2. Use a run-wide maximum of three credential `LOGIN` submissions. The first is immediate; wait 10 seconds before attempt 2 and 30 seconds before attempt 3. Before every submission, re-check the exact host and expected form.
3. Enter credentials only after the exact-host check. Directly click and clear each field, then run `scripts/type-keychain-chrome.zsh username` and `scripts/type-keychain-chrome.zsh password` while the corresponding field is focused. Never use `Tab`, `Shift-Tab`, `Return`, synthesized keystrokes, or keyboard navigation between credential fields. Keep `KAIST Members` selected.
4. After credential `LOGIN`, select `SMS` immediately, directly focus the editable `Input your OTP` field, and monitor the visible screen for at most 30 seconds. When the dark macOS Messages popover with a speech-bubble icon, `Fill code` first line, and `From Messages` second line appears, click its center without reading or reporting any digits. If it remains visible while the field is visibly empty, click its center once more only. Use the visual dismissal/population signal and click the current `Login`; never require AX to reveal the OTP.
5. Confirm the authenticated portal at the exact host `/dana/user/`. Expand `Client Application Sessions` and click its `IVANTI SECURE ACCESS CLIENT` `Start` control. If Chrome shows `Open PulseApplicationLauncher.app?`, click `Open` (the web-to-native handoff is authorized). Never click a generic download. If the launcher is reported missing, do not claim success; stop with a non-secret failure, except that one safe LaunchServices registration refresh and one Start retry may be used only when the known launcher bundle is already present and registered.
6. In native Ivanti Secure Access Client, use only the recorded profile `SA (kvpn.kaist.ac.kr)`. If it is inactive, choose `Connect`. If it already shows `1 Active Connection` and `Disconnect`, do not disconnect, suspend, or extend; continue to verification. If `User input timeout (1382)` appears, dismiss it with `Cancel`, never `Retry`, then inspect the main window. Native success requires `1 Active Connection` plus `Disconnect`.
7. Run the bounded read-only check `ssh -o BatchMode=yes -o ConnectTimeout=10 -o ConnectionAttempts=1 messi 'hostname'`. End-to-end success requires exit code 0. A nonzero result or timeout is a failure even if the web portal is authenticated. Leave a successful native connection in place.

## Retry and terminal failures

Retry only ordinary page-load, focus, credential-assignment, SMS, OTP-autofill, or unconnected timeout failures while attempts remain: stop using the current page, return to a fresh exact-host page, and never click an in-page `Retry`. Treat `Error:1308` as a terminal native error unless the automation explicitly allows its one clean restart. Treat other numeric/product/server errors, TLS or certificate errors, unexpected host/form, account lock or disable, IP block, permission denial, password expiry, invalid realm, unsupported client, CAPTCHA, Keychain prompts, missing profile, or blocked browser access as terminal. After the third ordinary attempt, stop and report the last non-secret reason with the attempt count.

## Safety

- Transmit username, password, and SMS OTP only to the exact `kvpn.kaist.ac.kr` authentication flow.
- Never expose, copy, log, OCR, transcribe, or report secrets or OTP digits.
- Never touch MapleStory (`com.nexon.maplestory.kr.v1`) or unrelated user work. Do not use BetterDisplay, virtual displays, AeroSpace workspace moves, global focus/frontmost tricks, `pkill`, `kill -9`, `sudo`, administrator passwords, or root-service termination.
- Do not claim web-only authentication as system VPN success. Keep a successful native connection open long enough to verify it and the SSH check.

## Scheduled run contract

The scheduled prompt must authorize stored Keychain credential entry and SMS autofill at `kvpn.kaist.ac.kr`, use the bounded retry policy, and return only a concise non-secret status and authentication-attempt count.

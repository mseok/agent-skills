# Current security contract, 2026-10-13

Use the self-contained personal app or `monitor.cjs`, not direct authentication
through `run.cjs`. The SKILL.md Security update section supersedes historical
Mail-reader, sender-hash, old-runtime and no-flag login instructions below.
No Mail access is used. Exact sender/domain/full-body DKIM, signed Subject with
fixed ASCII code extraction, same-ID Gmail metadata receipt, request-ID binding
and the HTTPS CONNECT allowlist are required. Original Keychain names and native
recovery boundaries remain. Existing-session continuation is authorized when
the exact native profile is inactive. Preserve process handles and never print
raw mail, OTP, credentials, authentication URLs or private browser logs.

The following retained evidence describes historical behavior.

# Ivanti Daily Login

For scoped manual recovery, use the installed background runner on the Mac mini:

```sh
/opt/homebrew/bin/node /Users/mseok/.codex/skills/ivanti-daily-login/scripts/background-login/run.cjs
```

Scheduled maintenance uses `monitor.cjs` from SKILL.md. The underlying runner uses the installed **Google Chrome** in headless mode with a separate profile and a private DevTools pipe. It does not use the user's Chrome profile, an in-app browser, Apple Events JavaScript, global input, window activation, a virtual display, or the macOS Mail app. The user authorized background VPN connection, private Keychain access, read-only Gmail connector access, read-only access to locally synced KVPN email messages, the portal's Ivanti launcher handoff, and reconnecting the account when its previous web session remains.

## Verified behavior — 2026-09-14

The original background flow completed Keychain login, an OTP submission, the existing-session confirmation, portal client-section expansion, the actual Start button, and native PulseApplicationLauncher delivery. The exact `SA (kvpn.kaist.ac.kr)` submenu then offered an enabled `Disconnect`; messi SSH exited 0 and returned `master`. Closing the headless browser preserved the VPN. The installed runner was then executed against that live connection and returned `connected`, `ssh: ok`, `attempts: 0`, and `reusedConnection: true`.

The authentication and launcher stages were verified in the persistent controller during implementation. The installed consolidated runner's already-connected path was also verified. The Mail reader was validated against existing locally synced KVPN OTP messages, but do not describe a new unattended email cold-start run as separately tested until one actually completes. It never launches Mail to make that happen. The Gmail-connector bridge is also not a live reconnection proof until it completes one end-to-end run. Do not disconnect a working VPN merely to manufacture either test.

If the native handoff presents the exact `User input timeout. (1382)` sheet, it can temporarily hide the profile's `Disconnect` action even though SA is connected. The runner dismisses only that exact sheet with its `Cancel` button, then rechecks the exact tray state and SSH. It never presses `Retry`, resubmits credentials, or requests another SMS for this condition.

If the initial native inspection is unavailable or indeterminate while the Ivanti user app is running and Accessibility access is available, the runner first makes one normal termination request. If that app does not exit, it makes one scoped use of Ivanti's exact `Exit` item in its own status menu, accepting only the immediate confirmation it causes: the current 22.8 client exposes an `OK`/`Cancel` `AXWindow` dialog, while an explicitly labelled `Exit`/`Cancel` form is also accepted for compatible versions. It then relaunches Ivanti hidden without activation and rechecks the exact profile. It never force-quits a process or terminates Ivanti services. If the recheck finds the explicit inactive state it continues with the ordinary authenticated flow; if the state remains unavailable or indeterminate, it stops safely.

On 2026-09-22, this recovery route was exercised after an indeterminate native state: normal termination timed out, the scoped Exit confirmation was completed, the user app disappeared, hidden relaunch reached the explicit inactive SA state, and the background connector flow ended with exact SA plus messi SSH verified. This is the live evidence for the current confirmation handling; it did not activate the user's desktop apps.

## Session timeout window — 2026-10-04

KVPN ends each session about 10 hours after connect (`ISACEvents.log`: `disconnected by server`; `PulseClient.log`: `session timed out`). With the server-pushed profile attribute `reconnect-at-session-timeout: "true"`, Ivanti retries by itself within three seconds (`onRetry direct now (session expired/deleted)`) and shows its embedded-browser login window (`Mac prompt window display`, `Using Embedded browser for login`) in front of the app in use. That window, not the monitor, was the reported interruption; the monitor-driven reconnect on 2026-10-04 created no Ivanti web page or prompt window.

`scripts/set-ivanti-session-reconnect.sh off` flips only that attribute in `/Library/Application Support/Pulse Secure/Pulse/connstore.dat` and `.bak`, keeps a copy beside them, and restarts `net.pulsesecure.AccessService` so the change is read; `on` restores the server default. It needs the user's own `sudo` and drops a live VPN once, so never run it on the user's behalf or to manufacture a test. The attribute is world-readable: `grep reconnect-at-session-timeout` on `connstore.dat` shows the current value.

Applied on 2026-10-04 03:27 KST: the restarted service loaded `"false"` and wrote it back to `connstore.dat`, then resumed the still-valid session by itself within 14 seconds (`Retrieved existing DSID for resumption check`) with no prompt window and no OTP. The script is silent for about 30 seconds while it waits for the two service restarts; an interrupt during that wait leaves the change applied.

First timeout with `"false"`, 2026-10-04 10:56:12 KST: Ivanti went to `disconnected` within three seconds with no prompt window, no web page and no UI restart; the next 10-minute check reconnected from the explicit inactive state at 11:06:48 with one credential submission and no model call. `connstore.dat`, rewritten by that portal-launched connect, still read `"false"` at version 20, so the value survived the server's profile script.

The server re-sends its profile script (connection version 20, attribute `"true"`) through `jamCommand -import` on every portal-launched connect. If the local value is found back at `"true"`, report it; do not reapply silently. A timeout is handled correctly when no `Mac prompt window display` line follows `session timed out` and the next scheduled check reconnects from the explicit inactive state.

## Execution contract

1. Run once and retain the process/session handle until it exits. A progress line is not completion. If observation times out, poll the same live handle; do not launch another process merely because a tool wait ended.
2. If the Ivanti user app is absent but Accessibility access is available, start the installed app once with foreground activation disabled, hidden, and with no user prompt, then wait briefly for the exact tray profile. When native state is not connected, hide any existing Ivanti windows without changing focus. Do not use its credential UI, force-stop a process, or synthesize input. Final success still requires a `connected` JSON result and exit code 0: it verifies the **exact profile's submenu** and a bounded `ssh -o BatchMode=yes -o ConnectTimeout=10 -o ConnectionAttempts=1 messi hostname`. A global Disconnect button alone is insufficient. The main Ivanti window can remain closed; do not foreground it to obtain a literal “1 Active Connection” label.
3. If already connected, verify SSH and exit with zero credential submissions and zero SMS requests. If SSH fails while native state is connected, report the SSH failure; do not replace the connection by blindly reauthenticating. When a running user app has an unavailable or indeterminate native state, make one normal user-app exit; only if it fails to exit, use the exact Ivanti status-menu `Exit` action once and accept only its immediate expected confirmation (`OK`/`Cancel` in the current client, or `Exit`/`Cancel` in compatible versions), then relaunch hidden and recheck. Do not force-quit a process or stop Ivanti services. A native state is eligible for reauthentication only when the exact profile explicitly offers Connect and the tray explicitly reports no active connections; a state still unavailable or indeterminate after that one restart stops without credentials or email OTPs.
4. When that explicit inactive state is present, authenticate through exact origin `https://kvpn.kaist.ac.kr`, with `KAIST Members`. The observed OTP iframe must have exact origin `https://kvpnportal.kaist.ac.kr:8443` under that top-level page. Select only its exact Email OTP option. Credentials come from Keychain services `codex.ivanti-daily-login.username` and `codex.ivanti-daily-login.password`.
5. Before an email authentication run, the runner never launches, activates, or drives macOS Mail. The read-only Mail reader captures a request time and the non-secret hash of the sole historical KVPN OTP sender immediately before the Email choice. It accepts only a newly synced local Mail message from that pinned sender matching the exact KVPN OTP template and freshness window. The operating system's existing background mail synchronization may populate that local cache; if it does not, the runner reports the bounded email timeout without opening a mail app. Its secret-bearing output is private child-process IPC only. Email timeout can retry after 10 seconds and 30 seconds, with a run-wide maximum of three credential submissions. Unexpected forms, credential rejection, permissions, native state failures, or other non-timeout errors stop the run.
6. KVPN can show `Confirmation` with `Continue the session` after OTP. It warns that the previous web session will end. The authorized reconnection flow handles this immediately when native preflight was inactive; waiting on that screen caused an authentication failure during diagnosis. Do not confuse this screen with OTP failure or request another SMS while it is pending. Any failed run leaves its web session open, so the next login always gets this screen; after `Continue the session` the page passes `/dana/home/starter0.cgi`, whose document can have no body yet, so wait predicates must use `document.body?.innerText` (a null-body exception looped every recovery on 2026-10-19 and was fixed on 2026-10-20).
7. Authentication can redirect to `/download/`; the observed portal link is `/dana/user/`. The new React client-section header and Start control did not respond reliably to simulated mouse clicks. In the dedicated headless profile, exact DOM clicks on the observed client header and `#client_card_start_button` succeeded.
8. Before entering the portal page and before clicking Start, observe any portal-generated `pulsesecure:` navigation privately and deliver that exact URI through the compiled `open-launcher.swift` helper to the installed PulseApplicationLauncher, with foreground activation disabled, hidden, and no user prompt. This also handles a launcher navigation that aborts the portal page load. After handoff, hide the Ivanti app once without changing focus. Wait up to three minutes for the exact native profile and SSH verification, dismissing only the exact `User input timeout. (1382)` sheet with Cancel if it appears. Never reconstruct session tokens, use the native credential-login UI, or press Retry. Other native errors or prompts that prevent verified connection are failures, not success.
9. Leave a successful native connection open. Close only the task-owned headless browser. Never kill Ivanti services, restart the user's Chrome, move workspaces, touch MapleStory, or synthesize global keyboard/mouse input.

## Gmail connector mode for scheduled Codex runs

When the scheduled Codex agent has the connected Gmail plugin, run the primary command once with `--connector-otp` and retain that process handle. This mode never launches Mail and does not use the local Mail cache to wait for fresh mail. It uses the existing cache only to pin the non-secret hash of the known KVPN sender before requesting Email OTP.

When the runner emits its sanitized `authenticating` / `email` progress status, it creates a 0700-runtime, one-time Unix socket request. The agent must call `scripts/background-login/submit-connector-gmail-otp.cjs --request` to obtain only its safe capture and expiry timestamps; use Gmail search and a `format: "raw"` message read privately to find a message received after that capture time. Pass only the returned raw Gmail message through the helper's standard input with `--received-at-ms <connector received milliseconds>` from that search result. Do this within a `functions.exec` tool script and never emit the Gmail tool result, raw message, OTP, sender, or helper input. The helper locally validates the pinned sender hash, exact KVPN OTP template, and freshness, then forwards the OTP over the one-time socket without printing or saving it. It returns only a sanitized status.

If no validated fresh Gmail message arrives by the 90-second window, preserve the runner's bounded three-attempt policy. Do not fall back to opening, activating, or driving macOS Mail. The no-flag default remains the local-cache-only mode for manual maintenance checks.

## Dependencies and files

- `scripts/background-login/run.cjs`: complete background runner.
- `scripts/background-login/submit-connector-gmail-otp.cjs`: private stdin-to-socket bridge that locally validates a Gmail raw message and never prints or persists its OTP.
- `scripts/background-login/package.json` and `package-lock.json`: pinned `playwright-core` 1.63.0; its dependency is installed locally. Google Chrome itself is already installed; no separate browser download is needed.
- `scripts/preflight.swift`: read-only native tray inspection, scoped to the exact SA profile for Connect/Disconnect state.
- `scripts/launch-ivanti.swift`: starts the installed Ivanti user app only when it is absent, with foreground activation disabled; it never opens a credential form or uses global input.
- `scripts/restart-ivanti.swift`: requests normal termination of only the Ivanti user app, waits for it to exit, and never force-quits a process or touches services.
- `scripts/exit-ivanti.swift`: bounded fallback that presses only Ivanti's exact status-menu `Exit` item and its immediate expected confirmation (`OK`/`Cancel` in the current client or `Exit`/`Cancel` in compatible versions), then verifies the user app has exited.
- `scripts/hide-ivanti.swift`: hides or minimizes windows belonging only to an already-running Ivanti app without changing focus, processes, menu-bar state, or any other app.
- `scripts/mail-otp.swift`: read-only local Mail reader scoped to the Gmail mailbox and exact KVPN OTP template. A non-secret `--probe` is allowed through ordinary tools. Never invoke its `--wait` mode through a tool that displays stdout.
- `scripts/open-launcher.swift`: private-stdin launcher URL handoff with no foreground activation, visible window, or prompt.
- `scripts/dismiss-timeout.swift`: scoped accessibility recovery for the exact non-secret `User input timeout. (1382)` sheet; it can only press its `Cancel` button.
- Runtime cache: `~/Library/Caches/codex-ivanti-background`, mode 0700. It contains compiled helpers, the separate Chrome profile and the run lock. Never copy that profile into reports, outputs, version control or another Chrome profile.
- A live lock owner blocks duplicate runs. The runner removes a stale lock only after confirming its recorded PID no longer exists. Do not remove a lock based only on its age. A browser/profile failure does not authorize terminating unrelated processes.

If dependencies are absent, install only this local package with `npm ci --ignore-scripts --no-audit --no-fund` in the resolved `scripts/background-login` directory. The runner compiles its Swift helpers into the private runtime cache when needed. Keychain prompts, unavailable or stale local Mail data, or lack of Accessibility permission require a non-secret failure report; do not keep requesting email OTPs.

## Secrets and diagnosis

Never expose credentials, OTP digits, Messages bodies, full authentication URLs, iframe src values, session-bearing launcher URIs, browser logs, or raw child-process exceptions. Keep values in private process memory and private pipes; clear credential/code variables after use. Output only the runner's sanitized JSON result and concise failure reason.

The user's Chrome “Allow JavaScript from Apple Events” setting is **not required** by this workflow. In earlier diagnosis, Chromium rejected synthesized clicks on that security toggle; the user had clicked through remote control. Do not ask them to toggle it again, spoof event provenance, edit browser preference files, or reuse the obsolete foreground/AutoFill helpers for the background task.

## Scheduled run

The current entrypoint is `scripts/background-login/monitor.cjs`, described in
SKILL.md. It performs model-free health checks and Gmail-mediated recovery;
the manual connector procedure above is retained for scoped maintenance.
Retire the old hourly Codex heartbeat only after verifying the actual LaunchAgent result: exact SA profile plus messi SSH. Installation alone is insufficient.

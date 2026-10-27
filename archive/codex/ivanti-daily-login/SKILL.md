---
name: ivanti-daily-login
description: Maintain KAIST KVPN on the Mac mini with model-free health checks and bounded background recovery, using the existing private Keychain and Gmail connector flow. Inspect a failure or deliberately retry recovery without interrupting desktop work.
---

# KAIST VPN maintenance

The LaunchAgent runs the self-contained app monitor every 20 seconds. Healthy
checks and the established reconnection flow need no model. Gmail is called
through an ephemeral Codex tool context without a model turn; OTPs travel only
through private memory, stdin and the existing one-time socket.

Scheduled runs are owned by `~/Applications/KAIST VPN Monitor.app`. Its macOS
Accessibility permission is separate from Codex's permission. The secured app bundles its runtime and compiled helpers. Do not use the legacy
`install-monitor.py` to overwrite it. Refresh only while no monitor or authentication
run is active, preserving its bundle identity and a rollback copy. Opening the app requests user approval;
never change privacy databases or grant permission on the user's behalf. Verify
the actual LaunchAgent result before retiring a previous schedule. For interval
changes, preserve the installed app and edit only its external LaunchAgent.

Use the installed shared Node executable `/opt/homebrew/bin/node`:

- `scripts/background-login/monitor.cjs --status`: read the compact last status.
- `scripts/background-login/monitor.cjs --check-only`: inspect exact SA state
  and bounded messi SSH reachability without reconnecting or changing apps.
- `scripts/background-login/monitor.cjs`: check and perform authorized known
  recovery if needed. Preserve the live process handle; do not launch copies.
- `scripts/background-login/monitor.cjs --retry`: deliberately retry a latched
  incident after its cause has been addressed or retry was explicitly requested.

The monitor preserves the runner's existing three-attempt email-timeout bound,
exact origin/profile checks and credential handling. A connector failure stops
before authentication when detected during preflight. Native-connected plus
SSH-failed is not permission to reauthenticate. Credential rejections and other failed incidents remain latched while scheduled
read-only health checks continue. A recognized Gmail failure during email authentication
can resume after search, raw and same-message metadata readiness checks pass,
with at most three credential submissions across the incident. A healthy observation
clears the incident. A Gmail connector preflight failure with zero authentication
attempts is checked again on the next scheduled run, so temporary unavailability
after login does not permanently stop recovery. No authentication begins until
the connector is ready; repeated connector outages do not repeat notifications.
The LaunchAgent uses RunAtLoad to start at user login after reboot.
Report meaningful recovery or required action, not unchanged
healthy checks. The secured monitor never starts model inference.

Current state: `~/.local/state/codex-vpn-monitor/state.json`. Old `diagnosis.txt` files may be historical. These records contain no mail,
OTP, sender, authentication URL or browser output. Use them before old chat logs.

KVPN ends every session about 10 hours after connect. Ivanti's profile attribute
`reconnect-at-session-timeout` should be `"false"`: with the server default
`"true"` Ivanti opens its own login window in the foreground at each timeout.
`scripts/set-ivanti-session-reconnect.sh off` sets it; it needs the user's own
`sudo` and restarts Ivanti's service, so the VPN drops once. See the session
timeout section of the recovery contract before touching it.

Read [the recovery contract](references/recovery.md) only when diagnosing or
changing authentication, the native app helpers or the private connector bridge.
It retains exact verification evidence and existing authorization boundaries.
Do not disconnect a working VPN without explicit user authorization for a real reconnect test. Never activate
Mail, the user's Chrome, games or other apps, or use global keyboard/mouse input.

## Security update, 2026-10-13

App commands: `~/Applications/KAIST VPN Monitor.app/Contents/MacOS/kaist-vpn-monitor`
with `--status`, `--check-only`, `--scheduled`, or `--retry`. The app uses its
bundled scripts; this skill copy is kept aligned for deliberate diagnostics.
Personal configuration is `~/.config/codex-vpn-monitor/config.json` (0600).
Private runtime is `~/Library/Caches/codex-ivanti-background-secure-v021` (0700);
the older runtime remains untouched for rollback and is not used by this version.
Keychain services remain `codex.ivanti-daily-login.username` and `.password`.
There is no Mail-reader fallback. Recovery requires the monitor Gmail bridge.
It verifies exact sender/domain and full-body DKIM, uses same-ID Gmail metadata
`internal_date`, and binds submission to a fresh request ID. Real KVPN mail uses
a signed Subject and exactly one literal ASCII code; unsigned MIME is ignored.
Recent delivery does not prove recent creation: replay of a genuine older mail
can cause a rejected OTP or recovery failure, not an established login bypass.
HTTPS egress is restricted by the reviewed two-origin CONNECT proxy.

## Audit notes (2026-10-17)

- The installed ad-hoc signature identifies this exact code, not just its bundle ID. Re-signing it changes the permission identity. Preserve the installed bundle for routine maintenance. A necessary code update needs a separately reviewed stable-identity migration, such as a fixed launcher with external scripts or a persistent signing identity; neither is already implemented. Exception verified on 2026-10-20: an in-place edit of one script under `Contents/Resources/scripts` without re-signing kept the cdhash designated requirement and the Accessibility grant (scheduled native checks stayed normal); only `codesign --verify` reports the modified sealed resource.
- Port fixes into the installed personal app as a minimal patch on its current code; store rollback copies as `.app.backup` or a zip so LaunchServices never registers a second bundle with the same identifier.
- Report "fixed" only after the scheduled entry point completes a disconnected-to-connected run; the previous mechanism stays active until that passes. A mail-tool error during login must not latch the monitor off; classify it as transient and retry on the next scheduled run.

## Permission-preserving maintenance (2026-10-18)

- The current personal app is protected with reversible user immutable (`uchg`)
  flags. Do not clear them, overwrite the app, or re-sign it during diagnosis or
  an interval change. Check protection before stopping any existing schedule.
  The legacy installer now refuses to overwrite this self-contained app.
- Direct commands launched from Codex can report `accessibility_unavailable`
  while the app's own LaunchAgent remains healthy. Inspect `--status`, its fresh
  timestamp and the actual scheduled result before asking for any reapproval.
  A direct caller's denial does not establish a missing grant for the scheduler.
- The 20-second interval permits at most 4,320 healthy checks per day. Each check
  reads the exact native profile and verifies SSH; model calls remain zero.
  Launchd and the existing locks prevent overlapping recovery. The existing
  three-submission incident budget is unchanged. These are checks, not a
  guarantee that a full reconnection finishes within 20 seconds.
- For schedule-only maintenance, verify the unchanged designated requirement,
  strict deep signature, loaded interval and fresh scheduled native/SSH results.
  Do not disconnect a healthy VPN for that check. Authentication-code changes
  still require the real recovery evidence described above.
- The Mac mini restore manifest and task script are in
  `/Volumes/ExternalSSD/inbox/kaist-vpn-maintenance-20261018/restore-manifest.json`
  and `maintain.py` beside it. Restore only the recorded flags and interval when
  rollback is requested. A deliberate code update must address permission
  identity before removing protection, and keep the working schedule until
  its replacement is approved and verified.

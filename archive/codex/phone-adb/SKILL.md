---
name: phone-adb
description: Operate the user's Android phone (Galaxy Z Fold 7) over adb for a specific requested input, such as typing a code, tapping a named button or posting a prepared listing. Use when the user says 폰에서, 핸드폰, adb, 당근에 올려줘, or asks to press or type something on the phone. Not for exploring the phone, screenshots for curiosity, or changing phone settings.
---

# Phone input over adb

## Connect

1. Use the connection helper `scripts/nxplay.py` beside this file: `nxplay.py status` shows the connection, screen, lock state and foreground app; `nxplay.py adb <args>` runs adb against the resolved endpoint. It tries the existing connection, the last working endpoint, port 5555, the wireless-debugging port on the LAN, then the phone's Tailscale address.
2. Wireless debugging must be switched on by the user, and Android turns it off after Wi-Fi drops and at reboot; the port changes each time. If no connection is found, tell the user exactly that in one line and wait. Pairing codes come from the user; never store them in memory or notes.
3. `persist` (adb on port 5555 until reboot) needs the user's explicit agreement each time; do not make it automatic.

## Act

1. Check the foreground app and screen state immediately before every tap or text input; after any delay, check again. Type into the target app only.
2. Perform only the requested input. No exploratory taps, no browsing other pages, no screenshots except to confirm the exact screen before and after the requested action.
3. Never enter the phone's PIN, pattern, passwords or app-lock codes, and never accept other prompts.
4. Temporary setting changes (keyboard, developer options) are reverted at the end and reported.
5. Report what the phone showed after the action; if unclear, say so. An expired OTP needs a new one from the user; do not retry an old code.

## Known apps

- Marketplace posting (당근): prepare the listing text and images locally, show them to the user, post only after approval, and verify the published listing on screen.

## Verified additions (2026-10-17 audit)

- Provisioning the user's own app on the phone (installs, grants, start-on-boot, VPN) follows the same per-action approvals as any setting change; each persistent setting is listed with its revert command. Never route adb around a macOS Local Network block through another already-permitted binary; name the block and the setting that grants it.

#!/bin/zsh
set -euo pipefail

readonly account="ivanti-daily-login"
readonly username_service="codex.ivanti-daily-login.username"
readonly password_service="codex.ivanti-daily-login.password"

print -r -- "Store the Ivanti username in macOS Keychain."
print -r -- "At the next hidden prompt, enter the username used on the recorded VPN Login page."
/usr/bin/security add-generic-password -U -a "$account" -s "$username_service" -w

print -r -- "Store the Ivanti password in macOS Keychain."
print -r -- "At the next hidden prompt, enter the password used on the recorded VPN Login page."
/usr/bin/security add-generic-password -U -a "$account" -s "$password_service" -w

/usr/bin/security find-generic-password -a "$account" -s "$username_service" >/dev/null
/usr/bin/security find-generic-password -a "$account" -s "$password_service" >/dev/null

print -r -- "Ivanti credentials are configured in macOS Keychain."

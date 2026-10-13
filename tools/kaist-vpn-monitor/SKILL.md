---
name: kaist-vpn-monitor
description: Install, configure, inspect, or maintain the macOS KAIST VPN Monitor Community app from this self-contained skill. Use for KAIST KVPN and Ivanti background reconnection setup; preserve any existing personal VPN automation.
---

# KAIST VPN Monitor Community

Use this folder as the program source; it includes the installer and runtime.
Read [README.md](README.md) for requirements, commands, permission steps, and known
limits. Read [VALIDATION.md](VALIDATION.md) before describing tested compatibility and
[SECURITY-REVIEW.md](SECURITY-REVIEW.md) before answering security questions.

## Install the program

Treat a request to install this tool as permission to prepare its local dependencies,
configuration, and app. Preserve an existing installation, connected VPN and other
scheduled monitors. Do not enable a second monitor alongside an existing one.

1. Locate this skill's actual directory. Check macOS, Node >=22.19, npm, Swift compiler,
   Chrome, official Ivanti, and a logged-in Codex CLI with Gmail access. Do not install
   unrelated global software or change security settings to satisfy prerequisites.
   Report missing prerequisites and continue independent preparation.
2. Determine the user's authorized SSH verification alias. Use an explicitly supplied
   alias or an established setting; do not choose an arbitrary host from SSH config.
   Ask for missing settings when necessary. The expected OTP sender must come from a user-verified legitimate message, never inferred from arbitrary inbox contents. Check the configured executable
   path for Codex. Neither setting contains the VPN password.
3. From this folder, run `npm ci --prefix scripts/background-login --ignore-scripts
   --no-audit --no-fund`. Write settings with
   `node setup.cjs --ssh-target ALIAS --codex /absolute/path/to/codex --otp-sender VERIFIED_SENDER`, passing values
   as separate arguments with proper quoting. Preserve existing settings unless
   the user asked to change them.
4. Have the user run `zsh scripts/configure-keychain.zsh` in their own terminal.
   Never ask them to paste credentials or OTPs into chat. Do not run hidden-password
   prompts in a recorded agent terminal, read Keychain secrets for inspection, or
   handle the user's password through tool arguments.
5. Run `node install.cjs --install`. If the user already unpacked the matching
   release app at the documented path, verify its identity/version and skip
   rebuilding it. Do not overwrite another installed app. Verify the bundle with
   `codesign --verify --deep --strict "$HOME/Applications/KAIST VPN Monitor Community.app"`.
   Installation alone must leave scheduling off. Do not launch or foreground apps
   just to inspect installation.
6. Explain the user-controlled Accessibility step in the README. Full Disk Access
   and local Mail data are not required. Exact sender and full-body DKIM plus same-ID Gmail metadata receipt are
   required; the signed-Subject ASCII KVPN format ignores unsigned MIME. Creation
   freshness is not guaranteed and genuine historical-mail replay can deny service; never disable verification to accommodate an unsigned message.
   Never grant privacy permissions programmatically or modify TCC databases.
7. After those steps, run the installed binary's `--check-only` against an already
   connected VPN. Require exact native state and SSH success. First recovery
   (`--retry`) is an actual login and can terminate an existing account session;
   explain this and obtain authorization unless already explicitly given. Do not
   disconnect a healthy VPN to manufacture a test.
8. Enable `node install.cjs --enable` only when automatic reconnection was requested
   and a first live recovery has succeeded. If the VPN is still healthy and a first
   recovery cannot be verified, report installed/prepared with scheduling off.
   Preserve process handles during recovery. Verify the actual scheduled result
   and timestamp before claiming automatic reconnection works.

Do all independent authorized preparation before handing back a required user
step. A missing credential or permission is not a reason to leave the app unbuilt.
Name exactly what is ready and what remains; installation, connection, and
unattended recovery are distinct outcomes.

## Maintenance boundaries

`--status` reads stored state; `--check-only` checks without authenticating.
`--retry` deliberately retries a latched incident. Do not reset a latch or rerun
authentication until its cause is addressed. Use `install.cjs --disable` to stop
the Community schedule when requested. Do not modify the private `ivanti-daily-login`
skill, another monitor's cache, Ivanti services, or system profile attributes.

Never print raw mail, OTPs, authentication URLs, browser state, or credentials.
Do not replace this dedicated headless runtime with the user's foreground browser
or a new automation backend to work around failure. Preserve the runner's bounds
and exact origin/profile checks. A connected VPN with failed SSH is a diagnostic
failure, not permission to reauthenticate.

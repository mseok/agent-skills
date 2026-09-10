#!/bin/zsh
set -euo pipefail

readonly account="ivanti-daily-login"
readonly script_dir="${0:A:h}"

case "${1:-}" in
  username)
    readonly service="codex.ivanti-daily-login.username"
    ;;
  password)
    readonly service="codex.ivanti-daily-login.password"
    ;;
  *)
    print -u2 -r -- "Expected one field argument: username or password"
    exit 64
    ;;
esac

# Keep the Keychain value in the private pipe and assign it directly to the
# focused Chrome field.  Nothing in this helper prints or copies the value.
/usr/bin/security find-generic-password -a "$account" -s "$service" -w \
  | /usr/bin/osascript -l JavaScript "$script_dir/type-chrome-stdin.js" "${1}" >/dev/null

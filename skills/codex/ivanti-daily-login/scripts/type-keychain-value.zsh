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

/usr/bin/security find-generic-password -a "$account" -s "$service" -w \
  | /usr/bin/osascript -l JavaScript "$script_dir/type-stdin.js" "${1}" >/dev/null

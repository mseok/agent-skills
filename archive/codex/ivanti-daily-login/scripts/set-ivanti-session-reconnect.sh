#!/bin/sh
# KVPN ends every session after 10 hours.  The server-pushed profile carries
# reconnect-at-session-timeout "true", so Ivanti then opens its own login
# window in front of whatever is in use.  This flips only that attribute and
# restarts Ivanti's service so it reads the change; the scheduled monitor then
# reconnects in the background as usual.
#
#   sudo sh set-ivanti-session-reconnect.sh off   # no Ivanti window at timeout
#   sudo sh set-ivanti-session-reconnect.sh on    # restore the server default
set -eu

dir="/Library/Application Support/Pulse Secure/Pulse"
service="system/net.pulsesecure.AccessService"
key="reconnect-at-session-timeout"

case "${1:-}" in
  off) from=true; to=false ;;
  on) from=false; to=true ;;
  *) echo "usage: sudo sh $0 off|on" >&2; exit 2 ;;
esac

count() { grep -c "^  $key: \"$1\"\$" "$dir/$2" || true; }
service_pid() { launchctl print "$service" 2>/dev/null | awk '$1 == "pid" {print $3}'; }
await_restart() {
  i=0
  while [ "$i" -lt 30 ]; do
    pid="$(service_pid)"
    if [ -n "$pid" ] && [ "$pid" != "$1" ]; then return 0; fi
    sleep 1; i=$((i + 1))
  done
  echo "Ivanti service did not come back; nothing further was changed." >&2
  exit 1
}

if [ "$(count "$to" connstore.dat)" = 1 ] && [ "$(count "$from" connstore.dat)" = 0 ]; then
  echo "already $1"; exit 0
fi
if [ "$(count "$from" connstore.dat)" != 1 ]; then
  echo "expected exactly one '$key: \"$from\"' in connstore.dat; not changing anything." >&2
  exit 1
fi
[ "$(id -u)" = 0 ] || { echo "run with sudo" >&2; exit 1; }

# Stop gracefully first so a live tunnel is torn down cleanly, and let the
# restarted service finish loading.  The second stop is immediate so the
# service cannot write its in-memory copy back over the edit; Ivanti then runs
# its own recovery and resumes a still-valid session without a login window.
echo "restarting the Ivanti service twice; this is silent for about 30 seconds"
old="$(service_pid)"
launchctl kill SIGTERM "$service"
await_restart "$old"
sleep 3
old="$(service_pid)"
[ -e "$dir/connstore.dat.before-session-reconnect-change" ] ||
  cp -p "$dir/connstore.dat" "$dir/connstore.dat.before-session-reconnect-change"
for file in connstore.dat connstore.bak; do
  [ -f "$dir/$file" ] || continue
  sed -i '' "s/^  $key: \"$from\"\$/  $key: \"$to\"/" "$dir/$file"
done
launchctl kill SIGKILL "$service"
await_restart "$old"
sleep 3

if [ "$(count "$to" connstore.dat)" = 1 ] && [ "$(count "$from" connstore.dat)" = 0 ]; then
  echo "$key is now \"$to\""
else
  echo "the service restored the previous value; $key is unchanged." >&2
  exit 1
fi

# Reconnect now through the existing monitor instead of waiting for its next
# scheduled run.  It is a no-op while a monitor run is already active.
if [ -n "${SUDO_UID:-}" ]; then
  launchctl kickstart "gui/$SUDO_UID/local.mseok.kaist-vpn-monitor" || true
fi

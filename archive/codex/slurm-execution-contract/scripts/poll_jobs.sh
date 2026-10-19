#!/usr/bin/env bash
# Poll Slurm jobs with backoff and print only state changes.
# Usage: poll_jobs.sh --interval SECONDS [--max-interval SECONDS] [--check CMD] JOBID...
#   --interval      first wait between polls (default 1800 = 30 min)
#   --max-interval  cap for the backoff (default 4x the first interval)
#   --check CMD     shell command run once after the first job completes, e.g. a test that one
#                   output artifact exists; its output is printed with the state change
# Exits 0 when every job has left the queue (then prints sacct terminal states), 2 on usage error.
set -euo pipefail
interval=1800; max_interval=""; check=""; jobs=()
while [ $# -gt 0 ]; do
  case "$1" in
    --interval) interval=$2; shift 2;;
    --max-interval) max_interval=$2; shift 2;;
    --check) check=$2; shift 2;;
    -h|--help) sed -n '2,9p' "$0"; exit 0;;
    *) jobs+=("$1"); shift;;
  esac
done
[ ${#jobs[@]} -gt 0 ] || { echo "usage: poll_jobs.sh --interval SECONDS JOBID..." >&2; exit 2; }
[ -n "$max_interval" ] || max_interval=$((interval * 4))
ids=$(IFS=,; echo "${jobs[*]}")
last=""; wait=$interval; checked=0
while :; do
  now=$(squeue -h -j "$ids" -o '%i %T %M %R' 2>/dev/null | sort || true)
  if [ "$now" != "$last" ]; then
    printf '%s state change\n%s\n' "$(date '+%F %T')" "${now:-<none in queue>}"
    last=$now; wait=$interval
    if [ -n "$check" ] && [ $checked -eq 0 ]; then
      if ! echo "$now" | grep -q ' RUNNING\| PENDING'; then checked=1; echo "check: $check"; sh -c "$check" || echo "check FAILED"; fi
    fi
  else
    wait=$(( wait * 2 > max_interval ? max_interval : wait * 2 ))
  fi
  [ -n "$now" ] || break
  sleep "$wait"
done
echo "terminal states:"; sacct -X -j "$ids" -o JobID,State,ExitCode,Elapsed -n 2>/dev/null || true

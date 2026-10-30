#!/bin/sh
# Screenshot every slide of an HTML deck (final build state) to PNG for visual QA.
#   usage: tools/shots.sh deck/index.html out/shots [scale]
#   scale: device scale factor, default 0.5 (960x540 PNGs); use 1 for full 1920x1080.
# Slide n is captured at index.html?export#/n/99 (99 is clamped to the slide's last build).
set -eu
[ $# -ge 2 ] || { echo "usage: $0 deck/index.html out_dir [scale]" >&2; exit 2; }
IN="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
OUT="$2"; SCALE="${3:-0.5}"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[ -x "$CHROME" ] || { echo "Chrome not found at $CHROME (set CHROME=...)" >&2; exit 1; }
mkdir -p "$OUT"
N="$(python3 -c 'import re,sys; s=re.sub(r"<!--.*?-->","",open(sys.argv[1],encoding="utf-8").read(),flags=re.S); print(len(re.findall(r"<section class=\"slide", s)))' "$IN")"
UD="$(mktemp -d "${TMPDIR:-/tmp}/deck-chrome.XXXXXX")"
i=1
while [ "$i" -le "$N" ]; do
  P="$OUT/$(printf 'slide-%02d.png' "$i")"
  "$CHROME" --headless=new --disable-gpu --no-first-run --no-default-browser-check --user-data-dir="$UD" \
    --window-size=1920,1080 --force-device-scale-factor="$SCALE" --virtual-time-budget=8000 \
    --screenshot="$P" "file://$IN?export#/$i/99" >/dev/null 2>&1
  echo "$P"
  i=$((i + 1))
done

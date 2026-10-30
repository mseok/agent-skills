#!/bin/sh
# Build one PNG contact sheet from a folder of slide PNGs (for a quick whole-deck visual scan).
#   usage: tools/contact_sheet.sh shots_dir out.png [per_row]
set -eu
DIR="$(cd "$1" && pwd)"; OUT="$2"; PER="${3:-5}"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
HTML="$DIR/.contact.html"
N="$(ls "$DIR"/*.png | wc -l | tr -d ' ')"
ROWS=$(( (N + PER - 1) / PER ))
TW=$(( 1920 / PER ))
TH=$(( TW * 9 / 16 + 26 ))
{
  echo "<!DOCTYPE html><meta charset=utf-8><style>body{margin:0;background:#ddd;font:12px -apple-system,Helvetica,sans-serif}.g{display:grid;grid-template-columns:repeat($PER,1fr)}.c{position:relative;padding:4px}.c img{width:100%;display:block;box-shadow:0 1px 3px rgba(0,0,0,.3)}.c span{display:block;text-align:center;color:#333;height:18px;line-height:18px}</style><div class=g>"
  for f in "$DIR"/*.png; do b="$(basename "$f")"; echo "<div class=c><img src=\"$b\"><span>$b</span></div>"; done
  echo "</div>"
} > "$HTML"
UD="$(mktemp -d "${TMPDIR:-/tmp}/deck-chrome.XXXXXX")"
"$CHROME" --headless=new --disable-gpu --no-first-run --no-default-browser-check --user-data-dir="$UD" \
  --window-size=1920,$(( ROWS * TH + 8 )) --force-device-scale-factor=1 --virtual-time-budget=6000 \
  --screenshot="$OUT" "file://$HTML" >/dev/null 2>&1
echo "$OUT ($N slides, $ROWS rows)"

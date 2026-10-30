#!/bin/sh
# Export an HTML deck to a multi-page PDF (one 1920x1080 page per slide, final build state).
# Uses the deck's ?print mode and Google Chrome headless; nothing to install besides Chrome.
#   usage: tools/export_pdf.sh deck/index.html out/deck.pdf
#   env  : CHROME=/path/to/chrome   (default: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome)
set -eu
[ $# -eq 2 ] || { echo "usage: $0 deck/index.html out.pdf" >&2; exit 2; }
IN="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
OUT="$2"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[ -x "$CHROME" ] || { echo "Chrome not found at $CHROME (set CHROME=...)" >&2; exit 1; }
mkdir -p "$(dirname "$OUT")"
UD="$(mktemp -d "${TMPDIR:-/tmp}/deck-chrome.XXXXXX")"
"$CHROME" --headless=new --disable-gpu --no-first-run --no-default-browser-check --user-data-dir="$UD" \
  --no-pdf-header-footer --virtual-time-budget=12000 --print-to-pdf="$OUT" "file://$IN?print" >/dev/null 2>&1
[ -s "$OUT" ] || { echo "PDF was not written" >&2; exit 1; }
echo "$OUT"

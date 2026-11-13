#!/usr/bin/env python3
"""Regression gate for changes to the kit: render every worked example with the current kit and say which ones changed.

usage: check_examples.py [--out DIR] [--accept]

Renders assets/examples/*.html into DIR (default: a new temporary folder), prints each example's errors and warnings,
and compares each preview with assets/examples/renders/<name>.png. A kit change can alter any example without a
warning, so every example listed as CHANGED must be looked at (preview and tiles, references/inspection.md) before the
change is kept. --accept copies the new previews over the stored ones; use it only after that look.
Exit status: 0 nothing changed and no errors, 1 errors or an unexpected warning, 3 previews changed and not accepted.
"""
import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

SKILL = pathlib.Path(__file__).resolve().parent.parent
EXAMPLES = SKILL / "assets" / "examples"
SHEET_WARNINGS = {"colour-roles", "words", "empty-space"}  # kit-sheet.html is a specimen sheet, not a figure


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out")
    ap.add_argument("--accept", action="store_true")
    args = ap.parse_args()
    out = pathlib.Path(args.out).resolve() if args.out else pathlib.Path(tempfile.mkdtemp(prefix="concept-figure-examples-"))
    out.mkdir(parents=True, exist_ok=True)
    bad, changed = False, []
    for html in sorted(EXAMPLES.glob("*.html")):
        run = subprocess.run([sys.executable, str(SKILL / "scripts" / "render.py"), str(html), "--out", str(out)], capture_output=True, text=True)
        report_path = out / f"{html.stem}.report.json"
        if run.returncode == 2 or not report_path.exists():
            print(f"{html.stem}: did not render\n{run.stderr.strip()}")
            bad = True
            continue
        report = json.loads(report_path.read_text(encoding="utf-8"))
        issues = [i for i in report["issues"] if not (html.stem == "kit-sheet" and i["code"] in SHEET_WARNINGS)]
        new, old = out / f"{html.stem}.preview.png", EXAMPLES / "renders" / f"{html.stem}.png"
        same = old.exists() and hashlib.sha256(new.read_bytes()).digest() == hashlib.sha256(old.read_bytes()).digest()
        print(f"{html.stem}: {report['errors']} errors, {len(issues)} warnings to fix, {'unchanged' if same else 'CHANGED'}")
        for i in issues:
            print(f"    {i['level']} {i['code']}: {i['msg']}")
        bad = bad or bool(issues)
        if not same:
            changed.append(html.stem)
            if args.accept:
                shutil.copy(new, old)
    print(f"renders: {out}")
    if changed:
        print(("accepted: " if args.accept else "look at each before accepting (preview and tiles): ") + ", ".join(changed))
    return 1 if bad else 3 if changed and not args.accept else 0


if __name__ == "__main__":
    sys.exit(main())

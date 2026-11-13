#!/usr/bin/env python3
"""Start a concept-figure folder from a worked example, or open the next version of an existing one.

usage: new_figure.py DEST --example {architecture,pipeline,comparison,contrast,concept,agent-loop} [--width WIDTH]
       new_figure.py DEST --next

The first form creates DEST/v01/ holding figure.html (a copy of the example) and kit/ (figure.css, figure.js,
icons.js and KaTeX), so the folder renders on its own. The second copies the highest vNN to the next number
without its rendered outputs. WIDTH is neurips, iclr, icml, icml-col, nature, nature-col or a CSS length (120mm).
"""
import argparse
import pathlib
import re
import shutil
import sys

SKILL = pathlib.Path(__file__).resolve().parents[1]
KIT = SKILL / "assets" / "kit"
EXAMPLES = SKILL / "assets" / "examples"


def versions(dest):
    return sorted(p for p in dest.glob("v[0-9][0-9]") if p.is_dir())


def skip_outputs(_folder, names):
    stems = {pathlib.Path(n).stem for n in names if n.endswith(".html")}
    return [n for n in names if any(n in (f"{s}.pdf", f"{s}.png", f"{s}.preview.png", f"{s}.report.json") for s in stems)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dest")
    ap.add_argument("--example", choices=sorted(p.stem for p in EXAMPLES.glob("*.html") if p.stem != "kit-sheet"))
    ap.add_argument("--width")
    ap.add_argument("--next", action="store_true")
    args = ap.parse_args()
    dest = pathlib.Path(args.dest).resolve()
    if args.next:
        have = versions(dest)
        if not have:
            sys.exit(f"no vNN folder in {dest}")
        new = dest / f"v{int(have[-1].name[1:]) + 1:02d}"
        shutil.copytree(have[-1], new, ignore=skip_outputs)
        print(new / "figure.html")
        return
    if not args.example:
        ap.error("--example is required for a new figure")
    if versions(dest):
        sys.exit(f"{dest} already has versions; use --next")
    if not (KIT / "katex" / "katex.min.js").exists():
        sys.exit(f"KaTeX not found through {KIT / 'katex'} (it links to the html-research-deck skill's vendor folder)")
    new = dest / "v01"
    new.mkdir(parents=True)
    shutil.copytree(KIT, new / "kit")
    html = (EXAMPLES / f"{args.example}.html").read_text(encoding="utf-8").replace("../kit/", "kit/")
    if args.width:
        html = re.sub(r'data-width="[^"]*"', f'data-width="{args.width}"', html, count=1)
    (new / "figure.html").write_text(html, encoding="utf-8")
    print(new / "figure.html")


if __name__ == "__main__":
    main()

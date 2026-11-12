#!/usr/bin/env python3
"""Scaffold an HTML deck folder from this skill's assets, in the research theme or in the Folio layout.

usage: new_deck.py DEST --title "덱 제목" [--theme research|folio] [--lang ko] [--slides title,figure,closing] [--force]

DEST gets css/, js/, vendor/ (engine + themes + fonts + KaTeX), assets/figs/, qa/ and an index.html assembled from
templates/index.template.html (research: the shape sprite inlined) or templates/index.folio.template.html (Folio, references/folio.md)
with the requested slide fragments in order (research: templates/slide-*.html, default title,figure,closing; Folio:
templates/folio-*.html, default cover,opener,plate).
With --force an existing DEST keeps its files and only index.html is rewritten (a backup index.html.bak is kept).
Standard library only.
"""
import argparse
import shutil
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / 'assets' / 'deck'
TEMPLATES = ASSETS / 'templates'


PREFIX = {'research': 'slide-', 'folio': 'folio-'}
DEFAULT = {'research': 'title,figure,closing', 'folio': 'cover,opener,plate'}


def available_slides(theme='research'):
    return sorted(p.stem[len(PREFIX[theme]):] for p in TEMPLATES.glob(PREFIX[theme] + '*.html'))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('dest', help='deck folder to create (absolute path recommended)')
    ap.add_argument('--title', required=True, help='window title of the deck')
    ap.add_argument('--lang', default='ko', help='html lang attribute (ko or en)')
    ap.add_argument('--theme', default='research', choices=sorted(PREFIX), help='research (default) or folio')
    ap.add_argument('--slides', help='comma-separated slide fragments, in order (research: %s; folio: %s)'
                    % (', '.join(available_slides()), ', '.join(available_slides('folio'))))
    ap.add_argument('--force', action='store_true', help='allow an existing DEST; rewrite index.html only')
    a = ap.parse_args()

    dest = Path(a.dest).expanduser().resolve()
    if dest.exists() and not a.force:
        sys.exit(f'{dest} already exists; pass --force to rewrite its index.html')
    names = [s.strip() for s in (a.slides or DEFAULT[a.theme]).split(',') if s.strip()]
    frags = []
    for n in names:
        p = TEMPLATES / f'{PREFIX[a.theme]}{n}.html'
        if not p.is_file():
            sys.exit(f'unknown slide template "{n}" for the {a.theme} theme; available: {", ".join(available_slides(a.theme))}')
        frags.append(p.read_text(encoding='utf-8').strip())

    dest.mkdir(parents=True, exist_ok=True)
    for sub in ('css', 'js', 'vendor'):
        target = dest / sub
        if not target.exists():
            shutil.copytree(ASSETS / sub, target)
    (dest / 'assets' / 'figs').mkdir(parents=True, exist_ok=True)
    (dest / 'qa').mkdir(exist_ok=True)

    tpl = (TEMPLATES / ('index.folio.template.html' if a.theme == 'folio' else 'index.template.html')).read_text(encoding='utf-8')
    sprite = (ASSETS / 'sprite-research.svg').read_text(encoding='utf-8').strip()
    html = (tpl.replace('{{TITLE}}', a.title).replace('{{LANG}}', a.lang)
            .replace('{{SPRITE}}', sprite).replace('{{SLIDES}}', '\n\n'.join(frags)))
    index = dest / 'index.html'
    if index.exists():
        shutil.copy2(index, dest / 'index.html.bak')
    index.write_text(html, encoding='utf-8')
    print(index)
    print(f'theme: {a.theme} · slides: {", ".join(names)}')
    print('next: edit index.html; then scripts/check_deck.py, scripts/shots.sh, scripts/export_pdf.sh (see references/qa.md)')
    return 0


if __name__ == '__main__':
    sys.exit(main())

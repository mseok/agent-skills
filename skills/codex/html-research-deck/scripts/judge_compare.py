#!/usr/bin/env python3
"""judge_compare.py — compare two or more message-judge files (same deck or successive iterations).

usage: python3 judge_compare.py judge-msg-A.json judge-msg-B.json [more.json ...]

Prints, per file, the judged half as score_message.py computes it (N1 mean/2 × 12, N2 mean/2 × 8, N3, N4 mean/2 × 8, N5),
then a per-slide table of N1 N2 N4, the slides each judge flagged (any item < 2), the overlap between flagged sets, and the
first 300 characters of each N5 evidence. Use it to measure judge-to-judge variance on an unchanged copy dump before
attributing a score change to the deck. Read-only.
"""
import json
import sys
from pathlib import Path


def load(path):
    d = json.loads(Path(path).read_text(encoding='utf-8'))
    j = d.get('judge') or d
    slides = {s['n']: s for s in j.get('slides', [])}
    deck = j.get('deck', {})
    return slides, deck, d.get('cost_usd')


def judged_total(slides, deck):
    n = len(slides) or 1
    mean = lambda k: sum(s.get(k, 0) for s in slides.values()) / n  # noqa: E731 - one-line helper
    parts = {'N1': mean('N1') / 2 * 12, 'N2': mean('N2') / 2 * 8, 'N3': float(deck.get('N3', 0)), 'N4': mean('N4') / 2 * 8, 'N5': float(deck.get('N5', 0))}
    return parts, sum(parts.values())


def main():
    files = sys.argv[1:]
    if len(files) < 2:
        print(__doc__); sys.exit(2)
    runs = [(Path(f).name, *load(f)) for f in files]
    for name, slides, deck, cost in runs:
        parts, total = judged_total(slides, deck)
        print(f"{name}: judged {total:.2f}/50  " + ' '.join(f"{k} {v:.2f}" for k, v in parts.items()) + f"  cost ${cost}" if cost else '')
    ns = sorted(set().union(*[set(s) for _, s, _, _ in runs]))
    print('\nslide ' + '  '.join(f"{name[10:23]:>13}" for name, *_ in runs) + '   (N1 N2 N4)')
    flagged = []
    for _, slides, _, _ in runs:
        flagged.append({n for n, s in slides.items() if any(s.get(k, 2) < 2 for k in ('N1', 'N2', 'N4'))})
    for n in ns:
        cells = []
        for _, slides, _, _ in runs:
            s = slides.get(n)
            cells.append(f"{s.get('N1', '-')} {s.get('N2', '-')} {s.get('N4', '-')}" if s else '-')
        print(f"{n:>5} " + '  '.join(f"{c:>13}" for c in cells))
    for i, (name, *_) in enumerate(runs):
        print(f"flagged by {name}: {sorted(flagged[i])}")
    if len(runs) >= 2:
        a, b = flagged[0], flagged[1]
        print(f"overlap of the first two: {sorted(a & b)}  only-first: {sorted(a - b)}  only-second: {sorted(b - a)}")
    for name, _, deck, _ in runs:
        print(f"\n{name} N5 {deck.get('N5')}: {(deck.get('N5_evidence') or '')[:300]}")
        print(f"{name} N3 {deck.get('N3')}: {(deck.get('N3_evidence') or '')[:200]}")


if __name__ == '__main__':
    main()

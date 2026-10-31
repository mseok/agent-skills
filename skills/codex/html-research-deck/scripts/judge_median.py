#!/usr/bin/env python3
"""judge_median.py — merge several message-judge runs on the same copy dump into one judge file (per-item median).

usage: python3 judge_median.py --out /abs/deck/qa/judge-msg-<ts>.json run1.json run2.json [run3.json ...]

Why: two Opus 5.5 max runs on identical text scored the CausalGame deck 37.22 and 34.56 of 50 and placed the N5
deductions on different slides, so a single run cannot separate a better deck from a lenient draw near the threshold.
The merged file keeps the judge-file shape score_message.py reads (judge.slides[].N1/N2/N4, judge.deck.N3/N5) with
the median over runs for every item (lower middle value for an even number of runs; per-slide items stay integers 0–2 as score_message.py requires), concatenates each run's evidence with a run tag so the builder still sees every
finding, sums the costs and lists the run files. The rubric, weights and threshold are untouched — only the estimator
changes from one draw to the median of several. Read-only apart from --out.
"""
import argparse
import datetime
import json
from pathlib import Path


def low_median(vals):
    """Median for an odd count; the lower middle value for an even count (score_message.py accepts only 0, 1, 2 per
    slide item, and rounding a .5 upward would flatter the deck)."""
    s = sorted(vals)
    return s[(len(s) - 1) // 2]


def load(path):
    d = json.loads(Path(path).read_text(encoding='utf-8'))
    if d.get('parse_error') or not d.get('judge'):
        raise SystemExit(f'{path}: parse_error={d.get("parse_error")!r} or no judge block — fix or drop this run first')
    return d


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', required=True)
    ap.add_argument('runs', nargs='+')
    a = ap.parse_args()
    runs = [load(r) for r in a.runs]
    if len(runs) < 2:
        raise SystemExit('need at least two runs')
    tags = [f'r{i + 1}' for i in range(len(runs))]
    slides = {}
    for tag, d in zip(tags, runs):
        for s in d['judge'].get('slides', []):
            slides.setdefault(s['n'], []).append((tag, s))
    merged = []
    for n in sorted(slides):
        rows = slides[n]
        item = {'n': n}
        for k in ('N1', 'N2', 'N4'):
            vals = [int(s.get(k, 0) or 0) for _, s in rows]
            item[k] = low_median(vals)
        item['runs'] = {tag: {k: s.get(k) for k in ('N1', 'N2', 'N4')} for tag, s in rows}
        item['evidence'] = ' | '.join(f"[{tag}] {s.get('evidence', '')}" for tag, s in rows)
        merged.append(item)
    deck = {}
    for k in ('N3', 'N5'):
        vals = [float(d['judge'].get('deck', {}).get(k, 0) or 0) for d in runs]
        deck[k] = low_median(vals)
        deck[f'{k}_runs'] = dict(zip(tags, vals))
        deck[f'{k}_evidence'] = ' | '.join(f"[{tag}] {d['judge'].get('deck', {}).get(f'{k}_evidence', '')}" for tag, d in zip(tags, runs))
    summary = {'worst': [f'[{tag}] {w}' for tag, d in zip(tags, runs) for w in (d['judge'].get('summary', {}).get('worst') or [])],
               'best': ' | '.join(f"[{tag}] {d['judge'].get('summary', {}).get('best', '')}" for tag, d in zip(tags, runs)),
               'memorable': ' | '.join(f"[{tag}] {d['judge'].get('summary', {}).get('memorable', '')}" for tag, d in zip(tags, runs))}
    out = {'at': datetime.datetime.now().isoformat(timespec='seconds'), 'model': runs[0].get('model'), 'effort': runs[0].get('effort'),
           'copy': runs[0].get('copy'), 'slides_total': runs[0].get('slides_total'), 'median_of': len(runs), 'runs': [str(Path(r).resolve()) for r in a.runs],
           'cost_usd': round(sum(float(d.get('cost_usd') or 0) for d in runs), 6), 'duration_ms': max(int(d.get('duration_ms') or 0) for d in runs),
           'is_error': False, 'parse_error': '',
           'judge': {'judge': f"median of {len(runs)} × {runs[0].get('model')}", 'slides': merged, 'deck': deck, 'summary': summary}}
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    n = len(merged) or 1
    judged = sum(s['N1'] for s in merged) / n / 2 * 12 + sum(s['N2'] for s in merged) / n / 2 * 8 + sum(s['N4'] for s in merged) / n / 2 * 8 + deck['N3'] + deck['N5']
    print(f"median of {len(runs)} runs → judged {judged:.2f}/50 (N3 {deck['N3']:g} · N5 {deck['N5']:g}; per run N5 {deck['N5_runs']}) · cost ${out['cost_usd']} → {a.out}")


if __name__ == '__main__':
    main()

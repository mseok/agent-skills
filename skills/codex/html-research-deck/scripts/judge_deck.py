#!/usr/bin/env python3
"""Run the independent judge (rubric items G–J, 40 points) on the full-size slide PNGs with a model that did not build the deck.

usage: judge_deck.py /abs/deck/qa/shots-full --out /abs/deck/qa/judge-<ts>.json [--model claude-opus-5-5] [--effort max]

The judge gets only the PNGs, references/judge-prompt.md and the judged rows of references/rubric.md: it runs `claude -p` from the
PNG folder with the Read tool only, so it cannot see the builder's code, notes or earlier scores. The raw model output is kept in
the result file next to the parsed JSON.
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('shots'); ap.add_argument('--out', required=True); ap.add_argument('--model', default='claude-opus-5-5'); ap.add_argument('--effort', default='max')
    ap.add_argument('--timeout', type=int, default=1800)
    a = ap.parse_args()
    shots = Path(a.shots).resolve()
    pngs = sorted(p for p in shots.glob('slide-*.png'))
    if len(pngs) < 3:
        sys.exit(f'need the full-size slide PNGs in {shots}')
    n = len(pngs)
    rubric = (SKILL / 'references' / 'rubric.md').read_text(encoding='utf-8')
    judged = rubric[rubric.index('## 심사 항목'):rubric.index('## 정직성 규칙')]
    prompt = ((SKILL / 'references' / 'judge-prompt.md').read_text(encoding='utf-8') + '\n\n---\n채점표 심사 항목:\n' + judged +
              f'\n\n---\n슬라이드 PNG ({n}장, 이 폴더): ' + ', '.join(p.name for p in pngs) +
              f'\n내용 슬라이드 = 2 … {n - 1} (1장 표지, {n}장 정리 제외). 모든 PNG를 Read 도구로 열어 본 뒤 JSON만 출력하라.')
    cmd = ['claude', '-p', prompt, '--model', a.model, '--effort', a.effort, '--output-format', 'json', '--allowedTools', 'Read']
    t0 = datetime.datetime.now()
    try:
        r = subprocess.run(cmd, cwd=str(shots), capture_output=True, text=True, timeout=a.timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        sys.exit(f'judge run exceeded {a.timeout}s')
    try:
        env = json.loads(r.stdout)
    except json.JSONDecodeError:
        sys.exit('claude did not return JSON: ' + r.stdout[-800:] + r.stderr[-400:])
    text = env.get('result') or ''
    m = re.search(r'```json\s*(\{.*?\})\s*```', text, re.S) or re.search(r'(\{.*\})', text, re.S)
    parsed = None; err = ''
    if m:
        try:
            parsed = json.loads(m.group(1))
        except json.JSONDecodeError as e:
            err = f'judge JSON unparsable: {e}'
    else:
        err = 'no JSON block in judge output'
    if parsed:
        rows = {int(s.get('n', 0)): s for s in parsed.get('slides', [])}
        missing = [i for i in range(2, n) if i not in rows]
        bad = [i for i, s in rows.items() if any(s.get(k) not in (0, 1, 2) for k in 'GHIJ')]
        if missing or bad:
            err = f'judge file incomplete: missing {missing} bad {bad}'
    out = {'at': t0.isoformat(timespec='seconds'), 'model': a.model, 'effort': a.effort, 'shots': str(shots), 'slides_total': n,
           'cost_usd': env.get('total_cost_usd'), 'duration_ms': env.get('duration_ms'), 'usage': env.get('usage'),
           'is_error': env.get('is_error'), 'parse_error': err, 'judge': parsed, 'raw': text}
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f"judge {a.model}/{a.effort}: cost ${env.get('total_cost_usd')} · {env.get('duration_ms')} ms · {'OK' if parsed and not err else 'PROBLEM: ' + err} → {a.out}")
    sys.exit(0 if parsed and not err else 1)


if __name__ == '__main__':
    main()

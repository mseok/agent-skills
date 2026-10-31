#!/usr/bin/env python3
"""copy_lint.py — count the message-rule slips a builder can fix before the judge runs.

usage: python3 copy_lint.py deck/index.html [--json deck/qa/copy.json] [--strict]

Reads the visible copy (deck_copy.dump on the index, or a saved copy.json) and reports per content slide:
  banned   closing-line words that turn an observation into identity or exclusion
           (뿐, 유일, =, 막는/막아, 설명되지 않 → 금지; 아니라, 때문에, 덕분에 → 확인)
  numbers  closing lines that carry a number, with the scope words found in the same sentence
           (판에서, 두 판, 504판 중, 모델에서, 시나리오에서 …) — a case number without a scope word is the
           iteration-6 slide-18 deduction
  marks    lane headers or labels that carry 저자/발표자/모식/번역 (these belong in the cite line or the notes)
  rhythm   closing lines of the "A, B" two-clause comma form vs single-clause lines
  handoff  whether a word of the closing line's last clause reappears in the next slide's kicker subtopic or title
  split    titles and lane headers that contain a comma — review which are the "주제, 요점" label form (a colon
           in disguise); parallel clauses and lists are fine
  repeat   content words the closing line repeats from the title

Every check is a heuristic for the builder's self-check (builder-brief-message.md, section I); the judge decides.
--strict exits 1 when a 금지 word is found. The script never edits anything.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

BANNED = [
    ('금지', '뿐', re.compile(r'뿐')),
    ('금지', '유일', re.compile(r'유일')),
    ('금지', '=', re.compile(r'=')),
    ('금지', '막는', re.compile(r'막는|막아|막은|막음')),
    ('금지', '설명되지 않', re.compile(r'설명되지\s*않')),
    ('확인', '아니라', re.compile(r'아니라')),
    ('확인', '때문에', re.compile(r'때문에')),
    ('확인', '덕분에', re.compile(r'덕분에')),
]
SCOPE = re.compile(r'(?:^|\s)(?:두|세|네|다섯) 판|\d[\d,]*판(?: 중|에서| 가운데|의)|\d+개 (?:모델|시나리오)|모델 모두|모델에서|모델 중|시나리오 평균|시나리오에서|시나리오 중|판에서는|구간에서|함정에서|게임에서|저자가 고른|이 게임|가운데|개 중')
MARKS = re.compile(r'저자|발표자|모식|번역')
TOKEN = re.compile(r'[가-힣]{2,}|[A-Za-z]{3,}')
STOP = {'있음', '없음', '그래도', '모두', '아님', '아니라', '판은', '판의', '판에', '에서', '으로', '하는', '하고', '이지만', '그리고', '대신'}


def load(args):
    if args.json:
        doc = json.loads(Path(args.json).read_text(encoding='utf-8'))
    else:
        from deck_copy import dump  # same folder
        doc = dump(Path(args.index))
    return doc['slides'] if isinstance(doc, dict) else doc


def stems(text):
    return [t[:2] for t in TOKEN.findall(text) if t not in STOP and t[:2] not in STOP]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('index', nargs='?', default='deck/index.html')
    ap.add_argument('--json', default='')
    ap.add_argument('--strict', action='store_true')
    a = ap.parse_args()
    slides = load(a)
    content = [s for s in slides if s.get('n', 0) != 1 and s.get('closing')]
    last_n = max((s['n'] for s in slides), default=0)
    by_n = {s['n']: s for s in slides}

    banned_hits, check_hits, numeric, no_scope, marks, two_clause, one_clause, handoff_yes, handoff_total, split, repeats = [], [], [], [], [], [], [], [], 0, [], []
    lines = []
    for s in content:
        n, closing, title = s['n'], s['closing'], s.get('h2') or s.get('title', '')
        cells = []
        hits = [(sev, name) for sev, name, rx in BANNED if rx.search(closing)]
        if hits:
            cells.append(' '.join(f'[{sev}] {name}' for sev, name in hits))
            if any(sev == '금지' for sev, _ in hits):
                banned_hits.append(n)
            else:
                check_hits.append(n)
        nums = [x.rstrip(',.') for x in re.findall(r'[−\-+]?\d[\d.,]*%?', closing)]
        if nums:
            numeric.append(n)
            sc = SCOPE.findall(closing)
            cells.append(f"숫자 {' '.join(nums)} · 범위 말 {('·'.join(sc)) if sc else '없음'}")
            if not sc:
                no_scope.append(n)
        body = ' | '.join(list(s.get('lanes', [])) + list(s.get('visible', [])))
        m = sorted(set(MARKS.findall(body)))
        if m:
            marks.append(n)
            cells.append('본문 표시 ' + '·'.join(m))
        if ',' in closing or '，' in closing:
            two_clause.append(n)
            cells.append('두 절')
        else:
            one_clause.append(n)
            cells.append(f'한 절 {len(closing)}자')
        nxt = by_n.get(n + 1)
        if nxt and nxt.get('n') != last_n + 1:
            handoff_total += 1
            last_clause = re.split(r'[,，]', closing)[-1]
            target = (nxt.get('kicker', '').split('·')[-1] + ' ' + (nxt.get('h2') or nxt.get('title', '')))
            shared = [t for t in stems(last_clause) if t in target]
            if shared:
                handoff_yes.append(n)
            cells.append(f"손잡이→{n + 1} {'·'.join(shared) if shared else '없음'}")
        for label, text in [('제목', title)] + [('레인', l) for l in s.get('lanes', [])]:
            if ',' in text or '，' in text:
                parts = [p.strip() for p in re.split(r'[,，]', text, maxsplit=1)]
                if len(parts) == 2 and len(parts[0]) >= 4 and len(parts[1]) >= 4:
                    split.append((n, label, text))
        shared_title = sorted(set(stems(title)) & set(stems(closing)))
        if shared_title:
            repeats.append((n, shared_title))
            cells.append('되풀이 ' + '·'.join(shared_title))
        tag = ' (정리 장)' if n == last_n else ''
        lines.append(f"{n:>2}{tag}  " + ' | '.join(cells))

    print('\n'.join(lines))
    total = len(content)
    print()
    print(f"요약: 금지어 {len(banned_hits)}장{(' ' + str(banned_hits)) if banned_hits else ''} · 확인어 {len(check_hits)}장{(' ' + str(check_hits)) if check_hits else ''}"
          f" · 숫자 있는 마무리줄 {len(numeric)}/{total} (범위 말 없음 {len(no_scope)}장{(' ' + str(no_scope)) if no_scope else ''})"
          f" · 본문 표시 {len(marks)}장{(' ' + str(marks)) if marks else ''}"
          f" · 두 절 쉼표형 {len(two_clause)}/{total} · 한 절 {len(one_clause)}/{total}"
          f" · 손잡이 후보 {len(handoff_yes)}/{handoff_total}"
          f" · 쉼표가 든 제목·레인 {len(split)}건(주제, 요점 꼴인지 확인; 대구·열거는 괜찮음)" + (': ' + '; '.join(f'{n}장 {lab} "{t}"' for n, lab, t in split) if split else ''))
    if a.strict and banned_hits:
        sys.exit(1)


if __name__ == '__main__':
    main()

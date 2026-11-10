#!/usr/bin/env python3
"""banned_copy_lint.py — pass/fail check of the copy patterns this skill already bans.

usage: python3 banned_copy_lint.py /abs/deck/index.html [--json /abs/deck/qa/banned-copy.json] [--copy-json copy.json]

Reads the visible copy through deck_copy.dump (or a saved copy.json) and reports one finding per hit. The cover slide
is not checked. The cite line and the speaker notes are never checked: attribution and paper locators belong there.
copy_lint.py counts advisory rhythm and scope slips; this script is the gate for the patterns below. Exit 1 on any error.

  author-token   error  저자 / 발표자 / 모식 / 번역 in a kicker, title, lane header, label or closing line
                         (rubric-message M10; user 2026-11-01 "발표자 생각 이런 멘트가 너무 별로다")
  colon-label    error  a colon in a title, kicker, lane header or closing line, outside TeX
                         (message-style rule 1; user 2026-10-31 "A:B 이런 스타일로 왜이렇게 많이 쓰는거지?")
  locator        error  §, Table n, Fig. n, Appendix X, Observation n, 그림 n, 표 n in a title, kicker, lane header or closing line;
                 warn   the same in other visible text (message-style rule 4: locators go to the cite line)
  closing-banned error  뿐 / 유일 / = / 막는 / 설명되지 않 in a closing line; warn for 아니라 / 때문에 / 덕분에
                         (message-style rule 9; the same list as copy_lint.py)
  gloss-paren    warn   a Hangul or Latin word followed by a Hangul gloss in parentheses, e.g. 세션(게임 한 판)
                         (message-style rule 4; user 2026-10-31 on meaningless parentheses)
  dash-prefix    warn   " — " or " – " inside a title or lane header (message-style rule 1: only rarely)

The script never edits anything.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from copy_lint import BANNED

TOKEN = re.compile(r'저자|발표자|모식|번역')
COLON = re.compile(r'(?<!\d)[:：]|[:：](?!\d)')
LOCATOR = re.compile(r'§|\b(?:Table|Tab\.|Fig\.|Figure|Appendix|Observation)\s*[A-Z0-9]\w*|(?<![가-힣])(?:그림|표)\s?\d+(?![가-힣\d])')
GLOSS = re.compile(r'[가-힣A-Za-z]\([가-힣][가-힣 ]+\)')
DASH = re.compile(r'\s[—–]\s')
MATH = re.compile(r'\$[^$]+\$')
HEAD_FIELDS = ('kicker', 'h1', 'h2', 'closing')


def load(index, copy_json):
    if copy_json:
        doc = json.loads(Path(copy_json).read_text(encoding='utf-8'))
    else:
        from deck_copy import dump
        doc = dump(index)
    return doc['slides'] if isinstance(doc, dict) else doc


def fields(slide):
    """(field name, is header-like, text) for every checked piece of visible copy."""
    for name in HEAD_FIELDS:
        if slide.get(name):
            yield name, True, slide[name]
    for lane in slide.get('lanes', []):
        yield 'lane', True, lane
    for text in slide.get('visible', []):
        yield 'text', False, text


def lint_slide(slide):
    found = []
    for name, head, raw in fields(slide):
        text = MATH.sub(' ', raw)
        if TOKEN.search(text):
            found.append(('author-token', 'error', name, raw))
        if head and name != 'h1' and COLON.search(text):
            found.append(('colon-label', 'error', name, raw))
        if LOCATOR.search(text):
            found.append(('locator', 'error' if head else 'warn', name, raw))
        if name == 'closing':
            for severity, _, rx in BANNED:
                if rx.search(text):
                    found.append(('closing-banned', 'error' if severity == '금지' else 'warn', name, raw))
                    break
        if GLOSS.search(text):
            found.append(('gloss-paren', 'warn', name, raw))
        if head and name in ('h2', 'lane') and DASH.search(text):
            found.append(('dash-prefix', 'warn', name, raw))
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('index', nargs='?', default='deck/index.html')
    ap.add_argument('--json', default='')
    ap.add_argument('--copy-json', default='')
    a = ap.parse_args()
    findings = []
    for slide in load(a.index, a.copy_json):
        if 'title-slide' in slide.get('cls', '') or slide.get('n') == 1:
            continue
        for rule, severity, name, text in lint_slide(slide):
            findings.append({'slide': slide['n'], 'rule': rule, 'severity': severity, 'field': name, 'text': text})
    errors = sum(f['severity'] == 'error' for f in findings)
    for f in findings:
        print(f"slide {f['slide']:>2}  {f['severity'].upper():<5} {f['rule']:<14} {f['field']}: {f['text']}")
    print(f'{errors} errors · {len(findings) - errors} warnings')
    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps({'findings': findings, 'errors': errors}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())

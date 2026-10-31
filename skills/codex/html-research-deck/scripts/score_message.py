#!/usr/bin/env python3
"""Score the copy of an HTML research deck against references/rubric-message.md: measured items (50) from the visible text,
plus an independent judge file (50) written by judge_message.py. Records SHA-256 of the rubric and the scripts so a score made
after the rules changed is marked invalid, and checks that the storyline's id/role/evidence still match the approved v1 snapshot.

usage: score_message.py /abs/deck/index.html [--judge /abs/deck/qa/judge-msg-<ts>.json] [--out /abs/deck/qa/score-message.json]
                        [--storyline-v1 /abs/work/storyline-v1.json] [--design-frozen /abs/deck/qa/rubric-frozen.json]
                        [--freeze /abs/deck/qa/rubric-message-frozen.json | --frozen <same path>]
"""
import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))
from deck_copy import dump  # noqa: E402  (skill script, trusted)

WATCHED = [SKILL / 'references' / 'rubric-message.md', SKILL / 'references' / 'judge-message-prompt.md', HERE / 'score_message.py', HERE / 'deck_copy.py']
DESIGN_WATCHED = [SKILL / 'references' / 'rubric.md', SKILL / 'references' / 'judge-prompt.md', HERE / 'score_deck.py', HERE / 'check_layout.py', HERE / 'check_deck.py']
BAN = re.compile(r'\b(CR[123]|ED1|RQ1|DU1)\b|§|\bTable\s*\d|\bFig\.?\s*\d|\bAppendix\b|\bObservation\s*\d')
SECTION_PREFIX = re.compile(r'^\s*(결과|배경|방법|분석|사례|발견|정리|프로토콜|평가|게임 설정|실험 설정|요약|한 장 요약)\s*\d*\s*[:：]')
NUM = re.compile(r'\d[\d,.]*')
JARGON = ['SCM', 'DEF', 'HP', 'EMI', 'ICC', 'Spearman', 'Agentic', 'Prompting', 'ReAct', 'OpenCode', 'openapi', 'hardened', 'SMC', 'Pareto', 'pp',
          '루브릭', '스캐폴딩', '베이스라인', '문턱', '궤적', '세션', '가족', '탐색 격차', '균형 표본', '반사실']
HOOK = ['우리', '연구실', '신약', '스크리닝', '실험 데이터', '구조 데이터', '여러분', '우리 데이터']
HONEST_NOTE = re.compile(r'모식|좌표에서|발표자\s*(해석|가설|번역|프레이밍|의견)')
HONEST_MARK = re.compile(r'모식|좌표|발표자')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def toks(s):
    return {t.lower() for t in re.findall(r'[가-힣A-Za-z0-9]+', s or '')}


def jaccard(a, b):
    a, b = toks(a), toks(b)
    return len(a & b) / len(a | b) if (a | b) else 0.0


def find_term(text, term):
    if term.isascii():
        m = re.search(r'(?<![A-Za-z])' + re.escape(term) + r'(?![A-Za-z])', text)
        return m.start() if m else -1
    return text.find(term)


def glossed(text, idx, term):
    after = text[idx + len(term): idx + len(term) + 36]
    before = text[max(0, idx - 24): idx]
    if re.match(r'^\s*\((?!\s*\d)[^)]*[가-힣]{2,}[^)]*\)', after):   # 용어(풀이) — a parenthesis that starts with a number is a unit, not a gloss
        return True
    if re.match(r'^\s*[=:—→]\s*[^.。|]{0,30}[가-힣]{2,}', after):      # 용어 = 풀이 / 용어: 풀이
        return True
    if re.search(r'[가-힣]{2,}\s*\($', before) and re.match(r'^[^()]{0,12}\)', after):  # 풀이(용어 …)
        return True
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('index'); ap.add_argument('--judge'); ap.add_argument('--out'); ap.add_argument('--storyline-v1'); ap.add_argument('--design-frozen')
    ap.add_argument('--freeze'); ap.add_argument('--frozen')
    a = ap.parse_args()
    index = Path(a.index).resolve()
    doc = dump(str(index))
    S = doc['slides']; n = len(S)
    content = [s for s in S if 1 < s['n'] < n]
    nc = max(1, len(content))
    D = {'title': {}, 'kicker': {}, 'closing': {}, 'banned': {}, 'jargon': {}, 'numbers': {}, 'guide': {}, 'honesty': {}}

    def vis_text(s):
        return ' '.join([s['kicker'], s['h2']] + s['lanes'] + s['visible'] + [s['closing']])

    # M1 titles
    ok = 0
    for s in content:
        t = s['h2'] or s['title']; why = []
        if SECTION_PREFIX.search(t): why.append('절 이름 접두사')
        if len(NUM.findall(t)) >= 3 or t.count('×') >= 2: why.append('변수 나열')
        if len(t) > 34: why.append(f'{len(t)}자 > 34')
        if BAN.search(t): why.append('금지 토큰')
        D['title'][s['n']] = why or 'ok'
        ok += not why
    M1 = round(8 * ok / nc, 2)
    # M2 kickers
    ok = 0; sections = set()
    for s in content:
        k = s['kicker']; m = re.match(r'^(.{1,14}) · (.{1,24})$', k)
        D['kicker'][s['n']] = 'ok' if m else f'형식 아님: {k!r}'
        if m: sections.add(m.group(1).strip())
        ok += bool(m)
    M2 = round(4 * ok / nc, 2)
    if len(sections) > 6: M2 = min(M2, 2.0)
    D['kicker']['sections'] = sorted(sections)
    # M3 closing lines
    ok = 0
    for s in content:
        c = s['closing']; why = []
        if not c: why.append('없음')
        else:
            if not (12 <= len(c) <= 48): why.append(f'{len(c)}자')
            if len(NUM.findall(c)) > 2: why.append('숫자 > 2')
            if BAN.search(c): why.append('금지 토큰')
            j = jaccard(s['h2'], c)
            if j >= 0.6: why.append(f'제목 되풀이 (jaccard {j:.2f})')
        D['closing'][s['n']] = why or 'ok'
        ok += not why
    M3 = round(8 * ok / nc, 2)
    # M4 jargon: (a) banned tokens incl. closing slide, (b) jargon avoided (plain Korean instead of term + parenthetical gloss)
    scope = [s for s in S if s['n'] > 1]
    clean = 0
    for s in scope:
        hits = sorted(set(m.group(0) for m in BAN.finditer(vis_text(s))))
        D['banned'][s['n']] = hits or 'ok'
        clean += not hits
    M4a = round(4 * clean / max(1, len(scope)), 2)
    present = 0
    for term in JARGON:
        for s in S:
            text = vis_text(s); idx = find_term(text, term)
            if idx >= 0:
                present += 1
                D['jargon'][term] = {'first_slide': s['n'], 'glossed': glossed(text, idx, term), 'context': text[max(0, idx - 20): idx + len(term) + 36]}
                break
    M4b = round(6 * (1 - present / len(JARGON)), 2)
    M4 = round(M4a + M4b, 2)
    # M5 number budget in kicker/h2/closing/lanes
    ok = 0
    for s in content:
        cnt = len(NUM.findall(' '.join([s['kicker'], s['h2'], s['closing']] + s['lanes'])))
        D['numbers'][s['n']] = cnt
        ok += cnt <= 3
    M5 = round(4 * ok / nc, 2)
    # M6 guide sentence and audience hook
    guide = any(re.search(r'(^|\s)(이 발표|오늘)', r) for s in S if 2 <= s['n'] <= 4 for r in s['visible'] + s['lanes'] + [s['closing']])
    hook = any(any(h in r for h in HOOK) for s in S if 2 <= s['n'] <= 3 for r in s['visible'] + s['lanes'] + [s['closing'], s['h2']])
    D['guide'] = {'this_talk_sentence_in_2_4': guide, 'audience_hook_in_2_3': hook}
    M6 = (2 if guide else 0) + (2 if hook else 0)
    # M7 honesty marks must sit in the cite line (not as parenthetical tags in titles or labels)
    app = 0; ok = 0
    for s in scope:
        if HONEST_NOTE.search(s['notes'] or ''):
            app += 1
            shown = bool(HONEST_MARK.search(s['cite'] or ''))
            D['honesty'][s['n']] = 'ok' if shown else '노트에는 있으나 인용줄 표시 없음'
            ok += shown
    M7 = round(4 * ok / app, 2) if app else 4.0
    # M8 no colon constructions in title, closing line and lane headers (user decision 2026-10-31)
    ok = 0; D['colon'] = {}
    for s in content:
        cnt = sum(t.count(':') + t.count('：') for t in [s['h2'], s['closing']] + s['lanes'])
        D['colon'][s['n']] = cnt
        ok += cnt == 0
    M8 = round(4 * ok / nc, 2)
    # M9 no parenthetical tags in title, closing line, lane headers and visible runs (user decision 2026-10-31);
    # a parenthesis that holds a number or only a unit (%, pp, 점, 회 …) carries information and is exempt, as the rubric says
    ok = 0; D['paren'] = {}
    PAREN = re.compile(r'[(（]([^()（）]*)[)）]')
    UNIT = re.compile(r'^\s*(%|pp|%p|포인트|점|회|대|개|명|초|분|시간|GPU-h|kB|MB)\s*$')
    for s in content:
        tags = [m.group(1) for t in [s['h2'], s['closing']] + s['lanes'] + s['visible'] for m in PAREN.finditer(t) if not re.search(r'\d', m.group(1)) and not UNIT.match(m.group(1))]
        D['paren'][s['n']] = tags or 'ok'
        ok += not tags
    M9 = round(4 * ok / nc, 2)
    measured = {'M1': M1, 'M2': M2, 'M3': M3, 'M4': M4, 'M5': M5, 'M6': M6, 'M7': M7, 'M8': M8, 'M9': M9}
    measured_total = round(sum(measured.values()), 2)

    judged = {'N1': 0.0, 'N2': 0.0, 'N3': 0.0, 'N4': 0.0, 'N5': 0.0, 'missing_slides': []}
    judge_meta = None
    if a.judge:
        jd = json.loads(Path(a.judge).read_text(encoding='utf-8'))
        jj = jd.get('judge') or {}
        rows = {int(r.get('n', 0)): r for r in jj.get('slides', [])}
        want = [s['n'] for s in content]
        judged['missing_slides'] = [i for i in want if i not in rows]
        def avg(k):
            vals = [rows[i].get(k) if i in rows and rows[i].get(k) in (0, 1, 2) else 0 for i in want]
            return sum(vals) / len(vals) if vals else 0
        judged['N1'] = round(12 * avg('N1') / 2, 2); judged['N2'] = round(8 * avg('N2') / 2, 2); judged['N4'] = round(8 * avg('N4') / 2, 2)
        deck = jj.get('deck') or {}
        judged['N3'] = round(max(0, min(10, float(deck.get('N3', 0) or 0))), 2); judged['N5'] = round(max(0, min(12, float(deck.get('N5', 0) or 0))), 2)
        judge_meta = {'file': str(Path(a.judge).resolve()), 'model': jd.get('model'), 'cost_usd': jd.get('cost_usd'), 'parse_error': jd.get('parse_error'), 'summary': jj.get('summary')}
    judged_total = round(judged['N1'] + judged['N2'] + judged['N3'] + judged['N4'] + judged['N5'], 2)

    hashes = {p.name: sha(p) for p in WATCHED}
    valid, why = True, []
    if a.frozen:
        fro = json.loads(Path(a.frozen).read_text(encoding='utf-8'))
        diff = [k for k in hashes if fro.get('hashes', {}).get(k) != hashes[k]]
        if diff: valid = False; why.append('message rubric or scripts changed since freeze: ' + ', '.join(diff))
    if a.design_frozen:
        fro = json.loads(Path(a.design_frozen).read_text(encoding='utf-8'))
        dh = {p.name: sha(p) for p in DESIGN_WATCHED}
        diff = [k for k in dh if fro.get('hashes', {}).get(k) != dh[k]]
        if diff: valid = False; why.append('design rubric or scripts changed since freeze: ' + ', '.join(diff))
    story = None
    if a.storyline_v1:
        v1p = Path(a.storyline_v1)
        cur = v1p.parent / 'storyline.json'
        if not v1p.exists():
            valid = False; why.append('no storyline-v1 snapshot')
        else:
            v1 = json.loads(v1p.read_text(encoding='utf-8')); st = json.loads(cur.read_text(encoding='utf-8')) if cur.exists() else {'slides': []}
            inv = [(x.get('id'), x.get('role'), x.get('evidence')) for x in v1.get('slides', [])]
            now_ = [(x.get('id'), x.get('role'), x.get('evidence')) for x in st.get('slides', [])]
            story = {'v1_slides': len(inv), 'deck_slides': n, 'invariants_equal': inv == now_}
            if len(inv) != n: valid = False; why.append(f'slide count {n} != storyline-v1 {len(inv)}')
            if inv != now_: valid = False; why.append('storyline id/role/evidence differ from v1')
    out = {'at': datetime.datetime.now().astimezone().isoformat(timespec='seconds'), 'index': str(index), 'slides': n,
           'measured': measured, 'measured_total': measured_total, 'judged': judged, 'judged_total': judged_total,
           'total': round(measured_total + judged_total, 2), 'valid': valid, 'invalid_reason': '; '.join(why), 'hashes': hashes,
           'judge': judge_meta, 'storyline': story, 'detail': D}
    if a.out:
        Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    if a.freeze:
        Path(a.freeze).write_text(json.dumps({'frozen_at': out['at'], 'hashes': hashes}, indent=1) + '\n', encoding='utf-8')
    print('measured: ' + ' · '.join(f'{k} {v:g}' for k, v in measured.items()) + f' = {measured_total:g}/50')
    print(('judged:   ' + ' · '.join(f'{k} {judged[k]:g}' for k in ('N1', 'N2', 'N3', 'N4', 'N5')) + f' = {judged_total:g}/50') if a.judge else 'judged:   (no judge file) 0/50')
    print(f"TOTAL {out['total']:g}/100  valid={valid}{'  ' + out['invalid_reason'] if why else ''}")


if __name__ == '__main__':
    main()

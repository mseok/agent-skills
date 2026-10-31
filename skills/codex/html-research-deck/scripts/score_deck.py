#!/usr/bin/env python3
"""Score an HTML research deck against references/rubric.md: measured items (60) from check_deck.py, check_layout.py and the
HTML itself, plus an independent judge file (40) written by judge_deck.py. Records SHA-256 of the rubric and the scripts so a
score made after the rules changed is marked invalid.

usage: score_deck.py /abs/deck/index.html [--judge /abs/deck/qa/judge-<ts>.json] [--out /abs/deck/qa/score.json]
                     [--storyline /abs/work/storyline.json] [--freeze /abs/deck/qa/rubric-frozen.json | --frozen <same path>]
"""
import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
WATCHED = [SKILL / 'references' / 'rubric.md', SKILL / 'references' / 'judge-prompt.md', HERE / 'score_deck.py', HERE / 'check_layout.py', HERE / 'check_deck.py']
MUTED = ('rgb(154,165,177)', 'rgb(138,150,163)')  # --muted #9AA5B1 and the builder's MUTED #8A96A3: reference-style gray text
SOURCE = re.compile(r'(§|Table|Tab\.|Fig\.?|Figure|Appendix|Observation|Abstract|Eq\.)', re.I)


def is_muted(run):
    return run.get('fill', '').replace(' ', '').lower() in MUTED


def commentary(P):
    """Free commentary lines of a panel: wide text runs outside any shape that are not the lane header, not muted reference
    text, not inside the drawing's vertical span and not a label sitting right above a shape (bar/box headings)."""
    runs = P.get('runs', [])
    if not runs:
        return []
    top = min(r['y'] for r in runs)
    ink = P.get('ink') or {}
    shapes = P.get('shapeBoxes', [])
    out = []
    for r in runs:
        if not r.get('free') or is_muted(r) or r['y'] <= top + 1:
            continue
        if ink and r['y'] + r['h'] > ink['y'] + 4 and r['y'] < ink['y'] + ink['h'] - 4:
            continue
        if any(0 <= sh['y'] - (r['y'] + r['h']) <= 30 and r['x'] < sh['x'] + sh['w'] and r['x'] + r['w'] > sh['x'] for sh in shapes):
            continue
        out.append(r)
    return out


def figure_extent(P):
    """Drawing extent including its labels (every text run that is not commentary): share of the panel's inner area."""
    ink = P.get('ink')
    if not ink:
        return 0.0
    com = {id(r) for r in commentary(P)}
    xs = [ink['x'], ink['x'] + ink['w']]; ys = [ink['y'], ink['y'] + ink['h']]
    for r in P.get('runs', []):
        if id(r) in com or is_muted(r):
            continue
        xs += [r['x'], r['x'] + r['w']]; ys += [r['y'], r['y'] + r['h']]
    pb = P['box']
    return round((max(xs) - min(xs)) * (max(ys) - min(ys)) / max(1, (pb['w'] - 40) * (pb['h'] - 40)), 3)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=900)


def sections(html):
    doc = re.sub(r'<!--.*?-->', '', html, flags=re.S)
    out = []
    for m in re.finditer(r'<section class="slide([^"]*)"([^>]*)>(.*?)</section>', doc, re.S):
        body = m.group(3)
        notes = re.search(r'<aside class="notes">(.*?)</aside>', body, re.S)
        cite = re.search(r'<div class="cite">(.*?)</div>', body, re.S)
        strip = lambda s: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or '')).strip()
        out.append({'title': (re.search(r'data-title="([^"]*)"', m.group(2)) or [None, ''])[1], 'kicker': '<div class="kicker' in body,
                    'h2': '<h2' in body or '<h1' in body, 'closing': 'class="takeaway' in body, 'cite': strip(cite.group(1) if cite else ''),
                    'notes': strip(notes.group(1) if notes else ''), 'canvas': '<canvas' in body, 'uppercase': 'text-transform:uppercase' in body.replace(' ', ''),
                    'gradtext': 'background-clip:text' in body.replace(' ', '') or '-webkit-background-clip:text' in body.replace(' ', ''),
                    'wash': 'class="wash"' in body, 'solid': 'takeaway solid' in body})
    return out, doc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('index'); ap.add_argument('--judge'); ap.add_argument('--out'); ap.add_argument('--storyline')
    ap.add_argument('--freeze'); ap.add_argument('--frozen')
    a = ap.parse_args()
    index = Path(a.index).resolve()
    html = index.read_text(encoding='utf-8')
    secs, doc = sections(html)
    n = len(secs)
    content = list(range(1, n - 1))  # 0-based indices of content slides (title and closing excluded)
    with tempfile.TemporaryDirectory() as td:
        cd = run([sys.executable, '-I', str(HERE / 'check_deck.py'), str(index), '--json', f'{td}/check.json'])
        m = re.search(r'(\d+) slides · (\d+) errors · (\d+) warnings', cd.stdout)
        cd_err, cd_warn = (int(m.group(2)), int(m.group(3))) if m else (99, 99)
        cl = run([sys.executable, '-I', str(HERE / 'check_layout.py'), str(index), '--json', f'{td}/layout.json', '--quiet'])
        layout = json.loads(Path(f'{td}/layout.json').read_text(encoding='utf-8')) if Path(f'{td}/layout.json').exists() else None
    if not layout:
        sys.exit('check_layout.py produced no JSON: ' + cl.stderr[-500:] + cl.stdout[-500:])
    L = layout['slides']
    S = {}
    S['A1'] = 5 if cd_err == 0 else 0
    clean = sum(1 for i in content if not L[i]['findings'])
    S['A2'] = round(10 * clean / max(1, len(content)), 2)
    bad = total = 0; under19 = False
    for i in content:
        for P in L[i]['panels']:
            runs = P.get('runs', [])
            dense = len(runs) > 40
            for r in runs:
                total += 1
                if r['fs'] < 19:
                    under19 = True
                if r['fs'] < 22:
                    if is_muted(r) or (dense and r['fs'] >= 19):
                        continue
                    bad += 1
    r_bad = bad / total if total else 0
    S['B1'] = 6 if r_bad == 0 else 5 if r_bad <= 0.02 else 3 if r_bad <= 0.05 else 0
    S['B2'] = 0 if under19 else 2
    kinds = [f['kind'] for s in L for f in s['findings']]
    S['B3'] = 0 if ('closing-wraps' in kinds or 'html-overflow' in kinds) else 2
    panels = [P for i in content for P in L[i]['panels']]
    ok_free = sum(1 for P in panels if len(commentary(P)) <= 3)
    S['C1'] = round(6 * ok_free / max(1, len(panels)), 2)
    chars = {i: sum(sum(r['chars'] for r in commentary(P)) for P in L[i]['panels']) for i in content}
    S['C2'] = round(6 * sum(1 for i in content if chars[i] <= 220) / max(1, len(content)), 2)
    fig = {f"{i + 1}.{P['i']}": figure_extent(P) for i in content for P in L[i]['panels']}
    fig_ok = sum(1 for i in content if any(fig[f"{i + 1}.{P['i']}"] >= 0.30 for P in L[i]['panels']))
    S['D1'] = round(6 * fig_ok / max(1, len(content)), 2)
    deco = {k for s in secs for k in ('canvas', 'uppercase', 'gradtext', 'wash', 'solid') if s[k]}
    S['D2'] = max(0, 4 - len(deco))
    S['E1'] = round(4 * sum(1 for i in content if SOURCE.search(secs[i]['cite'])) / max(1, len(content)), 2)
    S['E2'] = round(4 * sum(1 for i in content if len(secs[i]['notes']) >= 200 and SOURCE.search(secs[i]['notes'])) / max(1, len(content)), 2)
    f_viol = []
    if 'theme-research.css' not in html: f_viol.append('theme-research.css not linked')
    if 'Pretendard' not in html and 'Pretendard' not in (index.parent / 'css' / 'deck.css').read_text(encoding='utf-8', errors='ignore'): f_viol.append('Pretendard missing')
    if any(not (secs[i]['kicker'] and secs[i]['h2']) for i in content): f_viol.append('kicker/h2 missing on a content slide')
    if any(not secs[i]['closing'] for i in content): f_viol.append('closing line missing on a content slide')
    if any(s['canvas'] for s in secs): f_viol.append('canvas animation')
    S['F'] = max(0, 5 - len(f_viol))
    measured = round(sum(S.values()), 2)
    judge = None; J = {}
    if a.judge:
        jd = json.loads(Path(a.judge).read_text(encoding='utf-8'))
        judge = jd.get('judge', jd)
        rows = {int(s['n']): s for s in judge.get('slides', [])}
        avg = {}
        missing = []
        for k in 'GHIJ':
            vals = []
            for i in content:
                row = rows.get(i + 1)
                v = row.get(k) if row else None
                if row is None: missing.append(i + 1)
                if v in (0, 1, 2) and (v == 2 or (row.get('evidence') or '').strip()):
                    vals.append(v)
                else:
                    vals.append(0)  # missing slide, bad value or a deduction without evidence counts 0
            avg[k] = sum(vals) / (2 * max(1, len(content)))
        J = {'G': round(10 * avg['G'], 2), 'H': round(14 * avg['H'], 2), 'I': round(8 * avg['I'], 2), 'J': round(8 * avg['J'], 2)}
        J['missing_slides'] = sorted(set(missing))
    judged = round(sum(v for k, v in J.items() if k in 'GHIJ'), 2)
    hashes = {p.name: sha(p) for p in WATCHED}
    valid = True; why = ''
    if a.frozen:
        fro = json.loads(Path(a.frozen).read_text(encoding='utf-8'))
        diff = [k for k in hashes if fro.get('hashes', {}).get(k) != hashes[k]]
        if diff: valid, why = False, 'rubric or scripts changed since freeze: ' + ', '.join(diff)
    story = None
    if a.storyline:
        st = json.loads(Path(a.storyline).read_text(encoding='utf-8'))
        story = {'slides_expected': len(st.get('slides', [])), 'slides_found': n, 'status': st.get('status'), 'flow_sha256': (st.get('approval') or {}).get('flow_sha256')}
        if story['slides_expected'] != n: valid, why = False, (why + '; ' if why else '') + f"slide count {n} != storyline {story['slides_expected']}"
    out = {'index': str(index), 'at': datetime.datetime.now().astimezone().isoformat(timespec='seconds'), 'content_slides': [i + 1 for i in content],
           'measured': S, 'measured_total': measured, 'judge_file': a.judge, 'judged': J, 'judged_total': judged,
           'total': round(measured + judged, 2), 'valid': valid, 'invalid_reason': why, 'hashes': hashes, 'storyline': story,
           'detail': {'check_deck': {'errors': cd_err, 'warnings': cd_warn}, 'layout_findings': {i + 1: [f['kind'] for f in L[i]['findings']] for i in range(n) if L[i]['findings']},
                      'small_runs': {'bad': bad, 'total': total, 'where': {i + 1: [f"{r['fs']}px {r['t']}" for P in L[i]['panels'] for r in P.get('runs', []) if r['fs'] < 22 and not is_muted(r) and not (len(P.get('runs', [])) > 40 and r['fs'] >= 19)] for i in content}},
                      'commentary_chars': {i + 1: chars[i] for i in content},
                      'commentary_lines': {f"{i + 1}.{P['i']}": [r['t'] for r in commentary(P)] for i in content for P in L[i]['panels']},
                      'figure_share': fig,
                      'decoration': sorted(deco), 'style_violations': f_viol}}
    if a.freeze:
        Path(a.freeze).write_text(json.dumps({'frozen_at': out['at'], 'hashes': hashes}, indent=1) + '\n', encoding='utf-8')
    if a.out:
        Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('measured: ' + ' · '.join(f'{k} {v:g}' for k, v in S.items()) + f' = {measured:g}/60')
    if J:
        print('judged:   ' + ' · '.join(f'{k} {J[k]:g}' for k in 'GHIJ') + f' = {judged:g}/40' + (f"  (missing slides in judge file: {J['missing_slides']})" if J['missing_slides'] else ''))
    else:
        print('judged:   (no judge file) 0/40')
    print(f"TOTAL {out['total']:g}/100  valid={valid}{'  ' + why if why else ''}")


if __name__ == '__main__':
    main()

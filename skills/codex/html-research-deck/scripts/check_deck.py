#!/usr/bin/env python3
"""Static checks for a research-theme HTML deck before rendering.

usage: check_deck.py /absolute/deck/index.html [--json /absolute/qa/check.json]

Errors (exit 1): panel grid off the 24 px gutter / 176–898 band / 110–1810 width, unequal heights in a row,
a content slide without a closing line, a visible citation marker [n] missing from the cite line, a Korean
declarative ending in visible copy, a <use href="#..."> without the inlined sprite, scene text below 15 px.
Warnings: scene text 15–18 px, closing line longer than 70 characters, missing speaker notes, missing cite line.
The checks read the HTML only; rendered overlaps and legibility still need the PNG pass (references/qa.md).
"""
import argparse
import html as H
import json
import re
import sys

L, R, TOP, BOTTOM, GAP = 110, 1810, 176, 898, 24
SEC = re.compile(r'<section class="slide([^"]*)"([^>]*)>(.*?)</section>', re.S)
PANEL = re.compile(r'<div class="panel"[^>]*style="([^"]*)"')
NOTES = re.compile(r'<aside class="notes">.*?</aside>', re.S)
CITE = re.compile(r'<div class="cite">(.*?)</div>', re.S)
TAKE = re.compile(r'<div class="takeaway[^"]*">(.*?)</div>', re.S)
SC = re.compile(r'<svg class="sc"[^>]*>.*?</svg>', re.S)
DECL = re.compile(r'(한다|된다|있다|이다|했다|됐다|습니다|입니다)\s*[.\]]*$')
MARK = re.compile(r'\[(\d+(?:\s*[,–-]\s*\d+)*)\]')


def px(style, key):
    m = re.search(rf'(?:^|;)\s*{key}:\s*(-?\d+(?:\.\d+)?)px', style)
    return float(m.group(1)) if m else None


def units(fragment):
    return [H.unescape(u).strip() for u in re.findall(r'>([^<>]+)<', fragment) if H.unescape(u).strip()]


def marks(text):
    out = set()
    for m in MARK.finditer(text):
        for part in m.group(1).split(','):
            part = part.strip()
            rg = re.split(r'\s*[–-]\s*', part)
            if len(rg) == 2 and all(x.isdigit() for x in rg):
                out.update(range(int(rg[0]), int(rg[1]) + 1))
            elif part.isdigit():
                out.add(int(part))
    return out


def check_panels(styles, err, tag):
    boxes = []
    for st in styles:
        b = (px(st, 'left'), px(st, 'top'), px(st, 'width'), px(st, 'height'))
        if None in b:
            err.append(f'{tag}: panel without left/top/width/height ({st})')
        else:
            boxes.append(b)
    if not boxes:
        return 0
    for l, t, w, h in boxes:
        if l < L or l + w > R:
            err.append(f'{tag}: panel spans x {l:g}..{l + w:g}, outside {L}..{R}')
        if t < TOP or t + h > BOTTOM:
            err.append(f'{tag}: panel spans y {t:g}..{t + h:g}, outside {TOP}..{BOTTOM}')
    top = min(b[1] for b in boxes)
    bottom = max(b[1] + b[3] for b in boxes)
    if top != TOP:
        err.append(f'{tag}: first panel row starts at y={top:g}, expected {TOP}')
    if bottom != BOTTOM:
        err.append(f'{tag}: last panel row ends at y={bottom:g}, expected {BOTTOM}')
    rows = {}
    for b in boxes:
        rows.setdefault(b[1], []).append(b)
    for t, row in sorted(rows.items()):
        row.sort()
        if row[0][0] != L:
            err.append(f'{tag}: row at y={t:g} starts at x={row[0][0]:g}, expected {L}')
        if row[-1][0] + row[-1][2] != R:
            err.append(f'{tag}: row at y={t:g} ends at x={row[-1][0] + row[-1][2]:g}, expected {R}')
        for a, b in zip(row, row[1:]):
            gap = b[0] - (a[0] + a[2])
            if gap != GAP:
                err.append(f'{tag}: horizontal gap {gap:g} px in the row at y={t:g}, expected {GAP}')
        heights = sorted({b[3] for b in row})
        if len(heights) > 1:
            err.append(f'{tag}: panels in the row at y={t:g} have different heights {heights}')
    for a in boxes:
        below = [b for b in boxes if b[1] > a[1] and not (b[0] + b[2] <= a[0] or b[0] >= a[0] + a[2])]
        if below:
            nb = min(below, key=lambda b: b[1])
            gap = nb[1] - (a[1] + a[3])
            if gap != GAP:
                err.append(f'{tag}: vertical gap {gap:g} px between the panels at y={a[1]:g} and y={nb[1]:g}, expected {GAP}')
    return len(boxes)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('index')
    ap.add_argument('--json')
    a = ap.parse_args()
    doc = re.sub(r'<!--.*?-->', '', open(a.index, encoding='utf-8').read(), flags=re.S)  # comments are not slides
    err, warn, report = [], [], []
    has_sprite = 'class="sprite"' in doc
    for i, m in enumerate(SEC.finditer(doc), 1):
        classes, body = m.group(1), m.group(3)
        title = re.search(r'data-title="([^"]*)"', m.group(2))
        tag = f'slide {i} ({title.group(1) if title else "untitled"})'
        is_title = 'title-slide' in classes
        vis = NOTES.sub('', body)
        n_panels = check_panels(PANEL.findall(vis), err, tag)
        take = TAKE.search(vis)
        if not is_title and not take:
            err.append(f'{tag}: no closing line (.takeaway)')
        if take:
            t = ' '.join(units(take.group(0)))
            if len(t) > 75:
                warn.append(f'{tag}: closing line is {len(t)} characters; it may wrap to two lines')
        cite = CITE.search(vis)
        used = marks(' '.join(units(CITE.sub('', vis))))
        cited = marks(cite.group(1)) if cite else set()
        if used and not cite:
            err.append(f'{tag}: citation markers {sorted(used)} but no cite line')
        elif used - cited:
            err.append(f'{tag}: markers {sorted(used - cited)} are used but absent from the cite line')
        if not cite and not is_title:
            warn.append(f'{tag}: no cite line')
        if not NOTES.search(body):
            warn.append(f'{tag}: no speaker notes')
        bad = [u for u in units(vis) if DECL.search(u)]
        for u in bad:
            err.append(f'{tag}: declarative ending in visible copy: "{u}"')
        if '<use href="#' in vis and not has_sprite:
            err.append(f'{tag}: uses sprite shapes but the document has no inlined <svg class="sprite">')
        small, tiny = [], []
        for scene in SC.findall(vis):
            for v in re.findall(r'font-size[:=]\s*"?(\d+(?:\.\d+)?)', scene):
                v = float(v)
                (tiny if v < 15 else small if v < 19 else []).append(v)
        if tiny:
            err.append(f'{tag}: scene text below 15 px: {sorted(set(tiny))}')
        if small:
            warn.append(f'{tag}: scene text between 15 and 18 px ({len(small)} runs: {sorted(set(small))}); keep only for badge digits and capsule labels')
        report.append({'slide': i, 'title': title.group(1) if title else '', 'panels': n_panels,
                       'visible_words': sum(len(u.split()) for u in units(vis)), 'markers': sorted(used)})
    for r in report:
        print(f"slide {r['slide']:>2}  panels={r['panels']}  words={r['visible_words']:>3}  markers={r['markers']}  {r['title']}")
    for e in err:
        print('ERROR  ' + e)
    for w in warn:
        print('WARN   ' + w)
    print(f'{len(report)} slides · {len(err)} errors · {len(warn)} warnings')
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump({'slides': report, 'errors': err, 'warnings': warn}, f, ensure_ascii=False, indent=1)
    return 1 if err else 0


if __name__ == '__main__':
    sys.exit(main())

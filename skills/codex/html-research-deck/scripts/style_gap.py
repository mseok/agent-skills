#!/usr/bin/env python3
"""style_gap.py — how far a deck's look is from the accepted Opus decks, measured on the rendered PNGs. No model, standard library only.

usage: style_gap.py /abs/work-folder [--json out.json]     (holds deck/index.html, deck/qa/shots-full/slide-NN.png, work/storyline-v1.json)

Measured inside the panel band of each content slide:
  mass       share that is drawn at all (neither white nor stage)
  anchor     largest connected drawn region: the shape the eye lands on (a density field, wide bars, a solid box)
  emptyrect  largest rectangle with nothing in it: space left over in one lump, as opposed to spread evenly
  whitebox   largest connected pure-white region: stage first (user 2026-11-02) keeps figures on the warm stage and white for a card that holds one thing
Limits come from the accepted Opus decks rendered under the stage-first theme (Latent SI first build and v11, CausalGame v12; 2026-11-02): a figure slide never fell below mass 9.8,
anchor 0.9 or above emptyrect 11.7 there, a result slide never below mass 3.8 or above emptyrect 20; their medians on figure slides were mass 13-23, anchor 3.8-12.6, emptyrect 6.8-8.3, and a GPT
build before this script had 11.8, 3.2, 11.0. A kit-built deck can also overshoot, with big filled boxes in place of drawings (medians 33-38 on CausalGame), hence the upper limit on mass.
This measures resemblance, not quality: it has no view on the argument.
Also flagged: a formula row that starts with an operator, which is one relation split over two rows (user 2026-11-02), and a formula card taller than 170 px that holds one row (the judges' empty blue card, 2026-11-02).
The whitebox limit: the Yuanqi Du deck's median is 6, v10 with white figure panels 29, six chart cards on one slide 16 each. Also checked: the cover is the title-slide template with the title on the stage; titles and closing lines against the approved storyline.
Prints one FIX line per finding and exits 0; the builder fixes them and runs it again.
"""
import argparse
import glob
import html
import json
import re
import statistics
import struct
import sys
import zlib
from pathlib import Path

FIGURE_MEDIANS = {'mass': (13.0, 28.0), 'anchor': (3.5, None), 'emptyrect': (None, 9.0)}
RESULT_MEDIANS = {'mass': (13.0, 32.0), 'emptyrect': (None, 11.5)}
FIGURE_SLIDE = {'mass': (9.0, None), 'anchor': (0.9, None), 'emptyrect': (None, 12.0), 'whitebox': (None, 20.0)}
RESULT_SLIDE = {'mass': (3.5, None), 'emptyrect': (None, 20.0), 'whitebox': (None, 20.0)}
HEAVY = '칠한 면이 너무 많다: 글을 담은 큰 상자와 넓은 색 띠를 줄이고 곡선, 점, 작은 도형으로 그린다'
WHY = {'mass': '그림이 얇다: 선과 작은 상자 대신 채운 도형으로, 더 크게', 'anchor': '눈이 먼저 갈 큰 도형이 없다: hero_bridge, 큰 model_box, 넓은 막대처럼 패널을 차지하는 중심을 둔다',
       'emptyrect': '패널에 큰 빈 곳이 있다: 그림을 키워 그 자리를 채운다',
       'whitebox': '큰 흰 박스가 있다: 그림은 흰 패널 없이 무대 위에 바로 놓고, 흰색은 수식이나 작은 차트 하나만 담는 카드에만 쓴다'}
NOT_SCORED = {'title', 'conclusion'}
SPLIT_ROW = re.compile(r'^\s*\$\s*(?:\\[;,:!]|\\quad|\\qquad|\s)*(?:\+|-|−|=|\\ge\b|\\le\b|\\geq\b|\\leq\b|\\propto\b|\\approx\b)')


def read_png(path):
    data = Path(path).read_bytes()
    pos, idat, w, h, ct = 8, [], 0, 0, 0
    while pos < len(data):
        n = struct.unpack('>I', data[pos:pos + 4])[0]
        kind, body = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + n]
        if kind == b'IHDR':
            w, h, depth, ct = struct.unpack('>IIBB', body[:10])
            if depth != 8 or ct not in (2, 6):
                raise ValueError(f'{path}: PNG depth {depth} colour type {ct}')
        elif kind == b'IDAT':
            idat.append(body)
        pos += 12 + n
    raw = zlib.decompress(b''.join(idat))
    bpp = 3 if ct == 2 else 4
    stride = w * bpp
    rows, prev, i = [], bytearray(stride), 0
    for _ in range(h):
        ft = raw[i]
        line = bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if ft == 1:
                line[x] = (line[x] + a) & 255
            elif ft == 2:
                line[x] = (line[x] + b) & 255
            elif ft == 3:
                line[x] = (line[x] + ((a + b) >> 1)) & 255
            elif ft == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else (b if pb <= pc else c))) & 255
        rows.append(line)
        prev = line
    return w, h, bpp, rows


def features(path, step=3):
    _, _, bpp, rows = read_png(path)
    y0, y1, x0, x1 = 176, 898, 110, 1810
    gw, gh = (x1 - x0) // step, (y1 - y0) // step
    g = [[0] * gw for _ in range(gh)]
    w = [[0] * gw for _ in range(gh)]
    for j in range(gh):
        row = rows[y0 + j * step]
        for i in range(gw):
            x = (x0 + i * step) * bpp
            r, gr, b = row[x], row[x + 1], row[x + 2]
            w[j][i] = int(min(r, gr, b) >= 254)
            if min(r, gr, b) >= 250 or (abs(r - 250) <= 3 and abs(gr - 248) <= 3 and abs(b - 243) <= 4):
                continue
            g[j][i] = 1
    n = gw * gh

    def largest(mask):
        seen = [[False] * gw for _ in range(gh)]
        best = 0
        for j0 in range(gh):
            for i0 in range(gw):
                if not mask[j0][i0] or seen[j0][i0]:
                    continue
                stack, a = [(i0, j0)], 0
                seen[j0][i0] = True
                while stack:
                    i, j = stack.pop()
                    a += 1
                    for u, v in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                        if 0 <= u < gw and 0 <= v < gh and mask[v][u] and not seen[v][u]:
                            seen[v][u] = True
                            stack.append((u, v))
                best = max(best, a)
        return best

    anchor, whitebox = largest(g), largest(w)
    c = 4
    cw, ch = gw // c, gh // c
    heights, empty = [0] * cw, 0
    for j in range(ch):
        for i in range(cw):
            full = any(g[j * c + b][i * c + a] for a in range(c) for b in range(c))
            heights[i] = 0 if full else heights[i] + 1
        stack = []
        for i in range(cw + 1):
            hh = heights[i] if i < cw else 0
            start = i
            while stack and stack[-1][1] >= hh:
                s, sh = stack.pop()
                empty = max(empty, sh * (i - s))
                start = s
            stack.append((start, hh))
    return {'mass': round(sum(map(sum, g)) / n * 100, 1), 'anchor': round(anchor / n * 100, 1), 'emptyrect': round(empty / (cw * ch) * 100, 1), 'whitebox': round(whitebox / n * 100, 1)}


def plain(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('work'); ap.add_argument('--json')
    a = ap.parse_args()
    root = Path(a.work).resolve()
    doc = (root / 'deck' / 'index.html').read_text(encoding='utf-8')
    secs = re.findall(r'<section\b.*?</section>', doc, flags=re.S)
    fixes = []
    first = secs[0]
    if 'title-slide' not in first[:200]:
        fixes.append('FIX slide 1: 표지가 title-slide가 아니다. scene_kit.cover()로 만든다')
    head = re.sub(r'<div class="panel.*', '', first, flags=re.S)
    if '<h1' not in head:
        fixes.append('FIX slide 1: 제목이 흰 패널 안에 있거나 h1이 없다. 제목은 무대 위에 둔다')
    if re.search(r'class="takeaway|class="kicker|<h2', first):
        fixes.append('FIX slide 1: 표지에는 kicker, h2, 마무리줄을 두지 않는다')
    st_path = root / 'work' / 'storyline-v1.json'
    st = json.loads(st_path.read_text(encoding='utf-8')) if st_path.exists() else {'slides': []}
    roles = {i + 1: s.get('role', '') for i, s in enumerate(st.get('slides', []))}
    changed = []
    for i, (s, sec) in enumerate(zip(st.get('slides', []), secs), 1):
        m_h = re.search(r'<h2[^>]*>(.*?)</h2>', sec, flags=re.S)
        m_c = re.search(r'class="takeaway"[^>]*>(.*?)</div>', sec, flags=re.S)
        if i > 1 and m_h and plain(m_h.group(1)) != plain(s.get('title', '')):
            changed.append(f'{i}장 제목')
        if i > 1 and m_c and plain(m_c.group(1)) != plain(s.get('closing', '')):
            changed.append(f'{i}장 마무리줄')
    for i, sec in enumerate(secs, 1):
        body = re.sub(r'<aside class="notes">.*?</aside>', '', sec, flags=re.S)
        for row in re.findall(r'<p[^>]*>(.*?)</p>', body, flags=re.S):
            if SPLIT_ROW.match(html.unescape(row)):
                fixes.append(f'FIX slide {i}: 식이 두 줄로 나뉘었다({plain(row)[:40]}…). 한 관계식은 한 줄에: 카드를 넓히거나 24 px까지 줄인다')
        for m in re.finditer(r'<div class="fx box[^"]*"[^>]*height:([\d.]+)px[^>]*>(.*?)</div>', body, flags=re.S):
            if float(m.group(1)) > 170 and len(re.findall(r'<p[ >]', m.group(2))) == 1:
                fixes.append(f'FIX slide {i}: 식 한 줄에 높이 {float(m.group(1)):g} px 카드는 휑하다. 카드 높이를 내용에 맞춘다(한 줄이면 130 px 안팎)')
    rows = []
    for p in sorted(glob.glob(str(root / 'deck' / 'qa' / 'shots-full' / 'slide-*.png'))):
        n = int(re.search(r'slide-(\d+)', p).group(1))
        if roles.get(n) in NOT_SCORED or n == 1 or (not roles and n == len(secs)):
            continue
        f = features(p)
        f['n'] = n
        f['kind'] = 'result' if roles.get(n) in ('result', 'limitation', 'finding', 'analysis', 'example') else 'figure'
        rows.append(f)
    if not rows:
        print('no rendered slides: run shots.sh into deck/qa/shots-full first', file=sys.stderr)
        return 2
    for f in rows:
        for key, (lo, hi) in (RESULT_SLIDE if f['kind'] == 'result' else FIGURE_SLIDE).items():
            if (lo is not None and f[key] < lo) or (hi is not None and f[key] > hi):
                fixes.append(f"FIX slide {f['n']}: {key} {f[key]} (한계 {'≥ ' + str(lo) if lo is not None else '≤ ' + str(hi)}) {WHY[key]}")
    meds = {}
    for kind, target in (('figure', FIGURE_MEDIANS), ('result', RESULT_MEDIANS)):
        sel = [f for f in rows if f['kind'] == kind]
        if not sel:
            continue
        for key, (lo, hi) in target.items():
            m = statistics.median(f[key] for f in sel)
            meds[f'{kind}.{key}'] = m
            if (lo is not None and m < lo) or (hi is not None and m > hi):
                over = hi is not None and m > hi
                fixes.append(f"FIX deck {kind} median {key} {m:.1f} (목표 {'≤ ' + str(hi) if over else '≥ ' + str(lo)}) {HEAVY if key == 'mass' and over else WHY[key]}")
    print('slide kind    mass anchor emptyrect whitebox')
    for f in rows:
        print(f"{f['n']:5d} {f['kind']:6s} {f['mass']:5.1f} {f['anchor']:6.1f} {f['emptyrect']:9.1f} {f['whitebox']:8.1f}")
    if changed:
        print(f"note: 스토리라인과 다른 문구 {len(changed)}곳: {', '.join(changed[:24])}. message-style.md 규칙에 걸린 곳이 아니면 스토리라인 문구로 되돌린다")
    print('\n'.join(fixes) if fixes else 'no findings')
    print(f'style gap: {len(fixes)} findings · medians ' + ' '.join(f'{k} {v:.1f}' for k, v in meds.items()))
    if a.json:
        Path(a.json).write_text(json.dumps({'slides': rows, 'medians': meds, 'fixes': fixes, 'changed': changed}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())

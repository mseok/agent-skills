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
The Opus 5 and Sonnet 5.5 decks of the DDSBM paper were accepted as they are (user 2026-11-03: '지금 이대로가 좋은거같고') and widened the lower and upper limits: Opus 5's slide 2, a thin graph over a table, has mass 7.5 and emptyrect 13.3, and a stricter limit would tell a builder to inflate exactly what the user liked.
This measures resemblance, not quality: it has no view on the argument.
Also flagged: a crop stretched past its source pixels (data-native, user 2026-11-03: "astra 17페이지의 분자 그림은 매우 해상도가 낮네"), one graph twice on a slide, a slide whose panels are all two far-apart bars, two-bar charts over 340 px tall, more than three slides of alike bar panels, a bar flattened to the axis, a closing slide with a large empty lump, a graph drawn heavier than the accepted decks (user 2026-11-03: lines over 4.6 px or unlabelled discs over 48 px wide; the GPT decks that drew 68-82 px discs and 8 px sticks had passed mass and anchor), paper_crop overuse (more than four slides, narrower than 480 px or 296 px on the cover, the same region twice, or a slide that is only a crop; the first GPT builds with the tool cropped 8 and 11 slides), a formula row that starts with an operator, which is one relation split over two rows (user 2026-11-02), and a formula card taller than 170 px that holds one row (the judges' empty blue card, 2026-11-02).
The whitebox limit: the Yuanqi Du deck's median is 6, v10 with white figure panels 29, six chart cards on one slide 16 each. Also checked: the cover is the title-slide template with the title on the stage; titles and closing lines against the approved storyline.
Prints one FIX line per finding and exits 0; the builder fixes them and runs it again.
"""
import argparse
import glob
import html
import json
import math
import re
import statistics
import struct
import sys
import zlib
from pathlib import Path

FIGURE_MEDIANS = {'mass': (13.0, 24.0), 'anchor': (3.5, None), 'emptyrect': (None, 10.0)}
RESULT_MEDIANS = {'mass': (13.0, 26.0), 'emptyrect': (None, 12.0)}
FIGURE_SLIDE = {'mass': (6.0, None), 'anchor': (0.9, None), 'emptyrect': (None, 16.0), 'whitebox': (None, 20.0)}
RESULT_SLIDE = {'mass': (3.5, None), 'emptyrect': (None, 20.0), 'whitebox': (None, 20.0)}
HEAVY = '칠한 면이 너무 많다: 글을 담은 큰 상자와 넓은 색 띠를 줄이고 곡선, 점, 작은 도형으로 그린다'
WHY = {'mass': '그림이 부족하다: 분포, 막대, 곡선, 논문 그림을 더한다. 원을 키우거나 선을 굵게 하지 않는다', 'anchor': '눈이 먼저 갈 큰 도형이 없다: hero_bridge, 큰 model_box, 넓은 막대처럼 패널을 차지하는 중심을 둔다',
       'emptyrect': '패널에 큰 빈 곳이 있다: 표나 차트를 더하거나 그림을 옮긴다. 원과 선은 키우지 않는다',
       'whitebox': '큰 흰 박스가 있다: 그림은 흰 패널 없이 무대 위에 바로 놓고, 흰색은 수식이나 작은 차트 하나만 담는 카드에만 쓴다'}
NOT_SCORED = {'title', 'conclusion'}
CLOSING_EMPTY = 25.0  # the closing slide's largest empty rectangle: accepted decks 7.1-17.0, GPT decks that held only questions 48-70
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


def attr(tag, name):
    m = re.search(rf'\b{name}="([^"]*)"', tag)
    return m.group(1) if m else None


def twin_graphs(body):
    """Cells of one panel that draw the same graph: same discs, edges and labels at the same relative places. Returns how many extra copies there are."""
    extra = 0
    for svg in re.findall(r'<svg\b.*?</svg>', body, flags=re.S):
        discs = sorted((float(attr(t, 'cx')), float(attr(t, 'cy')), float(attr(t, 'r')), attr(t, 'fill'), attr(t, 'stroke')) for t in re.findall(r'<circle\b[^>]*>', svg) if attr(t, 'r') and attr(t, 'cx') and float(attr(t, 'r')) >= 8)
        cells, cur = [], []
        for d in discs:
            if cur and d[0] - cur[-1][0] > 90:
                cells.append(cur)
                cur = []
            cur.append(d)
        if cur:
            cells.append(cur)
        lines = [tuple(attr(t, a) for a in ('x1', 'y1', 'x2', 'y2')) + (attr(t, 'stroke'),) for t in re.findall(r'<line\b[^>]*>', svg)]
        lines = [(float(a), float(b), float(c), float(d_), s) for a, b, c, d_, s in lines if None not in (a, b, c, d_)]
        texts = [(float(m.group(1)), float(m.group(2)), re.sub(r'<[^>]+>', '', m.group(3))) for m in re.finditer(r'<text\b[^>]*?\bx="(-?[\d.]+)"[^>]*?\by="(-?[\d.]+)"[^>]*>(.*?)</text>', svg, flags=re.S)]
        seen = {}
        for c in cells:
            if len(c) < 6:  # a small icon may repeat (the accepted Sonnet 5.5 deck has a 4-node one twice); a figure of its own may not
                continue
            x0, x1, y0, y1 = min(d[0] for d in c), max(d[0] for d in c), min(d[1] for d in c), max(d[1] for d in c)
            nodes = tuple((round(d[0] - x0), round(d[1] - y0), d[3], d[4]) for d in c)
            edges = tuple(sorted((round(a - x0), round(b - y0), round(p - x0), round(q - y0), s) for a, b, p, q, s in lines if x0 - 5 <= min(a, p) and max(a, p) <= x1 + 5 and y0 - 5 <= min(b, q) and max(b, q) <= y1 + 5))
            words = tuple(sorted((round(a - x0), round(b - y0), t) for a, b, t in texts if x0 - 30 <= a <= x1 + 30 and y0 - 30 <= b <= y1 + 30))
            seen[(nodes, edges, words)] = seen.get((nodes, edges, words), 0) + 1
        extra += sum(k - 1 for k in seen.values())
    return extra


def bar_panels(body):
    """Bars of each panel, read off the SVG: (panel width, sorted [(x, width, height)]). A bar is a filled rectangle with no outline, 24 to 200 px wide, in a set of equal widths."""
    out = []
    for m in re.finditer(r'<div class="panel[^"]*"[^>]*?width:(\d+)px[^>]*>\s*<svg\b(.*?)</svg>', body, flags=re.S):
        rects = []
        for t in re.findall(r'<rect\b[^>]*>', m.group(2)):
            w, h = attr(t, 'width'), attr(t, 'height')
            if w and h and 24 <= float(w) <= 200 and attr(t, 'stroke') in (None, 'none') and attr(t, 'fill') not in ('#fff', '#FFFFFF', 'none', None):
                rects.append((float(attr(t, 'x')), float(w), float(h)))
        widths = {}
        for r in rects:
            widths.setdefault(r[1], []).append(r)
        bars = sorted(max(widths.values(), key=len)) if widths else []
        out.append((int(m.group(1)), bars if len(bars) >= 2 else []))
    return out


def graph_weight(body):
    """Node-link figures on a slide, panel by panel: (edges, widest edge in px, median radius of discs with no letter in them). An edge is a line with both ends at a disc of r ≥ 8."""
    def num(tag, name):
        m = re.search(rf'\b{name}="(-?[\d.]+)"', tag)
        return float(m.group(1)) if m else None
    edges, widest, radii = 0, 0.0, []
    for svg in re.findall(r'<svg\b.*?</svg>', body, flags=re.S):
        discs = [(num(t, 'cx'), num(t, 'cy'), num(t, 'r')) for t in re.findall(r'<circle\b[^>]*>', svg)]
        discs = [d for d in discs if None not in d and d[2] >= 8]
        labels = [(num(t, 'x'), num(t, 'y')) for t in re.findall(r'<text\b[^>]*>', svg)]
        here = 0
        for t in re.findall(r'<line\b[^>]*>', svg):
            x1, y1, x2, y2 = (num(t, a) for a in ('x1', 'y1', 'x2', 'y2'))
            if None in (x1, y1, x2, y2) or math.hypot(x2 - x1, y2 - y1) <= 6:
                continue
            if all(any(math.hypot(px - a, py - b) <= r + 20 for a, b, r in discs) for px, py in ((x1, y1), (x2, y2))):
                here += 1
                m = re.search(r'stroke-width[=:]"?\s*([\d.]+)', t)
                widest = max(widest, float(m.group(1)) if m else 0.0)
        if here >= 3:
            edges += here
            radii += [r for a, b, r in discs if not any(x is not None and y is not None and math.hypot(x - a, y - b) <= r + 2 for x, y in labels)]
    return edges, widest, statistics.median(radii) if radii else 0.0


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
    crop_slides, crop_boxes, alike_slides = [], [], []
    for i, sec in enumerate(secs, 1):
        body = re.sub(r'<aside class="notes">.*?</aside>', '', sec, flags=re.S)
        crop_tags = re.findall(r'<image\b[^>]*\bdata-crop="[^"]*"[^>]*>', body)
        if crop_tags:
            crop_slides.append(i)
            area = 0.0
            for t in crop_tags:
                src = re.search(r'data-crop="(\d+):([\d.,]+)"', t)
                w_, h_ = float(re.search(r'\bwidth="([\d.]+)"', t).group(1)), float(re.search(r'\bheight="([\d.]+)"', t).group(1))
                area += w_ * h_
                if w_ < (296 if i == 1 else 480):
                    fixes.append(f'FIX slide {i}: 자른 그림의 폭이 {w_:g} px다. 표지 밖에서는 480 px 이상으로 놓거나 빼고 직접 그린다')
                box = [float(v) for v in src.group(2).split(',')]
                for j, page, other in crop_boxes:
                    if page == src.group(1):
                        ow = max(0.0, min(box[2], other[2]) - max(box[0], other[0])); oh = max(0.0, min(box[3], other[3]) - max(box[1], other[1]))
                        if ow * oh > 0.3 * min((box[2] - box[0]) * (box[3] - box[1]), (other[2] - other[0]) * (other[3] - other[1])):
                            fixes.append(f'FIX slide {i}: 자른 그림이 {j}장과 같은 부분이다. 같은 부분을 두 번 쓰지 않는다')
                            break
                crop_boxes.append((i, src.group(1), box))
            drawn = len(re.findall(r'<(?:circle|line|path|rect|polygon)\b', body))
            if area / (1700 * 722) > 0.45 and drawn < 6:
                fixes.append(f'FIX slide {i}: 자른 그림이 패널의 {100 * area / (1700 * 722):.0f}%이고 직접 그린 도형이 {drawn}개다. 분포, 차트, 표를 직접 그려 함께 둔다')
        for t in crop_tags:
            w_, native = float(attr(t, 'width')), attr(t, 'data-native')
            if native and float(native) < 0.98 * w_:
                fixes.append(f'FIX slide {i}: 자른 그림의 원본이 {float(native):.0f} px인데 {w_:g} px로 늘려 흐리다. PDF 안의 비트맵이라 dpi를 올려도 선명해지지 않는다. pdfimages -list로 더 선명한 그림을 찾거나 ggraph()로 그린다')
        twins = twin_graphs(body)
        if twins:
            fixes.append(f'FIX slide {i}: 한 장의 칸들에 같은 graph가 {twins + 1}번 있다. 칸마다 달라지는 것을 표시하거나 칸을 줄인다')
        panels_b = bar_panels(body)
        with_bars = [p for p in panels_b if p[1]]
        if with_bars and len(with_bars) == len(panels_b) and all(len(b) == 2 and b[1][0] - (b[0][0] + b[0][1]) > 200 for _, b in with_bars):
            fixes.append(f'FIX slide {i}: 넓은 패널에 막대 두 개뿐이라 가운데가 비었다. 갤러리 18장처럼 좁은 패널 P3A, P3B에 두고 P3C에 그 차이가 어디서 왔는지 그린다')
        if with_bars and all(len(b) == 2 for _, b in with_bars) and max(r[2] for _, b in with_bars for r in b) > 340:
            fixes.append(f'FIX slide {i}: 막대 두 개짜리 차트의 막대가 높이 {max(r[2] for _, b in with_bars for r in b):.0f} px다(받아들여진 덱은 304 px까지). 300 px 아래로 줄이고 남는 자리에 차이 숫자, 설명 그림, 논문 그림을 둔다(갤러리 18, 19장)')
        if len(with_bars) >= 2 and len({len(b) for _, b in with_bars}) == 1:
            alike_slides.append(i)
        for _, b in with_bars:
            if len(b) == 2 and max(r[2] for r in b) > 100 and min(r[2] for r in b) < 0.05 * max(r[2] for r in b):
                fixes.append(f'FIX slide {i}: 막대 하나가 바닥에 붙어 막대 한 개처럼 보인다. 두 값을 big()으로 크게 적거나 다른 그림으로 바꾼다')
        gedges, gwide, gr = graph_weight(body)
        if gedges >= 3 and (gwide > 4.6 or gr > 24):
            fixes.append(f'FIX slide {i}: graph가 무겁다(선 {gwide:g} px, 글자 없는 원 지름 {2 * gr:g} px; 받아들여진 덱은 3.4 px, 44 px). 논문 그림이 있으면 paper_crop(), 없으면 ggraph()로 다시 그린다(갤러리 16·17장)')
        for row in re.findall(r'<p[^>]*>(.*?)</p>', body, flags=re.S):
            if SPLIT_ROW.match(html.unescape(row)):
                fixes.append(f'FIX slide {i}: 식이 두 줄로 나뉘었다({plain(row)[:40]}…). 한 관계식은 한 줄에: 카드를 넓히거나 24 px까지 줄인다')
        for m in re.finditer(r'<div class="fx box[^"]*"[^>]*height:([\d.]+)px[^>]*>(.*?)</div>', body, flags=re.S):
            if float(m.group(1)) > 170 and len(re.findall(r'<p[ >]', m.group(2))) == 1:
                fixes.append(f'FIX slide {i}: 식 한 줄에 높이 {float(m.group(1)):g} px 카드는 휑하다. 카드 높이를 내용에 맞춘다(한 줄이면 130 px 안팎)')
    if len(alike_slides) > 3:
        fixes.append(f'FIX deck: 같은 모양의 막대 패널을 나란히 둔 장이 {len(alike_slides)}장이다({alike_slides}). 받아들여진 덱은 2장까지다. 일부를 선(갤러리 7, 12장), 순위 점(11장), 상자(13장), 작은 카드(14장), 작은 차트와 논문 그림(19장)으로 바꾼다')
    if len(crop_slides) > 4:
        fixes.append(f'FIX deck: paper_crop을 {len(crop_slides)}장에 썼다({crop_slides}). 4장까지다: 연구 대상의 선 그림만 남기고 분포, 경로, 기전, 차트는 kit으로 그린다')
    last = root / 'deck' / 'qa' / 'shots-full' / f'slide-{len(secs):02d}.png'
    if last.exists():
        fl = features(str(last))
        if fl['emptyrect'] > CLOSING_EMPTY:
            fixes.append(f"FIX slide {len(secs)}: 마지막 장의 {fl['emptyrect']:.0f}%가 한 덩어리로 비었다(받아들여진 덱은 7–17%). 갤러리 8장을 복사한다: 왼쪽에 논문이 보여 준 것, 오른쪽 패널에만 질문")
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

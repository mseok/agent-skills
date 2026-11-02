#!/usr/bin/env python3
"""kit_gallery.py — fifteen worked slides drawn with scene_kit.py, with toy content and no paper in them. Copy a slide's code, keep its sizes and positions, change the content.

usage: kit_gallery.py /abs/deck   (a folder scaffolded by new_deck.py). Renders are kept in assets/kit-gallery/ of this skill.
Numbers, names and curves here are invented to show the drawing; nothing on these slides is a result.
"""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scene_kit import *  # noqa: E402,F403
from scene_kit import AMBER, AMBERD, BAR_OTHER, BIMODAL, BLUE, CORAL, FULL, GHOST, GRAY, GRAYL, INK, L2, MUTED, NAVY, R2, RED, SOFT, STEEL, STEELD  # noqa: E402

CITE = '예시 내용 · 숫자와 이름은 그리는 법을 보이려고 지어낸 것'
F = Field(0.62, BIMODAL, sig=1.0)


def g1_cover():
    """Cover: the title on the stage; on the right one figure on a panel: a density field over a chain."""
    fr, s = hero_bridge('g1', F, 70, 670, 44, 366, yr=(-2.5, 2.5), bulge=50, n=7, seed=3, axis=False, dots=False)
    s += line(275, 478, 70, 370, GRAYL, 2) + line(465, 478, 670, 370, GRAYL, 2)
    c, _ = chain(540, [('picture', 92), ('enc', 118, 104), ('model', 180, 104, '모델'), ('dec', 118, 104), ('picture', 92)], 0, 740)
    s += c + T(370, 650, '한 loss로 jointly 학습하는 세 모델', 26, 700, NAVY, 'middle')
    h = tex(20, 30, '$z_0$ prior', 24, 650, AMBERD) + tex(740, 30, '$z_1$ latent', 24, 650, STEELD, 'end')
    return cover('예시 논문의<br><em>강조할 말</em><br>제목 셋째 줄', 'English Title of the Paper', '이 발표가 무엇을 보여 주는지 한 줄',
                 '저자 이름 · 저자 이름', '소속 · 소속', '학회 2026 · arXiv:0000.00000 · 연구실 논문 세미나', s, h, notes('표지의 그림은 예시 분포에서 계산한 모식입니다.'))


def g2_two_chains():
    """Two panels side by side: two rows of chains on the left, the proposal with its gradients on the right; a strip closes each panel."""
    y1 = 180
    l = lane(0, 24, '지금의 습관은 두 단계') + badge(17, 62, 1) + T(46, 70, '먼저 앞뒤 모델만 학습해 고정', 24, 650)
    c, xs = chain(y1, [('picture', 110), ('enc', 132, 106), ('latent', 100), ('dec', 132, 106), ('picture', 110)], name='g2a')
    l += c + lock(xs[1], y1 - 80, 1.15) + lock(xs[3], y1 - 80, 1.15) + T(xs[1], y1 + 90, 'encode', 22, None, SOFT, 'middle') + T(xs[3], y1 + 90, 'decode', 22, None, SOFT, 'middle')
    y2 = 428
    l += badge(17, 326, 2) + T(46, 334, '굳은 latent 위에 생성 모델 학습', 24, 650)
    c, xs = chain(y2, [('prior', 104), ('model', 224, 88, '생성 모델'), ('latent', 100)], 0, 560, 'arb', 'g2b')
    l += c + T(xs[1], y2 + 74, 'prior를 굳은 latent로 transport', 22, None, SOFT, 'middle')
    hl = fx(0, 536, 798, 124, ['<b style="color:#1D3A5F;font-weight:700">representation이 먼저 정해지고</b>', '<b style="color:#1D3A5F;font-weight:700">생성 모델은 그 위에서 배움</b>'], 26)
    r = lane(0, 24, '제안은 한 loss로 함께') + T(0, 70, '처음부터 세 모델을 joint training', 24, 650)
    c, xs = chain(y1, [('picture', 110), ('enc', 132, 106), ('latent', 100), ('dec', 132, 106), ('picture', 110)], name='g2c')
    r += c + arrow(xs[2], 342, xs[2], 234, 'arb') + model_box(xs[2], 384, 224, 84, '생성 모델')
    r += curve(f'M{xs[1]} 534 L{xs[1]} 282', 'grad') + curve(f'M{xs[2] - 60} 534 L{xs[2] - 60} 430', 'grad') + curve(f'M{xs[3]} 534 L{xs[3]} 282', 'grad')
    r += T(xs[3] + 12, 404, 'gradient', 22, 600, BLUE) + T(xs[2] + 12, 300, 'transport', 22, 600, BLUE)
    hr = fx(0, 536, 798, 124, [r'한 loss $=$ reconstruction $+$ latent 맞추기', '세 모델이 같은 loss로 움직임'], 26, 'box blue')
    return slide('예시', '예시 · 두 패널의 사슬', '먼저 굳히는 습관과 jointly 학습하는 제안', [panel(*L2, l, hl), panel(*R2, r, hr)],
                 '<b>representation과 생성 모델</b>을 한 loss로 묶는 것이 제안', CITE, notes('사슬 두 줄과 gradient를 보여 주는 장입니다.'))


def g3_table():
    """A table of approaches: a small drawing per row, the idea, the catch, checks in three columns, this paper's row tinted."""
    cols, y0, rh = [1290, 1430, 1570], 46, 154
    s = T(190, 28, '갈래', 24, 650, SOFT) + T(445, 28, '맞는 생각', 24, 650, SOFT) + T(830, 28, '그러나', 24, 650, RED)
    for cx, lab in zip(cols, ['조건 하나', '조건 둘', '조건 셋']):
        s += T(cx, 28, lab, 24, 650, SOFT, 'middle')
    rows = [('첫째 갈래', '방법 A', ['encode한 공간에서', '모델을 학습'], ['앞단이 고정이라', 'representation이 움직이지 않음'], (0, 1, 0)),
            ('둘째 갈래', '방법 B · 방법 C', ['representation과 모델을', '한 틀에서 학습'], ['단순한 prior에 묶임'], (0, 1, 1)),
            ('셋째 갈래', '방법 D', ['어떤 두 분포든', '잇는 유연한 틀'], ['양 끝 sample이 보여야 함'], (1, 0, 0))]
    for i, (name, sub, good, but, marks) in enumerate(rows):
        cy = y0 + i * rh + rh / 2
        s += line(0, y0 + i * rh, 1660, y0 + i * rh, '#E3E7EB', 2) + T(190, cy - 6, name, 26, 700) + T(190, cy + 26, sub, 22, None, SOFT)
        s += lines(445, cy - 6, good, 24, 34) + lines(830, cy - (6 if len(but) == 2 else -8), but, 24, 34)
        s += ''.join(check_mark(cx, cy, bool(m)) for cx, m in zip(cols, marks))
    c0, c1, c2 = y0 + rh / 2, y0 + rh * 1.5, y0 + rh * 2.5
    s += enc(82, c0 + 10, 112, 86, lab='') + lock(82, c0 - 54, 1.05)
    d = profile_path(profile(gauss1(0, 0.8), -2.6, 2.6, 80), (10, 160), c1 + 44, 86, vertical=False)
    s += f'<path d="{d}" fill="{AMBER}" fill-opacity=".75" stroke="{AMBERD}" stroke-width="2"/>'
    fr = Frame(36, c2 - 58, 104, 116, (0, 1), (-2.4, 2.4))
    s += ''.join(strand([fr.px(t, v) for t, v in bridge(a, b, 0.9, 30, 11 + k)], NAVY, 1.5, 0.55) for k, (a, b) in enumerate([(-0.8, 1.2), (0.2, -1.2), (0.7, 1.3), (-0.3, -1.3)]))
    s += vprof(F.p0(), -2.4, 2.4, 36, c2 + 58, c2 - 58, -26, AMBER, AMBERD) + vprof(F.p1(), -2.4, 2.4, 140, c2 + 58, c2 - 58, 26, STEEL, STEELD)
    y = y0 + 3 * rh
    c3 = y + (682 - y) / 2 - 2
    s = rect(0, y + 4, 1660, 682 - y - 8, 14, '#EEF3FA', 'none', 0) + s
    s += enc(34, c3, 52, 62, lab='') + model_box(90, c3, 46, 62, '') + dec(146, c3, 52, 62, lab='')
    s += T(190, c3 - 6, '이 논문', 26, 700, NAVY) + lines(445, c3 - 6, ['임의의 prior에서 출발해', '세 모델을 하나의 loss로 학습'], 24, 34, 650, NAVY)
    s += ''.join(check_mark(cx, c3, True) for cx in cols)
    return slide('예시', '예시 · 앞선 갈래들', '맞는 생각이었지만 저마다 빈칸을 남긴 세 갈래', [panel(*FULL, s)],
                 '세 칸을 다 채우는 이 논문의 출발점은 <b>셋째 갈래</b>', CITE, notes('체크 표는 발표자 정리입니다.'))


def g4_hero():
    """The hero: one big picture fills the panel, the key equation under it, one line on each side of the strip."""
    x0, x1, y0, y1 = 300, 1360, 58, 420
    fr, s = hero_bridge('g4', F, x0, x1, y0, y1, bulge=170, n=9, seed=7)
    mid = (x0 + x1) / 2
    h = tex(x0 - 150, 34, r'$x_0\sim p_0$ prior', 26, 700, AMBERD) + tex(x1 + 150, 34, r'$x_1\sim p_1$ 데이터', 26, 700, STEELD, 'end')
    h += tex(x0, y1 + 52, '$t=0$', 24, 600, None, 'middle') + tex(x1, y1 + 52, '$t=1$', 24, 600, None, 'middle')
    h += tex(mid, y1 + 54, r'$t=\frac{1}{2}$에서 noise 폭 $\sqrt{t(1-t)}$ 최대', 24, 600, None, 'middle')
    h += fx(190, 494, 1280, 76, [r'$x_t=(1-t)\,x_0+t\,x_1+\sqrt{t(1-t)}\,\epsilon,\quad \epsilon\sim\mathcal{N}(0,I)$'], 30, 'box blue')
    s += lines(190, 620, ['이동 방향을 least squares로 배워', '시작 sample을 데이터 sample로 transport'], 24, 34, 600)
    s += lines(1470, 620, ['단, 양 끝 sample이', '둘 다 관측되어야 함'], 26, 34, 700, RED, 'end')
    return slide('예시', '예시 · 큰 그림 하나', '두 분포를 noise 섞인 trajectory로 잇는 방법', [panel(*FULL, s, h)],
                 '양 끝 sample이 보여야만 놓을 수 있는 <b>trajectory</b>', CITE + ' · density와 경로는 예시 분포에서 계산', notes('density와 경로는 예시 분포에서 계산한 모식입니다.'))


def g5_mechanism():
    """A mechanism on one panel: the field joins the two distributions, sampling runs below it, training above it, and the loss strip sends a gradient arrow back into every model."""
    cy = 196
    s = lane(0, 24, '학습은 위쪽 길, 생성은 아래쪽 길')
    s += dens('g5-z0', gaussian((0, 0), (0.85, 0.85)), 6, cy - 82, 164, 164, tint=AMBER, n=44, seed=5)
    Fm = Field(0.62, BIMODAL, sig=0.85)
    fr, img = field('g5', Fm, 170, cy - 78, 672, 156, fade=0.08)
    paths, _ = strands(fr, Fm, 6, 12)
    s += img + paths
    s += dens('g5-z1', gmm([(0.34, (-0.95, 0.8), (0.34, 0.3)), (0.36, (1.0, 0.45), (0.36, 0.34)), (0.3, (0.0, -1.1), (0.36, 0.3))]), 842, cy - 82, 164, 164, tint=STEEL, n=44, seed=6)
    s += picture(1490, cy - 82, 164)
    ey, dy = 78, 360
    s += enc(1250, ey, 180, 112, lab='encoder', size=26) + qarrow(1508, cy - 86, 1470, ey, 1346, ey) + qarrow(1156, ey, 1040, ey, 972, cy - 58)
    s += model_box(506, 384, 340, 92, '생성 모델', 28)
    s += qarrow(88, cy + 72, 96, 384, 330, 384, 'arb') + qarrow(682, 384, 900, 384, 920, cy + 66, 'arb')
    s += dec(1250, dy, 180, 112, lab='decoder', size=26) + qarrow(972, cy + 66, 1040, dy, 1156, dy) + qarrow(1346, dy, 1470, dy, 1508, cy + 86)
    zx, zy = fr.px(0.5, 0.15)
    s += arrow(zx, zy + 8, zx, 334, 'arb') + circle(zx, zy, 8, NAVY, '#fff', 2.5)
    s += curve('M506 504 L506 434', 'grad') + curve('M1250 504 L1250 420', 'grad') + qarrow(1086, 504, 1096, 200, 1190, 138, 'grad') + T(1110, 470, 'gradient', 24, 650, BLUE)
    h = tex(88, cy - 94, '$z_0$', 26, 700, AMBERD, 'middle') + tex(924, cy - 94, '$z_1$', 26, 700, STEELD, 'middle') + tex(506, cy - 94, r'bridge에서 $z_t$를 바로 뽑기', 25, 650, NAVY, 'middle')
    h += tex(zx + 14, 324, r'$z_t,\ t$', 25, 650, NAVY) + tex(1572, cy - 94, '이미지', 26, 700, None, 'middle')
    h += tex(790, 432, '여러 step', 24, 600, BLUE, 'middle') + tex(214, 432, r'$z_0$ 뽑기', 24, 600, BLUE, 'middle')
    h += tex(1360, 56, 'encode', 24, 600) + tex(1360, 412, 'decode', 24, 600)
    h += fx(150, 508, 1360, 152, [r'$\E\Big[\underbrace{-\ln p(x|z)}_{\text{reconstruction}}+\frac{\beta}{2}\underbrace{\big\|z_1-z_0-h(z_t,t)\big\|^2}_{\text{latent 맞추기}}\Big]$'], 30, 'box blue')
    return slide('예시', '예시 · 기전 한 장', '세 모델을 한 loss로 묶는 기전', [panel(*FULL, s, h)],
                 '세 모델이 한 loss를 나눠 갖는 열쇠는 바로 뽑는 <b>$z_t$</b>', CITE + ' · density와 경로는 모식', notes('파란 점선은 gradient가 흐르는 곳입니다. loss에서 세 모델 모두로 갑니다.'))


def g6_bars():
    """Two charts: wide bars, bold values, a legend under the lane header; the number the slide is about is the largest thing on the panel."""
    l = lane(0, 24, '품질은 세 크기에서 비슷함') + legend(0, 70, [('이 모델', BLUE), ('기준 모델', '#C5CDD5')])
    b, h = bars(30, 790, 620, 130, [('$64^2$', (2.6, 2.5)), ('$128^2$', (3.1, 3.5)), ('$256^2$', (3.9, 3.8))], 4.2, fmt='{:.1f}')
    l += b
    h += tex(798, 24, '낮을수록 좋음', 22, 500, MUTED, 'end')
    r = lane(0, 24, '한 step 계산량은 이 모델이 작음') + legend(0, 70, [('이 모델', BLUE), ('기준 모델', '#C5CDD5')])
    b2, h2 = bars(140, 790, 470, 110, [('$64^2$', (160, 200)), ('$128^2$', (330, 470)), ('$256^2$', (450, 1290))], 1290, val_size=28)
    r += b2 + line(0, 596, 798, 596, '#E3E7EB', 2) + T(0, 650, '백 step 절감', 23, 600, SOFT)
    r += big(465, 652, '30%') + big(682, 652, '65%')
    return slide('예시', '예시 · 막대 두 장', '비슷한 품질에 한 step이 더 가벼운 모델', [panel(*L2, l, h), panel(*R2, r, h2)],
                 '가장 큰 크기에서 백 step이면 <b>65% 절감</b>', CITE, notes('막대는 숫자로 그리고 값을 바로 위에 적습니다.'))


def g7_lines():
    """Line charts: thick line, one point picked out, a dashed baseline with its value on the chart, the gain written next to the arrow."""
    x0, x1, y0, y1 = 70, 790, 64, 604
    xs = [-6, -5, -4, -3]
    px = lambda b: x0 + (b + 6.42) / 4.22 * (x1 - x0)
    py = lambda v: y1 - (v - 3.4) / 3.0 * (y1 - y0)
    l = line(x0, y1, x1, y1, GRAY, 2) + line(x0, y0, x0, y1, GRAY, 2)
    h = tex(0, 24, r'$\beta$를 키울 때의 품질', 24, 650, SOFT) + tex(798, 24, '낮을수록 좋음', 22, 500, MUTED, 'end')
    for b in xs:
        l += line(px(b), y1, px(b), y1 + 9, GRAY, 2)
        h += tex(px(b), y1 + 44, f'$10^{{{b}}}$', 24, 600, None, 'middle')
    for v in (4, 5, 6):
        l += line(x0 - 8, py(v), x0, py(v), GRAY, 2) + T(x0 - 14, py(v) + 8, str(v), 22, None, SOFT, 'end')
    l += line(x0, py(4.5), x1, py(4.5), SOFT, 2.4, '9 7')
    h += tex(x0 + 12, py(4.5) - 12, '기준 <b>4.5</b>', 25, 650, SOFT)
    pts = [(px(b), py(v)) for b, v in zip(xs, (4.3, 3.9, 3.7, 6.0))]
    l += strand(pts, BLUE, 4, 1)
    for k, (x, y) in enumerate(pts):
        l += circle(x, y, 11 if k == 2 else 8, BLUE, '#fff', 2.5)
    l += T(pts[0][0], pts[0][1] + 38, '4.3', 26, 650, None, 'middle') + T(pts[1][0], pts[1][1] + 38, '3.9', 26, 650, None, 'middle') + T(pts[3][0] - 18, pts[3][1] + 8, '6.0', 26, 650, None, 'end')
    l += big(pts[2][0] + 22, pts[2][1] + 16, '3.7', 40, BLUE, None) + arrow(pts[2][0], py(4.5) + 6, pts[2][0], pts[2][1] - 18, 'arb', 3)
    h += tex(pts[2][0] - 14, py(4.2), '약 17% 개선', 27, 750, BLUE, 'end')
    r = lane(0, 24, '같은 축의 reconstruction 품질')
    h2 = tex(798, 24, '높을수록 좋음', 22, 500, MUTED, 'end')
    py2 = lambda v: y1 - (v - 39.1) / 3.2 * (y1 - y0)
    r += line(x0, y1, x1, y1, GRAY, 2) + line(x0, y0, x0, y1, GRAY, 2)
    for b in xs:
        r += line(px(b), y1, px(b), y1 + 9, GRAY, 2)
        h2 += tex(px(b), y1 + 44, f'$10^{{{b}}}$', 24, 600, None, 'middle')
    for v in (40, 41, 42):
        r += line(x0 - 8, py2(v), x0, py2(v), GRAY, 2) + T(x0 - 14, py2(v) + 8, str(v), 22, None, SOFT, 'end')
    pts2 = [(px(b), py2(v)) for b, v in zip(xs, (41.8, 41.8, 41.0, 39.6))]
    r += strand(pts2, CORAL, 4, 1)
    for (x, y), v in zip(pts2, (41.8, 41.8, 41.0, 39.6)):
        r += circle(x, y, 8, CORAL, '#fff', 2.5) + T(x + 16, y - 16, f'{v:.1f}', 26, 650)
    r += lines(x0 + 30, py2(40.3), ['너무 큰 값에서는', 'reconstruction이 무너지고 품질도 나빠짐'], 25, 36, 650, '#B4492F')
    return slide('예시', '예시 · 선 두 장', 'jointly 학습하면 품질이 좋아지는 구간', [panel(*L2, l, h), panel(*R2, r, h2)],
                 '이 모델에서 representation이 생성 과정에 맞춰 바뀌면 <b>약 17% 개선</b>', CITE, notes('곡선은 숫자로 그리고 핵심 점만 크게 표시합니다.'))


def g8_closing():
    """The closing: four findings, each with a tiny drawing, on the left; the questions on the right are the presenter's slot."""
    l = lane(0, 24, '논문이 보여 준 것')
    ys = [50, 204, 358, 512]
    rows = [('한 loss로 세 모델을 함께', 'encoder, decoder, 생성 모델'), ('비슷한 품질에 더 가벼운 step', '가장 큰 크기에서 65% 절감'), ('joint training이 separate training보다 좋음', '4.5에서 3.7로'), ('prior와 sampler의 자유', '여러 분포, guidance, inversion')]
    for y, (a, b) in zip(ys, rows):
        l += card(0, y, 798, 146) + T(216, y + 65, a, 27, 700) + T(216, y + 101, b, 24, None, SOFT)
    c = ys[0] + 73
    l += enc(40, c, 56, 62, lab='') + model_box(100, c, 48, 62, '') + dec(160, c, 56, 62, lab='')
    c = ys[1] + 73
    l += rect(62, c - 22, 40, 54, 4, BLUE, 'none', 0) + rect(112, c - 48, 40, 80, 4, '#C5CDD5', 'none', 0)
    c = ys[2] + 73
    l += strand([(40, c - 22), (84, c + 2), (128, c + 14), (172, c + 18)], BLUE, 4, 1) + strand([(40, c - 28), (172, c - 28)], SOFT, 2.4, 1, '8 6')
    c = ys[3] + 73
    l += vprof(gauss1(0, 0.8), -2.4, 2.4, 100, c + 44, c - 44, -44, AMBER, AMBERD)
    r = lane(0, 24, '우리에게 던지는 질문')
    for i, q in enumerate((['우리 모델의 representation은', '생성 모델보다 먼저 굳어 있는가'], ['noise와 크기를', '우리는 어떻게 정해 왔는가'], ['prior를 고를 수 있다면', '어떤 선택지가 있는가'])):
        cy = 162 + i * 226
        r += circle(44, cy, 26, NAVY) + T(44, cy + 11, str(i + 1), 30, 700, '#fff', 'middle') + lines(96, cy - 8, q, 32, 46, 700, NAVY)
    return slide('예시', '예시 · 정리와 질문', 'jointly 학습하는 것이 우리에게 주는 뜻', [panel(*L2, l), panel(*R2, r)],
                 '우리 representation에도 <b>누가 먼저 굳었나</b> 묻기', CITE, notes('오른쪽은 발표자가 발표마다 직접 쓰는 자리입니다.'))


def g9_causal():
    """A causal story in three cells on one panel: the same graph, a small plot of what each agent sees, and the outcome at the end of the chain."""
    rng = random.Random(4)
    cxs, py, ph, pw = (260, 830, 1400), 316, 146, 340
    s = lane(cxs[0] - 260, 24, '보이는 상관은 속일 수 있음') + lane(cxs[1] - 260, 24, '상관을 인과로 읽은 쪽') + lane(cxs[2] - 260, 24, '직접 바꿔 본 쪽')
    cx = cxs[0]
    s += node(cx, 104, 'U', 38, hidden=True) + T(cx + 50, 113, '숨은 원인', 24, 600, SOFT) + node(cx - 170, 250, 'X', 38) + node(cx + 170, 250, 'Y', 38)
    s += edge(cx, 104, cx - 170, 250, 38, 38, GRAY, '7 6') + edge(cx, 104, cx + 170, 250, 38, 38, GRAY, '7 6')
    s += line(cx - 128, 250, cx + 128, 250, RED, 3, '3 7') + T(cx, 236, '상관', 24, 700, RED, 'middle')
    pts = [(t / 26 + 0.02, min(0.97, max(0.04, 0.12 + 0.76 * t / 26 + rng.gauss(0, 0.07)))) for t in range(1, 26)]
    s += plot_axes(cx - pw / 2, py, pw, ph, 'X', 'Y') + dots(pts, cx - pw / 2, py, pw, ph, '#8FA7CF') + fit_line(pts, cx - pw / 2, py, pw, ph, RED, 3, '3 7')
    s += arr(cx, 476, cx, 544, GRAY, 3) + T(cx + 16, 520, '왜?', 24, 700, SOFT) + node(cx, 606, '이유는\n관측 밖', 58, hidden=True)
    cx = cxs[1]
    s += node(cx, 104, 'U', 38, hidden=True) + T(cx + 50, 113, '보지 못함', 24, 600, SOFT) + node(cx - 170, 250, 'X', 38) + node(cx + 170, 250, 'Y', 38)
    s += edge(cx, 104, cx - 170, 250, 38, 38, GHOST, '7 6') + edge(cx, 104, cx + 170, 250, 38, 38, GHOST, '7 6') + edge(cx - 170, 250, cx + 170, 250, 38, 38, RED)
    s += T(cx, 236, '믿음은 X가 Y를 올림', 24, 700, RED, 'middle')
    fx0 = cx - pw / 2
    s += plot_axes(fx0, py, pw, ph, 'X', 'Y') + line(fx0 + 20, py + ph - 26, fx0 + pw - 20, py + 22, GRAY, 2.6, '8 7') + T(fx0 + 40, py + 44, '예측', 24, 600, SOFT)
    s += line(fx0 + 20, py + ph - 34, fx0 + pw - 20, py + ph - 34, CORAL, 3.4) + ''.join(circle(fx0 + 42 + k * 64, py + ph - 34, 7, CORAL, '#fff', 1.5) for k in range(5))
    s += T(fx0 + pw - 14, py + ph - 50, '실제 Y는 그대로', 24, 700, '#B4492F', 'end') + arr(cx, 476, cx, 544, CORAL, 3) + node(cx, 606, '차선의\n결과', 58, outcome=True)
    cx = cxs[2]
    s += node(cx, 104, 'U', 38, stroke=BLUE) + T(cx + 50, 113, '원인을 찾음', 24, 700, BLUE) + node(cx - 170, 250, 'X', 38) + node(cx + 170, 250, 'Y', 38)
    s += edge(cx, 104, cx - 170, 250, 38, 38, GHOST, '7 6') + edge(cx, 104, cx + 170, 250, 38, 38, BLUE, None, 3) + T(cx + 100, 172, 'Y를 결정', 24, 700, BLUE)
    fx0 = cx - pw / 2
    s += plot_axes(fx0, py, pw, ph, '', 'Y')
    for k, (lab, hh, col) in enumerate((('X 낮춤', 50, BAR_OTHER), ('X 올림', 50, BAR_OTHER), ('원인 조정', 126, BLUE))):
        bx = fx0 + 16 + k * 110
        s += rect(bx, py + ph - hh, 88, hh, 3, col, 'none', 0) + T(bx + 44, py + ph + 30, lab, 24, 700 if k == 2 else 500, BLUE if k == 2 else SOFT, 'middle')
    s += arr(cx + 110, 504, cx + 46, 562, BLUE, 3) + node(cx, 606, '훨씬 나은\n결과', 58, outcome=True)
    return slide('예시', '예시 · 인과 그래프 세 칸', '같은 상관을 보고 갈리는 두 판단', [panel(*FULL, s)], '보기만 한 쪽은 속고 <b>손대 본 쪽</b>은 기전을 찾음', CITE + ' · 작은 차트 셋은 모식', notes('같은 그래프를 세 칸에 반복하고 달라지는 것만 색으로 표시합니다.'))


def g10_matrix():
    """A comparison table of dots: one dot per item, filled when it has the property; the last row and last column tinted so the empty cell is the message."""
    rows = [('첫째 분류', '예시 3개', [(1, 0, 0, 0, 1, 0), (1, 0, 0, 0, 1, 0), (1, 0, 0, 0, 1, 0)]), ('둘째 분류', '예시 5개', [(1, 0, 1, 0, 0, 0), (1, 0, 1, 0, 0, 0), (1, 0, 0, 0, 0, 0), (1, 0, 0, 1, 0, 0), (1, 0, 1, 0, 1, 0)]),
            ('셋째 분류', '예시 4개', [(0, 1, 1, 1, 0, 0), (0, 0, 1, 1, 0, 0), (1, 1, 1, 1, 0, 0), (0, 1, 1, 1, 0, 0)]), ('넷째 분류', '예시 1개', [(1, 0, 0, 1, 0, 0)]), ('이 논문', '제안', [(1, 1, 1, 1, 1, 1)])]
    heads = ['자동 채점', '실험 설계', '재시도', '인과 관계', '설명 채점', '세 왜곡']
    y0, rh, colx = 54, 113, [540, 740, 940, 1140, 1340, 1560]
    bottom = y0 + rh * len(rows)
    s = rect(colx[5] - 100, 2, 200, bottom - 2, 0, '#EEF2F7', 'none', 0) + rect(0, bottom - rh, colx[5] - 100, rh, 0, '#EEF2F7', 'none', 0) + T(10, 36, '분류', 24, 650, SOFT)
    for i, h in enumerate(heads):
        s += T(colx[i], 36, h, 26 if i == 5 else 24, 700 if i == 5 else 650, NAVY if i == 5 else SOFT, 'middle')
    s += line(0, y0, 1660, y0, GHOST, 2)
    for r, (grp, sub, flags) in enumerate(rows):
        yy, last = y0 + r * rh, r == len(rows) - 1
        s += line(0, yy, 1660, yy, '#D9DEE3', 1.5) if r else ''
        s += T(10, yy + 50, grp, 30 if last else 28, 800 if last else 700, NAVY if last else None) + T(10, yy + 86, sub, 24, 500, SOFT)
        for i, cx in enumerate(colx):
            for k, fl in enumerate(flags):
                dx, cy = cx + (k - (len(flags) - 1) / 2) * 34, yy + rh / 2
                s += circle(dx, cy, 13, NAVY) if last else circle(dx, cy, 13, BLUE) if fl[i] else circle(dx, cy, 12, '#fff', GHOST, 2)
    s += line(0, bottom, 1660, bottom, GHOST, 2) + circle(20, bottom + 28, 13, BLUE) + T(44, bottom + 37, '갖춤', 24, 500, SOFT) + circle(130, bottom + 28, 12, '#fff', GHOST, 2) + T(154, bottom + 37, '없음', 24, 500, SOFT) + T(250, bottom + 37, '원 1개 = 방법 1개', 24, 500, SOFT)
    return slide('예시', '예시 · 점 행렬', '맞는 방향이지만 마지막 칸은 비어 있는 방법들', [panel(*FULL, s)], '여섯 칸을 다 채운 것은 <b>하나</b>', CITE, notes('한 점이 한 방법입니다. 빈 칸이 이 장의 말입니다.'))


def g11_rank():
    """Thirty items ranked as dots on one axis: only the best and the worst are named, the threshold and the target band sit on the axis, an arrow names the gap."""
    vals = [68.0, 67.8, 67.8, 66.9, 66.8, 66.5, 65.4, 65.4, 65.0, 64.6, 64.5, 64.4, 64.1, 63.4, 63.2, 62.3, 62.0, 61.5, 61.0, 60.4, 59.1, 59.0, 58.7, 58.2, 58.2, 57.6, 57.3, 56.0, 53.0, 48.5]
    y0, rh, axis_y = 72, 18.4, 640
    xv = lambda v: 40 + (v - 45) * 40.5
    s = lane(0, 28, '여러 번 실행한 평균 score (%)') + rect(xv(78), 44, xv(85) - xv(78), axis_y - 45, 0, '#E3EAF4', 'none', 0) + line(xv(75), 44, xv(75), axis_y, SOFT, 2.4, '7 6')
    s += T(xv(75) - 8, 32, '기준 75%', 24, 600, SOFT, 'end') + T(xv(78), 34, '이론 최적 78–85%', 30, 700, NAVY) + line(xv(45), axis_y, xv(85), axis_y, SOFT, 2)
    for v in (50, 60, 70, 80):
        s += line(xv(v), axis_y, xv(v), axis_y + 7, SOFT, 2) + T(xv(v), axis_y + 29, str(v), 22, 500, SOFT, 'middle')
    for i, v in enumerate(vals):
        s += circle(xv(v), y0 + i * rh + rh / 2, 11 if i == 0 else 8, NAVY if i == 0 else '#8FA7CF')
    s += T(xv(68) - 18, y0 + rh / 2 + 13, '68.0', 38, 700, NAVY, 'end') + T(xv(68) - 118, y0 + rh / 2 + 9, '가장 높은 모델', 24, 700, NAVY, 'end')
    s += T(xv(48.5) + 34, y0 + 29 * rh + rh / 2 + 9, '48.5', 24, 700, SOFT) + T(xv(48.5) + 98, y0 + 29 * rh + rh / 2 + 9, '가장 낮은 모델', 24, 500)
    cy = y0 + rh / 2
    s += arr(xv(68) + 14, cy, xv(78), cy, RED, 2.6, None, 13) + T((xv(68) + xv(75)) / 2, cy - 12, '남은 격차', 26, 700, RED, 'middle')
    s += T(0, 232, '점 하나가 모델 하나', 26, 700) + T(xv(75) - 20, 506, '평균은 모두 기준 아래', 26, 700, None, 'end')
    return slide('예시', '예시 · 순위 점 그림', '평균으로는 30개 모델 모두 기준 아래', [panel(*FULL, s)], '가장 높은 모델도 <b>68.0</b>에서 멈춤', CITE, notes('이름은 처음과 끝에만 적고 나머지 값은 노트로 보냅니다.'))


def g12_tiers():
    """Lines across tiers with the band that matters tinted: the line of the claim thick and labelled at both ends, the others thin and named once."""
    top, bot, xs, names = 96, 590, [130, 270, 410, 550, 690], ['~50', '50–68', '68–75', '75–82', '82~']
    sv = lambda v: bot - v * (bot - top)
    def base(th=480):
        o = rect(th, top, 798 - th, bot - top, 0, '#EEF2F7', 'none', 0) + T(600, top + 36, '이긴 구간', 24, 700, NAVY) + line(th, top - 4, th, bot, SOFT, 2, '7 6') + T(th, top - 12, '기준 75%', 24, 600, SOFT, 'middle')
        o += line(56, top, 798, top, NAVY, 2, '7 6') + T(64, top - 12, '만점 1.0', 24, 700, NAVY) + line(56, bot, 798, bot, SOFT, 2) + line(56, top, 56, bot, SOFT, 2)
        for v in (0, 0.5, 1.0):
            o += T(46, sv(v) + 8, f'{v:.1f}' if v else '0', 24, 500, SOFT, 'end')
        for x, n in zip(xs, names):
            o += T(x, bot + 34, n, 24, 500, SOFT, 'middle')
        return o + T(798, bot + 70, 'score 구간 (%)', 24, 500, SOFT, 'end')
    def series(vals, col, sw, r):
        return strand([(x, sv(v)) for x, v in zip(xs, vals)], col, sw, 1) + ''.join(circle(x, sv(v), r, col, '#fff', 1.5) for x, v in zip(xs, vals))
    l = lane(0, 24, '첫째 경우는 오르지만 만점과 먼 거리') + base() + series((0.2, 0.3, 0.25, 0.27, 0.26), '#9FB3D1', 2.6, 5) + series((0.53, 0.5, 0.5, 0.35, 0.09), CORAL, 3.4, 8) + series((0.05, 0.1, 0.2, 0.3, 0.42), BLUE, 4, 9)
    l += T(xs[0], sv(0.05) - 22, '0.05', 30, 700, BLUE, 'middle') + T(xs[4] + 14, sv(0.42) - 4, '0.42', 30, 700, BLUE) + T(xs[4] + 14, sv(0.09) + 11, '0.09', 30, 700, '#B4492F') + T(xs[1] + 14, sv(0.5) - 22, '자기 점검', 24, 700, '#B4492F', 'middle')
    r = lane(0, 24, '둘째 경우는 모든 구간 바닥 근처') + base() + series((0.3, 0.32, 0.3, 0.28, 0.3), '#9FB3D1', 2.6, 5) + series((0.45, 0.4, 0.42, 0.5, 0.44), CORAL, 3.4, 8) + series((0.04, 0.05, 0.05, 0.06, 0.05), BLUE, 4, 9)
    r += T(xs[4] + 14, sv(0.05) + 11, '0.05', 30, 700, BLUE) + T(xs[2], sv(0.42) - 22, '자기 점검', 24, 700, '#B4492F', 'middle')
    return slide('예시', '예시 · 구간 강조 선 그래프', '이겼다고 이유를 짚은 것은 아님', [panel(*L2, l), panel(*R2, r)], '구간이 올라가도 굵은 선은 <b>만점과 먼 거리</b>', CITE, notes('주장의 선 하나만 굵게 그리고 값은 양 끝에만 적습니다.'))


def g13_boxes():
    """Box plots on a shared scale: a zero line, direction words on the axis, the means as the largest numbers on the panel."""
    gy = lambda v: 418 - 14.2 * v
    def axis(x0):
        o = line(x0, gy(0), 798, gy(0), SOFT, 2.4)
        for v, lab in ((20, '+20'), (10, '+10'), (0, '0'), (-10, '−10')):
            o += T(x0 - 8, gy(v) + 8, lab, 24, 500, SOFT, 'end')
        return o
    l = lane(0, 24, '설명을 맞힌 경우의 격차가 더 작음') + axis(216) + T(0, gy(14), '↑ 나빠짐', 24, 700, '#B4492F') + T(0, gy(-6), '↓ 오히려 좋아짐', 24, 700, BLUE)
    l += box_stat(320, (-14, -8, -3, 2, 9), gy, BLUE, 96) + box_stat(570, (-8, 0, 4, 10, 20), gy, CORAL, 96)
    l += circle(320, gy(-3), 8, INK, '#fff', 2) + circle(570, gy(4.5), 8, INK, '#fff', 2) + big(388, gy(-3) + 13, '−3.0', 38, BLUE, None) + T(388, gy(-3) + 45, '평균', 24, 500, SOFT) + big(638, gy(4.5) + 13, '+4.5', 38, '#B4492F', None) + T(638, gy(4.5) + 45, '평균', 24, 500, SOFT)
    l += T(320, 664, '맞힌 경우', 26, 700, BLUE, 'middle') + T(570, 664, '못 맞힌 경우', 26, 700, '#B4492F', 'middle')
    r = lane(0, 24, '다른 세 항목은 뚜렷한 차이 없음') + axis(70) + rect(290, 46, 24, 24, 4, BLUE, 'none', 0) + T(322, 66, '채운 경우', 24, 500, SOFT) + rect(444, 46, 24, 24, 4, CORAL, 'none', 0) + T(476, 66, '못 채운 경우', 24, 500, SOFT)
    for name, c, a, b in (('항목 하나', 200, (-10, -3, 2, 7, 15), (-9, -2, 3, 8, 16)), ('항목 둘', 440, (-11, -4, 1, 6, 14), (-10, -2, 2, 7, 15)), ('항목 셋', 680, (-9, -2, 3, 8, 17), (-10, -3, 2, 8, 16))):
        r += box_stat(c - 42, a, gy, BLUE, 64) + box_stat(c + 42, b, gy, CORAL, 64) + T(c, 664, name, 26, 700, None, 'middle')
    return slide('예시', '예시 · 상자 그림', '설명을 맞힌 경우에 더 작았던 격차', [panel(*L2, l), panel(*R2, r)], '평균 격차 <b>+4.5</b>와 <b>−3.0</b>', CITE, notes('같은 눈금을 두 패널이 나눠 씁니다. 평균이 패널에서 가장 큰 글자입니다.'))


def g14_cards():
    """Six small charts of one kind, one on each white card: a small multiple is the one place a chart takes a card. Name and formula on top, a gray filled base, one thick curve for what changes."""
    base = mixture1([(0.42, -1.5, 0.42), (0.36, 0.25, 0.38), (0.22, 1.7, 0.36)])
    grid = [-3.2 + 6.4 * i / 150 for i in range(151)]
    top = max(base(v) for v in grid)

    def chart(cell, name, form, warp, second=None):
        x, y, w, h = cell
        iw, ih = w - 40, h - 40
        bx0, bx1, by0, by1 = 10, iw - 10, 92, ih - 4
        X = lambda v: bx0 + (v + 3.2) / 6.4 * (bx1 - bx0)
        Y = lambda p: by1 - p * (by1 - by0)
        tilt = [warp(v, base(v) / top) for v in grid]
        mx = max(tilt) or 1
        b = [(X(v), Y(0.5 * base(v) / top)) for v in grid]
        area = 'M' + ' L'.join(f'{px:.1f} {py:.1f}' for px, py in b) + f' L{X(3.2):.1f} {by1:.1f} L{X(-3.2):.1f} {by1:.1f} Z'
        s = T(0, 28, name, 26, 700) + f'<path d="{area}" fill="#DAD8D2" stroke="{MUTED}" stroke-width="2"/>'
        if second:
            s += strand([(X(v), Y(0.5 * second(v))) for v in grid], MUTED, 2.2, 1, '7 6')
        s += strand([(X(v), Y(q / mx)) for v, q in zip(grid, tilt)], CORAL, 4.5, 1) + line(bx0, by1, bx1, by1, MUTED, 2)
        return panel(x, y, w, h, s, tex(0, 66, form, 24, 500, SOFT), 'panel card')

    H = 349
    r2 = 176 + H + 24
    gg = gauss1(1.7, 0.45)
    cells = [(110, 176, 550, H), (684, 176, 552, H), (1260, 176, 550, H), (110, r2, 550, H), (684, r2, 552, H), (1260, r2, 550, H)]
    specs = [('변환 하나', r'$q \propto p^{\beta},\ \beta = 3$', lambda v, p: p ** 3, None),
             ('변환 둘', r'$q \propto p_1\, p_2$', lambda v, p: p * gauss1(0.6, 1.1)(v), gauss1(0.6, 1.1)),
             ('변환 셋', r'$q \propto p\, e^{r}$', lambda v, p: p * 2.718 ** (1.1 * v), None),
             ('변환 넷', r'$q \propto p\, p(y|x)$', lambda v, p: p * gauss1(0.3, 0.5)(v), gauss1(0.3, 0.5)),
             ('변환 다섯', r'$q \propto p_c^{w}\, p^{1-w}$', lambda v, p: p ** 0.5 * gg(v), gg),
             ('변환 여섯', r'$q \propto p\cdot 1_A$', lambda v, p: p if v > 0.9 else 0.0, None)]
    panels = [chart(c, *sp) for c, sp in zip(cells, specs)]
    return slide('예시', '예시 · 흰 카드 여섯 장', '다시 학습하지 않고 sample 분포를 바꾸는 여섯 가지 변환', panels,
                 '같은 base model에서 <b>sampling</b>만 바꿔 여섯 target', CITE + ' · 곡선은 예시 분포에서 계산', notes('작은 차트 여러 개만 흰 카드에 하나씩 담습니다. 큰 그림 하나는 카드에 넣지 않습니다.'))


def g15_derivation():
    """A derivation: the formulas are the content. One table row per step, one relation on each line, the result on the key-equation card, and beside it a picture of what the result means. Never a chain of boxes holding step names."""
    theta, sig, z0 = 1.6, 1.3, 1.7
    fr = Frame(40, 92, 560, 396, (0, 1), (-3.4, 3.2))
    sd = lambda t: sig * math.sqrt((1 - math.exp(-2 * theta * t)) / (2 * theta))
    mean = lambda t: z0 * math.exp(-theta * t)
    l = lane(0, 24, '어느 시점이든 바로 뽑는 sample')
    for k, end in enumerate((1.1, 0.2, -0.8)):
        l += strand([fr.px(t, v) for t, v in bridge(z0, end, 0.8, 40, 40 + k)], GRAYL, 2, 1)
    l += strand([fr.px(i / 40, mean(i / 40)) for i in range(41)], NAVY, 3, 1, '10 8')
    h = tex(40, fr.px(0, z0)[1] - 38, r'$z_0$', 26, 700, AMBERD, 'middle') + tex(320, 80, r'mean은 $e^{-\theta t} z_0$로 감소', 24, 650, NAVY, 'middle')
    for t, draw in ((0.25, 0.9), (0.5, -0.8), (0.75, 0.6)):
        x, m, s_ = fr.px(t, 0)[0], mean(t), sd(t)
        l += vprof(gauss1(m, s_), m - 2.6 * s_, m + 2.6 * s_, x, fr.px(t, m - 2.6 * s_)[1], fr.px(t, m + 2.6 * s_)[1], 52, '#DCE6F5', BLUE, 0.9)
        l += circle(x, fr.px(t, m + draw * s_)[1], 9, RED, '#fff', 2) + line(x, 500, x, 512, GRAY, 2)
        h += tex(x, 548, f'$t = {t:g}$', 22, 600, SOFT, 'middle')
    l += line(40, 506, 600, 506, GRAY, 2) + circle(*fr.px(0, z0), 15, '#F8E3BF', AMBERD, 2.6)
    h += tex(320, 592, r'폭은 $s_t$, $t$와 함께 증가', 24, 650, BLUE, 'middle') + fx(0, 610, 624, 50, ['어느 $t$든 Gaussian에서 한 번에 뽑음'], 24)
    rows = [(r'$dz_t = -\theta\,z_t\,dt + \sigma\,dw_t$', 'linear drift와 additive noise'),
            (r'$z_t\,|\,z_0 \sim \mathcal N\big(e^{-\theta t} z_0,\; s_t^2 I\big)$', 'transition이 Gaussian'),
            (r'$s_t^2 = \frac{\sigma^2}{2\theta}\big(1 - e^{-2\theta t}\big)$', 'variance가 식으로 풀림'),
            (r'$z_t = e^{-\theta t} z_0 + s_t\,\epsilon$', 'noise 하나로 씀')]
    r, hr = derive(rows)
    r = lane(0, 24, 'linear SDE에서 sample 식까지 네 단계') + r + arrow(120, 356, 120, 420)
    hr += tex(140, 396, r'$\epsilon \sim \mathcal N(0, I)$이면 경로를 풀 필요 없음', 26, 700)
    hr += fx(0, 428, 972, 232, [r'$z_t = e^{-\theta t} z_0 + \frac{\sigma}{\sqrt{2\theta}}\sqrt{1 - e^{-2\theta t}}\;\epsilon$', '<span style="color:#1D3A5F;font-weight:700;font-size:26px">한 줄에 한 식, 줄바꿈은 서로 다른 식 사이에서만</span>'], 34, 'box blue')
    return slide('예시', '예시 · 식이 내용인 유도', '식으로 풀리는 transition으로 바로 뽑는 sample', [panel(110, 176, 664, 722, l, h), panel(798, 176, 1012, 722, r, hr)],
                 '경로를 풀지 않아도 <b>어느 $t$든</b> 한 번에 sample', CITE + ' · Ornstein-Uhlenbeck 과정의 교과서 식', notes('유도를 말하는 장은 식이 내용입니다. 단계 이름만 적은 상자로 바꾸지 않습니다. 한 식은 한 줄에 둡니다.'))


if __name__ == '__main__':
    init(sys.argv[1])
    write_deck([g() for g in (g1_cover, g2_two_chains, g3_table, g4_hero, g5_mechanism, g6_bars, g7_lines, g8_closing, g9_causal, g10_matrix, g11_rank, g12_tiers, g13_boxes, g14_cards, g15_derivation)])

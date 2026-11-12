#!/usr/bin/env python3
"""folio_gallery.py — nine worked slides in the Folio layout, drawn with folio_kit.py, with toy content and no paper in them.
Copy a slide's code, keep its sizes and positions, change the content.

usage: folio_gallery.py /abs/deck   (a folder scaffolded by new_deck.py --theme folio). Renders are kept in assets/folio-gallery/ of this skill.
Numbers, names and curves here are invented to show the drawing; nothing on these slides is a result.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from folio_kit import *  # noqa: E402,F403
from folio_kit import BAR_OTHER, INDIGO, INDIGO_FILL, INK, MACH_STROKE, MUTED, NAVY, OCHRE, OCHRE_FILL, OCHRE_MID, OPS_SMALL, PAPER, SOFT, SW, VERM  # noqa: E402

CITE = '예시 내용 · 숫자와 이름은 그리는 법을 보이려고 지어낸 것'
SECTIONS = ['질문', '바탕', '방법', '결과', '정리']
F = Field(0.62, ((0.5, -1.25, 0.32), (0.5, 1.25, 0.32)), 1.0)


def g1_cover():
    """Cover: the title on the left (<em> = the indigo words), one figure on the right-hand plate: a transport between two distributions as stepped level sets, with sample paths."""
    fr = Frame(96, 74, 676, 700, (0.0, 1.0), (-2.7, 2.7))
    s = field_bands(F, fr, 'gCover')
    st, ends = strands(F, fr, 11, seed=3)
    s += st + vprofile(F.p0(), fr, fr.x, -84, OCHRE_FILL, OCHRE) + vprofile(F.p1(), fr, fr.x + fr.w, 84, INDIGO_FILL, INDIGO)
    for x0, x1 in ends:
        s += circle(*fr.px(0, x0), 5, OCHRE, PAPER, 1.5) + circle(*fr.px(1, x1), 5, INDIGO, PAPER, 1.5)
    s += line(fr.x, 804, fr.x + fr.w, 804, MACH_STROKE, 2) + ''.join(line(fr.x + t * fr.w, 804, fr.x + t * fr.w, 814, MACH_STROKE, 2) for t in (0, 0.5, 1))
    h = (tex(fr.x, 46, '$z_0$ prior', 24, 650, OCHRE) + tex(fr.x + fr.w, 46, '$z_1$ latent', 24, 650, INDIGO, 'end')
         + tex(fr.x, 852, '$t = 0$', 24, 500, SOFT) + tex(fr.x + fr.w, 852, '$t = 1$', 24, 500, SOFT, 'end'))
    return cover('예시 논문의<br><em>강조할 말</em><br>제목 셋째 줄', '이 발표가 무엇을 보여 주는지 한 줄', '저자 이름 · 저자 이름 · 소속<br>학회 2026 · arXiv:0000.00000',
                 '논문 세미나 · 발표자', '연구실 세미나 · 날짜', s, h, notes('표지의 그림은 예시 분포에서 계산한 모식입니다.'))


def g2_opener():
    """A section opener: the section number and the one question the section answers, on ink. One per section, or only for the sections that turn the talk."""
    return opener('질문', '두 모델을 처음부터 함께 배울 수는 없는가', notes('절을 여는 장에는 그 절이 답할 질문 한 줄만 둡니다.'))


def g3_concept():
    """A concept on one plate: the (t, x) field between two end distributions, one path picked out in ink, the axis under it and the one formula on a card. recall lists the symbols of this slide."""
    fr = Frame(176, 112, 824, 500, (0.0, 1.0), (-2.7, 2.7))
    s = lane(0, 28, '두 끝이 보이는 trajectory') + field_bands(F, fr, 'gG3')
    st, ends = strands(F, fr, 7, seed=5)
    s += st + polyline([fr.px(t, v) for t, v in bridge(ends[0][0], ends[0][1], F.sig, 64, 500)], INK, 2.8)
    s += vprofile(F.p0(), fr, fr.x, -120, OCHRE_FILL, OCHRE) + vprofile(F.p1(), fr, fr.x + fr.w, 120, INDIGO_FILL, INDIGO)
    for i, (x0, x1) in enumerate(ends):
        s += circle(*fr.px(0, x0), 7 if i == 0 else 5, OCHRE, PAPER, 1.5) + circle(*fr.px(1, x1), 7 if i == 0 else 5, INDIGO, PAPER, 1.5)
    ay = 642
    s += line(fr.x, ay, fr.x + fr.w, ay, MACH_STROKE, 2)
    for t, lab in ((0, '0'), (0.5, '½'), (1, '1')):
        s += line(fr.x + t * fr.w, ay, fr.x + t * fr.w, ay + 10, MACH_STROKE, 2) + T(fr.x + t * fr.w, ay + 42, lab, 24, 500, SOFT, 'middle')
    h = (tex(56, 90, '$t = 0$ · prior $p_0$', 24, 650, OCHRE) + tex(1120, 90, '$t = 1$ · 데이터 $p_1$', 24, 650, INDIGO, 'end') + tex(fr.x + fr.w + 26, ay + 8, '$t$', 24, 500, SOFT)
         + tex(588, 738, r'가운데서 가장 넓어지는 noise $\sqrt{t(1-t)}\,\epsilon$', 24, 600, INK, 'middle')
         + fx(138, 778, 900, 86, [r'$x_t = (1-t)\,x_0 + t\,x_1 + \sqrt{t(1-t)}\,\epsilon,\qquad \epsilon \sim \mathcal N(0, I)$'], 28))
    return slide('바탕', '두 분포 사이의 길', '두 분포를 noise 섞인 trajectory로 잇는 방법', s, h, '<b>양 끝 sample이 보여야만</b> 놓을 수 있는 trajectory',
                 CITE + ' · 밀도와 trajectory는 예시 분포에서 계산', notes('분포는 숫자에서 계산한 계단식 등고 띠로 그립니다. 라벨은 띠와 선 위에 두지 않습니다.'),
                 recall=[('$x_0$', 'prior의 sample'), ('$x_1$', '데이터의 sample'), (r'$\epsilon$', 'Gaussian noise')])


def g4_mechanism():
    """A mechanism read from top to bottom: the generation row, the training row, and under them what each feeds into the one loss (a white card with the paper's equation number); dashed arrows carry the gradient back to the three models. The plate is nearly 4:3, so rows stack instead of running in one long chain."""
    prior = gaussian((0.0, 0.0), (1.3, 0.85))
    yg, yt, yl = 122, 400, 596
    s = T(0, 30, '생성', 26, 700, INK)
    fg = Frame(0, yg - 62, 196, 124, (-3.3, 3.3), (-2.1, 2.1))
    s += bands2d(prior, fg, OCHRE_MID, ops=OPS_SMALL) + dots(prior, fg, 40, seed=21, r=2.2, color=OCHRE)
    s += arrow(206, yg, 276, yg, INDIGO, 3) + model(282, yg - 44, 284, 88, '생성 모델') + arrow(572, yg, 652, yg, INDIGO, 3) + grid(692, yg, 68)
    s += arrow(734, yg, 806, yg) + trap(812, yg - 52, 170, 104, 'decoder', False) + arrow(988, yg, 1044, yg) + photo(1108, yg, 116, 88)
    s += T(0, 308, '학습', 26, 700, INK)
    ft = Frame(0, yt - 62, 196, 124, (-3.3, 3.3), (-2.1, 2.1))
    s += bands2d(prior, ft, OCHRE_MID, ops=OPS_SMALL) + dots(prior, ft, 40, seed=22, r=2.2, color=OCHRE)
    rng, mid = random.Random(77), None
    for i in range(3):
        pts = [xy for _, xy in bridge(ft.px(*prior.sample(rng)), (654, yt - 9 + i * 9), 22, 48, 80 + i)]
        s += polyline(pts, INDIGO, 2.2)
        mid = pts if i == 1 else mid
    zt = min(mid, key=lambda q: abs(q[0] - 430))
    s += circle(zt[0], zt[1], 9, VERM, '#fff', 2) + grid(692, yt, 68)
    s += arrow(806, yt, 734, yt) + trap(812, yt - 52, 170, 104, 'encoder', False) + arrow(1044, yt, 988, yt) + photo(1108, yt, 116, 88)
    mx, dx, cy = zt[0], 640, 744
    s += arrow(mx, zt[1] + 13, mx, yl - 47, VERM, 2.8) + model(mx - 142, yl - 44, 284, 88, '생성 모델')
    s += arrow(692, yt + 37, 692, trap_edge(dx, yl - 52, 170, 104, 692) - 3) + trap(dx, yl - 52, 170, 104, 'decoder', False)
    s += arrow(dx + 176, yl, 866, yl) + photo(928, yl, 112, 86, soft=True)
    s += arrow(mx - 40, yl + 47, mx - 40, cy - 4, INDIGO, 3) + arrow(928, yl + 46, 928, cy - 4)
    s += arrow(mx + 70, cy - 4, mx + 70, yl + 48, INDIGO, 2.2, '7 6', 13)
    s += arrow(dx + 100, cy - 4, dx + 100, trap_edge(dx, yl - 52, 170, 104, dx + 100, top=False) + 3, INDIGO, 2.2, '7 6', 13)
    s += qarrow(1096, cy - 4, 1092, 516, 904, trap_edge(812, yt - 52, 170, 104, 904, top=False) + 4, INDIGO, 2.2, '7 6', 13)
    h = (tex(0, yg + 100, r'$z_0 \sim p_0$, 어떤 prior든', 22, 500, SOFT) + tex(692, yg - 50, '$z_1$', 24, 600, INK, 'middle') + tex(1108, yg + 100, 'sample $x_1$', 22, 500, SOFT, 'middle')
         + tex(98, yt + 100, '$z_0$', 24, 600, INK, 'middle') + tex(430, yt - 84, '길 위의 $z_t$를 바로 뽑음', 24, 650, INK, 'middle')
         + tex(692, yt - 50, '$z_1$', 24, 600, INK, 'middle') + tex(1108, yt + 100, '데이터 $x_1$', 22, 500, SOFT, 'middle') + tex(994, yl + 9, r'$\hat x_1$', 24, 600, INK)
         + tex(mx + 84, yl + 104, 'gradient', 22, 500, INDIGO) + tex(dx + 114, yl + 104, 'gradient', 22, 500, INDIGO) + tex(1076, yl + 64, 'gradient', 22, 500, INDIGO, 'end')
         + fx(60, cy, 1056, 116, [r'$\text{loss} \;=\; \textcolor{#27477D}{\underbrace{\tfrac{\beta}{2}\,\big\|\,v_t - h_\theta(z_t, t)\big\|^2}_{\text{길 맞추기}}} \;+\; \underbrace{\big\|x_1 - \hat x_1\big\|^2}_{\text{reconstruction}}$'], 28, eq='7'))
    return slide('방법', '한 그림으로', '세 모델을 loss 하나로 묶는 학습', s, h, '생성에는 encoder가 필요 없고 학습의 열쇠는 <b>길 위에서 뽑은 $z_t$</b>',
                 CITE, notes('행을 위에서 아래로 쌓습니다. 같은 배우는 모든 행에서 같은 모양입니다.'),
                 recall=[('$z_0$', 'prior의 sample'), ('$z_1$', 'encoder가 준 latent'), ('$z_t$', '길 위의 latent'), (r'$h_\theta$', '모델의 drift')])


def g5_derivation():
    """A derivation: full-width rows of one relation each, the paper's equation number flush right and what the row gives flush left, a hairline between rows; the result is the one white card. Under it, an axis of regimes with the value each gave."""
    s = lane(0, 28, 'linear SDE에서 sample 식까지') + line(0, 174, SW, 174) + line(0, 290, SW, 290)
    h = (fx(0, 70, SW, 92, [r'$dz_t = -\theta\,z_t\,dt + \sigma\,dw_t$'], 28, 'box plain', eq='1', note='linear drift, additive noise')
         + fx(0, 186, SW, 92, [r'$z_t\,|\,z_0 \sim \mathcal N\big(e^{-\theta t} z_0,\; s_t^2 I\big)$'], 28, 'box plain', eq='2', note='transition이 Gaussian')
         + fx(0, 310, SW, 160, [r'$z_t = e^{-\theta t} z_0 + \frac{\sigma}{\sqrt{2\theta}}\sqrt{1 - e^{-2\theta t}}\;\epsilon$'], 34, eq='4', note='noise 하나로 쓰면')
         + tex(150 + SW / 2 - 42, 526, r'$\epsilon \sim \mathcal N(0, I)$이면 경로를 풀 필요 없음', 26, 700, INK, 'middle'))
    s += lane(0, 628, '가중 β가 학습에 하는 일')
    ax = 752
    s += arrow(40, ax, 1124, ax, MACH_STROKE, 2.4, size=16)
    for x, on in ((196, False), (588, True), (980, False)):
        s += circle(x, ax, 12 if on else 10, INDIGO if on else PAPER, PAPER if on else MACH_STROKE, 3 if on else 2.6)
    for x, lab in ((196, '따로 배우는 두 단계'), (588, 'representation 적응'), (980, 'reconstruction 하락')):
        s += T(x, ax + 56, lab, 24, 500, SOFT, 'middle')
    for x, lab, col in ((196, '품질 4.5', INK), (588, '품질 3.7', INDIGO), (980, '품질 다시 나빠짐', INK)):
        s += T(x, ax + 104, lab, 30, 750, col, 'middle', 'num')
    h += (tex(196, ax - 34, r'$\beta \to 0$', 26, 700, INK, 'middle') + tex(588, ax - 34, r'적당한 $\beta$', 26, 700, INDIGO, 'middle')
          + tex(980, ax - 34, r'$\beta$ 너무 큼', 26, 700, INK, 'middle') + tex(1140, ax + 8, r'$\beta$', 24, 500, SOFT))
    return slide('방법', '식이 내용인 유도', r'식으로 풀리는 transition과 가중 $\beta$의 저울질', s, h, r'경로를 풀지 않아도 <b>어느 $t$든</b> 한 번에 sample',
                 CITE + ' · Ornstein-Uhlenbeck 과정의 교과서 식, 식 번호도 예시', notes('유도를 말하는 장은 식이 내용입니다. 한 식은 한 줄에 둡니다.'),
                 recall=[(r'$\theta$', '되돌리는 세기'), (r'$\sigma$', 'diffusion coefficient'), (r'$\beta$', '두 항의 상대 가중')])


def g6_rows():
    """Results as rows: one row per condition; values that are alike stay numbers, the values that differ become bars. A metric is defined in the rail at its first use (recall with a name instead of a symbol)."""
    s = (T(130, 30, '품질 지표, 낮을수록 좋음', 24, 650, SOFT) + T(500, 30, '한 step의 계산량', 24, 650, SOFT) + T(130, 76, '제안', 24, 700, INDIGO) + T(270, 76, '기준', 24, 700, SOFT)
         + rect(500, 58, 20, 20, INDIGO, rx=3) + T(530, 76, '제안', 24, 700, INDIGO) + rect(604, 58, 20, 20, BAR_OTHER, rx=3) + T(634, 76, '기준', 24, 700, SOFT))
    sc = 560 / 860
    for i, (res, a, b_, ga, gb, note) in enumerate((('작음', '2.6', '2.6', 160, 200, None), ('중간', '3.1', '3.5', 250, 470, '100 step이면 30% 절감'), ('큼', '3.9', '3.9', 300, 860, '100 step이면 65% 절감'))):
        yc = 200 + i * 238
        s += line(0, yc - 119, SW, yc - 119) if i else ''
        s += T(0, yc + 14, res, 38, 750, INK) + T(130, yc + 14, a, 38, 750, INDIGO, cls='num') + T(270, yc + 14, b_, 38, 500, INK, cls='num')
        s += rect(500, yc - 48, ga * sc, 42, INDIGO, rx=4) + T(500 + ga * sc + 14, yc - 17, str(ga), 28, 750, INDIGO, cls='num')
        s += rect(500, yc + 6, gb * sc, 42, BAR_OTHER, rx=4) + T(500 + gb * sc + 14, yc + 37, str(gb), 28, 600, INK, cls='num')
        s += T(500, yc + 92, note, 24, 650, INK) if note else ''
    s += T(0, 858, 'decoder는 sample마다 한 번', 24, 500, SOFT)
    return slide('결과', '품질과 계산량', '비슷한 품질에 한 step이 더 가벼운 제안 모델', s, '', '가장 큰 크기에서 <b>65%</b>까지 커지는 계산 이득', CITE,
                 notes('비슷한 값은 숫자로, 차이가 나는 값은 막대로 보입니다.'), recall=[('품질 지표', '실제 분포와의 거리'), ('계산량', 'forward 한 번, GFLOPs')])


def g7_small_multiples():
    """Small multiples as rows: the shape, its name, a bar from zero and the value; the one row the slide is about is indigo."""
    s = lane(0, 28, '네 가지 prior로 학습한 모델의 품질 지표')
    bx, bs = 500, 620 / 5.5
    s += line(bx, 108, bx, 870, MACH_STROKE, 2)
    for i, (name, pdf, v, on) in enumerate((('uniform', uniform1(-1.5, 1.5), 4.8, False), ('Laplacian', laplace1(0, 0.55), 4.4, False), ('Gaussian', gauss1(0, 0.8), 3.8, True),
                                             ('mixture', mixture1([(1, -1.2, 0.3), (1, 1.2, 0.3)]), 4.3, False))):
        yc = 188 + i * 208
        s += hprofile(pdf, -2.8, 2.8, 0, 236, yc + 52, 100) + T(268, yc + 10, name, 26, 700, INK)
        s += rect(bx, yc - 26, v * bs, 52, INDIGO if on else BAR_OTHER, rx=4) + T(bx + v * bs + 16, yc + 14, f'{v:.1f}', 40, 750, INDIGO if on else INK, cls='num')
    return slide('결과', '학습 전에 고르는 prior', 'Gaussian을 벗어나도 학습되지만 품질은 Gaussian이 최선', s, '', '나머지 셋도 4.3에서 4.8로 <b>비슷한 품질</b>', CITE + ' · 분포 모양은 모식',
                 notes('막대는 0에서 시작합니다.'))


def g8_closing():
    """The closing: what the paper answered as a ledger of question, answer and the one number behind it; the white cards below are the presenter's slot (a content header and two or three questions)."""
    s = lane(0, 28, '논문이 보여 준 것') + line(0, 54, SW, 54, INK, 2.4)
    for i, (q, a, big, small) in enumerate((('세 모델을 함께 배울 수 있는가', '한 loss로 셋을 함께', 'loss 1개', 'encoder · decoder · 생성 모델'),
                                            ('함께 배우면 품질을 내주는가', '비슷한 품질에 더 가벼운 step', '300 대 860', '가장 큰 크기, step마다 계산량'),
                                            ('따로 배울 때보다 나은가', 'joint training이 더 좋음', '4.5 → 3.7', '품질 지표, separate → joint training'),
                                            ('prior를 고를 수 있는가', 'prior와 sampler의 자유', '3.8', 'Gaussian prior, 나머지 4.3–4.8'))):
        y0 = 54 + i * 128
        s += line(0, y0, SW, y0) if i else ''
        s += T(0, y0 + 80, str(i + 1), 44, 750, MUTED, cls='num') + T(60, y0 + 50, q, 23, 500, SOFT) + T(60, y0 + 92, a, 29, 700, INK)
        s += T(SW, y0 + 58, big, 38, 750, INDIGO, 'end', 'num') + T(SW, y0 + 96, small, 22, 500, SOFT, 'end')
    s += line(0, 54 + 4 * 128, SW, 54 + 4 * 128, INK, 2.4) + lane(0, 632, '우리에게 던지는 질문')
    for i, q in enumerate(('우리 representation은 누가 먼저 굳혔나', 'noise와 크기를 우리는 어떻게 정해 왔는가', 'prior를 고를 수 있다면 무엇을 담나')):
        s += card(0, 656 + i * 78, SW, 64) + T(28, 698 + i * 78, q, 26, 700, NAVY)
    return slide('정리', '뜻과 질문', 'jointly 학습하는 것이 우리에게 주는 뜻', s, '', '우리 representation에도 <b>누가 먼저 굳었나</b> 묻기', CITE,
                 notes('아래 세 칸은 발표자가 발표마다 직접 쓰는 자리입니다.'))


def g9_spread_table():
    """A backup spread: the full table behind a chart of the talk, on a full-width plate under a one-line title; numbered B1, outside the spine."""
    t = table(['크기', '제안', '기준', '제안', '기준', '제안, step마다', '제안 decoder, 한 번', '기준, step마다'],
              [['작음', '2.6', '2.6', ('390', '5 / 5 / 380'), '400', ('160', '', 'em'), '15', '200'],
               ['중간', '3.1', '3.5', ('390', '5 / 5 / 380'), '400', ('250', '', 'em'), '60', '470'],
               ['큼', '3.9', '3.9', ('390', '5 / 5 / 380'), '405', ('300', '', 'em'), '240', '860']],
              groups=[('품질 지표', 2), ('parameter, M', 2), ('계산량', 3)], x=0, y=56, w=1744, row_h=150)
    return spread('부록 · 세 크기의 전체 값', '크기가 커질수록 벌어지는 step마다의 계산', lane(0, 28, '세 크기의 제안 모델과 기준 모델'), t,
                  '가장 큰 크기에서 step마다 드는 계산은 <b>300 대 860</b>', CITE + ' · parameter 아래 작은 글씨는 encoder / decoder / 모델',
                  notes('본문의 막대 뒤에 있는 전체 값입니다.'))


if __name__ == '__main__':
    init(sys.argv[1], SECTIONS)
    write_deck([g() for g in (g1_cover, g2_opener, g3_concept, g4_mechanism, g5_derivation, g6_rows, g7_small_multiples, g8_closing, g9_spread_table)])

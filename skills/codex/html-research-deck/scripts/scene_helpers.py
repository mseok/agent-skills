#!/usr/bin/env python3
"""scene_helpers.py — the scene primitives of an accepted ML deck (Latent SI v10, 2026-11-01), ready to import in work/build.py.

    from scene_helpers import *   # after sys.path.insert(0, '<skill>/scripts')

Palette constants fix what a colour means across a deck. One actor, one drawing on every slide:
    trap()       encoder (narrow_right=True) or decoder (narrow_right=False), gray trapezoid with its name inside
    model_box()  the deck's main model, the one blue actor        latent()  the latent code z, a small grid (ghost=True: not observed)
    photo()      a picture, frame with a hill and a sun            grad()    a gradient, red dashed arrow from the loss into a model
    lock()       frozen, red padlock                               check(), xmark()  yes / no
    arr(), curve()  straight and curved arrows (no right-angled wiring); T(), tex(), fx()  a label, a label with KaTeX, a KaTeX strip
    path_between(), bridge_path()  smooth sample paths; vprofile(), hprofile()  1-D densities; density.cloud() for 2-D densities
    gbars(), vbars(), xy_chart()  charts drawn from numbers       scene(), panel(), slide(), lane(), say()  assembly
Layout presets (x, y, w, h) that pass check_deck.py's grid: ONE, L2/R2, LS/RS, LN/RN, P3A/P3B/P3C.
Scene coordinates are local to the panel's <svg>; fx() and tex() add the panel padding themselves.
"""
import html
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from density import brownian, profile_path  # noqa: E402

INK, SOFT, MUTED, NAVY, BLUE, RED, CORAL, AMBER, GRAY, LIGHT = (
    '#1F2933', '#52606D', '#66727F', '#1D3A5F', '#4C72B0', '#D1495B', '#E76F51', '#B7793A', '#9AA5B1', '#D9DEE3')
BAR, BAR_HL, BAR_MUTED = '#8FA7CF', '#4C72B0', '#C5CDD5'
ARROW, EDGE, RUST = '#6B7885', '#AEB7C0', '#B4492F'
NODE_FILL, NODE_STROKE, OUT_FILL, AGENT_FILL, AGENT_STROKE, TRACK = '#EEF2F7', '#5F718A', '#F8E3BF', '#EEF1F4', '#8E9AA6', '#E4E8EC'
STEEL_FILL, STEEL_STROKE, BLUE_FILL, BLUE_STROKE, FORM_FILL = '#E2E9F2', '#5F718A', '#DCE6F5', '#2F4C7D', '#F4F6F8'


def esc(s):
    return html.escape(str(s), quote=False)


def T(x, y, s, size=24, weight=500, fill=INK, anchor='start', extra=''):
    return (f'<text x="{x:g}" y="{y:g}" text-anchor="{anchor}" '
            f'style="font-size:{size}px;font-weight:{weight};fill:{fill}{extra}">{esc(s)}</text>')


def rect(x, y, w, h, fill='#fff', stroke='none', sw=2, rx=0, dash='', extra=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{extra}/>'


def line(x1, y1, x2, y2, stroke=GRAY, sw=2, dash=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def head(x, y, ux, uy, color, size=16):
    """Concave arrowhead with its tip at (x, y), pointing along the unit vector (ux, uy)."""
    px, py = -uy, ux
    bx, by = x - ux * size, y - uy * size
    nx, ny = x - ux * size * 0.74, y - uy * size * 0.74
    w = size * 0.48
    return (f'<path d="M{x:.1f} {y:.1f} L{bx + px * w:.1f} {by + py * w:.1f} L{nx:.1f} {ny:.1f} '
            f'L{bx - px * w:.1f} {by - py * w:.1f} Z" fill="{color}"/>')


def arr(x1, y1, x2, y2, color=ARROW, sw=2.6, dash='', size=16):
    """Straight arrow: the shaft stops in the notch of the head, so the head sits on the line."""
    d = math.hypot(x2 - x1, y2 - y1) or 1
    ux, uy = (x2 - x1) / d, (y2 - y1) / d
    return line(x1, y1, x2 - ux * size * 0.7, y2 - uy * size * 0.7, color, sw, dash) + head(x2, y2, ux, uy, color, size)


def curve(x1, y1, cx, cy, x2, y2, color=ARROW, sw=2.6, dash='', size=16):
    """One smooth quadratic arrow with the head on the end tangent."""
    d = math.hypot(x2 - cx, y2 - cy) or 1
    ux, uy = (x2 - cx) / d, (y2 - cy) / d
    ex, ey = x2 - ux * size * 0.7, y2 - uy * size * 0.7
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<path d="M{x1:g} {y1:g} Q{cx:g} {cy:g} {ex:.1f} {ey:.1f}" fill="none" stroke="{color}" stroke-width="{sw}"{da}/>'
            + head(x2, y2, ux, uy, color, size))


def circle(cx, cy, r, fill='#fff', stroke=SOFT, sw=2, dash=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<circle cx="{cx:g}" cy="{cy:g}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def box(x, y, w, h, label, sub=None, fill='#fff', stroke=EDGE, size=24, rx=12, subsize=24, weight=700, color=INK, subcolor=None, dash='', sw=1.8):
    """Thin-border box; text centred. Label lines split on newline."""
    out = [rect(x, y, w, h, fill, stroke, sw, rx, dash)]
    cy = y + h / 2
    if sub:
        b1 = cy - (0.75 * size + subsize + 6 + 0.22 * subsize) / 2 + 0.75 * size
        out.append(T(x + w / 2, b1, label, size, weight, color, 'middle'))
        out.append(T(x + w / 2, b1 + subsize + 6, sub, subsize, 500, subcolor or SOFT, 'middle'))
    else:
        parts = label.split('\n')
        lh = size * 1.2
        for k, part in enumerate(parts):
            out.append(T(x + w / 2, cy - (len(parts) - 1) * lh / 2 + k * lh + size * 0.36, part, size, weight, color, 'middle'))
    return ''.join(out)


def formula(x, y, w, h, lines, size=26, weight=600, color=INK, fill=FORM_FILL, stroke='none', align='middle'):
    """A formula strip: one or more text lines centred inside a light rounded box (text in a shape, not a free line)."""
    out = [rect(x, y, w, h, fill, stroke, 1.5, 12)]
    lh = size * 1.35
    cy = y + h / 2
    for k, s in enumerate(lines):
        tx = x + w / 2 if align == 'middle' else x + 22
        out.append(T(tx, cy - (len(lines) - 1) * lh / 2 + k * lh + size * 0.36, s, size, weight, color, align))
    return ''.join(out)


def xmark(cx, cy, r=10, color=RED):
    return (f'<circle cx="{cx:g}" cy="{cy:g}" r="{r + 8}" fill="#fff"/>'
            f'<g stroke="{color}" stroke-width="4" stroke-linecap="round"><line x1="{cx - r:g}" y1="{cy - r:g}" x2="{cx + r:g}" y2="{cy + r:g}"/>'
            f'<line x1="{cx + r:g}" y1="{cy - r:g}" x2="{cx - r:g}" y2="{cy + r:g}"/></g>')


def check(cx, cy, color=BLUE, s=1.0):
    return f'<path d="M{cx - 12 * s:g} {cy:g} L{cx - 3 * s:g} {cy + 9 * s:g} L{cx + 13 * s:g} {cy - 10 * s:g}" fill="none" stroke="{color}" stroke-width="{4 * s}" stroke-linecap="round" stroke-linejoin="round"/>'


def bridge_path(x1, y1, x2, y2, sigma, seed, color=ARROW, sw=2, n=48, dash='', pin=True):
    """One smooth Brownian-bridge curve from (x1, y1) to (x2, y2) (pin=True) or a free Brownian curve from (x1, y1) (pin=False)."""
    noise = brownian(n, seed, pin=pin)
    pts = [(x1 + (x2 - x1) * k / n, y1 + (y2 - y1) * k / n + sigma * noise[k]) for k in range(n + 1)]
    dd = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<polyline points="{" ".join(f"{px:.1f},{py:.1f}" for px, py in pts)}" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linejoin="round"{dd}/>'), pts


def photo(cx, cy, w=96, h=74, stroke=NODE_STROKE, ghost=False, blur=False):
    """A picture: frame with a hill and a sun; ghost = dashed empty frame; blur = washed-out (poor reconstruction)."""
    x, y = cx - w / 2, cy - h / 2
    out = [rect(x, y, w, h, 'none' if ghost else '#fff', EDGE if ghost else stroke, 2.2, 8, '6 5' if ghost else '')]
    if not ghost:
        col, sun = (LIGHT, '#EBD9B3') if blur else (NODE_FILL, '#E9B96A')
        out.append(f'<path d="M{x + 6:g} {y + h - 7:g} L{x + w * 0.36:g} {y + h * 0.42:g} L{x + w * 0.55:g} {y + h * 0.7:g} '
                   f'L{x + w * 0.7:g} {y + h * 0.52:g} L{x + w - 6:g} {y + h - 7:g} Z" fill="{col}" stroke="{EDGE if blur else stroke}" stroke-width="1.8" stroke-linejoin="round"/>')
        out.append(circle(x + w * 0.76, y + h * 0.3, 7, sun, 'none', 0))
    return ''.join(out)


def trap(x, y, w, h, label, narrow_right=True, fill=NODE_FILL, stroke=NODE_STROKE, size=24, sub=None):
    """Encoder (narrows to the right) or decoder (widens to the right): a gray trapezoid with its name inside."""
    k = h * 0.24
    pts = f'{x},{y} {x + w},{y + k} {x + w},{y + h - k} {x},{y + h}' if narrow_right else f'{x},{y + k} {x + w},{y} {x + w},{y + h} {x},{y + h - k}'
    out = [f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="2.2" stroke-linejoin="round"/>']
    if sub:
        out.append(T(x + w / 2, y + h / 2 + size * 0.36, label, size, 700, INK, 'middle'))
        out.append(T(x + w / 2, y + h + 28, sub, size - 2, 500, SOFT, 'middle'))
    else:
        out.append(T(x + w / 2, y + h / 2 + size * 0.36, label, size, 700, INK, 'middle'))
    return ''.join(out)


def latent(cx, cy, s=60, fill=NODE_FILL, stroke=NODE_STROKE, ghost=False):
    """The latent code z: a small 3×3 grid; ghost = dashed outline (not observed)."""
    out = [rect(cx - s / 2, cy - s / 2, s, s, 'none' if ghost else fill, EDGE if ghost else stroke, 2.2, 8, '6 5' if ghost else '')]
    if not ghost:
        for k in (1, 2):
            out.append(line(cx - s / 2 + k * s / 3, cy - s / 2, cx - s / 2 + k * s / 3, cy + s / 2, stroke, 1.4))
            out.append(line(cx - s / 2, cy - s / 2 + k * s / 3, cx + s / 2, cy - s / 2 + k * s / 3, stroke, 1.4))
    return ''.join(out)


def model_box(x, y, w, h, label, sub=None, size=24):
    """The deck's main model: the one blue actor, the same box on every slide."""
    return box(x, y, w, h, label, sub, BLUE_FILL, BLUE_STROKE, size, 14, size - 2, 700, INK, SOFT, sw=2.4)


def lock(cx, cy, s=1.0, color=RED):
    return (f'<g transform="translate({cx:g} {cy:g}) scale({s})">'
            f'<path d="M-9 -3 V-10 a9 9 0 0 1 18 0 V-3" fill="none" stroke="{color}" stroke-width="3.2"/>'
            f'<rect x="-14" y="-3" width="28" height="22" rx="4" fill="{color}"/></g>')


def axes(x, y, w, h, color=SOFT):
    return line(x, y, x, y + h, color, 2) + line(x, y + h, x + w, y + h, color, 2)


def vbars(x, y, w, h, items, vmax, label_size=24, gap_ratio=0.38, value_fmt='{:g}', name_size=24, hl_color=BAR_HL, color=BAR, value_dy=-12):
    """Vertical bars from a baseline at y+h: items = (name, value, highlight). Values printed above each bar."""
    n = len(items)
    slot = w / n
    bw = slot * (1 - gap_ratio)
    out = []
    for i, (name, val, hl) in enumerate(items):
        bh = h * val / vmax
        bx = x + i * slot + (slot - bw) / 2
        out.append(rect(bx, y + h - bh, bw, bh, hl_color if hl else color, 'none', 0, 4))
        out.append(T(bx + bw / 2, y + h - bh + value_dy, value_fmt.format(val), label_size + 2, 700, NAVY if hl else INK, 'middle'))
        for k, part in enumerate(name.split('\n')):
            out.append(T(bx + bw / 2, y + h + 32 + k * 28, part, name_size, 700 if hl else 500, NAVY if hl else SOFT, 'middle'))
    return ''.join(out)


def panel(x, y, w, h, inner, html_blocks=()):
    return f'<div class="panel" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">{inner}{"".join(html_blocks)}</div>'


def fx(x, y, w, h, lines, size=26, cls='box'):
    """A KaTeX formula strip: HTML block in panel coordinates (scene x, y → +20). A line without $ is a Korean caption (.k)."""
    ps = ''.join(f'<p{"" if "$" in l else " class=\"k\""}>{l}</p>' for l in lines)
    return f'<div class="fx {cls}" style="left:{x + 20:g}px;top:{y + 20:g}px;width:{w:g}px;height:{h:g}px;font-size:{size}px">{ps}</div>'


def tex(x, y, s, size=24, weight=700, color=INK, anchor='start'):
    """A label with inline KaTeX, placed like T(): y is the baseline, x the anchor (start / middle / end)."""
    tx = {'start': '0', 'middle': '-50%', 'end': '-100%'}[anchor]
    return (f'<div class="fx" style="left:{x + 20:g}px;top:{y + 20 - size * 0.9:g}px;font-size:{size}px;font-weight:{weight};color:{color};'
            f'transform:translate({tx},0)">{s}</div>')


def path_between(p0, p1, sigma, seed, color=None, sw=2.2, dash='', end_r=3.6):
    """A smooth bridge between two sample positions in scene px; its two ends are dots, so the path visibly starts and lands on samples."""
    noise = brownian(64, seed)
    pts = [(p0[0] + (p1[0] - p0[0]) * k / 64, p0[1] + (p1[1] - p0[1]) * k / 64 + sigma * noise[k]) for k in range(65)]
    c = color or BLUE
    return polyline(pts, c, sw, dash) + circle(pts[0][0], pts[0][1], end_r, c, '#fff', 1) + circle(pts[-1][0], pts[-1][1], end_r, c, '#fff', 1), pts


def vprofile(curve, y_lo, y_hi, axis_x, bulge, fill, stroke):
    """A 1-D density as a filled profile along a vertical axis (the reference deck's vDensity)."""
    return f'<path d="{profile_path(curve, (y_lo, y_hi), axis_x, bulge)}" fill="{fill}" stroke="{stroke}" stroke-width="2.4" stroke-linejoin="round"/>'


def hprofile(curve, x_lo, x_hi, base_y, bulge, fill, stroke):
    """A 1-D density as a filled profile along a horizontal baseline, bulging upward."""
    return f'<path d="{profile_path(curve, (x_lo, x_hi), base_y, bulge, vertical=False)}" fill="{fill}" stroke="{stroke}" stroke-width="2.4" stroke-linejoin="round"/>'


def polyline(pts, color, sw=3, dash=''):
    dd = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<polyline points="{" ".join(f"{px:.1f},{py:.1f}" for px, py in pts)}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"{dd}/>'


def gbars(x, y, w, h, groups, vmax, fmt='{:g}', bw=None, val_size=26):
    """Grouped bars from a baseline at y+h: groups = (name, [(value, highlight), …]). Values printed above the bars."""
    out = [line(x, y + h, x + w, y + h, SOFT, 2)]
    slot = w / len(groups)
    k = len(groups[0][1])
    bw = bw or slot * 0.26
    for i, (name, vals) in enumerate(groups):
        gx = x + i * slot + slot / 2 - (k * bw + (k - 1) * 10) / 2
        for j, (val, hl) in enumerate(vals):
            bh = h * val / vmax
            bx = gx + j * (bw + 10)
            out.append(rect(bx, y + h - bh, bw, bh, BAR_HL if hl else BAR_MUTED, 'none', 0, 4))
            out.append(T(bx + bw / 2, y + h - bh - 12, fmt.format(val), val_size, 700, NAVY if hl else SOFT, 'middle'))
        out.append(T(x + i * slot + slot / 2, y + h + 34, name, 24, 700, INK, 'middle'))
    return ''.join(out)


def img(x, y, w, h, name):
    return f'<image href="assets/figs/{name}" x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" preserveAspectRatio="xMidYMid slice"/>'


def xy_chart(x, y, w, h, xt, yt, xlab='', ylab=''):
    """Axes with tick labels: xt = [(pos01, label)], yt = [(value01, label)] in unit coordinates."""
    out = [axes(x, y, w, h)]
    for p, lab in xt:
        out.append(line(x + w * p, y + h, x + w * p, y + h + 8, SOFT, 2))
        if lab:
            out.append(T(x + w * p, y + h + 36, lab, 22, 600, SOFT, 'middle'))
    for p, lab in yt:
        out.append(line(x - 8, y + h - h * p, x, y + h - h * p, SOFT, 2)); out.append(T(x - 16, y + h - h * p + 8, lab, 22, 600, SOFT, 'end'))
    if xlab:
        out.append(T(x + w + 14, y + h + 8, xlab, 22, 600, SOFT))
    if ylab:
        out.append(T(x - 12, y - 18, ylab, 22, 600, SOFT, 'end'))
    return ''.join(out)


def trap_y(x, y, w, h, px, narrow_right=True, top=False):  # noqa: AS100  (called from deck build.py files, outside this repository)
    """y of a trapezoid's top or bottom edge at px, so an arrow can end on the slanted edge."""
    f = (px - x) / w if narrow_right else 1 - (px - x) / w
    k = h * 0.24
    return y + k * f if top else y + h - k * f


def grad(x1, y1, x2, y2, cx=None, cy=None):
    """The gradient arrow: one red dashed line (or quadratic through (cx, cy)) from the loss into a model."""
    return arr(x1, y1, x2, y2, RED, 2.4, '7 5') if cx is None else curve(x1, y1, cx, cy, x2, y2, RED, 2.4, '7 5')


def scene(w, h, body):
    return f'<svg class="sc" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'


def lane(x, y, s):
    return T(x, y + 4, s, 24, 650, SOFT)


def slide(title, kicker, panels_html, takeaway, cite, notes, section, cls=''):
    return (f'<section class="slide{cls}" data-title="{esc(title)}" data-section="{esc(section)}">\n'
            f'  <div class="kicker blue">{esc(kicker)}</div>\n  <h2>{esc(title)}</h2>\n  {panels_html}\n'
            f'  <div class="takeaway">{esc(takeaway).replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")}</div>\n  <div class="cite">{cite}</div>\n'
            f'  <aside class="notes">{notes}</aside>\n</section>')


def say(talk, nxt):
    """Speaker script at the head of the notes: how to open the slide and how to hand over to the next one."""
    return f'<p><b>말하기</b> {talk} <b>다음 장으로</b> {nxt}</p>'


# layout presets on the deck grid
ONE = (110, 176, 1700, 722)
L2, R2 = (110, 176, 838, 722), (972, 176, 838, 722)
LS, RS = (110, 176, 1012, 722), (1146, 176, 664, 722)
LN, RN = (110, 176, 664, 722), (798, 176, 1012, 722)
P3A, P3B, P3C = (110, 176, 550, 722), (684, 176, 552, 722), (1260, 176, 550, 722)

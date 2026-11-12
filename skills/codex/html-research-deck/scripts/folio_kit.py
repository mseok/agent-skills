#!/usr/bin/env python3
"""folio_kit.py — the page and drawing kit of the Folio layout (references/folio.md), importable from a deck's work/build.py.

    import sys; sys.path.insert(0, '<skill>/scripts')
    from folio_kit import *
    init('<talk>/deck', sections=['왜', '바탕', '방법', '실험', '우리에게'])   # a folder scaffolded by new_deck.py --theme folio
    ...
    write_deck([cover(...), opener('왜', '…'), slide('바탕', …), …, spread(…)])

scripts/folio_gallery.py is the worked example (toy content; renders in assets/folio-gallery/). Copy a slide's code, keep its sizes and
positions, change the content. Scene coordinates are plate pixels: the drawing area is SW x SH = 1176 x 888 (a spread: 1744 x 650); tex()
and fx() take the same coordinates and add the 20 px padding themselves.

    cover()            the title on the left, one figure on the right-hand plate
    opener()           a section opener: the section number and the one question the section answers, on ink
    slide()            rail + plate: title (a noun phrase, four lines at most), recall = the symbols or metrics this slide uses, the closing
                       line in its card, one figure on the plate, the cite line under the figure
    spread()           a full-width plate under a one-line title, for a table or a wide figure; backup=True numbers it B1
    notes(), lane()    speaker notes; a lane header on the plate
    field_bands(), strands(), vprofile()   the (t, x) picture of a transport between two distributions as stepped level sets; Field is its density
    bands2d(), dots()  a 2-D distribution as stepped level sets with real samples; no outline, no alpha (PDF engines disagree on alpha)
    hprofile()         a 1-D density as a filled profile on a baseline
    trap(), grid(), photo(), model()       the actors: encoder or decoder, latent code, picture, the model of interest
    T(), tex(), fx()   text; a label with KaTeX; a formula block: fx(..., 'box') the white card for the key formula, fx(..., 'box plain',
                       eq='13', note='…') one numbered row of a derivation (eq = the paper's own equation number)
    table()            a three-rule table (from scene_kit); step(), at() builds (from scene_kit)
    arrow(), qarrow(), line(), rect(), card(), circle(), path(), polyline()
The spine and the section numbers are filled in by write_deck() from the order of the slides. A label never sits on a band or a path:
check_layout.py reports it. No reported number ever comes from these drawings; the cite line says what is schematic.
"""
import math
import random
import re
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
from density import Frame, bridge, gauss1, gaussian, gmm, laplace1, mixture1, samples, uniform1  # noqa: E402,F401
from scene_kit import Field as _KitField  # noqa: E402
from scene_kit import at, step, table  # noqa: E402,F401

# ---- colour (one meaning per hue)
PAPER, INK, SOFT, MUTED, RULE, FAINT = '#F6F3EB', '#17191C', '#4A4F55', '#666B70', '#CFC9BA', '#E3DED1'
INDIGO, INDIGO_MID, INDIGO_FILL = '#27477D', '#5B7FB8', '#DDE5F1'      # the model or value of interest
OCHRE, OCHRE_MID, OCHRE_FILL = '#B8791F', '#D9A441', '#F1E0BC'         # the prior
VERM = '#CF3F2A'                                                       # the section number and one key phrase
MACH_FILL, MACH_STROKE = '#E9E4D8', '#77736A'                          # machinery: encoder, decoder, frames
BAR_OTHER = '#BDB8AB'                                                  # bars that are not the point
NAVY, ARROW = '#1E3A66', '#6B6F74'

# ---- geometry
PLATE = (624, 72, 1216, 928)
SPREAD = (76, 196, 1784, 690)
COVER = (932, 72, 908, 928)
SW, SH = 1176, 888
CARD_TOP, SPINE_H = 832, 928

_S = SimpleNamespace(deck=None, sections=[])


def init(deck_dir, sections):
    """Set the deck folder (scaffolded by new_deck.py --theme folio) and the section names in order; call once at the top of build.py."""
    _S.deck = Path(deck_dir).resolve()
    _S.sections = list(sections)
    (_S.deck / 'assets' / 'figs').mkdir(parents=True, exist_ok=True)


def _plain(s):
    return re.sub(r'<[^>]+>', ' ', s).replace('$', '').replace('\\', '').replace('"', '').strip()


# ---------------------------------------------------------------- primitives
def T(x, y, s, size=24, weight=500, fill=INK, anchor='start', cls=''):
    """SVG text. cls='num' sets tabular numerals for a value."""
    a = '' if anchor == 'start' else f' text-anchor="{anchor}"'
    c = f' class="{cls}"' if cls else ''
    return f'<text x="{x:g}" y="{y:g}" font-size="{size:g}" font-weight="{weight}" fill="{fill}"{a}{c}>{s}</text>'


def lane(x, y, s):
    return T(x, y, s, 24, 650, SOFT)


def line(x1, y1, x2, y2, stroke=RULE, sw=1.5, dash=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{stroke}" stroke-width="{sw:g}" stroke-linecap="round"{d}/>'


def rect(x, y, w, h, fill='#fff', stroke='none', sw=2, rx=0, dash=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx:g}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:g}"{d}/>'


def card(x, y, w, h, rx=14):
    """A white card: it holds one thing."""
    return (f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx:g}" fill="#fff" '
            'style="filter:drop-shadow(0 1px 2px rgba(23,25,28,.05)) drop-shadow(0 4px 14px rgba(23,25,28,.07))"/>')


def circle(cx, cy, r, fill=INK, stroke='none', sw=2):
    return f'<circle cx="{cx:g}" cy="{cy:g}" r="{r:g}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:g}"/>'


def path(d, fill='none', stroke=INK, sw=2):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:g}" stroke-linejoin="round" stroke-linecap="round"/>'


def polyline(pts, color=INDIGO, sw=2.2, op=1.0, dash=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    o = f' stroke-opacity="{op:g}"' if op < 1 else ''
    return (f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{color}" stroke-width="{sw:g}" '
            f'stroke-linejoin="round" stroke-linecap="round"{o}{d}/>')


def _head(x, y, ux, uy, color, size):
    nx, ny = -uy, ux
    bx, by = x - ux * size, y - uy * size
    return (f'<polygon points="{x:.1f},{y:.1f} {bx + nx * size * 0.42:.1f},{by + ny * size * 0.42:.1f} '
            f'{bx - nx * size * 0.42:.1f},{by - ny * size * 0.42:.1f}" fill="{color}"/>')


def arrow(x1, y1, x2, y2, color=ARROW, sw=2.6, dash='', size=15):
    """A straight arrow; the shaft stops inside the head so the tip stays sharp."""
    L = math.hypot(x2 - x1, y2 - y1) or 1.0
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    return line(x1, y1, x2 - ux * size * 0.8, y2 - uy * size * 0.8, color, sw, dash) + _head(x2, y2, ux, uy, color, size)


def qarrow(x1, y1, cx, cy, x2, y2, color=ARROW, sw=2.6, dash='', size=15):
    """One smooth quadratic curve with the head on its end tangent."""
    L = math.hypot(x2 - cx, y2 - cy) or 1.0
    ux, uy = (x2 - cx) / L, (y2 - cy) / L
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<path d="M{x1:g} {y1:g} Q{cx:g} {cy:g} {x2 - ux * size * 0.8:.1f} {y2 - uy * size * 0.8:.1f}" fill="none" stroke="{color}" '
            f'stroke-width="{sw:g}" stroke-linecap="round"{d}/>') + _head(x2, y2, ux, uy, color, size)


# ---------------------------------------------------------------- KaTeX blocks (HTML, plate coordinates = scene + 20)
def tex(x, y, s, size=24, weight=600, color=INK, anchor='start'):
    """A label with inline KaTeX, placed like T(): y is the baseline, x the anchor."""
    tx = {'start': '0', 'middle': '-50%', 'end': '-100%'}[anchor]
    return (f'<div class="fx" style="left:{x + 20:g}px;top:{y + 20 - size * 0.9:g}px;font-size:{size}px;font-weight:{weight};color:{color};'
            f'transform:translate({tx},0)">{s}</div>')


def fx(x, y, w, h, rows, size=26, cls='box', eq=None, note=None):
    """A sized formula block. cls 'box' is the white card for the key formula, 'box plain' a display equation on the paper. One relation
    per row, never split. eq is the paper's own equation number (flush right, in parentheses), note says what the row gives (flush left):
    a derivation is a stack of full-width 'box plain' rows with a hairline between them, and its result is the one 'box' row."""
    ps = ''.join(f'<p>{r}</p>' if '$' in r else f'<p class="k">{r}</p>' for r in rows)
    tag = (f'<span class="note">{note}</span>' if note else '') + (f'<span class="eqn">({eq})</span>' if eq else '')
    return f'<div class="fx {cls}" style="left:{x + 20:g}px;top:{y + 20:g}px;width:{w:g}px;height:{h:g}px;font-size:{size}px">{ps}{tag}</div>'


# ---------------------------------------------------------------- actors
def trap(x, y, w, h, label, narrow_right=True, size=24):
    """Encoder or decoder: a flat machinery trapezoid, narrow on the side of the latent, with its name inside."""
    k = h * 0.24
    pts = f'{x},{y} {x + w},{y + k} {x + w},{y + h - k} {x},{y + h}' if narrow_right else f'{x},{y + k} {x + w},{y} {x + w},{y + h} {x},{y + h - k}'
    return (f'<polygon points="{pts}" fill="{MACH_FILL}" stroke="{MACH_STROKE}" stroke-width="2.2" stroke-linejoin="round"/>'
            + T(x + w / 2, y + h / 2 + size * 0.36, label, size, 700, INK, 'middle'))


def trap_edge(x, y, w, h, px, top=True, narrow_right=False):
    """y of the top or bottom edge of trap(x, y, w, h, …) at scene x = px, for an arrow that lands on it."""
    f = (px - x) / w
    k = h * 0.24 * (f if narrow_right else 1 - f)
    return y + k if top else y + h - k


def grid(cx, cy, s=64, ghost=False):
    """The latent code: a 3 x 3 grid."""
    out = [rect(cx - s / 2, cy - s / 2, s, s, 'none' if ghost else '#fff', MACH_STROKE, 2.2, 7, '6 5' if ghost else '')]
    if not ghost:
        for k in (1, 2):
            out.append(line(cx - s / 2 + k * s / 3, cy - s / 2, cx - s / 2 + k * s / 3, cy + s / 2, MACH_STROKE, 1.4))
            out.append(line(cx - s / 2, cy - s / 2 + k * s / 3, cx + s / 2, cy - s / 2 + k * s / 3, MACH_STROKE, 1.4))
    return ''.join(out)


def photo(cx, cy, w=112, h=86, soft=False):
    """A picture: a frame with a hill and a sun; soft = a reconstruction (lighter)."""
    x, y = cx - w / 2, cy - h / 2
    hill, sun = (FAINT, '#EBD9B3') if soft else (MACH_FILL, OCHRE_MID)
    return (rect(x, y, w, h, '#fff', MACH_STROKE, 2.2, 7)
            + f'<path d="M{x + 7:g} {y + h - 8:g} L{x + w * 0.36:g} {y + h * 0.42:g} L{x + w * 0.55:g} {y + h * 0.7:g} L{x + w * 0.7:g} {y + h * 0.52:g} '
              f'L{x + w - 7:g} {y + h - 8:g} Z" fill="{hill}" stroke="{MACH_STROKE}" stroke-width="1.8" stroke-linejoin="round"/>'
            + circle(x + w * 0.76, y + h * 0.3, 7, sun))


def model(x, y, w, h, label, size=24):
    """The model of interest: the one indigo actor of a deck."""
    return rect(x, y, w, h, INDIGO_FILL, INDIGO, 2.4, 14) + T(x + w / 2, y + h / 2 + size * 0.36, label, size, 700, INK, 'middle')


# ---------------------------------------------------------------- densities as stepped level sets
def _loops(vals, level):
    """Marching squares on a grid padded with zeros, so every contour closes. Returns loops of (col, row) points in padded-grid units."""
    ny, nx = len(vals), len(vals[0])
    g = [[0.0] * (nx + 2)] + [[0.0] + list(r) + [0.0] for r in vals] + [[0.0] * (nx + 2)]

    def cross(key):
        kind, i, j = key
        if kind == 'h':            # between (i, j) and (i + 1, j)
            a, b = g[j][i], g[j][i + 1]
            return (i + (level - a) / (b - a), float(j))
        a, b = g[j][i], g[j + 1][i]
        return (float(i), j + (level - a) / (b - a))

    link = {}

    def join(k1, k2):
        link.setdefault(k1, []).append(k2)
        link.setdefault(k2, []).append(k1)

    for j in range(ny + 1):
        for i in range(nx + 1):
            a, b, c, d = g[j][i] >= level, g[j][i + 1] >= level, g[j + 1][i + 1] >= level, g[j + 1][i] >= level
            idx = a | (b << 1) | (c << 2) | (d << 3)
            if idx in (0, 15):
                continue
            top, right, bottom, left = ('h', i, j), ('v', i + 1, j), ('h', i, j + 1), ('v', i, j)
            mid = (g[j][i] + g[j][i + 1] + g[j + 1][i + 1] + g[j + 1][i]) / 4 >= level
            pairs = {1: [(left, top)], 2: [(top, right)], 3: [(left, right)], 4: [(right, bottom)], 6: [(top, bottom)], 7: [(left, bottom)],
                     8: [(left, bottom)], 9: [(top, bottom)], 11: [(right, bottom)], 12: [(left, right)], 13: [(top, right)], 14: [(left, top)],
                     5: [(top, right), (left, bottom)] if mid else [(left, top), (right, bottom)],
                     10: [(left, top), (right, bottom)] if mid else [(top, right), (left, bottom)]}[idx]
            for k1, k2 in pairs:
                join(k1, k2)
    loops, seen = [], set()
    for start in link:
        if start in seen:
            continue
        loop, prev, cur = [], None, start
        while cur not in seen:
            seen.add(cur)
            loop.append(cross(cur))
            nxt = [k for k in link[cur] if k != prev]
            if not nxt:
                break
            prev, cur = cur, (nxt[0] if nxt[0] not in seen or nxt[0] == start else nxt[-1])
        if len(loop) >= 4:
            loops.append(loop)
    return loops


def _chaikin(pts, times=2):
    for _ in range(times):
        out = []
        for k, p in enumerate(pts):
            q = pts[(k + 1) % len(pts)]
            out.append((0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]))
            out.append((0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1]))
        pts = out
    return pts


def _mix(base, top, a):
    """The opaque colour of `top` at alpha a over `base` (hex strings)."""
    b, t = [int(base[i:i + 2], 16) for i in (1, 3, 5)], [int(top[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(x + (y - x) * a):02X}' for x, y in zip(b, t))


def _cum(ops):
    """Alpha of the stack after each step: the steps are nested, so step k shows 1 - prod(1 - op_i) of the tint."""
    out, keep = [], 1.0
    for op in ops:
        keep *= 1 - op
        out.append(1 - keep)
    return out


def _band_paths(vals, fr, levels, fills, smooth=2):
    """One filled path per level over the frame fr; vals[row][col] in 0..1, row 0 at the top. Fills are opaque (see bands2d)."""
    ny, nx = len(vals), len(vals[0])
    out = []
    for level, fill in zip(levels, fills):
        d = []
        for loop in _loops(vals, level):
            pts = _chaikin(loop, smooth) if smooth else loop
            # padded-grid units -> scene px: node (i, j) of the padded grid is the centre of cell (i - 1, j - 1) of vals
            px = [(fr.x + min(max((i - 0.5) / nx, 0.0), 1.0) * fr.w, fr.y + min(max((j - 0.5) / ny, 0.0), 1.0) * fr.h) for i, j in pts]
            d.append('M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in px) + ' Z')
        if d:
            out.append(f'<path d="{" ".join(d)}" fill="{fill}" fill-rule="evenodd" stroke="none"/>')
    return ''.join(out)


LEVELS = (0.10, 0.28, 0.48, 0.68, 0.86)
OPS = (0.16, 0.16, 0.17, 0.18, 0.2)
OPS_SMALL = (0.24, 0.2, 0.2, 0.2, 0.22)      # a cloud under about 250 px wide needs a firmer first step


def bands2d(dist, fr, tint=INDIGO_MID, levels=LEVELS, ops=OPS, n=72, base=PAPER):
    """A 2-D density as stepped level sets of p / p_max over the frame (vector, no outline). Each step is painted in the opaque colour the
    stack would have over `base` (the paper, or '#FFFFFF' on a card): PDF engines draw a translucent or gradient-with-alpha fill
    differently (Poppler dropped the alpha of a gradient fill in the first Folio export, 2026-11-12)."""
    nx, ny = n, max(8, round(n * fr.h / fr.w))
    peak = dist.peak()
    vals = []
    for j in range(ny):
        y = fr.yr[1] - (j + 0.5) / ny * (fr.yr[1] - fr.yr[0])
        vals.append([math.exp(dist.logpdf(fr.xr[0] + (i + 0.5) / nx * (fr.xr[1] - fr.xr[0]), y) - peak) for i in range(nx)])
    return _band_paths(vals, fr, levels, [_mix(base, tint, a) for a in _cum(ops)])


def dots(dist, fr, n, seed=0, r=2.6, color=INDIGO, core=LEVELS[1]):
    """n real samples, only where the density is clearly visible."""
    out = []
    for dx, dy in samples(dist, n, seed, core):
        px, py = fr.px(dx, dy)
        if fr.x + r < px < fr.x + fr.w - r and fr.y + r < py < fr.y + fr.h - r:
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:g}" fill="{color}" stroke="{PAPER}" stroke-width="0.7"/>')
    return ''.join(out)


class Field(_KitField):
    """Marginal density p_t(x) of x_t = (1-t) x0 + t x1 + sig*sqrt(t(1-t)) eps, x0 ~ N(mu0, s0^2), x1 a Gaussian mixture [(weight, mean, sd)]
    (scene_kit.Field: pdf(t, x), p0(), p1()), plus draw() for a pair of end samples."""

    def draw(self, rng):
        x0 = rng.gauss(self.mu0, self.s0)
        u, acc, pick = rng.random(), 0.0, self.comps[-1]
        for c in self.comps:
            acc += c[0]
            if u <= acc:
                pick = c
                break
        return x0, rng.gauss(pick[1], pick[2])


def field_bands(F, fr, gid, c0=OCHRE_MID, c1=INDIGO_MID, levels=LEVELS, ops=OPS, nt=96, nx=120, base=PAPER):
    """The (t, x) plane as stepped level sets of p_t(x) / max_x p_t(x); the fill runs from the prior's ochre to the target's indigo.
    One opaque two-stop gradient per step (no alpha, see bands2d). gid must be unique in the deck."""
    cols = []
    for i in range(nt):
        t = (i + 0.5) / nt
        col = [F.pdf(t, fr.yr[1] - (j + 0.5) / nx * (fr.yr[1] - fr.yr[0])) for j in range(nx)]
        m = max(col) or 1.0
        cols.append([c / m for c in col])
    vals = [[cols[i][j] for i in range(nt)] for j in range(nx)]
    alphas = _cum(ops)
    grads = ''.join(f'<linearGradient id="{gid}{i}" gradientUnits="userSpaceOnUse" x1="{fr.x:g}" y1="0" x2="{fr.x + fr.w:g}" y2="0">'
                    f'<stop offset="0" stop-color="{_mix(base, c0, a)}"/><stop offset="1" stop-color="{_mix(base, c1, a)}"/></linearGradient>'
                    for i, a in enumerate(alphas))
    return f'<defs>{grads}</defs>' + _band_paths(vals, fr, levels, [f'url(#{gid}{i})' for i in range(len(alphas))])


def strands(F, fr, n, seed, color=INK, sw=1.6, op=0.5, steps=64):
    """n sample paths of F between real end samples, as smooth curves. Returns (svg, [(x0, x1)])."""
    rng = random.Random(seed)
    out, ends = '', []
    for k in range(n):
        x0, x1 = F.draw(rng)
        out += polyline([fr.px(t, v) for t, v in bridge(x0, x1, F.sig, steps, seed * 100 + k)], color, sw, op)
        ends.append((x0, x1))
    return out, ends


def vprofile(pdf, fr, at_x, bulge, fill, stroke, n=160):
    """A 1-D density as a filled profile along the frame's vertical axis at x = at_x, bulging by `bulge` px (negative = to the left)."""
    lo, hi = fr.yr
    vs = [pdf(lo + (hi - lo) * k / n) for k in range(n + 1)]
    m = max(vs) or 1.0
    pts = [(at_x + bulge * v / m, fr.y + fr.h - fr.h * k / n) for k, v in enumerate(vs)]
    d = f'M{at_x:g} {fr.y + fr.h:g} ' + ' '.join(f'L{x:.1f} {y:.1f}' for x, y in pts) + f' L{at_x:g} {fr.y:g} Z'
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="2.2" stroke-linejoin="round"/>'


def hprofile(pdf, lo, hi, x0, x1, base_y, bulge, fill=OCHRE_FILL, stroke=OCHRE, n=160):
    """A 1-D density as a filled profile along a horizontal baseline, bulging upward."""
    vs = [pdf(lo + (hi - lo) * k / n) for k in range(n + 1)]
    m = max(vs) or 1.0
    pts = [(x0 + (x1 - x0) * k / n, base_y - bulge * v / m) for k, v in enumerate(vs)]
    d = f'M{x0:g} {base_y:g} ' + ' '.join(f'L{x:.1f} {y:.1f}' for x, y in pts) + f' L{x1:g} {base_y:g} Z'
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="2.2" stroke-linejoin="round"/>'


# ---------------------------------------------------------------- page
def _plate(svg, html, box, cls='panel'):
    x, y, w, h = box
    return (f'<div class="{cls}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            f'<svg class="sc" width="{w - 40}" height="{h - 40}" viewBox="0 0 {w - 40} {h - 40}">{svg}</svg>{html}</div>')


def notes(*paras):
    return '<aside class="notes">' + ''.join(f'<p>{p}</p>' for p in paras) + '</aside>'


def _note(note):
    return note if note.lstrip().startswith('<aside') else f'<aside class="notes">{note}</aside>'


def _sec(section):
    if section not in _S.sections:
        raise ValueError(f'section "{section}" is not in init(sections=…): {_S.sections}')
    return _S.sections.index(section)


def _closing(s):
    """The closing line: <b>key phrase</b> and $math$ are kept; a particle stays on the line of the key phrase it follows."""
    t = re.sub(r'(<b>[^<]*</b>)([^\s<]+)', r'<span class="nb">\1\2</span>', s)
    return f'<div class="takeaway"><span>{t}</span></div>'


def _recall(rows):
    """The symbols or metrics a slide uses, stacked upward from the closing card: [(tex or name, meaning)]."""
    if not rows:
        return ''
    pitch = 42
    top = CARD_TOP - 34 - pitch * len(rows)
    out = [f'<div class="recall-rule" style="top:{top - 14}px"></div>']
    for i, (sym, mean) in enumerate(rows):
        term = '' if '$' in sym else ' term'     # a symbol (KaTeX) or a metric's name defined at first use
        out.append(f'<p class="recall{term}" style="top:{top + i * pitch + 6}px"><span class="sym">{sym}</span><span>{mean}</span></p>')
    return ''.join(out)


def cover(title, subtitle='', venue='', who='', aff='', hero='', hero_html='', note=''):
    """The title slide. title is HTML: <em> marks the indigo words, <br> breaks the line, <small> an English sub-line.
    hero is the SVG of one figure on the right-hand plate (868 x 888)."""
    body = f'<h1>{title}</h1>'
    for cls, val in (('subtitle', subtitle), ('venue', venue), ('who', who), ('aff', aff)):
        if val:
            body += f'\n  <div class="{cls}">{val}</div>'
    plate = '\n  ' + _plate(hero, hero_html, COVER, 'panel cover') if hero else ''
    return (f'<section class="slide title-slide fo-cover" data-title="{_plain(title)}" data-section="표지">\n  {body}\n  <!--spine:-1:0-->{plate}\n'
            f'  {_note(note)}\n</section>')


def opener(section, question, note=''):
    """A section opener: the section number and the one question the section answers, on ink."""
    i = _sec(section)
    return (f'<section class="slide fo-dark" data-title="{_plain(question)}" data-section="{section}">\n'
            f'  <div class="sec-big">{i + 1:02d}</div>\n  <div class="sec-name">{section}</div>\n  <h2><span>{question}</span></h2>\n  <!--spine:{i}:1-->\n'
            f'  {_note(note)}\n</section>')


def slide(section, sub, title, svg='', html='', closing='', cite='', note='', recall=()):
    """Rail + plate. title is the slide's point as a noun phrase (four lines at most in the rail); recall = [(tex or name, meaning)],
    four rows at most; svg and html are the figure of the plate in scene coordinates (1176 x 888)."""
    i = _sec(section)
    kick = f'<div class="kicker"><span class="sec">{i + 1:02d}</span><span>{section}{" · " + sub if sub else ""}</span></div>'
    return (f'<section class="slide fo" data-title="{_plain(title)}" data-section="{section}">\n'
            f'  {kick}\n  <h2>{title}</h2>\n  {_recall(recall)}\n  {_closing(closing)}\n  <!--spine:{i}:0-->\n'
            f'  {_plate(svg, html, PLATE)}\n  <div class="cite">{cite}</div>\n  {_note(note)}\n</section>')


def spread(kicker, title, svg='', html='', closing='', cite='', note='', section='부록', backup=True):
    """A full-width plate (1744 x 650) under a one-line title, for a table or a wide figure. backup=True puts it after the closing
    slide's count: it is numbered B1, B2, … and has no spine."""
    return (f'<section class="slide fo fo-spread" data-title="{_plain(title)}" data-section="{section}"{" data-backup" if backup else ""}>\n'
            f'  <div class="kicker"><span>{kicker}</span></div>\n  <h2>{title}</h2>\n  {_plate(svg, html, SPREAD)}\n  {_closing(closing)}\n'
            f'  <div class="cite">{cite}</div>\n  {_note(note)}\n</section>')


def _spine(counts, sec_i, k, dark, h=SPINE_H, gap=12):
    """One segment per section (length by slide count); the current section in ink, a dot at slide k of that section."""
    quiet, loud = ('#5E6369', PAPER) if dark else (RULE, INK)
    if sec_i < 0 or not counts:           # the cover: one unbroken hairline
        return f'<svg class="spine" width="24" height="{h}" viewBox="0 0 24 {h}"><line x1="12" y1="0" x2="12" y2="{h}" stroke="{quiet}" stroke-width="1.6" stroke-linecap="round"/></svg>'
    live = [i for i in sorted(counts) if counts[i]]
    unit = (h - gap * (len(live) - 1)) / sum(counts[i] for i in live)
    out, y = [], 0.0
    for i in live:
        L = unit * counts[i]
        on = i == sec_i
        out.append(f'<line x1="12" y1="{y:.1f}" x2="12" y2="{y + L:.1f}" stroke="{loud if on else quiet}" stroke-width="{2.6 if on else 1.6}" stroke-linecap="round"/>')
        if on:
            out.append(f'<circle cx="12" cy="{y + L * (k + 0.5) / counts[i]:.1f}" r="6.5" fill="{loud}" stroke="{INK if dark else PAPER}" stroke-width="2.5"/>')
        y += L + gap
    return f'<svg class="spine" width="24" height="{h}" viewBox="0 0 24 {h}">{"".join(out)}</svg>'


def write_deck(slides):
    """Fill in the spines from the order of the slides, replace the slides of deck/index.html (the head written by
    new_deck.py --theme folio stays) and return the path."""
    mark = re.compile(r'<!--spine:(-?\d+):(\d)-->')
    counts, seen, out = {}, {}, []
    for s in slides:
        m = mark.search(s)
        if m and int(m.group(1)) >= 0:
            counts[int(m.group(1))] = counts.get(int(m.group(1)), 0) + 1
    for s in slides:
        m = mark.search(s)
        if m:
            i, dark = int(m.group(1)), m.group(2) == '1'
            k = seen.get(i, 0)
            seen[i] = k + 1
            s = s[:m.start()] + _spine(counts, i, k, dark) + s[m.end():]
        out.append(s)
    start = '<div class="viewport"><div class="stage">'
    index = _S.deck / 'index.html'
    doc = index.read_text(encoding='utf-8')
    if 'theme-folio.css' not in doc:
        raise SystemExit(f'{index} is not a Folio deck: scaffold it with new_deck.py --theme folio')
    head = doc[:doc.index(start) + len(start)]
    index.write_text(head + '\n\n' + '\n\n'.join(out) + '\n\n</div></div>\n</body>\n</html>\n', encoding='utf-8')
    print(f'{index} · {len(out)} slides')
    return index

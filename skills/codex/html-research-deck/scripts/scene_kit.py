#!/usr/bin/env python3
"""scene_kit.py — the drawing kit of the accepted Claude Opus 5.5 decks, importable from any deck's work/build.py.

    import sys; sys.path.insert(0, '<skill>/scripts')
    from scene_kit import *
    init('<talk>/deck')                       # where assets/figs and index.html live
    ...
    write_deck([cover(...), slide(...), ...])

scripts/kit_gallery.py is the worked example: thirteen slides with toy content, rendered in assets/kit-gallery/. Copy a slide's code from there,
keep its sizes and positions, and change the content. Scene coordinates are local to the panel's <svg> (panel x, y + 20); fx() and tex() take the
same coordinates and add the padding themselves.

    cover()            title slide: the title sits on the warm stage, never in a white box; optional figure panel on the right
    slide(), panel(), notes(), lane()      a content slide; layout presets FULL, L2/R2, LW/RN, P3A/P3B/P3C pass check_deck.py's grid
    hero_bridge()      the big picture of a transport between two distributions: density field, sample paths, a filled profile at each end
    field(), strands(), vprof()            its parts, for a smaller or partial version; Field is the density of x_t between the ends
    dens()             a 2-D distribution: density raster plus real samples (density.cloud); no outline around it
    chain()            a left-to-right row of actors joined by arrows, sized to fill the given width
    enc(), dec(), model_box(), grid(), photo(), picture()   one actor, one drawing on every slide
    bars(), legend(), big()                charts from numbers, with bold value labels and the key number large
    T(), lines(), tex(), fx()              text, several lines, a label with KaTeX, a KaTeX strip (cls 'box' grey, 'box blue' the deck's key equation)
    node(), edge()     a causal graph: circles and arrows trimmed to their rims
    plot_axes(), dots(), fit_line(), swarm(), box_stat()   small plots: scatter with a fit, dots on a number line, box plots
    arrow(), qarrow(), curve(), arr(), line(), rect(), circle(), strand(), badge(), check_mark(), lock(), cross()
No reported number ever comes from these drawings; the cite line says what is schematic.
"""
import hashlib
import json
import math
import random
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
from density import (Frame, bridge, brownian, cloud, gauss1, gaussian, gmm, laplace, laplace1, mixture1, profile, profile_path, samples, uniform,  # noqa: E402,F401
                     uniform1, write_png)

NAVY, INK, SOFT, MUTED = '#1D3A5F', '#1F2933', '#52606D', '#66727F'
BLUE, BLUED, PALE = '#4C72B0', '#2F4C7D', '#DCE6F5'
AMBER, AMBERD, STEEL, STEELD = '#D9A552', '#B7793A', '#7FA7C9', '#4F7CA3'
RED, CORAL, GRAY, GRAYL, GHOST = '#D1495B', '#E76F51', '#8E9AA6', '#CDD3D9', '#AEB7C0'
BAR_OTHER = '#C5CDD5'

FULL = (110, 176, 1700, 722)
L2, R2 = (110, 176, 838, 722), (972, 176, 838, 722)
LW, RN = (110, 176, 1012, 722), (1146, 176, 664, 722)
P3A, P3B, P3C = (110, 176, 550, 722), (684, 176, 552, 722), (1260, 176, 550, 722)

BIMODAL = [(0.5, -1.25, 0.32), (0.5, 1.25, 0.32)]
XR2, YR2 = (-2.3, 2.3), (-2.3, 2.3)
DOTS = {STEEL: '#3F66A6', AMBER: AMBERD, '#9AA5B1': '#7C8894'}

_S = SimpleNamespace(deck=None, figs=None, cache_file=None, cache={})


def init(deck_dir):
    """Set the deck folder (holds index.html and assets/figs); call once at the top of build.py."""
    _S.deck = Path(deck_dir).resolve()
    _S.figs = _S.deck / 'assets' / 'figs'
    _S.figs.mkdir(parents=True, exist_ok=True)
    _S.cache_file = _S.figs / '.figcache.json'
    _S.cache = json.loads(_S.cache_file.read_text()) if _S.cache_file.exists() else {}


def write_deck(slides):
    """Replace the slides of deck/index.html (the head written by new_deck.py stays) and return the path."""
    mark = '<div class="viewport"><div class="stage">'
    index = _S.deck / 'index.html'
    doc = index.read_text(encoding='utf-8')
    head = doc[:doc.index(mark) + len(mark)]
    index.write_text(head + '\n\n' + '\n\n'.join(slides) + '\n\n</div></div>\n</body>\n</html>\n', encoding='utf-8')
    _S.cache_file.write_text(json.dumps(_S.cache, indent=0))
    print(f'{index} · {len(slides)} slides')
    return index


def _once(name, key, make):
    """A slow raster is rewritten only when its parameters change."""
    path = _S.figs / f'dens-{name}.png'
    digest = hashlib.sha256(repr(key).encode()).hexdigest()
    if _S.cache.get(name) != digest or not path.exists():
        make(path)
        _S.cache[name] = digest
    return f'assets/figs/{path.name}'


# ---------- text ----------
def T(x, y, s, size=24, w=None, fill=None, a=None):
    st = f'font-size:{size}px'
    if w:
        st += f';font-weight:{w}'
    if fill:
        st += f';fill:{fill}'
    anchor = f' text-anchor="{a}"' if a else ''
    return f'<text x="{x:g}" y="{y:g}"{anchor} style="{st}">{s}</text>'


def lane(x, y, s):
    return f'<text x="{x:g}" y="{y:g}" style="font-size:24px;font-weight:650;fill:{SOFT}">{s}</text>'


def inlabel(cx, cy, s, size=24, w=700, fill=None):
    return T(cx, cy + size * 0.36, s, size, w, fill, 'middle')


def lines(x, y, rows, size=24, lh=None, w=None, fill=None, a=None):
    lh = lh or round(size * 1.32)
    return ''.join(T(x, y + i * lh, r, size, w, fill, a) for i, r in enumerate(rows))


def big(x, y, s, size=36, fill=BLUE, a='middle'):
    """The one number a panel is about."""
    return T(x, y, s, size, 800, fill, a)


def fx(x, y, w, h, rows, size=26, cls='box'):
    """A formula strip (HTML + KaTeX). A row without $ is a Korean caption line. cls: 'box' grey, 'box blue' the deck's key equation."""
    ps = ''.join(f'<p>{r}</p>' if '$' in r else f'<p class="k">{r}</p>' for r in rows)
    return f'<div class="fx {cls}" style="left:{x + 20:g}px;top:{y + 20:g}px;width:{w:g}px;height:{h:g}px;font-size:{size}px">{ps}</div>'


def tex(x, y, s, size=24, w=600, color=None, a='start'):
    """A label with KaTeX: y is the baseline, x the start, middle or end by a."""
    tr = {'start': '', 'middle': 'transform:translateX(-50%);', 'end': 'transform:translateX(-100%);'}[a]
    col = f'color:{color};' if color else ''
    return f'<div class="fx" style="left:{x + 20:g}px;top:{y + 20 - size * 1.02:g}px;font-size:{size}px;font-weight:{w};{col}{tr}">{s}</div>'


# ---------- shapes ----------
def line(x1, y1, x2, y2, stroke=GRAY, sw=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{stroke}" stroke-width="{sw:g}"{d}/>'


def rect(x, y, w, h, rx=10, fill='#fff', stroke=GRAY, sw=2, dash=None, op=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    o = f' fill-opacity="{op}"' if op is not None else ''
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx:g}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:g}"{d}{o}/>'


def circle(cx, cy, r, fill='#fff', stroke='none', sw=2, op=None, dash=None):
    o = f' fill-opacity="{op}"' if op is not None else ''
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:g}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:g}"{o}{d}/>'


def curve(d, kind='ar', sw=None, dash=None):
    """kind: ar grey, ard dark grey, arb blue, grad blue dashed (a gradient), arc coral. The head sits on the tangent (sprite markers)."""
    style = {'ar': ('ar', 'ah', ''), 'ard': ('ar', 'ahd', f'stroke:{SOFT}'), 'arb': ('arb', 'ahb', ''),
             'grad': ('arb', 'ahb', 'stroke-dasharray:9 6'), 'arc': ('ar', 'ahc', f'stroke:{CORAL}')}[kind]
    st = style[2]
    if sw:
        st += f';stroke-width:{sw}'
    if dash:
        st += f';stroke-dasharray:{dash}'
    st = f' style="{st}"' if st else ''
    return f'<path class="{style[0]}" d="{d}" marker-end="url(#{style[1]})"{st}/>'


def arrow(x1, y1, x2, y2, kind='ar', sw=None, dash=None):
    return curve(f'M{x1:g} {y1:g} L{x2:g} {y2:g}', kind, sw, dash)


def qarrow(x1, y1, cx, cy, x2, y2, kind='ar', sw=None, dash=None):
    return curve(f'M{x1:g} {y1:g} Q{cx:g} {cy:g} {x2:g} {y2:g}', kind, sw, dash)


def arr(x1, y1, x2, y2, color=GRAY, sw=2.6, dash=None, size=14):
    """A straight arrow in any colour, for the cases arrow()'s four kinds do not cover. The shaft stops short of the head, which sits on the line."""
    d = math.hypot(x2 - x1, y2 - y1) or 1
    ux, uy = (x2 - x1) / d, (y2 - y1) / d
    bx, by = x2 - ux * size, y2 - uy * size
    nx, ny = -uy * size * 0.48, ux * size * 0.48
    return line(x1, y1, bx + ux * 2, by + uy * 2, color, sw, dash) + f'<path d="M{x2:.1f} {y2:.1f} L{bx + nx:.1f} {by + ny:.1f} L{bx - nx:.1f} {by - ny:.1f} Z" fill="{color}"/>'


def strand(pts, stroke=NAVY, sw=1.6, op=0.55, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    points = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    return f'<polyline points="{points}" fill="none" stroke="{stroke}" stroke-width="{sw:g}" stroke-opacity="{op:g}" stroke-linejoin="round"{d}/>'


# ---------- actors: one drawing on every slide ----------
def _trap(cx, cy, w, hl, hr, lab, size, ghost):
    x0, x1 = cx - w / 2, cx + w / 2
    pts = f'{x0:.1f},{cy - hl / 2:.1f} {x1:.1f},{cy - hr / 2:.1f} {x1:.1f},{cy + hr / 2:.1f} {x0:.1f},{cy + hl / 2:.1f}'
    if ghost:
        shape = f'<polygon points="{pts}" fill="none" stroke="{GHOST}" stroke-width="2.4" stroke-dasharray="7 5"/>'
    else:
        shape = f'<polygon points="{pts}" fill="url(#gGray)" stroke="{GRAY}" stroke-width="2.4"/>'
    return shape + (inlabel(cx, cy, lab, size, 700, MUTED if ghost else None) if lab else '')


def enc(cx, cy, w=130, h=100, narrow=0.5, lab='인코더', size=24, ghost=False):
    """Encoder: wide on the left, narrow on the right."""
    return _trap(cx, cy, w, h, h * narrow, lab, size, ghost)


def dec(cx, cy, w=130, h=100, narrow=0.5, lab='디코더', size=24, ghost=False):
    """Decoder: narrow on the left, wide on the right."""
    return _trap(cx, cy, w, h * narrow, h, lab, size, ghost)


def model_box(cx, cy, w=240, h=84, lab='모델', size=26):
    """The deck's main model: the one solid blue actor, the same box on every slide."""
    return rect(cx - w / 2, cy - h / 2, w, h, 14, BLUE, BLUED, 2.4) + (inlabel(cx, cy, lab, size, 700, '#fff') if lab else '')


def grid(cx, cy, s=60, ghost=False):
    """A latent code as a small grid; ghost = not observed."""
    out = rect(cx - s / 2, cy - s / 2, s, s, 8, 'none' if ghost else '#EEF2F7', GHOST if ghost else '#5F718A', 2.2, '6 5' if ghost else None)
    if not ghost:
        for k in (1, 2):
            out += line(cx - s / 2 + k * s / 3, cy - s / 2, cx - s / 2 + k * s / 3, cy + s / 2, '#5F718A', 1.4)
            out += line(cx - s / 2, cy - s / 2 + k * s / 3, cx + s / 2, cy - s / 2 + k * s / 3, '#5F718A', 1.4)
    return out


def photo(x, y, s, name):
    """A real image from the paper (assets/figs/<name>.png, taken out of the PDF with pdfimages, unprocessed)."""
    return f'<image href="assets/figs/{name}.png" x="{x:g}" y="{y:g}" width="{s:g}" height="{s:g}"/>'


def picture(x, y, s):
    """A stand-in when the paper has no image to show: a framed hill and sun."""
    w, h = s, s
    out = rect(x, y, w, h, 8, '#fff', '#5F718A', 2.2)
    out += f'<path d="M{x + 6:g} {y + h - 7:g} L{x + w * .36:g} {y + h * .42:g} L{x + w * .55:g} {y + h * .7:g} L{x + w * .7:g} {y + h * .52:g} L{x + w - 6:g} {y + h - 7:g} Z" fill="#EEF2F7" stroke="#5F718A" stroke-width="1.8" stroke-linejoin="round"/>'
    return out + circle(x + w * .76, y + h * .3, max(4, s / 12), '#E9B96A')


def lock(cx, cy, s=1.0, color=SOFT):
    r = 7.5 * s
    return (f'<path d="M{cx - r:.1f} {cy:.1f} v{-6 * s:.1f} a{r:.1f} {r:.1f} 0 0 1 {2 * r:.1f} 0 v{6 * s:.1f}" fill="none" stroke="{color}" stroke-width="{3 * s:.1f}"/>'
            + f'<rect x="{cx - 11 * s:.1f}" y="{cy:.1f}" width="{22 * s:.1f}" height="{17 * s:.1f}" rx="{3 * s:.1f}" fill="{color}"/>')


def cross(cx, cy, r=11):
    return (circle(cx, cy, r + 7, '#fff') + f'<line class="x" x1="{cx - r}" y1="{cy - r}" x2="{cx + r}" y2="{cy + r}"/>'
            + f'<line class="x" x1="{cx - r}" y1="{cy + r}" x2="{cx + r}" y2="{cy - r}"/>')


def badge(cx, cy, n):
    return circle(cx, cy, 17, NAVY) + T(cx, cy + 8, str(n), 22, 700, '#fff', 'middle')


def check_mark(cx, cy, on=True):
    if on:
        return circle(cx, cy, 24, NAVY) + (f'<path d="M{cx - 11} {cy + 1} L{cx - 3} {cy + 9} L{cx + 12} {cy - 9}" fill="none" stroke="#fff" '
                                           'stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>')
    return circle(cx, cy, 24, 'none', GHOST, 2.4, dash='6 5')


def node(cx, cy, label, r=36, hidden=False, outcome=False, size=24, stroke=None):
    """A variable in a causal graph: a flat circle; hidden = dashed and unfilled, outcome = amber. Label lines split on newline."""
    fill = 'none' if hidden else '#F8E3BF' if outcome else '#EEF2F7'
    edge_col = stroke or (GRAY if hidden else AMBERD if outcome else '#5F718A')
    out = circle(cx, cy, r, fill, edge_col, 2.6, dash='7 6' if hidden else None)
    parts = label.split('\n')
    lh = size * 1.18
    for k, part in enumerate(parts):
        out += T(cx, cy - (len(parts) - 1) * lh / 2 + k * lh + size * 0.36, part, size, 700, SOFT if hidden else None, 'middle')
    return out


def edge(x1, y1, x2, y2, r1=36, r2=36, color=GRAY, dash=None, sw=2.6):
    """An arrow between two nodes, trimmed to their rims."""
    d = math.hypot(x2 - x1, y2 - y1) or 1
    ux, uy = (x2 - x1) / d, (y2 - y1) / d
    return arr(x1 + ux * r1, y1 + uy * r1, x2 - ux * (r2 + 4), y2 - uy * (r2 + 4), color, sw, dash)


def plot_axes(x, y, w, h, xlab='', ylab=''):
    """L-shaped axes of a small schematic plot, with the axis letters beside the ends."""
    out = line(x, y, x, y + h, SOFT, 2) + line(x, y + h, x + w, y + h, SOFT, 2)
    return out + (T(x + w + 10, y + h + 8, xlab, 24, 600, SOFT) if xlab else '') + (T(x - 12, y + 16, ylab, 24, 600, SOFT, 'end') if ylab else '')


def dots(pts, x, y, w, h, fill=BLUE, r=5):
    """Scatter points of the unit square mapped into the frame (x, y, w, h)."""
    return ''.join(circle(x + px * w, y + h - py * h, r, fill) for px, py in pts)


def fit_line(pts, x, y, w, h, color=RED, sw=3, dash=None):
    """Least-squares line of unit-square points, across their x range inside the frame."""
    n = len(pts)
    mx, my = sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n
    den = sum((p[0] - mx) ** 2 for p in pts) or 1
    b = sum((p[0] - mx) * (p[1] - my) for p in pts) / den
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    return line(x + x0 * w, y + h - (my + b * (x0 - mx)) * h, x + x1 * w, y + h - (my + b * (x1 - mx)) * h, color, sw, dash)


def swarm(xs, y, r, color):
    """Dots on a number line (xs in scene px), stacked just enough that equal values stay visible."""
    placed, out = [], ''
    for v in sorted(xs):
        yy = y
        for k in (0, -1, 1, -2, 2, -3, 3):
            yy = y + k * (r + 3)
            if all(math.hypot(v - px, yy - py) >= 2 * r + 1 for px, py in placed):
                break
        placed.append((v, yy))
        out += circle(v, yy, r, color, '#fff', 1.2)
    return out


def box_stat(x, stat, y_of, color=BLUE, w=46):
    """One box of a box plot: whiskers, quartile box and a white median line. stat = (low, q1, median, q3, high); y_of maps a value to scene y."""
    lo, q1, med, q3, hi = stat
    return (line(x, y_of(lo), x, y_of(hi), color, 2.4) + rect(x - w / 2, y_of(q3), w, y_of(q1) - y_of(q3), 2, color, 'none', 0)
            + line(x - w / 2, y_of(med), x + w / 2, y_of(med), '#fff', 3))


# ---------- distributions ----------
def dens(name, dist, x, y, w, h, xr=XR2, yr=YR2, tint=STEEL, n=36, seed=1, r=None, alpha=0.72):
    """A 2-D distribution: raster fading along the density itself, plus real samples. Over 250 px wide: 70-80 dots at r 2.3; smaller: 40-60 at r 1.6-1.9; under 100 px: raster alone."""
    return cloud(dist, Frame(x, y, w, h, xr, yr), _S.figs, name, tint=tint, n=n, seed=seed, r=r or (2.3 if w > 250 else 1.8), dot=DOTS.get(tint), alpha=alpha)


def vprof(pdf, lo, hi, axis_x, ybot, ytop, bulge, fill, stroke, op=0.75, sw=2, dash=None):
    """A 1-D density on a vertical axis: value lo at ybot, hi at ytop, bulging sideways by bulge px (negative = to the left)."""
    d = profile_path(profile(pdf, lo, hi, 160), (ybot, ytop), axis_x, bulge, vertical=True)
    ds = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw:g}"{ds}/>'


class Field:
    """Marginal density p_t(x) of x_t = (1-t) x0 + t x1 + sig*sqrt(t(1-t)) eps, with x0 ~ N(mu0, s0²) and x1 a Gaussian mixture [(weight, mean, sd), …]."""

    def __init__(self, s0=0.62, comps=BIMODAL, sig=1.0, mu0=0.0):
        self.s0, self.comps, self.sig, self.mu0 = s0, comps, sig, mu0

    def pdf(self, t, x):
        p = 0.0
        for w, mu, sd in self.comps:
            m = (1 - t) * self.mu0 + t * mu
            v = max((1 - t) ** 2 * self.s0 ** 2 + t * t * sd * sd + self.sig ** 2 * t * (1 - t), 1e-6)
            p += w * math.exp(-0.5 * (x - m) ** 2 / v) / math.sqrt(v)
        return p

    def p0(self):
        return gauss1(self.mu0, self.s0)

    def p1(self):
        return mixture1(self.comps)


def _field_png(F, path, fr, ca=AMBER, cb=STEEL, alpha=0.8, gamma=0.5, scale=1.2, fade=0.0):
    W, H = int(fr.w * scale), int(fr.h * scale)
    ca_, cb_ = [tuple(int(c.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)) for c in (ca, cb)]
    cols = []
    for i in range(W):
        t = (i + 0.5) / W
        col = [F.pdf(t, fr.yr[1] - (j + 0.5) / H * (fr.yr[1] - fr.yr[0])) for j in range(H)]
        mx = max(col) or 1.0
        cols.append([c / mx for c in col])
    rows = []
    for j in range(H):
        row = bytearray()
        for i in range(W):
            t = (i + 0.5) / W
            q = cols[i][j]
            a = q ** gamma * min(1.0, q / 0.05)
            if fade:
                a *= min(1.0, t / fade, (1 - t) / fade)
            row += bytes((int(ca_[0] + (cb_[0] - ca_[0]) * t), int(ca_[1] + (cb_[1] - ca_[1]) * t), int(ca_[2] + (cb_[2] - ca_[2]) * t), int(255 * alpha * a)))
        rows.append(bytes(row))
    write_png(path, W, H, rows)


def field(name, F, x, y, w, h, yr=(-2.7, 2.7), **kw):
    """The (t, x) plane as a density raster whose colour moves from the prior's amber to the target's steel. Returns (frame, image svg)."""
    fr = Frame(x, y, w, h, (0.0, 1.0), yr)
    href = _once(name, ('field', F.s0, tuple(F.comps), F.sig, F.mu0, w, h, yr, sorted(kw.items())), lambda p: _field_png(F, p, fr, **kw))
    return fr, fr.image(href)


def strands(fr, F, n, seed, stroke=NAVY, sw=1.7, op=0.6, steps=64):
    """n sample paths of F between real end samples, as smooth curves. Returns (svg, [(x0, x1), …])."""
    rng = random.Random(seed)
    out, ends = '', []
    for k in range(n):
        x0 = rng.gauss(F.mu0, F.s0)
        u, acc, pick = rng.random(), 0.0, F.comps[-1]
        for c in F.comps:
            acc += c[0]
            if u <= acc:
                pick = c
                break
        x1 = rng.gauss(pick[1], pick[2])
        out += strand([fr.px(t, v) for t, v in bridge(x0, x1, F.sig, steps, seed * 100 + k)], stroke, sw, op)
        ends.append((x0, x1))
    return out, ends


def hero_bridge(name, F, x0, x1, y0, y1, yr=(-2.7, 2.7), bulge=170, n=9, seed=7, axis=True, dots=True):
    """The big transport picture between two distributions, spanning scene x0..x1 and y0..y1, with a filled profile bulging outward at each end.
    Leave bulge px free on both sides. Returns (frame, svg); put the labels on with tex()."""
    fr, img = field(name, F, x0, y0, x1 - x0, y1 - y0, yr)
    paths, ends = strands(fr, F, n, seed)
    s = img + paths
    s += vprof(F.p0(), yr[0], yr[1], x0, y1, y0, -bulge, AMBER, AMBERD) + vprof(F.p1(), yr[0], yr[1], x1, y1, y0, bulge, STEEL, STEELD)
    if dots:
        for a, b in ends:
            s += circle(*fr.px(0, a), 5, AMBERD, '#fff', 1.5) + circle(*fr.px(1, b), 5, STEELD, '#fff', 1.5)
    if axis:
        s += line(x0, y1 + 12, x1, y1 + 12, GRAY, 2)
        for t in (0, 0.5, 1):
            s += line(x0 + t * (x1 - x0), y1 + 12, x0 + t * (x1 - x0), y1 + 21, GRAY, 2)
    return fr, s


# ---------- chains and charts ----------
def chain(y, parts, x0=0, x1=798, kind='ar', name='chain'):
    """A row of actors joined by arrows, spread over x0..x1 so the row fills its panel. Each part is one of
    ('photo', image, size) ('picture', size) ('enc', w, h, label) ('dec', w, h, label) ('model', w, h, label) ('grid', size) ('prior', size) ('latent', size).
    Returns (svg, centres); use centres to hang labels, locks and gradient arrows on the actors."""
    widths = []
    for p in parts:
        widths.append(p[1] if p[0] in ('enc', 'dec', 'model', 'grid', 'prior', 'latent', 'picture') else p[2])
    gap = (x1 - x0 - sum(widths)) / (len(parts) - 1)
    if gap < 34:
        raise ValueError(f'chain does not fit: {gap:.0f} px between actors; shrink an actor or widen the row')
    out, centres, x = '', [], x0
    for i, (p, w) in enumerate(zip(parts, widths)):
        cx = x + w / 2
        centres.append(cx)
        k = p[0]
        if k == 'photo':
            out += photo(x, y - w / 2, w, p[1])
        elif k == 'picture':
            out += picture(x, y - w / 2, w)
        elif k == 'enc':
            out += enc(cx, y, w, p[2], lab=p[3] if len(p) > 3 else '인코더')
        elif k == 'dec':
            out += dec(cx, y, w, p[2], lab=p[3] if len(p) > 3 else '디코더')
        elif k == 'model':
            out += model_box(cx, y, w, p[2], p[3] if len(p) > 3 else '모델')
        elif k == 'grid':
            out += grid(cx, y, w)
        elif k == 'prior':
            out += dens(f'{name}-{i}', gaussian((0, 0), (0.85, 0.85)), x, y - w / 2, w, w, tint=AMBER, n=0 if w < 100 else 26, seed=i + 3)
        elif k == 'latent':
            d = gmm([(0.34, (-0.95, 0.8), (0.34, 0.3)), (0.36, (1.0, 0.45), (0.36, 0.34)), (0.3, (0.0, -1.1), (0.36, 0.3))])
            out += dens(f'{name}-{i}', d, x, y - w / 2, w, w, tint=STEEL, n=0 if w < 100 else 26, seed=i + 5)
        else:
            raise ValueError(k)
        if i < len(parts) - 1:
            out += arrow(x + w + 4, y, x + w + gap - 6, y, kind)
        x += w + gap
    return out, centres


def legend(x, y, items, size=23):
    """Colour squares with names on one line: items = [(name, colour), …]."""
    out = ''
    for lab, col in items:
        out += rect(x, y - 18, 22, 22, 4, col, 'none', 0) + T(x + 30, y, lab, size, 600)
        x += 30 + len(lab) * size * 0.78 + 28
    return out


def bars(x0, x1, base, top, groups, vmax, colors=(BLUE, BAR_OTHER), inks=(BLUE, INK), fmt='{:g}', val_size=30, name_size=26, hl=(), hl_color=BLUE):
    """Bars from numbers, wide and with bold values above them: groups = [(name, [v1, v2, …]), …], one colour per series, zero at base, vmax at top.
    hl = {(group, series), …} paints a bar in hl_color (a single series with one bar picked out). Names under the axis take KaTeX. Returns (svg, html)."""
    slot = (x1 - x0) / len(groups)
    k = len(groups[0][1])
    bw = min(96, (slot * 0.8 - (k - 1) * 8) / k)
    s, h = '', ''
    for i, (nm, vals) in enumerate(groups):
        cx = x0 + slot * (i + 0.5)
        left = cx - (k * bw + (k - 1) * 8) / 2
        for j, v in enumerate(vals):
            on = (i, j) in hl
            yt = base - (base - top) * v / vmax
            s += rect(left + j * (bw + 8), yt, bw, base - yt, 5, hl_color if on else colors[j % len(colors)], 'none', 0)
            s += T(left + j * (bw + 8) + bw / 2, yt - 12, fmt.format(v), val_size, 700, hl_color if on else inks[j % len(inks)], 'middle')
        h += tex(cx, base + 42, nm, name_size, 650, None, 'middle')
    return s + line(x0, base, x1, base, GRAY, 2), h


# ---------- slides ----------
def panel(x, y, w, h, svg='', html='', cls='panel'):
    iw, ih = w - 40, h - 40
    return (f'<div class="{cls}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            f'<svg class="sc" width="{iw}" height="{ih}" viewBox="0 0 {iw} {ih}">{svg}</svg>{html}</div>')


def notes(*paras):
    return '<aside class="notes">' + ''.join(f'<p>{p}</p>' for p in paras) + '</aside>'


def slide(section, kicker, h2, panels, closing, cite, note):
    """One content slide. h2 is the point of the slide, closing the one line under the panels."""
    plain = h2.replace('$', '').replace('\\', '')
    return (f'<section class="slide" data-title="{plain}" data-section="{section}">\n'
            f'  <div class="kicker blue">{kicker}</div>\n  <h2>{h2}</h2>\n  ' + '\n  '.join(panels) + '\n'
            f'  <div class="takeaway">{closing}</div>\n  <div class="cite">{cite}</div>\n  {note}\n</section>')


def cover(title, english='', subtitle='', who='', aff='', venue='', hero='', hero_html='', note='', section='표지'):
    """The title slide. The title sits on the warm stage, never in a white box, with no kicker, closing line or h2.
    title is HTML: <em> marks the blue words, <br> breaks the line. hero is the optional SVG of one figure on the right-hand panel; with a hero, break the title into three lines."""
    plain = title.replace('<br>', ' ').replace('<em>', '').replace('</em>', '')
    tall = title.count('<br>') >= 2
    h1 = f'{title}<small>{english}</small>' if english else title
    st = ['top:176px;width:880px;font-size:78px', 'top:540px', 'top:666px', 'top:718px', 'top:798px'] if tall else [f'width:{880 if hero else 1500}px', '', '', '', '']
    a = lambda s: f' style="{s}"' if s else ''
    body = f'<h1{a(st[0])}>{h1}</h1>'
    for cls, val, sty in (('subtitle', subtitle, st[1]), ('who', who, st[2]), ('aff', aff, st[3]), ('venue', venue, st[4])):
        if val:
            body += f'\n  <div class="{cls}"{a(sty)}>{val}</div>'
    if hero:
        body += '\n  ' + panel(1030, 176, 780, 722, hero, hero_html, 'panel cover')
    return f'<section class="slide title-slide" data-title="{plain}" data-section="{section}">\n  {body}\n  {note}\n</section>'

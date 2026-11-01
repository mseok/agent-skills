#!/usr/bin/env python3
"""density.py — distributions drawn from numbers, not from hand-drawn blobs (standard library only).

The reference deck (Yuanqi Du, 2026) draws every distribution the same way: a density raster whose alpha follows
(p/p_max)^0.5 in one tint, real samples of that distribution on top, and 1-D densities as filled profiles along an
axis. This module gives a builder the same pieces as SVG/PNG:

    from density import gaussian, gmm, laplace, uniform, density_png, samples, profile, bridge, Frame

    d = gmm([(0.3, (-1.2, 0.8), (0.45, 0.4)), (0.4, (0.9, 0.3), (0.5, 0.5)), (0.3, (0.1, -1.1), (0.4, 0.35))])
    fr = Frame(x=420, y=140, w=300, h=220, xr=(-2.6, 2.6), yr=(-2.2, 2.2))     # scene px box ↔ data window
    density_png(d, deck/'assets/figs/dens-data.png', fr, tint='#7FA7C9')         # writes an RGBA PNG (alpha = density)
    svg  = fr.image('assets/figs/dens-data.png')                                  # <image …> element for the scene
    pts  = [fr.px(x, y) for x, y in samples(d, 60, seed=7)]                        # real samples → circles

Distributions: gaussian(mu, sd), laplace(mu, b), uniform(lo, hi), gmm([(weight, mu, sd), …]); each has
.logpdf(x, y) and .sample(rng). profile(pdf1d, lo, hi, n) returns a normalised 1-D curve; bridge(x0, x1, sigma, n, seed)
returns a stochastic-interpolant path x_t = (1-t) x0 + t x1 + sigma * B_t with a Brownian bridge B_t (Var t(1-t)).
No reported number ever comes from these drawings; the cite line still says what is schematic.
"""
import math
import random
import struct
import zlib
from pathlib import Path


class _Dist:
    def logpdf(self, x, y):
        raise NotImplementedError

    def sample(self, rng):
        raise NotImplementedError


class gaussian(_Dist):
    def __init__(self, mu=(0.0, 0.0), sd=(1.0, 1.0)):
        self.mu, self.sd = mu, (sd if isinstance(sd, (tuple, list)) else (sd, sd))

    def logpdf(self, x, y):
        return -0.5 * (((x - self.mu[0]) / self.sd[0]) ** 2 + ((y - self.mu[1]) / self.sd[1]) ** 2) - math.log(self.sd[0] * self.sd[1])

    def sample(self, rng):
        return (rng.gauss(self.mu[0], self.sd[0]), rng.gauss(self.mu[1], self.sd[1]))


class laplace(_Dist):
    def __init__(self, mu=(0.0, 0.0), b=(0.7, 0.7)):
        self.mu, self.b = mu, (b if isinstance(b, (tuple, list)) else (b, b))

    def logpdf(self, x, y):
        return -abs(x - self.mu[0]) / self.b[0] - abs(y - self.mu[1]) / self.b[1] - math.log(self.b[0] * self.b[1])

    def sample(self, rng):
        def one(m, b):
            u = rng.random() - 0.5
            return m - b * math.copysign(1, u) * math.log(1 - 2 * abs(u))
        return (one(self.mu[0], self.b[0]), one(self.mu[1], self.b[1]))


class uniform(_Dist):
    """A box; the raster edge is softened over `soft` data units so it reads as a density, not a rectangle."""
    def __init__(self, lo=(-1.5, -1.5), hi=(1.5, 1.5), soft=0.12):
        self.lo, self.hi, self.soft = lo, hi, soft

    def logpdf(self, x, y):
        def edge(v, a, b):
            d = min(v - a, b - v)
            return 0.0 if d >= 0 else -(d / self.soft) ** 2
        return edge(x, self.lo[0], self.hi[0]) + edge(y, self.lo[1], self.hi[1])

    def sample(self, rng):
        return (rng.uniform(self.lo[0], self.hi[0]), rng.uniform(self.lo[1], self.hi[1]))


class gmm(_Dist):
    def __init__(self, comps):
        self.comps = [(w, mu, (sd if isinstance(sd, (tuple, list)) else (sd, sd))) for w, mu, sd in comps]
        z = sum(w for w, _, _ in self.comps)
        self.comps = [(w / z, mu, sd) for w, mu, sd in self.comps]

    def logpdf(self, x, y):
        ls = [math.log(w) - 0.5 * (((x - mu[0]) / sd[0]) ** 2 + ((y - mu[1]) / sd[1]) ** 2) - math.log(sd[0] * sd[1]) for w, mu, sd in self.comps]
        m = max(ls)
        return m + math.log(sum(math.exp(l - m) for l in ls))

    def sample(self, rng):
        u, acc = rng.random(), 0.0
        for w, mu, sd in self.comps:
            acc += w
            if u <= acc:
                return (rng.gauss(mu[0], sd[0]), rng.gauss(mu[1], sd[1]))
        w, mu, sd = self.comps[-1]
        return (rng.gauss(mu[0], sd[0]), rng.gauss(mu[1], sd[1]))


class Frame:
    """A scene-pixel box (x, y, w, h) showing the data window xr × yr (y up)."""
    def __init__(self, x, y, w, h, xr=(-3.0, 3.0), yr=(-3.0, 3.0)):
        self.x, self.y, self.w, self.h, self.xr, self.yr = x, y, w, h, xr, yr

    def px(self, dx, dy):
        return (self.x + (dx - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w,
                self.y + self.h - (dy - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h)

    def data(self, px, py):
        return (self.xr[0] + (px - self.x) / self.w * (self.xr[1] - self.xr[0]),
                self.yr[0] + (self.y + self.h - py) / self.h * (self.yr[1] - self.yr[0]))

    def image(self, href):
        return f'<image href="{href}" x="{self.x:g}" y="{self.y:g}" width="{self.w:g}" height="{self.h:g}"/>'


def _hex(c):
    c = c.lstrip('#')
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def write_png(path, w, h, rows):
    """rows: iterable of bytes objects, each 4*w bytes of RGBA."""
    raw = b''.join(b'\x00' + r for r in rows)

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))
    Path(path).write_bytes(png)
    return path


def density_png(dist, path, frame, tint='#7FA7C9', alpha=0.72, gamma=0.5, scale=1.0, floor=0.015):
    """Raster of (p/p_max)^gamma as the alpha of one tint, the way the reference deck shades densities.
    scale > 1 renders more pixels than the frame (crisper on retina / print); values below `floor` become fully transparent."""
    w, h = max(2, int(round(frame.w * scale))), max(2, int(round(frame.h * scale)))
    vals = []
    mx = -1e300
    for j in range(h):
        row = []
        for i in range(w):
            dx, dy = frame.data(frame.x + (i + 0.5) / scale, frame.y + (j + 0.5) / scale)
            v = dist.logpdf(dx, dy)
            row.append(v)
            if v > mx:
                mx = v
        vals.append(row)
    r, g, b = _hex(tint)
    rows = []
    for row in vals:
        out = bytearray()
        for v in row:
            a = math.exp(v - mx)
            q = a ** gamma if a > floor else 0.0
            out += bytes((r, g, b, int(round(255 * alpha * q))))
        rows.append(bytes(out))
    write_png(path, w, h, rows)
    return w, h


def samples(dist, n, seed=0):
    rng = random.Random(seed)
    return [dist.sample(rng) for _ in range(n)]


def profile(pdf, lo, hi, n=160):
    """Normalised 1-D density curve: [(x, p(x)/p_max)] on [lo, hi]."""
    xs = [lo + (hi - lo) * k / n for k in range(n + 1)]
    vs = [pdf(x) for x in xs]
    m = max(vs) or 1.0
    return [(x, v / m) for x, v in zip(xs, vs)]


def profile_path(curve, span_px, axis_x, bulge, vertical=True):
    """SVG path data of a filled profile. vertical=True: the variable runs along y from span_px[0] (lo) to span_px[1] (hi)
    at x = axis_x and the density bulges horizontally by `bulge` px (negative = to the left)."""
    lo, hi = curve[0][0], curve[-1][0]
    pts = []
    for x, v in curve:
        f = (x - lo) / (hi - lo)
        if vertical:
            pts.append((axis_x + bulge * v, span_px[0] + (span_px[1] - span_px[0]) * f))
        else:
            pts.append((span_px[0] + (span_px[1] - span_px[0]) * f, axis_x - bulge * v))
    start = (axis_x, span_px[0]) if vertical else (span_px[0], axis_x)
    end = (axis_x, span_px[1]) if vertical else (span_px[1], axis_x)
    d = [f'M{start[0]:.1f} {start[1]:.1f}'] + [f'L{px:.1f} {py:.1f}' for px, py in pts] + [f'L{end[0]:.1f} {end[1]:.1f} Z']
    return ' '.join(d)


def bridge(x0, x1, sigma, n=48, seed=0):
    """Stochastic-interpolant path between scalars (or equal-length tuples): [(t, x_t)], x_t = (1-t)x0 + t x1 + sigma*B_t."""
    rng = random.Random(seed)
    dim = len(x0) if isinstance(x0, (tuple, list)) else 1
    x0v = list(x0) if dim > 1 else [x0]
    x1v = list(x1) if dim > 1 else [x1]
    walks = []
    for _ in range(dim):
        w = [0.0]
        for _ in range(n):
            w.append(w[-1] + rng.gauss(0, math.sqrt(1 / n)))
        walks.append(w)
    out = []
    for k in range(n + 1):
        t = k / n
        xt = [(1 - t) * a + t * b + sigma * (w[k] - t * w[n]) for a, b, w in zip(x0v, x1v, walks)]
        out.append((t, xt[0] if dim == 1 else tuple(xt)))
    return out


def gauss1(mu=0.0, sd=1.0):
    return lambda x: math.exp(-0.5 * ((x - mu) / sd) ** 2) / sd


def laplace1(mu=0.0, b=1.0):
    return lambda x: math.exp(-abs(x - mu) / b) / b


def mixture1(comps):
    """comps: [(weight, mu, sd)] → 1-D pdf."""
    return lambda x: sum(w * math.exp(-0.5 * ((x - mu) / sd) ** 2) / sd for w, mu, sd in comps)


def uniform1(lo=-1.0, hi=1.0, soft=0.06):
    def f(x):
        d = min(x - lo, hi - x)
        return 1.0 if d >= 0 else math.exp(-(d / soft) ** 2)
    return f


if __name__ == '__main__':
    import sys
    import tempfile
    d = gmm([(0.3, (-1.2, 0.8), 0.45), (0.4, (0.9, 0.3), 0.5), (0.3, (0.1, -1.1), 0.4)])
    fr = Frame(0, 0, 240, 180, (-2.6, 2.6), (-2.2, 2.2))
    out = Path(tempfile.gettempdir()) / 'density-selftest.png'
    print(density_png(d, out, fr), out, len(samples(d, 10, 1)), bridge(-1.0, 1.0, 0.5, 8, 1)[-1], file=sys.stdout)

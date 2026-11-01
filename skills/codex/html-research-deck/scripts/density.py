#!/usr/bin/env python3
"""density.py — distributions drawn from numbers, not from hand-drawn blobs (standard library only).

The reference deck (Yuanqi Du, 2026) draws every distribution the same way: a density raster whose alpha follows
(p/p_max)^0.5 in one tint and dies away with the density itself, real samples of that distribution on top, and 1-D
densities as filled profiles along an axis. Paths between distributions are smooth curves. This module gives a builder
the same pieces as SVG/PNG, and cloud() is the one call a scene normally needs:

    from density import gaussian, gmm, laplace, uniform, cloud, profile, bridge, Frame

    d = gmm([(0.3, (-1.35, 0.95), (0.38, 0.32)), (0.4, (1.25, 0.55), (0.42, 0.34)), (0.3, (-0.05, -1.2), (0.36, 0.3))])
    fr = Frame(x=420, y=140, w=300, h=220, xr=(-3.4, 3.4), yr=(-2.8, 2.8))     # scene px box ↔ data window
    svg = cloud(d, fr, deck/'assets/figs', 'data', tint='#7FA7C9', n=60, seed=7, dot='#4C72B0')   # raster + samples as SVG
    pts = [fr.px(*xy) for _, xy in bridge(fr.data(100, 200), fr.data(300, 180), 0.4, seed=3)]     # a smooth path

Distributions: gaussian(mu, sd), laplace(mu, b), uniform(lo, hi), gmm([(weight, mu, sd), …]); each has .logpdf(x, y),
.sample(rng) and .peak(). Keep the modes of a multi-modal distribution apart (centres at least 3 sd apart) or it reads
as one blob. profile(pdf1d, lo, hi, n) returns a normalised 1-D curve; bridge(x0, x1, sigma, n, seed) returns a
stochastic-interpolant path x_t = (1-t) x0 + t x1 + sigma * B_t with B_t a Brownian bridge built from its first Fourier
terms, so the curve is smooth and still has the bridge's shape (Var close to t(1-t), zero at both ends).
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

    def peak(self):
        """The largest logpdf: at mu for one-peak distributions; gmm and uniform override it."""
        return self.logpdf(*self.mu)


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

    def peak(self):
        return 0.0


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

    def peak(self):
        return max(self.logpdf(*mu) for _, mu, _ in self.comps)


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


def density_png(dist, path, frame, tint='#7FA7C9', alpha=0.72, gamma=0.5, scale=1.0, fade=0.22):
    """Raster of (p/p_max)^gamma as the alpha of one tint, the way the reference deck shades densities. scale > 1 renders more
    pixels than the frame (crisper on retina / print). The colour dies away along the density's own level sets: q_e, the largest
    value on the frame border, and the band `fade` above it go smoothly to zero, so the cloud never shows the frame or a round
    rim of its own (Latent SI v9: a raised-cosine window on the frame read as a circle drawn around the dots)."""
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
    border = [v for k, row in enumerate(vals) for i, v in enumerate(row) if k in (0, h - 1) or i in (0, w - 1)]
    qe = math.exp(max(border) - mx) ** gamma
    r, g, b = _hex(tint)
    rows = []
    for row in vals:
        out = bytearray()
        for v in row:
            q = math.exp(v - mx) ** gamma
            s = min(1.0, max(0.0, (q - qe) / (fade * (1.0 - qe))))
            out += bytes((r, g, b, int(round(255 * alpha * q * s * s * (3.0 - 2.0 * s)))))
        rows.append(bytes(out))
    write_png(path, w, h, rows)
    return w, h


def samples(dist, n, seed=0, core=None):
    """n samples of dist. core keeps only those with p/p_max at or above it, so a dot never lands outside the visible cloud."""
    rng = random.Random(seed)
    if core is None:
        return [dist.sample(rng) for _ in range(n)]
    floor, out = dist.peak() + math.log(core), []
    while len(out) < n:
        xy = dist.sample(rng)
        if dist.logpdf(*xy) >= floor:
            out.append(xy)
    return out


def cloud(dist, frame, figs, name, tint='#7FA7C9', n=0, seed=0, r=2.6, dot=None, rim='#FFFFFF', alpha=0.72, scale=2.0, core=0.1, href_dir='assets/figs'):
    """One distribution for an SVG scene: writes <figs>/dens-<name>.png and returns the <image> plus n samples as dots.
    dot is the dot colour (default: tint); rim is a thin outline that keeps dots crisp over the raster. No outline around the cloud."""
    Path(figs).mkdir(parents=True, exist_ok=True)
    density_png(dist, Path(figs) / f'dens-{name}.png', frame, tint=tint, alpha=alpha, scale=scale)
    out = [frame.image(f'{href_dir}/dens-{name}.png')]
    for dx, dy in samples(dist, n, seed, core):
        px, py = frame.px(dx, dy)
        if frame.x + r < px < frame.x + frame.w - r and frame.y + r < py < frame.y + frame.h - r:
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:g}" fill="{dot or tint}" stroke="{rim}" stroke-width="0.7"/>')
    return ''.join(out)


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


def brownian(n=64, seed=0, modes=6, pin=True):
    """Standard Brownian noise on t = k/n from its first `modes` Karhunen-Loeve terms: a smooth curve. pin=True is a bridge,
    B_0 = B_1 = 0, sum of sqrt(2) sin(k pi t)/(k pi) Z_k (modes=6 keeps 93 % of the variance at t = 1/2); pin=False is a free
    path from B_0 = 0, sum of sqrt(2) sin((k-1/2) pi t)/((k-1/2) pi) Z_k."""
    rng = random.Random(seed)
    freq = [(k if pin else k - 0.5) * math.pi for k in range(1, modes + 1)]
    z = [rng.gauss(0, 1) for _ in freq]
    return [sum(zk * math.sqrt(2) * math.sin(f * k / n) / f for zk, f in zip(z, freq)) for k in range(n + 1)]


def bridge(x0, x1, sigma, n=64, seed=0, modes=6):
    """Stochastic-interpolant path between scalars (or equal-length tuples): [(t, x_t)], x_t = (1-t)x0 + t x1 + sigma*B_t,
    with B_t = brownian(); a smooth curve, not a jagged walk (the reference deck draws its paths this way)."""
    dim = len(x0) if isinstance(x0, (tuple, list)) else 1
    x0v = list(x0) if dim > 1 else [x0]
    x1v = list(x1) if dim > 1 else [x1]
    noise = [brownian(n, seed + 7919 * d, modes) for d in range(dim)]
    out = []
    for k in range(n + 1):
        t = k / n
        xt = [(1 - t) * a + t * b + sigma * w[k] for a, b, w in zip(x0v, x1v, noise)]
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
    d = gmm([(0.3, (-1.35, 0.95), 0.38), (0.4, (1.25, 0.55), 0.42), (0.3, (-0.05, -1.2), 0.36)])
    fr = Frame(0, 0, 240, 180, (-2.6, 2.6), (-2.2, 2.2))
    out = Path(tempfile.gettempdir()) / 'density-selftest.png'
    print(density_png(d, out, fr), out, len(samples(d, 10, 1, core=0.1)), bridge(-1.0, 1.0, 0.5, 8, 1)[-1], file=sys.stdout)

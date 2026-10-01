#!/usr/bin/env python3
"""Make the white background of a PNG transparent (soft edge) so labels placed on blank pixels stay visible.

usage: white_to_alpha.py in.png out.png [--low 225] [--high 250]
Artifact Tool draws pictures above shapes regardless of insertion order, so a figureLabel()/leader() inside a picture's box is hidden by an opaque white PNG.
Pixels whose darkest channel is >= --high become fully transparent, <= --low stay opaque, in between fade linearly. Needs Pillow and numpy."""
import argparse
import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('dst')
ap.add_argument('--low', type=int, default=225); ap.add_argument('--high', type=int, default=250)
a = ap.parse_args()
rgb = np.asarray(Image.open(a.src).convert('RGB')).astype(np.float32)
m = rgb.min(axis=2)
alpha = np.clip((a.high - m) / max(1, a.high - a.low), 0, 1)
out = np.dstack([rgb, alpha * 255]).astype(np.uint8)
Image.fromarray(out, 'RGBA').save(a.dst)
print(f'{a.dst}: {(alpha < 0.5).mean():.0%} of pixels transparent')

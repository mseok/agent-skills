#!/usr/bin/env python3
"""Rewrite rotated zero-height leader lines ('figure-leader') in an exported PPTX as plain bounding-box lines with flipV.

usage: flip_leaders.py in.pptx out.pptx
Apple's QuickLook renderer draws some rotated zero-height lines mirrored, so leaders no longer touch the structure. The kit's leader() now writes the
flip form directly; this repairs decks built before that."""
import math, re, sys, zipfile
src, dst = sys.argv[1], sys.argv[2]
zin = zipfile.ZipFile(src)
n = 0
XFRM = re.compile(r'<a:xfrm rot="(-?\d+)"([^>]*)><a:off x="(-?\d+)" y="(-?\d+)" ?/><a:ext cx="(\d+)" cy="0" ?/></a:xfrm>')
def fix_xfrm(m):
    rot, ns, x, y, cx = int(m.group(1)) / 60000, m.group(2), int(m.group(3)), int(m.group(4)), int(m.group(5))
    th = math.radians(rot)
    dx, dy = cx * math.cos(th), cx * math.sin(th)
    mx, my = x + cx / 2, y                      # centre of the original zero-height line
    w, h = round(abs(dx)), round(abs(dy))
    flip = ' flipV="1"' if dx * dy < -0.5 else ''
    return f'<a:xfrm{flip}{ns}><a:off x="{round(mx - w / 2)}" y="{round(my - h / 2)}" /><a:ext cx="{w}" cy="{h}" /></a:xfrm>'
def fix_sp(m):
    global n
    sp = m.group(0)
    if 'name="figure-leader"' not in sp:
        return sp
    new = XFRM.sub(fix_xfrm, sp)
    if new != sp:
        n += 1
    return new
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
    for i in zin.infolist():
        data = zin.read(i.filename)
        if re.fullmatch(r'ppt/slides/slide\d+\.xml', i.filename):
            data = re.sub(r'<p:sp>.*?</p:sp>', fix_sp, data.decode('utf8'), flags=re.S).encode('utf8')
        z.writestr(i.filename, data)
print(f'rewrote {n} rotated leader lines as flipped bounding-box lines -> {dst}')

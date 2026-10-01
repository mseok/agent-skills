#!/usr/bin/env python3
"""Set left/right text insets of node-label shapes to 0 in an exported PPTX (older decks used 18 pt).

usage: zero_node_insets.py in.pptx out.pptx
Apple's QuickLook renderer (and likely Keynote) shifts centered text right by the left inset, so labels poke out of ellipses/capsules."""
import re, sys, zipfile
src, dst = sys.argv[1], sys.argv[2]
zin = zipfile.ZipFile(src)
n = 0
def fix_sp(m):
    global n
    sp = m.group(0)
    if re.search(r'<p:cNvPr [^>]*name="node-label:', sp):
        new = re.sub(r'(<a:bodyPr[^>]*?)\blIns="\d+"', r'\1lIns="0"', sp)
        new = re.sub(r'(<a:bodyPr[^>]*?)\brIns="\d+"', r'\1rIns="0"', new)
        if new != sp:
            n += 1
        return new
    return sp
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
    for i in zin.infolist():
        data = zin.read(i.filename)
        if re.fullmatch(r'ppt/slides/slide\d+\.xml', i.filename):
            data = re.sub(r'<p:sp>.*?</p:sp>', fix_sp, data.decode('utf8'), flags=re.S).encode('utf8')
        z.writestr(i.filename, data)
print(f'zeroed left/right insets on {n} node-label shapes -> {dst}')

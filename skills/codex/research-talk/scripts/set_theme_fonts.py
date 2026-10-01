#!/usr/bin/env python3
"""Set the theme font scheme (heading and body fonts) of an exported PPTX, so text typed later in PowerPoint/Keynote uses the deck family instead of Calibri.

usage: set_theme_fonts.py in.pptx out.pptx [latin=Pretendard] [ea=latin]
Artifact Tool exposes the font scheme read-only, so the theme XML is rewritten after export (finalize.mjs does this automatically)."""
import re, sys, zipfile

src, dst = sys.argv[1], sys.argv[2]
latin = sys.argv[3] if len(sys.argv) > 3 else 'Pretendard'
ea = sys.argv[4] if len(sys.argv) > 4 else latin
zin = zipfile.ZipFile(src)
files = [(i.filename, zin.read(i.filename)) for i in zin.infolist()]
n = 0
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, data in files:
        if re.fullmatch(r'ppt/theme/theme\d+\.xml', name):
            t = data.decode('utf8')
            def fix(m):
                global n
                n += 1
                blk = m.group(0)
                blk = re.sub(r'<a:latin typeface="[^"]*"', f'<a:latin typeface="{latin}"', blk)
                blk = re.sub(r'<a:ea typeface="[^"]*"', f'<a:ea typeface="{ea}"', blk)
                return re.sub(r'<a:cs typeface="[^"]*"', f'<a:cs typeface="{latin}"', blk)
            t = re.sub(r'<a:(?:majorFont|minorFont)>.*?</a:(?:majorFont|minorFont)>', fix, t, flags=re.S)
            data = t.encode('utf8')
        z.writestr(name, data)
print(f'theme fonts set to {latin}/{ea} in {n} font blocks -> {dst}')

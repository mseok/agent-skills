#!/usr/bin/env python3
"""LEGACY / opt-in (the default is the single family Pretendard): pair fonts per run: Latin/digits/Greek in Helvetica Neue (the dissertation face), Hangul in Apple SD Gothic Neo.
usage: pair_fonts.py in.pptx out.pptx [latin="Helvetica Neue"] [ea="Apple SD Gothic Neo"]
Rewrites <a:latin>, <a:ea>, <a:cs> typefaces in slide and chart XML (`ppt/slides/charts/` as Artifact Tool writes them, and `ppt/charts/`; tables included). PowerPoint uses `latin` for Latin glyphs and `ea` for Hangul."""
import re, sys, zipfile
src, dst = sys.argv[1], sys.argv[2]
latin = sys.argv[3] if len(sys.argv) > 3 else 'Helvetica Neue'
ea = sys.argv[4] if len(sys.argv) > 4 else 'Apple SD Gothic Neo'
zin = zipfile.ZipFile(src)
files = [(i.filename, zin.read(i.filename)) for i in zin.infolist()]
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, data in files:
        if re.fullmatch(r'ppt/(slides/slide|slides/charts/chart|charts/chart)\d+\.xml', name):
            t = data.decode('utf8')
            t = re.sub(r'<a:latin typeface="[^"]*"', f'<a:latin typeface="{latin}"', t)
            t = re.sub(r'<a:ea typeface="[^"]*"', f'<a:ea typeface="{ea}"', t)
            t = re.sub(r'<a:cs typeface="[^"]*"', f'<a:cs typeface="{latin}"', t)
            data = t.encode('utf8')
        z.writestr(name, data)
print('paired', dst)

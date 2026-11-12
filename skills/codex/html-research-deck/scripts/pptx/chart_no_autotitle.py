#!/usr/bin/env python3
"""Add <c:autoTitleDeleted val="1"/> to every chart that has no chart-level title, so PowerPoint does not add the series name as a title above single-series charts.

usage: chart_no_autotitle.py in.pptx out.pptx
Artifact Tool omits the flag; PowerPoint treats a missing flag as "auto title on". The element goes right before <c:plotArea> (after an optional <c:title>, per the CT_Chart sequence). finalize.mjs applies this automatically."""
import re, sys, zipfile

src, dst = sys.argv[1], sys.argv[2]
zin = zipfile.ZipFile(src)
files = [(i.filename, zin.read(i.filename)) for i in zin.infolist()]
n = 0
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, data in files:
        if re.fullmatch(r'ppt/(slides/)?charts/chart\d+\.xml', name):
            t = data.decode('utf8')
            m = re.search(r'<c:chart>(.*?)<c:plotArea>', t, re.S)
            if m and 'autoTitleDeleted' not in m.group(1) and '<c:title' not in m.group(1):
                t = t.replace('<c:chart><c:plotArea>', '<c:chart><c:autoTitleDeleted val="1"/><c:plotArea>', 1) if '<c:chart><c:plotArea>' in t else t.replace('<c:plotArea>', '<c:autoTitleDeleted val="1"/><c:plotArea>', 1)
                n += 1
            data = t.encode('utf8')
        z.writestr(name, data)
print(f'autoTitleDeleted added to {n} charts -> {dst}')

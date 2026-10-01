#!/usr/bin/env python3
"""Report slide/notes characters that the deck's font family does not contain (they would render in a fallback font).

usage: check_font_glyphs.py deck.pptx [--family Pretendard] [--report out.json]
Uses fontconfig (`fc-list`). Family defaults to the most common typeface in the deck. Exit 1 when characters are missing from slide text.
"""
import argparse, collections, json, re, subprocess, sys, zipfile
from lxml import etree

NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pptx'); ap.add_argument('--family'); ap.add_argument('--report')
    a = ap.parse_args()
    z = zipfile.ZipFile(a.pptx)
    text = collections.defaultdict(str); faces = collections.Counter()
    for n in z.namelist():
        m = re.fullmatch(r'ppt/(slides/slide|notesSlides/notesSlide)(\d+)\.xml', n)
        if not m:
            continue
        root = etree.fromstring(z.read(n))
        kind = 'slide' if m.group(1) == 'slides/slide' else 'notes'
        text[(kind, int(m.group(2)))] += ''.join(root.xpath('//a:t/text()', namespaces=NS))
        if kind == 'slide':
            for e in root.iter('{%s}latin' % NS['a']):
                faces[e.get('typeface')] += 1
    family = a.family or (faces.most_common(1)[0][0] if faces else 'Pretendard')
    ea_faces = collections.Counter()
    for n in z.namelist():
        if re.fullmatch(r'ppt/slides/slide\d+\.xml', n):
            for e in etree.fromstring(z.read(n)).iter('{%s}ea' % NS['a']):
                ea_faces[e.get('typeface')] += 1
    ea_family = ea_faces.most_common(1)[0][0] if ea_faces else family
    chars = sorted({c for t in text.values() for c in t if ord(c) > 127 and not c.isspace()})
    missing = []
    for c in chars:
        face = ea_family if ord(c) > 0x2e80 else family   # Hangul/CJK use the east-asian slot's font
        out = subprocess.run(['fc-list', f'{face}:charset={ord(c):x}', 'family'], capture_output=True, text=True).stdout
        if not out.strip():
            where = sorted({(k, i) for (k, i), t in text.items() if c in t})
            missing.append({'char': c, 'codepoint': f'U+{ord(c):04X}', 'in': [f'{k}{i}' for k, i in where]})
    slide_missing = [m for m in missing if any(w.startswith('slide') for w in m['in'])]
    rep = {'family': family, 'checked_chars': len(chars), 'missing': missing, 'status': 'fail' if slide_missing else 'pass'}
    out = json.dumps(rep, ensure_ascii=False, indent=1)
    if a.report:
        open(a.report, 'w').write(out)
    print(out)
    sys.exit(1 if slide_missing else 0)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Shared deterministic metrics (imported by check_layout_quality.py).

usage:
  measure_deck.py --pptx deck.pptx --renders DIR [--out report.json]   # deck: XML + render metrics
  measure_deck.py --renders DIR --render-only [--out report.json]      # any PNG set (e.g. dissertation pages)

Render metrics work at any raster scale (grid based). XML metrics assume the
deck is 1920 x 1080 source points (24,384,000 x 13,716,000 EMU).
Metrics are signals for reviewers, not an aesthetic score.
"""
import argparse, glob, json, os, re, statistics, sys, zipfile
import numpy as np
from PIL import Image
from lxml import etree

NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
EMU_PT = 12700.0
GRID_W, GRID_H = 96, 54


def render_metrics(path):
    im = Image.open(path).convert('L')
    a = np.asarray(im, dtype=np.uint8)
    h, w = a.shape
    nonwhite = a < 232
    cells = np.zeros((GRID_H, GRID_W), dtype=bool)
    ch, cw = h / GRID_H, w / GRID_W
    for gy in range(GRID_H):
        for gx in range(GRID_W):
            blk = nonwhite[int(gy * ch):int((gy + 1) * ch), int(gx * cw):int((gx + 1) * cw)]
            cells[gy, gx] = blk.mean() > 0.012
    y0, y1 = int(GRID_H * 0.22), int(GRID_H * 0.88)  # content band ~ y 240..950 of 1080
    band = cells[y0:y1]
    fill = float(band.mean())
    # largest all-empty rectangle inside the band (maximal-rectangle on inverted grid)
    empty = ~band
    best = 0
    hist = np.zeros(empty.shape[1], dtype=int)
    for row in empty:
        hist = np.where(row, hist + 1, 0)
        stack = []
        for i in range(len(hist) + 1):
            cur = hist[i] if i < len(hist) else 0
            start = i
            while stack and stack[-1][1] >= cur:
                s, hh = stack.pop()
                best = max(best, hh * (i - s))
                start = s
            stack.append((start, cur))
    empty_rect = best / band.size
    ys, xs = np.where(nonwhite)
    if len(xs):
        bbox = [float(xs.min() / w), float(ys.min() / h), float(xs.max() / w), float(ys.max() / h)]
    else:
        bbox = [0, 0, 0, 0]
    # horizontal balance of ink inside the band
    sub = nonwhite[int(h * 0.22):int(h * 0.88)]
    cols = sub.sum(axis=0)
    left_ink = float(cols[: w // 2].sum()); right_ink = float(cols[w // 2:].sum())
    balance = (right_ink - left_ink) / max(1.0, right_ink + left_ink)
    return {'content_fill': round(fill, 3), 'largest_empty_rect': round(float(empty_rect), 3),
            'ink_bbox': [round(v, 3) for v in bbox], 'lr_ink_balance': round(float(balance), 3),
            'size': [w, h]}


def shape_name(sp):
    el = sp.find('.//p:cNvPr', NS)
    return (el.get('name') if el is not None else '') or ''


def xfrm(sp):
    off = sp.find('.//a:xfrm/a:off', NS)
    if off is None:
        off = sp.find('.//p:xfrm/a:off', NS)
    ext = sp.find('.//a:xfrm/a:ext', NS)
    if ext is None:
        ext = sp.find('.//p:xfrm/a:ext', NS)
    if off is None or ext is None:
        return None
    return [int(off.get('x')) / EMU_PT, int(off.get('y')) / EMU_PT, int(ext.get('cx')) / EMU_PT, int(ext.get('cy')) / EMU_PT]


def is_footer_like(name, text, y):
    n = name.lower()
    return n.startswith('reference-footer') or n.startswith('page-number') or (re.fullmatch(r'\s*\d{1,3}\s*', text or '') is not None and y is not None and y > 980)


def pptx_metrics(path):
    z = zipfile.ZipFile(path)
    pres = etree.fromstring(z.read('ppt/presentation.xml'))
    sz = pres.find('p:sldSz', NS)
    slide_w = int(sz.get('cx')) / EMU_PT; slide_h = int(sz.get('cy')) / EMU_PT
    ids = [e.get('{%s}id' % NS['r']) for e in pres.findall('.//p:sldId', NS)]
    rels = etree.fromstring(z.read('ppt/_rels/presentation.xml.rels'))
    rmap = {r.get('Id'): r.get('Target') for r in rels}
    slides = []
    fam = {}
    for idx, rid in enumerate(ids, 1):
        part = 'ppt/' + rmap[rid].lstrip('/').replace('ppt/', '')
        root = etree.fromstring(z.read(part))
        sizes_body, sizes_all, spacings = [], [], []
        pics_area = 0.0
        pic_boxes = []
        shape_fills = []
        text_boxes = []
        arrows, connectors, rect_tri = [], 0, 0
        arrow_shapes = []
        placeholders_left = []
        oob = []
        title_info = None
        for sp in root.iter('{%s}sp' % NS['p'], '{%s}pic' % NS['p'], '{%s}cxnSp' % NS['p'], '{%s}graphicFrame' % NS['p']):
            tag = etree.QName(sp).localname
            name = shape_name(sp)
            box = xfrm(sp)
            if tag == 'cxnSp':
                connectors += 1
            if tag == 'pic' and box:
                pics_area += max(0, box[2]) * max(0, box[3])
                pic_boxes.append({'name': name, 'box': box})
            geom = sp.find('.//a:prstGeom', NS)
            if geom is not None and geom.get('prst', '').lower().endswith('arrow'):
                arrows.append(geom.get('prst'))
                xf = sp.find('.//a:xfrm', NS)
                if box and xf is not None:
                    arrow_shapes.append({'name': name, 'prst': geom.get('prst'), 'box': box, 'rot': int(xf.get('rot') or 0) / 60000.0,
                                         'flipH': xf.get('flipH') == '1', 'flipV': xf.get('flipV') == '1'})
            if box:
                x, y, w, h = box
                if x < -2 or y < -2 or x + w > slide_w + 2 or y + h > slide_h + 2:
                    oob.append({'name': name, 'box': [round(v, 1) for v in box]})
            if tag == 'sp' and box:
                fe = sp.find('p:spPr/a:solidFill/a:srgbClr', NS)
                gm = sp.find('p:spPr/a:prstGeom', NS)
                paras = []
                for pp in sp.findall('.//a:p', NS):
                    ptxt = ''.join(pp.xpath('.//a:t/text()', namespaces=NS))
                    psz = max([int(r_.get('sz')) / 100.0 for r_ in pp.iter('{%s}rPr' % NS['a']) if r_.get('sz')] or [0])
                    if ptxt.strip():
                        paras.append([ptxt, psz])
                bp = sp.find('p:txBody/a:bodyPr', NS)
                shape_fills.append({'name': name, 'box': box, 'paras': paras, 'lIns': int(bp.get('lIns') or 0) / EMU_PT if bp is not None else 0, 'fill': fe.get('val').upper() if fe is not None else None,
                                    'geom': gm.get('prst') if gm is not None else None,
                                    'text': '\n'.join(''.join(pp.xpath('.//a:t/text()', namespaces=NS)) for pp in sp.findall('.//a:p', NS)).strip('\n')})
            txt_runs = []
            for p_ in sp.findall('.//a:p', NS):
                for r in p_.findall('a:r', NS):
                    t = ''.join(r.xpath('a:t/text()', namespaces=NS))
                    if not t.strip():
                        continue
                    rpr = r.find('a:rPr', NS)
                    s = int(rpr.get('sz')) / 100.0 if rpr is not None and rpr.get('sz') else None
                    for k in ('latin', 'ea'):
                        if rpr is not None:
                            f = rpr.find('a:' + k, NS)
                            if f is not None and f.get('typeface'):
                                key = f.get('typeface') if k == 'latin' else 'ea:' + f.get('typeface')
                                fam[key] = fam.get(key, 0) + 1
                    txt_runs.append((t, s))
                for ls in p_.findall('a:pPr/a:lnSpc/a:spcPct', NS):
                    spacings.append(int(ls.get('val')) / 1000.0)
            full = ''.join(t for t, _ in txt_runs)
            if re.search(r'\[[^\]\d][^\]]*\]', full) and ('placeholder' in name.lower() or re.search(r'\[(Title|Subtitle|Content|Insert|[A-Z][a-z]+ )', full)):
                placeholders_left.append(full[:60])
            if txt_runs and box:
                y_c = box[1] + box[3] / 2
                sizes = [s for _, s in txt_runs if s]
                if sizes:
                    mx = max(sizes)
                    sizes_all.extend(sizes)
                    if not is_footer_like(name, full, y_c):
                        sizes_body.extend(sizes)
                    ph = sp.find('.//p:nvPr/p:ph', NS)
                    if (ph is not None and ph.get('type') in ('title', 'ctrTitle')) and title_info is None:
                        title_info = {'text': full[:80], 'size': mx, 'box': [round(v, 1) for v in box]}
                text_boxes.append({'name': name, 'box': box, 'size': max(sizes) if sizes else None, 'text': full[:40], 'full': full,
                                   'container': tag == 'sp' and sp.find('.//a:prstGeom', NS) is not None and sp.find('.//a:prstGeom', NS).get('prst') not in ('rect', None) or False})
        # overlapping text boxes (>=15% of the smaller box) among pure text shapes
        overlaps = []
        tb = [t for t in text_boxes if t['box'] and not t['name'].lower().startswith(('node-label', 'prose')) and t['size'] and not re.fullmatch(r'\s*\d{1,3}\s*', t['text'])]
        for i in range(len(tb)):
            for j in range(i + 1, len(tb)):
                a, b = tb[i]['box'], tb[j]['box']
                ix = max(0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]))
                iy = max(0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))
                inter = ix * iy
                small = min(a[2] * a[3], b[2] * b[3])
                if small > 0 and inter / small >= 0.30:
                    overlaps.append([tb[i]['text'], tb[j]['text'], round(inter / small, 2)])
        notes_len = 0
        nrel = f'ppt/slides/_rels/{os.path.basename(part)}.rels'
        if nrel in z.namelist():
            for rel in etree.fromstring(z.read(nrel)):
                if rel.get('Type', '').endswith('/notesSlide'):
                    nt = 'ppt/notesSlides/' + os.path.basename(rel.get('Target'))
                    if nt in z.namelist():
                        notes_len = len(''.join(etree.fromstring(z.read(nt)).xpath('//a:t/text()', namespaces=NS)))
        # a bottom interpretation line: a text shape centred in y 900..1010 with size >= 34 that is not a footer
        takeaway = any(t['box'] and 900 <= t['box'][1] + t['box'][3] / 2 <= 1010 and (t['size'] or 0) >= 34 and not is_footer_like(t['name'], t['text'], t['box'][1] + t['box'][3] / 2) for t in text_boxes)
        xml_text = z.read(part).decode('utf8', 'ignore')
        red_runs = 0
        for rm in re.finditer(r'<a:r>.*?</a:r>', xml_text, re.S):
            cm = re.search(r'<a:srgbClr val="([0-9A-Fa-f]{6})"', rm.group(0))
            if cm:
                r_, g_, b_ = (int(cm.group(1)[i:i + 2], 16) for i in (0, 2, 4))
                if r_ > 190 and g_ < 90 and b_ < 90:
                    red_runs += 1
        slide_colors = sorted({m.upper() for m in re.findall(r'<a:srgbClr val="([0-9A-Fa-f]{6})"', z.read(part).decode('utf8', 'ignore'))})
        slides.append({
            'slide': idx,
            'colors': slide_colors,
            'red_runs': red_runs,
            'title': title_info,
            'body_size_pt': {'min': min(sizes_body) if sizes_body else None,
                             'median': statistics.median(sizes_body) if sizes_body else None,
                             'p10': float(np.percentile(sizes_body, 10)) if sizes_body else None},
            'runs_under_24pt': sum(1 for s in sizes_body if s < 24),
            'line_spacing_pct': sorted(set(spacings)),
            'picture_area_frac': round(pics_area / (slide_w * slide_h), 3),
            'native_arrows': arrows, 'arrow_shapes': arrow_shapes, 'connectors': connectors,
            'out_of_bounds': oob, 'text_overlaps': overlaps[:6],
            'placeholders_left': placeholders_left, 'notes_chars': notes_len,
            'has_bottom_takeaway': takeaway,
            'pic_boxes': pic_boxes,
            'shape_fills': shape_fills,
            'text_boxes': [{'name': t['name'], 'box': t['box'], 'text': t['text'], 'full': t.get('full', t['text']), 'size': t['size']} for t in text_boxes if t['box']],
        })
    return {'slide_size_pt': [slide_w, slide_h], 'font_families': fam, 'slides': slides}



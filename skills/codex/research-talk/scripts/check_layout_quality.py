#!/usr/bin/env python3
"""Dissertation-density and layout gate for an exported PPTX and its slide renders.

usage: check_layout_quality.py deck.pptx --renders DIR_OF_slide-NN.png [--report out.json] [--exempt 1,9]

Needs numpy, Pillow, lxml (the Codex runtime python has them). Renders may be any scale.
Thresholds come from the author's dissertation deck (84 pages, 71 content pages): content-band fill median 0.30, p10 0.235,
p5 0.181; largest empty rectangle median 0.13, p90 0.196, p95 0.216. Floors 0.22 / 0.22 clear ≈ 93–95 % of those pages. Dividers/covers are exempt automatically
(fill < 0.12 and no body text) or via --exempt. Exit 1 on any finding. This is a floor, not a score:
also look at every render beside the dissertation pages.
"""
import argparse, colorsys, glob, json, os, re, sys
from _measure_core import pptx_metrics, render_metrics

FILL_MIN, EMPTY_MAX, BODY_MIN_PT = 0.22, 0.22, 24
MAX_HUES = 2   # plain deck: black/gray plus an accent blue and red emphasis; pass --max-hues 3 only for a slide whose categories must be told apart


def hue_family(hexv):
    r, g, b = (int(hexv[i:i + 2], 16) / 255 for i in (0, 2, 4))
    h, sat, val = colorsys.rgb_to_hsv(r, g, b)
    if sat < 0.18 or val < 0.12:
        return None            # gray/black/white
    deg = h * 360
    for name, lo, hi in (('red', 330, 361), ('red', -1, 20), ('orange', 20, 50), ('yellow', 50, 70), ('green', 70, 170), ('blue', 170, 255), ('purple', 255, 330)):
        if lo <= deg < hi:
            return name
    return None

_FONT_CACHE = {}


def label_width(line, size, latin):
    """Width in pt of one label line. Pretendard decks use the bundled font's real advances (Bold = conservative); others keep a rough estimate (Hangul 1 em, Latin 0.57 em)."""
    if latin == {'Pretendard'}:
        try:
            if 'b' not in _FONT_CACHE:
                from PIL import ImageFont
                fd = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'fonts')
                _FONT_CACHE['b'] = ImageFont.truetype(os.path.join(fd, 'Pretendard-Bold.otf'), 1000)
            return _FONT_CACHE['b'].getlength(line) / 1000.0 * size
        except Exception:
            pass
    return sum((1.0 if ord(ch) > 0x2e80 else 0.57) * size for ch in line)


ALLOWED_ON_FIGURE = ('figure-label', 'residue', 'caption')
META = re.compile(r'다음\s*슬라이드|이전\s*슬라이드|앞\s*슬라이드|\b(?:next|previous|prior)\s+slide\b|\bsee\s+slide\b|\bTODO\b|\blorem\b|placeholder|자리\s*표시|빌드|build\s+note|QA\s+note|Literature-based schematic', re.I)


NEUTRAL = {'FFFFFF', 'F7F7F7', 'F2F2F2', 'EBEBEB', 'EEEEEE', 'DDDDDD', 'CCCCCC', 'D9D9D9', 'F0F0F0', 'FAFAFA', '000000'}


def is_pale_tint(hexv):
    # a light, non-neutral tint (cream, pastel blue/pink/green): high brightness, some channel spread
    if not hexv or hexv in NEUTRAL:
        return False
    r, g, b = (int(hexv[i:i + 2], 16) for i in (0, 2, 4))
    return min(r, g, b) >= 200 and (max(r, g, b) - min(r, g, b)) >= 6


def inter_frac(a, b):
    ix = max(0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))
    return ix * iy / max(1e-9, a[2] * a[3])



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pptx'); ap.add_argument('--renders', required=True)
    ap.add_argument('--report'); ap.add_argument('--exempt', default=''); ap.add_argument('--max-hues', type=int, default=MAX_HUES)
    a = ap.parse_args()
    exempt = {int(x) for x in a.exempt.split(',') if x.strip()}
    deck = pptx_metrics(a.pptx)
    files = sorted(glob.glob(os.path.join(a.renders, 'slide-*.png'))) or sorted(glob.glob(os.path.join(a.renders, '*.png')))   # scratch PNGs beside the slide renders must not count
    findings = []
    if len(files) != len(deck['slides']):
        findings.append({'slide': None, 'code': 'render-count', 'detail': f'{len(files)} renders for {len(deck["slides"])} slides'})
    # One Latin family; the east-asian (Hangul) slot may differ only when the deck uses the declared Latin+Hangul pairing.
    latin = {k for k in deck['font_families'] if not k.startswith('ea:')}
    deck_latin = latin
    ea = {k[3:] for k in deck['font_families'] if k.startswith('ea:')}
    if len(latin) > 1:
        findings.append({'slide': None, 'code': 'font-families', 'detail': f'{len(latin)} Latin families in editable runs: {sorted(latin)}'})
    if len(ea) > 1 or (ea and latin and ea != latin and not (latin == {'Helvetica Neue'} and ea == {'Apple SD Gothic Neo'})):
        findings.append({'slide': None, 'code': 'font-families', 'detail': f'east-asian slot {sorted(ea)} vs Latin {sorted(latin)}: use one family, or the Helvetica Neue + Apple SD Gothic Neo pairing'})
    for s in deck['slides']:
        i = s['slide']
        r = render_metrics(files[i - 1]) if i - 1 < len(files) else None
        divider = bool(r and r['content_fill'] < 0.12 and (s['body_size_pt']['median'] or 0) and s['picture_area_frac'] == 0 and s['runs_under_24pt'] == 0 and not s['has_bottom_takeaway'] and (s['body_size_pt']['median'] or 0) >= 60) or i in exempt
        def add(code, detail):
            findings.append({'slide': i, 'code': code, 'detail': detail})
        if s['out_of_bounds']:
            add('out-of-bounds', json.dumps(s['out_of_bounds'][:3], ensure_ascii=False))
        if s['runs_under_24pt']:
            add('small-text', f'{s["runs_under_24pt"]} runs under {BODY_MIN_PT} pt (min {s["body_size_pt"]["min"]})')
        if s['placeholders_left']:
            add('placeholder', '; '.join(s['placeholders_left'][:3]))
        if s['text_overlaps']:
            add('text-overlap', json.dumps(s['text_overlaps'][:3], ensure_ascii=False))
        # Blockquote/callout styles are prohibited (user, 2026-10-01): side bar + box, tinted panel holding a sentence, or callout/quote names.
        sf = s.get('shape_fills', [])
        for q in sf:
            if re.search(r'callout|blockquote|quote', q['name'], re.I):
                add('blockquote-style', f'shape named "{q["name"]}": quote/callout boxes are not used')
        for bar in sf:
            if bar['fill'] and bar['fill'] not in ('FFFFFF',) and bar['box'][2] <= 20 and bar['box'][3] >= 50:
                for panel in sf:
                    if panel is bar or not panel['fill'] or panel['box'][2] < 200:
                        continue
                    pb, bb = panel['box'], bar['box']
                    if abs(pb[0] - bb[0]) <= 6 and pb[1] - 6 <= bb[1] + bb[3] / 2 <= pb[1] + pb[3] + 6:
                        add('blockquote-style', f'narrow colored bar beside a filled box ("{panel["text"][:30]}"): no side-bar/quote styling')
                        break
        for q in sf:
            if is_pale_tint(q['fill']) and len(q['text'].split()) >= 6 and q['box'][2] >= 300:
                add('blockquote-style', f'tinted panel #{q["fill"]} holds a sentence ("{q["text"][:30]}"): state it as plain text')
        for q in s.get('shape_fills', []):
            if q['name'].startswith('node-label') and q.get('lIns', 0) > 0.5:
                add('node-inset', f'node label "{q["name"][11:40]}" has a {q["lIns"]:.0f} pt left/right inset: Apple\'s renderer shifts centred text right by it (labels poke out of ellipses/capsules). Use box()/stageCard() (zero side insets) or run scripts/zero_node_insets.py')
        for q in s.get('shape_fills', []):
            if not q.get('paras') or not q['name'].startswith('node-label') or q['box'][2] < 100:   # small chips/circles are checked by eye
                continue
            wid = lambda ln, sz: label_width(ln, sz, deck_latin)
            block_h = sum(sz * 1.2 for _, sz in q['paras'])
            if q.get('geom') == 'ellipse':
                # chord width of the ellipse at the outer edge of the text block
                import math
                factor = math.sqrt(max(0.05, 1 - (block_h / max(1.0, q['box'][3])) ** 2))
            else:
                factor = 1.0
            inner_w = q['box'][2] * factor - 16
            worst = max(wid(t_, sz) for t_, sz in q['paras'])
            if worst > inner_w:
                kind = 'ellipse' if q.get('geom') == 'ellipse' else 'box'
                add('label-overflow', f'label "{q["paras"][0][0][:24]}" (~{int(worst)} pt) does not fit its {kind} (usable width ~{int(inner_w)} pt{", an ellipse holds text only in the chord at the text block's edge" if kind == "ellipse" else ""}): widen the node or shorten the label')
        for t in s['text_boxes']:
            m = META.search(t.get('full', ''))
            if m:
                add('meta-text', f'slide text "{m.group(0)}" is navigation/build commentary; keep it in notes: "{t.get("full", "")[:50]}"')
        for t in s['text_boxes']:
            nm = t['name'].lower()
            if nm.startswith(ALLOWED_ON_FIGURE) or nm.startswith(('reference-footer', 'page-number')) or not t['text'].strip() or re.fullmatch(r'\s*\d{1,3}\s*', t['text']):
                continue
            for pb in s['pic_boxes']:
                if inter_frac(t['box'], pb['box']) >= 0.25:
                    add('text-over-picture', f'"{t["text"][:30]}" overlaps picture {pb["name"] or "?"}; move the text or name it figure-label: if it is an intentional label on the figure')
                    break
        feet = [t for t in s['text_boxes'] if t['name'].lower().startswith('reference-footer')]
        for ft in feet:
            for o in s['text_boxes'] + s['pic_boxes']:
                if o is ft or (o.get('name') or '').lower().startswith(('reference-footer', 'page-number')) or re.fullmatch(r'\s*\d{1,3}\s*', o.get('text', '') or 'x'):
                    continue
                if inter_frac(o['box'], ft['box']) > 0.02 or inter_frac(ft['box'], o['box']) > 0.02:
                    add('footer-collision', f'reference footer overlaps "{(o.get("text") or o.get("name") or "")[:30]}"; shorten references or move content up (footer is at most 2 rows in the lower right)')
                    break
        # Arrows must join their objects (r16 design judge: tips pointing into blank space). Both ends need a shape, picture or text box whose facing edge is
        # within 45 pt and whose span (axis perpendicular to the arrow; the central 60 % for ellipses, whose bounding-box corners are blank) contains the end point.
        targets = [(q['box'], q.get('geom')) for q in sf if q['box'] and not (q.get('geom') or '').lower().endswith('arrow') and q['box'][2] >= 20 and q['box'][3] >= 20]
        targets += [(t['box'], None) for t in s['text_boxes'] if t['text'].strip()] + [(pb['box'], None) for pb in s['pic_boxes']]
        for ar in s.get('arrow_shapes', []):
            x, y, w, h = ar['box']
            if round(ar['rot']) % 180 not in (0,) and abs(ar['rot']) > 1:
                continue    # rotated arrows are checked by eye
            kind = ar['prst'].lower()
            horiz = kind.startswith(('right', 'left')) or kind in ('leftrightarrow',)
            vert = kind.startswith(('up', 'down'))
            if not (horiz or vert):
                continue
            ends = [(x, y + h / 2), (x + w, y + h / 2)] if horiz else [(x + w / 2, y), (x + w / 2, y + h)]
            def lands(pt):
                near = False
                for (tx, ty, tw, th), tg in targets:
                    if (tx, ty, tw, th) == (x, y, w, h):
                        continue
                    inset = 0.2 if tg == 'ellipse' else 0.0
                    if horiz:
                        edge = min(abs(pt[0] - tx), abs(pt[0] - (tx + tw)))
                        ok_span = ty + inset * th - 4 <= pt[1] <= ty + (1 - inset) * th + 4
                        gap = max(ty + inset * th - pt[1], pt[1] - (ty + (1 - inset) * th), 0)
                    else:
                        edge = min(abs(pt[1] - ty), abs(pt[1] - (ty + th)))
                        ok_span = tx + inset * tw - 4 <= pt[0] <= tx + (1 - inset) * tw + 4
                        gap = max(tx + inset * tw - pt[0], pt[0] - (tx + (1 - inset) * tw), 0)
                    if edge <= 45 and ok_span:
                        return True
                    if edge <= 45 and gap <= 80:
                        near = True       # an object is right there but the end point misses its span
                return None if near else True     # None = near miss; True = lands, or deliberately free between panels
            bad = [i for i, pt in enumerate(ends) if lands(pt) is None]
            if bad:
                add('arrow-target', f'arrow "{ar["name"] or ar["prst"]}" at ({x:.0f},{y:.0f}) {"tail" if bad[0] == 0 else "tip"} stops beside an object but misses its span (a near miss reads as an error): centre the end on the object it links')
        fams = sorted({f for f in (hue_family(x) for x in s.get('colors', [])) if f})
        if len(fams) > a.max_hues:
            add('too-many-colors', f'{len(fams)} hue families {fams} in editable text/shapes/lines (limit {a.max_hues}: accent blue + red emphasis). Use one accent; a colour is spent on a key phrase or the proposed method, never decoration')
        if s.get('red_runs', 0) > 2:
            add('red-overuse', f'{s["red_runs"]} red emphasis runs (limit 2 per slide, one per text block): emphasis loses meaning when every statement carries it')
        if divider:
            continue
        if r:
            if r['content_fill'] < FILL_MIN:
                add('sparse', f'content fill {r["content_fill"]} < {FILL_MIN}: enlarge the evidence figure / fill the band')
            if r['largest_empty_rect'] > EMPTY_MAX:
                add('dead-zone', f'largest empty rectangle {r["largest_empty_rect"]} > {EMPTY_MAX} of the content band')
        if not s['has_bottom_takeaway'] and not any(t['name'].startswith('finding-number') for t in s['text_boxes']):   # numbered-findings slides carry the takeaway themselves
            add('no-takeaway', 'no ~40 pt interpretation line near y≈940 (design.md: short interpretation closes each content slide)')
        extra = [v for v in s['line_spacing_pct'] if v not in (100.0, 120.0)]
        if extra:
            add('line-spacing', f'unexpected line spacing {extra}; use 1.2x for multiline text, 1.0 only for single-line node labels')
    out = {'pptx': a.pptx, 'status': 'review' if findings else 'pass', 'findings': findings}
    if a.report:
        json.dump(out, open(a.report, 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))
    sys.exit(1 if findings else 0)


if __name__ == '__main__':
    main()

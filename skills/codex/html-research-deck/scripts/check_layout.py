#!/usr/bin/env python3
"""Measure the rendered layout of an HTML deck (headless Chrome) and report what the grid check cannot see:
text that leaves its panel or sits in the panel padding, labels that collide, labels that cross a shape rim,
HTML blocks that overflow, closing lines that wrap, and panels whose content leaves an empty band (top/bottom gap).

usage: check_layout.py /abs/deck/index.html [--json /abs/deck/qa/layout.json] [--slides 3,15,18] [--quiet]

Runs Chrome once on a temporary copy of index.html (same folder, so relative assets resolve) with a measuring
script appended; the copy and the Chrome profile are removed afterwards. Every slide is shown at its last build
(#/n/99). Coordinates are stage pixels (1920x1080). Exit 1 when errors were found, 2 when the run failed.

errors   : text-outside-panel, text-outside-stage, text-overlap, html-overflow, closing-wraps
warnings : text-in-padding (inside the 20 px inner margin), text-crosses-shape, text-crosses-line (a <line> segment
           runs through a glyph box), box-unbalanced (text inside a rect sits off-centre vertically by > 10 px),
           panel-underfilled (a gap > 80 px), panel-unbalanced (|top gap - bottom gap| > 24 px), panel-tight (a gap < 12 px)
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME = os.environ.get('CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
ERRORS = ('text-outside-panel', 'text-outside-stage', 'text-overlap', 'html-overflow', 'closing-wraps')

MEASURE = r'''
<script id="qa-layout-script">
(async function qaLayout() {
  const PAD = 20;
  // --dump-dom never produces compositor frames, so wait on timers (virtual time advances them), not requestAnimationFrame.
  const wait = ms => new Promise(res => setTimeout(res, ms));
  const pre = document.createElement('pre');
  pre.id = 'qa-layout';
  const report = { slides: [], done: false, progress: 'start' };
  const flush = () => { pre.textContent = JSON.stringify(report).replace(/[<>&]/g, c => '\\u' + c.charCodeAt(0).toString(16).padStart(4, '0')); };
  const mount = () => { if (!pre.isConnected) (document.body || document.documentElement).appendChild(pre); };
  try {
  if (document.readyState === 'loading') await new Promise(res => document.addEventListener('DOMContentLoaded', res, { once: true }));
  mount(); flush();
  await Promise.race([document.fonts.ready, wait(5000)]);
  await wait(100);
  const stage = document.querySelector('.stage');
  const slides = Array.from(document.querySelectorAll('section.slide'));
  const vis = el => {
    for (let e = el; e && e !== document.body; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) < 0.05) return false;
    }
    return true;
  };
  const R = v => Math.round(v * 10) / 10;
  const norm = r => { const s = stage.getBoundingClientRect(); const k = s.width / 1920; return { x: R((r.left - s.left) / k), y: R((r.top - s.top) / k), w: R(r.width / k), h: R(r.height / k) }; };
  const box = el => norm(el.getBoundingClientRect());
  const inter = (a, b) => ({ w: Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x), h: Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y) });
  const contains = (o, i, tol) => i.x >= o.x - tol && i.y >= o.y - tol && i.x + i.w <= o.x + o.w + tol && i.y + i.h <= o.y + o.h + tol;
  const segRect = (p, q, r) => {  // does segment p-q pass through rect r (Liang–Barsky clip)?
    let t0 = 0, t1 = 1; const dx = q.x - p.x, dy = q.y - p.y;
    const clip = (den, num) => { if (den === 0) return num <= 0; const t = num / den; if (den < 0) { if (t > t1) return false; if (t > t0) t0 = t; } else { if (t < t0) return false; if (t < t1) t1 = t; } return true; };
    return clip(-dx, p.x - r.x) && clip(dx, r.x + r.w - p.x) && clip(-dy, p.y - r.y) && clip(dy, r.y + r.h - p.y) && t0 <= t1;
  };
  const endpoints = el => {  // <line> endpoints in stage pixels
    const m = el.getScreenCTM(); if (!m) return null;
    const s = stage.getBoundingClientRect(); const k = s.width / 1920;
    const pt = (x, y) => { const d = new DOMPoint(x, y).matrixTransform(m); return { x: R((d.x - s.left) / k), y: R((d.y - s.top) / k) }; };
    return [pt(el.x1.baseVal.value, el.y1.baseVal.value), pt(el.x2.baseVal.value, el.y2.baseVal.value)];
  };
  const snip = el => (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 70);
  const em = t => { const ins = Math.max(0, (t.b.h - t.fs * 0.95) / 2); return { x: t.b.x, y: t.b.y + ins, w: t.b.w, h: t.b.h - 2 * ins }; };
  const STAGE = { x: 0, y: 0, w: 1920, h: 1080 };
  for (let i = 0; i < slides.length; i++) {
    const n = i + 1;
    report.progress = 'slide ' + n; flush();
    location.hash = '#/' + n + '/99';
    let tries = 0;
    while (!slides[i].classList.contains('active') && tries++ < 100) await wait(20);
    await wait(60);
    const s = slides[i];
    const S = { n, title: s.dataset.title || '', active: s.classList.contains('active'), panels: [], findings: [] };
    const panels = Array.from(s.querySelectorAll(':scope > .panel'));
    panels.forEach((p, pi) => {
      const pb = box(p);
      const inner = { x: pb.x + PAD, y: pb.y + PAD, w: pb.w - 2 * PAD, h: pb.h - 2 * PAD };
      const svgLeaves = Array.from(p.querySelectorAll('text, rect, circle, ellipse, line, path, polygon, polyline, image, use')).filter(el => el instanceof SVGElement && !el.closest('defs') && vis(el));
      const htmlLeaves = Array.from(p.querySelectorAll('p, li, h3, h4, img, .cap')).filter(el => !(el instanceof SVGElement) && vis(el));
      const texts = [], shapes = [], segs = [];
      let u = null;
      const add = b => { u = u ? { x: Math.min(u.x, b.x), y: Math.min(u.y, b.y), x2: Math.max(u.x2, b.x + b.w), y2: Math.max(u.y2, b.y + b.h) } : { x: b.x, y: b.y, x2: b.x + b.w, y2: b.y + b.h }; };
      svgLeaves.forEach(el => {
        const b = box(el); if (b.w === 0 && b.h === 0) return;
        const tag = el.tagName.toLowerCase();
        add(b);
        if (tag === 'text') texts.push({ b, fs: R(parseFloat(getComputedStyle(el).fontSize) || 0), t: snip(el), fill: getComputedStyle(el).fill, chars: (el.textContent || '').replace(/\s+/g, '').length });
        else if (tag === 'rect' || tag === 'circle' || tag === 'ellipse' || tag === 'use') shapes.push({ b, tag });
        else if (tag === 'line') { const e = endpoints(el); if (e) segs.push({ p: e[0], q: e[1] }); }
      });
      // figure extent: every non-text SVG element plus images (for the "is there a drawing, how much of the panel does it use" score)
      let fu = null;
      const addF = b => { fu = fu ? { x: Math.min(fu.x, b.x), y: Math.min(fu.y, b.y), x2: Math.max(fu.x2, b.x + b.w), y2: Math.max(fu.y2, b.y + b.h) } : { x: b.x, y: b.y, x2: b.x + b.w, y2: b.y + b.h }; };
      svgLeaves.forEach(el => { if (el.tagName.toLowerCase() === 'text') return; const b = box(el); if (b.w > 0 || b.h > 0) addF(b); });
      const htmlBlocks = [];
      htmlLeaves.forEach(el => { const b = box(el); if (b.w === 0 && b.h === 0) return; add(b); if (el.tagName.toLowerCase() === 'img') addF(b); htmlBlocks.push({ b, t: snip(el), tag: el.tagName.toLowerCase(), chars: (el.textContent || '').replace(/\s+/g, '').length }); });
      // bordered HTML rows/cards count as content for the fill measurement (their text may end above the border)
      Array.from(p.children).filter(el => !(el instanceof SVGElement) && vis(el)).forEach(el => { const b = box(el); if (b.w > 0 && b.h > 0) add(b); });
      const P = { i: pi + 1, box: pb, svg: svgLeaves.length, texts: texts.length, html: htmlBlocks.length };
      const innerArea = Math.max(1, (pb.w - 2 * PAD) * (pb.h - 2 * PAD));
      P.figure = fu ? { x: R(fu.x), y: R(fu.y), w: R(fu.x2 - fu.x), h: R(fu.y2 - fu.y), share: R(100 * (fu.x2 - fu.x) * (fu.y2 - fu.y) / innerArea) / 100 } : null;
      // text runs with size, colour and whether they are free commentary (not inside a shape, wider than 40 % of the inner width)
      P.runs = texts.map(t => ({ fs: t.fs, x: t.b.x, y: t.b.y, w: t.b.w, h: t.b.h, fill: t.fill, chars: t.chars, t: t.t.slice(0, 24), inShape: shapes.some(sh => contains(sh.b, em(t), 1.5)), free: !shapes.some(sh => contains(sh.b, em(t), 1.5)) && t.b.w >= 0.4 * (pb.w - 2 * PAD) }));
      P.shapeBoxes = shapes.map(sh => sh.b);
      P.ink = P.figure;  // non-text extent only (figure incl. labels is computed by score_deck.py)
      P.htmlChars = htmlBlocks.reduce((a, h) => a + (h.chars || 0), 0);
      if (u) {
        P.content = { x: R(u.x), y: R(u.y), w: R(u.x2 - u.x), h: R(u.y2 - u.y) };
        P.gap = { top: R(u.y - pb.y), bottom: R(pb.y + pb.h - u.y2), left: R(u.x - pb.x), right: R(pb.x + pb.w - u.x2) };
      }
      S.panels.push(P);
      texts.forEach(t => {
        if (!contains(pb, t.b, 0.5)) S.findings.push({ kind: 'text-outside-panel', panel: pi + 1, text: t.t, box: t.b, fs: t.fs, panelBox: pb });
        else if (!contains(inner, t.b, 0.5)) S.findings.push({ kind: 'text-in-padding', panel: pi + 1, text: t.t, box: t.b, fs: t.fs });
        if (!contains(STAGE, t.b, 0)) S.findings.push({ kind: 'text-outside-stage', panel: pi + 1, text: t.t, box: t.b });
      });
      htmlBlocks.forEach(t => { if (!contains(pb, t.b, 0.5)) S.findings.push({ kind: 'text-outside-panel', panel: pi + 1, text: t.t, box: t.b, tag: t.tag, panelBox: pb }); });
      for (let a = 0; a < texts.length; a++) for (let b = a + 1; b < texts.length; b++) {
        const o = inter(em(texts[a]), em(texts[b]));
        if (o.w > 1.5 && o.h > 1.5) S.findings.push({ kind: 'text-overlap', panel: pi + 1, a: texts[a].t, b: texts[b].t, overlap: { w: R(o.w), h: R(o.h) }, boxA: texts[a].b, boxB: texts[b].b });
      }
      texts.forEach(t => shapes.forEach(sh => {
        const o = inter(t.b, sh.b);
        if (o.w > 1 && o.h > 1 && !contains(sh.b, em(t), 1.5)) S.findings.push({ kind: 'text-crosses-shape', panel: pi + 1, text: t.t, shape: sh.tag, shapeBox: sh.b, box: t.b });
      }));
      texts.forEach(t => { const e = em(t); const r = { x: e.x + 1, y: e.y + 1, w: Math.max(0, e.w - 2), h: Math.max(0, e.h - 2) };
        segs.forEach(sg => { if (segRect(sg.p, sg.q, r)) S.findings.push({ kind: 'text-crosses-line', panel: pi + 1, text: t.t, box: t.b, line: [sg.p, sg.q] }); }); });
      // text inside a leaf box should sit centred: compare the gap above the first glyph with the gap below the last one.
      // Containers (a rect holding other shapes: cards with bars, column bands, grouped boxes) are judged by eye instead.
      shapes.filter(sh => sh.tag === 'rect' && sh.b.h >= 50 && sh.b.w >= 60 && !shapes.some(o => o !== sh && contains(sh.b, o.b, 1))).forEach(sh => {
        const inside = texts.filter(t => contains(sh.b, em(t), 1.5));
        if (!inside.length) return;
        const top = Math.min(...inside.map(t => t.b.y)), bot = Math.max(...inside.map(t => t.b.y + t.b.h));
        const gt = R(top - sh.b.y), gb = R(sh.b.y + sh.b.h - bot);
        if (Math.abs(gt - gb) > 10) S.findings.push({ kind: 'box-unbalanced', panel: pi + 1, box: sh.b, gapTop: gt, gapBottom: gb, text: inside[0].t });
      });
      if (P.gap) {
        if (P.gap.bottom > 80 || P.gap.top > 80) S.findings.push({ kind: 'panel-underfilled', panel: pi + 1, gap: P.gap });
        else if (Math.abs(P.gap.bottom - P.gap.top) > 24) S.findings.push({ kind: 'panel-unbalanced', panel: pi + 1, gap: P.gap });
        if (Math.min(P.gap.top, P.gap.bottom, P.gap.left, P.gap.right) < 12) S.findings.push({ kind: 'panel-tight', panel: pi + 1, gap: P.gap });
      }
    });
    Array.from(s.querySelectorAll('.takeaway, .lines, .cap, h2, .kicker, h1')).forEach(el => {
      if (!vis(el)) return;
      // 4 px slack: multi-line blocks report a scrollHeight one line-height rounding above clientHeight
      if (el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 4)
        S.findings.push({ kind: 'html-overflow', sel: (el.className && String(el.className)) || el.tagName.toLowerCase(), text: snip(el), scroll: [el.scrollWidth, el.scrollHeight], client: [el.clientWidth, el.clientHeight] });
    });
    const tk = s.querySelector(':scope > .takeaway');
    if (tk && vis(tk)) {
      const b = box(tk), cs = getComputedStyle(tk);
      const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.4;
      const padV = (parseFloat(cs.paddingTop) || 0) + (parseFloat(cs.paddingBottom) || 0);
      S.takeaway = b;
      if (b.h > padV + lh * 1.6) S.findings.push({ kind: 'closing-wraps', box: b, text: snip(tk) });
    }
    report.slides.push(S);
    flush();
  }
  report.done = true;
  report.progress = 'done';
  flush();
  document.title = 'qa-layout-done';
  } catch (e) {
    report.error = String(e && e.stack || e);
    mount(); flush();
  }
})();
</script>
'''


def fmt_box(b):
    return f"x {b['x']:g}–{b['x'] + b['w']:g} y {b['y']:g}–{b['y'] + b['h']:g}"


def describe(f):
    k = f['kind']
    if k in ('text-outside-panel', 'text-outside-stage'):
        extra = f" (panel {fmt_box(f['panelBox'])})" if f.get('panelBox') else ''
        return f"{k}: \"{f['text']}\" {fmt_box(f['box'])}{extra}"
    if k == 'text-in-padding':
        return f"{k}: \"{f['text']}\" {fmt_box(f['box'])} {f.get('fs', '')}px"
    if k == 'text-overlap':
        return f"{k}: \"{f['a']}\" × \"{f['b']}\" overlap {f['overlap']['w']:g}×{f['overlap']['h']:g} px at {fmt_box(f['boxA'])} / {fmt_box(f['boxB'])}"
    if k == 'text-crosses-shape':
        return f"{k}: \"{f['text']}\" {fmt_box(f['box'])} crosses {f['shape']} {fmt_box(f['shapeBox'])}"
    if k == 'text-crosses-line':
        p, q = f['line']
        return f"{k}: \"{f['text']}\" {fmt_box(f['box'])} crossed by line ({p['x']:g},{p['y']:g})–({q['x']:g},{q['y']:g})"
    if k == 'box-unbalanced':
        return f"{k}: rect {fmt_box(f['box'])} text gap top {f['gapTop']:g} · bottom {f['gapBottom']:g} (\"{f['text']}\" …)"
    if k in ('panel-underfilled', 'panel-unbalanced', 'panel-tight'):
        g = f['gap']
        return f"{k}: gaps top {g['top']:g} · bottom {g['bottom']:g} · left {g['left']:g} · right {g['right']:g}"
    if k == 'html-overflow':
        return f"{k}: {f['sel']} \"{f['text']}\" scroll {f['scroll']} > client {f['client']}"
    if k == 'closing-wraps':
        return f"{k}: closing line is {f['box']['h']:g} px tall: \"{f['text']}\""
    return json.dumps(f, ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('index')
    ap.add_argument('--json', help='write the full measurement report here')
    ap.add_argument('--slides', help='comma-separated slide numbers to print (all are measured)')
    ap.add_argument('--quiet', action='store_true', help='print findings only, no per-panel gaps')
    ap.add_argument('--budget', type=int, default=90000, help='Chrome virtual time budget in ms')
    a = ap.parse_args()
    src = Path(a.index).resolve()
    if not src.is_file():
        sys.exit(f'not a file: {src}')
    if not os.access(CHROME, os.X_OK):
        sys.exit(f'Chrome not found at {CHROME} (set CHROME=...)')
    html = src.read_text(encoding='utf-8')
    cut = html.rfind('</body>')
    if cut < 0:
        sys.exit('no </body> in index.html')
    tmp = src.with_name(f'.qa-layout-{os.getpid()}.html')
    profile = tempfile.mkdtemp(prefix='deck-chrome-qa.')
    try:
        tmp.write_text(html[:cut] + MEASURE + html[cut:], encoding='utf-8')
        cmd = [CHROME, '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', f'--user-data-dir={profile}',
               '--window-size=1920,1080', f'--virtual-time-budget={a.budget}', '--dump-dom', f'file://{tmp}?export#/1/99']
        run = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    finally:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        shutil.rmtree(profile, ignore_errors=True)
    m = re.search(r'<pre id="qa-layout">(.*?)</pre>', run.stdout, re.S)
    if not m:
        sys.stderr.write(run.stderr[-2000:] + '\n')
        sys.exit('measuring script did not finish (no qa-layout block in the DOM dump); raise --budget or check the console')
    report = json.loads(m.group(1))
    if report.get('error'):
        sys.exit(f"measuring script failed at {report.get('progress')}: {report['error']}")
    if not report.get('done'):
        sys.exit(f"measuring script did not finish (progress: {report.get('progress')}); raise --budget")
    only = {int(x) for x in a.slides.split(',')} if a.slides else None
    n_err = n_warn = 0
    for S in report['slides']:
        errs = [f for f in S['findings'] if f['kind'] in ERRORS]
        warns = [f for f in S['findings'] if f['kind'] not in ERRORS]
        n_err += len(errs)
        n_warn += len(warns)
        if only and S['n'] not in only:
            continue
        print(f"slide {S['n']:02d} · {S['title']}" + ('' if S['active'] else '  [NOT ACTIVE: measurement unreliable]'))
        if not a.quiet:
            for P in S['panels']:
                if P.get('gap'):
                    g = P['gap']
                    print(f"  panel {P['i']}: {fmt_box(P['box'])} · content {fmt_box(P['content'])} · gaps top {g['top']:g} / bottom {g['bottom']:g} / left {g['left']:g} / right {g['right']:g} · {P['texts']} texts")
                else:
                    print(f"  panel {P['i']}: {fmt_box(P['box'])} · empty")
        for f in errs:
            print('  ERROR ' + describe(f))
        for f in warns:
            print('  warn  ' + describe(f))
    print(f"{len(report['slides'])} slides · {n_err} errors · {n_warn} warnings")
    if a.json:
        Path(a.json).write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    sys.exit(1 if n_err else 0)


if __name__ == '__main__':
    main()

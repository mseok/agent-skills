#!/usr/bin/env python3
"""Measure the rendered layout of an HTML deck (headless Chrome) and report what the grid check cannot see.

usage: check_layout.py /abs/deck/index.html [--json /abs/deck/qa/layout.json] [--slides 3,15,18] [--quiet]

Runs Chrome once on a temporary copy of index.html (same folder, so relative assets resolve) with a measuring
script appended; the copy and the Chrome profile are removed afterwards. Every slide is shown at its last build
(#/n/99). Coordinates are stage pixels (1920x1080). Exit 1 when errors were found, 2 when the run failed.

errors   : text-outside-panel, text-outside-stage,
           text-clipped        a glyph box leaves its <svg> viewport (the browser cuts it off),
           text-in-padding     a glyph box inside the 20 px inner margin of its panel,
           text-overlap        two labels, or a label and an HTML block (.fx formula, .cap, <p>), whose boxes intersect,
           text-crosses-shape  a glyph box crosses the rim of a rect / circle / ellipse / polygon / sprite it does not sit inside
                               (circles and ellipses are tested on their true outline, the rest on their box),
           text-crosses-line   a <line> runs through a glyph box,
           text-crosses-path   a <path>, <polyline> or <polygon> outline (curve, arrowhead, chart line, blob) runs through a glyph box,
           text-crosses-image  a label lies on a raster (<image> or <img>) — labels sit beside renders, never on them,
           shape-clipped       a shape or image leaves its <svg> viewport,
           html-overflow       a clipping HTML block whose content scrolls (a formula wider than its .fx.box, a wrapped title column),
           html-overlap        two slide-level HTML blocks intersect (h1 / subtitle / who / aff on the title slide; h2, kicker,
                               panels, closing line, cite on content slides),
           h2-wraps            the slide title takes two lines,
           closing-wraps       the closing line takes two lines
warnings : box-unbalanced      text inside a rect sits off-centre vertically by > 10 px,
           shape-overlap       two shapes ≥ 24 px intersect without one containing the other (stacked cards, badges over boxes) —
                               fix, or name the reason in the report,
           panel-underfilled   a top or bottom gap > 80 px,  panel-unbalanced  |top gap − bottom gap| > 24 px,  panel-tight  a gap < 12 px
Delivery gate (references/qa.md): zero errors, and every warning either fixed or named with its reason.
Why these exist: the first Latent SI deck (2026-11-01) passed with 0/0 while the title wrapped over the subtitle, a chart curve
ran through a value label and a label was cut by the panel edge — HTML blocks, paths and clipping were not measured.
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
ERRORS = ('text-outside-panel', 'text-outside-stage', 'text-clipped', 'text-in-padding', 'text-overlap', 'text-crosses-shape',
          'text-crosses-line', 'text-crosses-path', 'text-crosses-image', 'shape-clipped', 'html-overflow', 'html-overlap',
          'h2-wraps', 'closing-wraps')

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
  await wait(150);
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
  const SB = () => stage.getBoundingClientRect();
  const norm = r => { const s = SB(); const k = s.width / 1920; return { x: R((r.left - s.left) / k), y: R((r.top - s.top) / k), w: R(r.width / k), h: R(r.height / k) }; };
  const box = el => norm(el.getBoundingClientRect());
  const inter = (a, b) => ({ w: Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x), h: Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y) });
  const contains = (o, i, tol) => i.x >= o.x - tol && i.y >= o.y - tol && i.x + i.w <= o.x + o.w + tol && i.y + i.h <= o.y + o.h + tol;
  const segRect = (p, q, r) => {  // does segment p-q pass through rect r (Liang–Barsky clip)?
    let t0 = 0, t1 = 1; const dx = q.x - p.x, dy = q.y - p.y;
    const clip = (den, num) => { if (den === 0) return num <= 0; const t = num / den; if (den < 0) { if (t > t1) return false; if (t > t0) t0 = t; } else { if (t < t0) return false; if (t < t1) t1 = t; } return true; };
    return clip(-dx, p.x - r.x) && clip(dx, r.x + r.w - p.x) && clip(-dy, p.y - r.y) && clip(dy, r.y + r.h - p.y) && t0 <= t1;
  };
  const toStage = (m, x, y) => { const s = SB(); const k = s.width / 1920; const d = new DOMPoint(x, y).matrixTransform(m); return { x: R((d.x - s.left) / k), y: R((d.y - s.top) / k) }; };
  const endpoints = el => { const m = el.getScreenCTM(); if (!m) return null; return [toStage(m, el.x1.baseVal.value, el.y1.baseVal.value), toStage(m, el.x2.baseVal.value, el.y2.baseVal.value)]; };
  const sampled = el => {  // the outline of a path / polyline / polygon as a chain of stage-pixel points
    let L; try { L = el.getTotalLength(); } catch (e) { return null; }
    if (!isFinite(L) || L <= 0) return null;
    const m = el.getScreenCTM(); if (!m) return null;
    const n = Math.min(600, Math.max(8, Math.ceil(L / 5)));
    const pts = [];
    for (let i = 0; i <= n; i++) { const p = el.getPointAtLength(L * i / n); pts.push(toStage(m, p.x, p.y)); }
    return pts;
  };
  const textOf = el => {  // rendered text only: KaTeX keeps a hidden MathML copy that would double every formula
    const c = el.cloneNode(true); c.querySelectorAll('.katex-mathml').forEach(x => x.remove()); return (c.textContent || '').replace(/\s+/g, ' ').trim();
  };
  const snip = el => textOf(el).slice(0, 70);
  const em = t => { if (t.kind === 'html') return t.b; const ins = Math.max(0, (t.b.h - t.fs * 0.95) / 2); return { x: t.b.x, y: t.b.y + ins, w: t.b.w, h: t.b.h - 2 * ins }; };
  const ellipseHas = (b, px, py) => { const cx = b.x + b.w / 2, cy = b.y + b.h / 2, rx = b.w / 2, ry = b.h / 2; if (rx <= 0 || ry <= 0) return false; const dx = (px - cx) / rx, dy = (py - cy) / ry; return dx * dx + dy * dy < 1; };
  const round = sh => sh.tag === 'circle' || sh.tag === 'ellipse';
  const hits = (sh, r) => {  // glyph box r touches shape sh (true outline for circles/ellipses, box for the rest)
    const o = inter(r, sh.b); if (!(o.w > 1 && o.h > 1)) return false;
    if (!round(sh)) return true;
    const cx = sh.b.x + sh.b.w / 2, cy = sh.b.y + sh.b.h / 2;
    return ellipseHas(sh.b, Math.max(r.x, Math.min(cx, r.x + r.w)), Math.max(r.y, Math.min(cy, r.y + r.h)));
  };
  const holds = (sh, r, tol) => {  // glyph box r sits inside shape sh
    if (!round(sh)) return contains(sh.b, r, tol);
    const g = { x: sh.b.x - tol, y: sh.b.y - tol, w: sh.b.w + 2 * tol, h: sh.b.h + 2 * tol };
    return [[r.x, r.y], [r.x + r.w, r.y], [r.x, r.y + r.h], [r.x + r.w, r.y + r.h]].every(([px, py]) => ellipseHas(g, px, py));
  };
  const STAGE = { x: 0, y: 0, w: 1920, h: 1080 };
  const SOLID = new Set(['rect', 'circle', 'ellipse', 'use', 'polygon', 'image']);
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
      const svgLeaves = Array.from(p.querySelectorAll('text, rect, circle, ellipse, line, path, polygon, polyline, image, use')).filter(el => el instanceof SVGElement && !el.closest('defs') && !el.closest('marker') && !el.closest('.fx, .katex, .cap, .lines') && vis(el));
      let htmlLeaves = Array.from(p.querySelectorAll('p, li, h3, h4, img, .cap, .fx')).filter(el => !(el instanceof SVGElement) && vis(el));
      htmlLeaves = htmlLeaves.filter(el => !htmlLeaves.some(o => o !== el && o.contains(el)));  // a .fx keeps its <p> lines
      const texts = [], shapes = [], segs = [];
      let u = null;
      const add = b => { u = u ? { x: Math.min(u.x, b.x), y: Math.min(u.y, b.y), x2: Math.max(u.x2, b.x + b.w), y2: Math.max(u.y2, b.y + b.h) } : { x: b.x, y: b.y, x2: b.x + b.w, y2: b.y + b.h }; };
      svgLeaves.forEach(el => {
        const b = box(el); if (b.w === 0 && b.h === 0) return;
        const tag = el.tagName.toLowerCase();
        add(b);
        const svgBox = el.ownerSVGElement ? box(el.ownerSVGElement) : null;
        const clipped = !!(svgBox && !contains(svgBox, b, 0.5));
        if (tag === 'text') { texts.push({ b, fs: R(parseFloat(getComputedStyle(el).fontSize) || 0), t: snip(el), fill: getComputedStyle(el).fill, chars: (el.textContent || '').replace(/\s+/g, '').length, clipped, kind: 'svg' }); return; }
        if (clipped) S.findings.push({ kind: 'shape-clipped', panel: pi + 1, shape: tag, box: b, svgBox });
        if (SOLID.has(tag)) shapes.push({ b, tag });
        if (tag === 'line') { const e = endpoints(el); if (e) segs.push({ p: e[0], q: e[1], kind: 'line' }); }
        else if (tag === 'path' || tag === 'polyline' || tag === 'polygon') { const pts = sampled(el); if (pts) for (let k = 1; k < pts.length; k++) segs.push({ p: pts[k - 1], q: pts[k], kind: tag }); }
      });
      // figure extent: every non-text SVG element plus images (for the "is there a drawing, how much of the panel does it use" score)
      let fu = null;
      const addF = b => { fu = fu ? { x: Math.min(fu.x, b.x), y: Math.min(fu.y, b.y), x2: Math.max(fu.x2, b.x + b.w), y2: Math.max(fu.y2, b.y + b.h) } : { x: b.x, y: b.y, x2: b.x + b.w, y2: b.y + b.h }; };
      svgLeaves.forEach(el => { if (el.tagName.toLowerCase() === 'text') return; const b = box(el); if (b.w > 0 || b.h > 0) addF(b); });
      const htmlBlocks = [];
      htmlLeaves.forEach(el => {
        const b = box(el); if (b.w === 0 && b.h === 0) return; add(b);
        const tag = el.tagName.toLowerCase();
        if (tag === 'img') { addF(b); shapes.push({ b, tag: 'image' }); return; }
        const isFx = el.classList.contains('fx'), isBox = isFx && el.classList.contains('box');
        const blk = { b, t: snip(el), tag: isFx ? 'fx' : tag, chars: textOf(el).replace(/\s+/g, '').length, fs: R(parseFloat(getComputedStyle(el).fontSize) || 0), box: isBox };
        htmlBlocks.push(blk);
        texts.push({ b, fs: blk.fs, t: blk.t, fill: getComputedStyle(el).color, chars: blk.chars, clipped: false, kind: 'html', box: isBox });
      });
      // bordered HTML rows/cards count as content for the fill measurement (their text may end above the border)
      Array.from(p.children).filter(el => !(el instanceof SVGElement) && vis(el)).forEach(el => { const b = box(el); if (b.w > 0 && b.h > 0) add(b); });
      const P = { i: pi + 1, box: pb, svg: svgLeaves.length, texts: texts.length, html: htmlBlocks.length };
      const innerArea = Math.max(1, (pb.w - 2 * PAD) * (pb.h - 2 * PAD));
      P.figure = fu ? { x: R(fu.x), y: R(fu.y), w: R(fu.x2 - fu.x), h: R(fu.y2 - fu.y), share: R(100 * (fu.x2 - fu.x) * (fu.y2 - fu.y) / innerArea) / 100 } : null;
      // text runs with size, colour and whether they are free commentary (not inside a shape, wider than 40 % of the inner width);
      // a .fx.box formula strip is its own box, never a free line
      P.runs = texts.map(t => { const inS = t.box || shapes.some(sh => holds(sh, em(t), 1.5)); return { fs: t.fs, x: t.b.x, y: t.b.y, w: t.b.w, h: t.b.h, fill: t.fill, chars: t.chars, t: t.t.slice(0, 24), kind: t.kind, inShape: inS, free: !inS && t.b.w >= 0.4 * (pb.w - 2 * PAD) }; });
      P.shapeBoxes = shapes.map(sh => sh.b);
      P.ink = P.figure;
      P.htmlChars = htmlBlocks.reduce((a, h) => a + (h.chars || 0), 0);
      if (u) {
        P.content = { x: R(u.x), y: R(u.y), w: R(u.x2 - u.x), h: R(u.y2 - u.y) };
        P.gap = { top: R(u.y - pb.y), bottom: R(pb.y + pb.h - u.y2), left: R(u.x - pb.x), right: R(pb.x + pb.w - u.x2) };
      }
      S.panels.push(P);
      texts.forEach(t => {
        if (!contains(pb, t.b, 0.5)) S.findings.push({ kind: 'text-outside-panel', panel: pi + 1, text: t.t, box: t.b, fs: t.fs, panelBox: pb });
        else if (t.clipped) S.findings.push({ kind: 'text-clipped', panel: pi + 1, text: t.t, box: t.b, fs: t.fs });
        else if (!contains(inner, t.b, 0.5)) S.findings.push({ kind: 'text-in-padding', panel: pi + 1, text: t.t, box: t.b, fs: t.fs });
        if (!contains(STAGE, t.b, 0)) S.findings.push({ kind: 'text-outside-stage', panel: pi + 1, text: t.t, box: t.b });
      });
      for (let a = 0; a < texts.length; a++) for (let b = a + 1; b < texts.length; b++) {
        const o = inter(em(texts[a]), em(texts[b]));
        if (o.w > 1.5 && o.h > 1.5) S.findings.push({ kind: 'text-overlap', panel: pi + 1, a: texts[a].t, b: texts[b].t, overlap: { w: R(o.w), h: R(o.h) }, boxA: texts[a].b, boxB: texts[b].b });
      }
      texts.forEach(t => { const e = em(t); shapes.forEach(sh => {
        if (!hits(sh, e)) return;
        if (sh.tag === 'image') S.findings.push({ kind: 'text-crosses-image', panel: pi + 1, text: t.t, box: t.b, shapeBox: sh.b });
        else if (!holds(sh, e, 1.5)) S.findings.push({ kind: 'text-crosses-shape', panel: pi + 1, text: t.t, shape: sh.tag, shapeBox: sh.b, box: t.b });
      }); });
      texts.forEach(t => { const e = em(t); const r = { x: e.x + 1, y: e.y + 1, w: Math.max(0, e.w - 2), h: Math.max(0, e.h - 2) };
        const seen = new Set();
        segs.forEach(sg => { if (!segRect(sg.p, sg.q, r)) return; const key = sg.kind + ':' + Math.round(sg.p.x / 8) + ':' + Math.round(sg.p.y / 8); if (seen.has(key)) return; seen.add(key);
          S.findings.push({ kind: sg.kind === 'line' ? 'text-crosses-line' : 'text-crosses-path', panel: pi + 1, text: t.t, box: t.b, shape: sg.kind, line: [sg.p, sg.q] }); }); });
      for (let a = 0; a < shapes.length; a++) for (let b = a + 1; b < shapes.length; b++) {
        const A = shapes[a], B = shapes[b];
        if (Math.min(A.b.w, A.b.h) < 24 || Math.min(B.b.w, B.b.h) < 24) continue;
        const o = inter(A.b, B.b);
        if (o.w >= 8 && o.h >= 8 && !contains(A.b, B.b, 1) && !contains(B.b, A.b, 1)) S.findings.push({ kind: 'shape-overlap', panel: pi + 1, a: A.tag, b: B.tag, boxA: A.b, boxB: B.b, overlap: { w: R(o.w), h: R(o.h) } });
      }
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
    // slide-level HTML blocks: none may intersect another (title slide h1 over its subtitle, a wrapped h2 over the panels …)
    const blocks = Array.from(s.querySelectorAll(':scope > h1, :scope > h2, :scope > .kicker, :scope > .subtitle, :scope > .who, :scope > .aff, :scope > .venue, :scope > .takeaway, :scope > .cite, :scope > .panel, :scope > .lines, :scope > p, :scope > .cap'))
      .filter(vis).map(el => ({ b: box(el), name: ((el.className && String(el.className).trim().split(/\s+/)[0]) || el.tagName.toLowerCase()), t: snip(el) })).filter(x => x.b.w > 0 && x.b.h > 0);
    for (let a = 0; a < blocks.length; a++) for (let b = a + 1; b < blocks.length; b++) {
      const o = inter(blocks[a].b, blocks[b].b);
      if (o.w > 1.5 && o.h > 1.5) S.findings.push({ kind: 'html-overlap', a: blocks[a].name, b: blocks[b].name, textA: blocks[a].t, textB: blocks[b].t, overlap: { w: R(o.w), h: R(o.h) }, boxA: blocks[a].b, boxB: blocks[b].b });
    }
    const h2 = s.querySelector(':scope > h2');
    if (h2 && vis(h2)) { const b = box(h2), cs = getComputedStyle(h2); const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.2; if (b.h > lh * 1.6) S.findings.push({ kind: 'h2-wraps', box: b, text: snip(h2) }); }
    Array.from(s.querySelectorAll('.takeaway, .lines, .cap, h2, .kicker, h1, .fx.box')).forEach(el => {
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
    if k in ('text-in-padding', 'text-clipped'):
        return f"{k}: \"{f['text']}\" {fmt_box(f['box'])} {f.get('fs', '')}px"
    if k == 'text-overlap':
        return f"{k}: \"{f['a']}\" × \"{f['b']}\" overlap {f['overlap']['w']:g}×{f['overlap']['h']:g} px at {fmt_box(f['boxA'])} / {fmt_box(f['boxB'])}"
    if k == 'text-crosses-shape':
        return f"{k}: \"{f['text']}\" {fmt_box(f['box'])} crosses {f['shape']} {fmt_box(f['shapeBox'])}"
    if k == 'text-crosses-image':
        return f"{k}: \"{f['text']}\" {fmt_box(f['box'])} lies on image {fmt_box(f['shapeBox'])}"
    if k in ('text-crosses-line', 'text-crosses-path'):
        p, q = f['line']
        return f"{k}: \"{f['text']}\" {fmt_box(f['box'])} crossed by {f.get('shape', 'line')} segment ({p['x']:g},{p['y']:g})–({q['x']:g},{q['y']:g})"
    if k == 'shape-clipped':
        return f"{k}: {f['shape']} {fmt_box(f['box'])} leaves its svg {fmt_box(f['svgBox'])}"
    if k == 'shape-overlap':
        return f"{k}: {f['a']} {fmt_box(f['boxA'])} × {f['b']} {fmt_box(f['boxB'])} overlap {f['overlap']['w']:g}×{f['overlap']['h']:g} px"
    if k == 'html-overlap':
        return f"{k}: {f['a']} \"{f['textA'][:30]}\" × {f['b']} \"{f['textB'][:30]}\" overlap {f['overlap']['w']:g}×{f['overlap']['h']:g} px at {fmt_box(f['boxA'])} / {fmt_box(f['boxB'])}"
    if k == 'h2-wraps':
        return f"{k}: title is {f['box']['h']:g} px tall: \"{f['text']}\""
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
                g = P.get('gap')
                fig = P.get('figure')
                print(f"  panel {P['i']} {fmt_box(P['box'])}: {P['texts']} texts · {P['svg']} svg · {P['html']} html"
                      + (f" · gaps t{g['top']:g} b{g['bottom']:g} l{g['left']:g} r{g['right']:g}" if g else ' · empty')
                      + (f" · figure {fig['share'] * 100:.0f}%" if fig else ''))
        for f in errs:
            print('  ERROR ' + describe(f))
        for f in warns:
            print('  warn  ' + describe(f))
    print(f"{len(report['slides'])} slides · {n_err} errors · {n_warn} warnings")
    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    sys.exit(1 if n_err else 0)


if __name__ == '__main__':
    main()

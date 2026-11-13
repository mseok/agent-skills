/* concept-figure kit: expands <fig-*> tags, routes wires between elements by id, and reports layout checks.
   Vocabulary and attributes: references/kit.md. window.figReady resolves to the report once the figure is laid out. */
(() => {
  'use strict';
  const PT = 96 / 72;
  const MM = 96 / 25.4;
  const WIDTHS = { neurips: '5.5in', iclr: '5.5in', icml: '6.75in', 'icml-col': '3.25in', nature: '183mm', 'nature-col': '89mm' };
  const NS = 'http://www.w3.org/2000/svg';
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const num = (el, name, dflt) => (el.hasAttribute(name) ? parseFloat(el.getAttribute(name)) : dflt);
  const list = (el, name) => (el.getAttribute(name) || '').split(',').map((s) => s.trim()).filter(Boolean);
  const f2 = (v) => (Math.round(v * 100) / 100).toString();
  /* Chrome snaps box edges and text baselines to whole layout pixels (0.75 pt at print size), in screenshots and in the PDF alike.
     The page is therefore laid out zoomed (8x when rendered, 2x on screen) and output scaled back, which cuts the snapping to
     1/8 px. getBoundingClientRect reports zoomed pixels; rectOf() returns them in the figure's own CSS pixels. */
  let ZOOM = 1;
  function rectOf(node) {
    const r = node.getBoundingClientRect();
    return { left: r.left / ZOOM, top: r.top / ZOOM, right: r.right / ZOOM, bottom: r.bottom / ZOOM, width: r.width / ZOOM, height: r.height / ZOOM };
  }

  function svgEl(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {})) e.setAttribute(k, v);
    if (parent) parent.appendChild(e);
    return e;
  }
  function rng(seed) {
    let a = seed >>> 0;
    return () => {
      a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  /* A glyph is an inline SVG whose user unit is 1 pt. */
  function glyph(el, w, h) {
    el.replaceChildren();
    return svgEl('svg', { class: 'glyph', width: `${w}pt`, height: `${h}pt`, viewBox: `0 0 ${w} ${h}` }, el);
  }

  /* ---------- glyph tags ---------- */
  let glyphCount = 0;
  const expand = {
    'fig-tokens'(el) {
      const n = num(el, 'n', 5);
      const mask = new Set(list(el, 'mask').map(Number));
      const gap = new Set(list(el, 'gap').map(Number));
      const colors = list(el, 'colors');
      const labels = list(el, 'labels');
      if (el.hasAttribute('size')) el.style.setProperty('--ts', `${num(el, 'size')}pt`);
      el.replaceChildren();
      for (let i = 0; i < n; i++) {
        const t = document.createElement('i');
        t.className = 'tok';
        if (gap.has(i)) { t.classList.add('gap'); t.textContent = el.hasAttribute('v') ? '⋮' : '…'; }
        else {
          if (mask.has(i)) t.classList.add('mask');
          if (colors[i] && colors[i] !== '-') t.dataset.c = colors[i];
          if (labels[i]) t.textContent = labels[i];
        }
        el.appendChild(t);
      }
    },
    'fig-matrix'(el) {
      const rows = num(el, 'rows', 4), cols = num(el, 'cols', rows), size = num(el, 'size', 7);
      const on = el.getAttribute('on') || '';
      const values = list(el, 'values').map(Number), labels = list(el, 'labels');
      const pairs = new Set(on.includes(':') ? on.split(',').map((s) => s.trim()) : []);
      const w = cols * size, h = rows * size, svg = glyph(el, w, h);
      svg.setAttribute('shape-rendering', 'crispEdges');
      for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
        const hit = on === 'all' || (on === 'diag' ? r === c : on === 'lower' ? c <= r : on === 'upper' ? c >= r : pairs.has(`${r}:${c}`));
        const v = values[r * cols + c];
        const fill = Number.isFinite(v) ? `color-mix(in oklab, var(--edge) ${Math.round(v * 100)}%, #fff)`
          : hit ? 'color-mix(in oklab, var(--edge) 38%, #fff)' : el.hasAttribute('dim') ? 'oklch(0.94 0.004 258)' : '#fff';
        svgEl('rect', { x: f2(c * size), y: f2(r * size), width: f2(size), height: f2(size), style: `fill:${fill}` }, svg);
        if (labels[r * cols + c]) svgEl('text', { x: f2((c + 0.5) * size), y: f2((r + 0.5) * size + 1.8), 'text-anchor': 'middle', 'font-size': 5, style: 'fill:var(--ink)' }, svg).textContent = labels[r * cols + c];
      }
      let d = '';
      for (let r = 0; r <= rows; r++) d += `M0,${f2(r * size)}H${f2(w)}`;
      for (let c = 0; c <= cols; c++) d += `M${f2(c * size)},0V${f2(h)}`;
      svgEl('path', { d, style: 'fill:none;stroke:color-mix(in oklab, var(--soft) 50%, var(--edge));stroke-width:0.5' }, svg);
    },
    'fig-dist'(el) {
      const w = num(el, 'w', 36), h = num(el, 'h', 16);
      const comps = list(el, 'mix').map((s) => s.split(':').map(Number));
      const mix = comps.length ? comps : [[0.5, 0.15, 1]];
      const pdf = (x) => mix.reduce((a, [m, s, wt = 1]) => a + (wt * Math.exp(-0.5 * ((x - m) / s) ** 2)) / s, 0);
      const N = 90, ys = Array.from({ length: N + 1 }, (_, i) => pdf(i / N)), top = Math.max(...ys);
      const base = h - 0.4;
      const d = 'M' + ys.map((y, i) => `${f2((i / N) * w)},${f2(base - (y / top) * (h - 1.4))}`).join('L');
      const svg = glyph(el, w, h);
      if (el.hasAttribute('fill')) svgEl('path', { d: `${d}L${w},${base}L0,${base}Z`, style: 'fill:var(--fill);stroke:none' }, svg);
      svgEl('path', { d, style: 'fill:none;stroke:var(--edge);stroke-width:0.8;stroke-linejoin:round' }, svg);
      if (!el.hasAttribute('noaxis')) svgEl('path', { d: `M0,${base}H${w}`, style: 'stroke:var(--line);stroke-width:0.5' }, svg);
    },
    'fig-noise'(el) {
      /* A small illustrated scene standing in for a photo, with gray noise laid over it by t in [0, 1] (0 clean, 1 all noise).
         view="x0,y0,x1,y1" shows a crop of the scene (image patches); scene="day|dusk|sunset" (sunset is dusk pushed further). */
      const w = num(el, 'w', 22), h = num(el, 'h', w), res = num(el, 'res', 12), t = num(el, 't', 0);
      const [vx0, vy0, vx1, vy1] = el.hasAttribute('view') ? list(el, 'view').map(Number) : [0, 0, 1, 1];
      const tone = { day: ['oklch(0.92 0.035 240)', 'oklch(0.97 0.015 235)', 'oklch(0.83 0.13 85)', 'oklch(0.72 0.055 165)', 'oklch(0.53 0.07 168)', 'oklch(0.81 0.085 140)'],
        dusk: ['oklch(0.88 0.06 45)', 'oklch(0.95 0.035 70)', 'oklch(0.67 0.17 30)', 'oklch(0.62 0.06 300)', 'oklch(0.41 0.06 285)', 'oklch(0.56 0.04 225)'],
        sunset: ['oklch(0.70 0.13 25)', 'oklch(0.88 0.10 65)', 'oklch(0.60 0.22 27)', 'oklch(0.47 0.09 305)', 'oklch(0.30 0.07 285)', 'oklch(0.40 0.05 240)'] }[el.getAttribute('scene') || 'day'];
      const svg = glyph(el, w, h), id = `sky${++glyphCount}`;
      const sky = svgEl('linearGradient', { id, x1: 0, y1: 0, x2: 0, y2: 1 }, svgEl('defs', {}, svg));
      svgEl('stop', { offset: 0, 'stop-color': tone[0] }, sky);
      svgEl('stop', { offset: 1, 'stop-color': tone[1] }, sky);
      const pic = svgEl('svg', { x: 0, y: 0, width: w, height: h, viewBox: `${f2(vx0 * 100)} ${f2(vy0 * 100)} ${f2((vx1 - vx0) * 100)} ${f2((vy1 - vy0) * 100)}`, preserveAspectRatio: 'none' }, svg);
      svgEl('rect', { x: 0, y: 0, width: 100, height: 100, fill: `url(#${id})` }, pic);
      svgEl('circle', { cx: 72, cy: 27, r: 10, fill: tone[2] }, pic);
      svgEl('path', { d: 'M0,76C14,60 28,44 41,47C55,50 60,70 76,64C88,60 100,68 100,68V100H0Z', fill: tone[3] }, pic);
      svgEl('path', { d: 'M0,84C18,70 34,64 50,72C66,80 82,78 100,86V100H0Z', fill: tone[4] }, pic);
      svgEl('rect', { x: 0, y: 90, width: 100, height: 10, fill: tone[5] }, pic);
      if (t > 0) {
        const rand = rng(num(el, 'seed', 7)), cw = w / res, ch = h / res, g = svgEl('g', { 'shape-rendering': 'crispEdges', opacity: f2(Math.min(1, t ** 0.75)) }, svg);
        for (let j = 0; j < res; j++) for (let i = 0; i < res; i++) {
          const v = Math.round(150 + 150 * (rand() - 0.5));
          svgEl('rect', { x: f2(i * cw), y: f2(j * ch), width: f2(cw + 0.05), height: f2(ch + 0.05), fill: `rgb(${v},${v},${Math.min(255, v + 4)})` }, g);
        }
      }
      if (!el.closest('.obj')) svgEl('rect', { x: 0, y: 0, width: w, height: h, style: 'fill:none;stroke:var(--hair);stroke-width:0.4' }, svg);
    },
    'fig-net'(el) {
      const layers = list(el, 'layers').map(Number);
      const L = layers.length ? layers : [3, 4, 2];
      const w = num(el, 'w', 34), h = num(el, 'h', 26), r = num(el, 'r', 1.9);
      const svg = glyph(el, w, h);
      const pos = L.map((n, li) => Array.from({ length: n }, (_, k) => [r + 0.5 + (li * (w - 2 * r - 1)) / (L.length - 1), (h * (k + 1)) / (n + 1)]));
      for (let li = 0; li + 1 < pos.length; li++) for (const a of pos[li]) for (const b of pos[li + 1])
        svgEl('path', { d: `M${f2(a[0])},${f2(a[1])}L${f2(b[0])},${f2(b[1])}`, style: 'stroke:var(--ink-3);stroke-width:0.3' }, svg);
      for (const layer of pos) for (const [x, y] of layer)
        svgEl('circle', { cx: f2(x), cy: f2(y), r, style: 'fill:var(--fill);stroke:var(--edge);stroke-width:0.5' }, svg);
    },
    'fig-points'(el) {
      /* clusters="x:y:spread:colour,..." in unit coordinates; ring="x:y:r" draws a dashed circle. */
      const w = num(el, 'w', 34), h = num(el, 'h', 26), n = num(el, 'n', 9), rand = rng(num(el, 'seed', 3));
      const svg = glyph(el, w, h);
      const gauss = () => Math.sqrt(-2 * Math.log(1 - rand())) * Math.cos(2 * Math.PI * rand());
      for (const spec of list(el, 'clusters')) {
        const [x, y, s, c] = spec.split(':');
        const g = svgEl('g', {}, svg);
        if (c) g.dataset.c = c;
        for (let i = 0; i < n; i++) {
          const px = Math.min(w - 1, Math.max(1, (+x + gauss() * +s) * w)), py = Math.min(h - 1, Math.max(1, (+y + gauss() * +s) * h));
          svgEl('circle', { cx: f2(px), cy: f2(py), r: num(el, 'r', 1), style: 'fill:var(--edge)' }, g);
        }
      }
      if (el.hasAttribute('ring')) {
        const [x, y, rr] = el.getAttribute('ring').split(':').map(Number);
        svgEl('circle', { cx: f2(x * w), cy: f2(y * h), r: f2(rr * Math.min(w, h)), style: 'fill:none;stroke:var(--line);stroke-width:0.5;stroke-dasharray:1.6 1.2' }, svg);
      }
    },
    'fig-blob'(el) {
      /* An organic stand-in for a rendered object: seeded smooth outline, flat fill, a lighter highlight. */
      const w = num(el, 'w', 30), h = num(el, 'h', w * 0.8), n = num(el, 'lobes', 7), rand = rng(num(el, 'seed', 11));
      const pts = Array.from({ length: n }, (_, i) => {
        const a = (i / n) * 2 * Math.PI + (rand() - 0.5) * 0.5, r = 0.36 + 0.13 * rand();
        return [w / 2 + Math.cos(a) * r * w, h / 2 + Math.sin(a) * r * h];
      });
      const smooth = (P, k = 1) => {
        let d = `M${f2(P[0][0])},${f2(P[0][1])}`;
        for (let i = 0; i < P.length; i++) {
          const p0 = P[(i + P.length - 1) % P.length], p1 = P[i], p2 = P[(i + 1) % P.length], p3 = P[(i + 2) % P.length];
          d += `C${f2(p1[0] + ((p2[0] - p0[0]) / 6) * k)},${f2(p1[1] + ((p2[1] - p0[1]) / 6) * k)} ${f2(p2[0] - ((p3[0] - p1[0]) / 6) * k)},${f2(p2[1] - ((p3[1] - p1[1]) / 6) * k)} ${f2(p2[0])},${f2(p2[1])}`;
        }
        return `${d}Z`;
      };
      const svg = glyph(el, w, h), id = `blob${++glyphCount}`;
      const grad = svgEl('radialGradient', { id, cx: '36%', cy: '30%', r: '78%' }, svgEl('defs', {}, svg));
      svgEl('stop', { offset: '0', style: 'stop-color:color-mix(in srgb, var(--edge) 38%, #fff)' }, grad);
      svgEl('stop', { offset: '0.55', style: 'stop-color:color-mix(in srgb, var(--edge) 78%, #fff)' }, grad);
      svgEl('stop', { offset: '1', style: 'stop-color:color-mix(in srgb, var(--edge) 88%, #000)' }, grad);
      svgEl('path', { d: smooth(pts), style: `fill:url(#${id});stroke:color-mix(in srgb, var(--edge) 80%, #000);stroke-width:0.45;stroke-linejoin:round` }, svg);
    },
    'fig-bars'(el) {
      const vals = list(el, 'values').map(Number), hi = new Set(list(el, 'on').map(Number));
      const w = num(el, 'w', 5 * vals.length), h = num(el, 'h', 16), bw = w / vals.length, top = Math.max(...vals);
      const svg = glyph(el, w, h);
      vals.forEach((v, i) => {
        const bh = (v / top) * (h - 1);
        svgEl('rect', { x: f2(i * bw + 0.5), y: f2(h - 0.4 - bh), width: f2(bw - 1), height: f2(bh), rx: 0.4,
          style: hi.size && !hi.has(i) ? 'fill:var(--hair)' : 'fill:var(--edge)' }, svg);
      });
      svgEl('path', { d: `M0,${h - 0.3}H${w}`, style: 'stroke:var(--line);stroke-width:0.5' }, svg);
    },
    'fig-icon'(el) {
      const size = num(el, 'size', 8), body = (window.FIG_ICONS || {})[el.getAttribute('name')];
      el.replaceChildren();
      const svg = svgEl('svg', { class: 'glyph', width: `${size}pt`, height: `${size}pt`, viewBox: '0 0 24 24', fill: 'none',
        stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, el);
      if (body) svg.innerHTML = body; else el.dataset.missing = '1';
    },
  };

  /* ---------- geometry ---------- */
  function boxOf(el, root) {
    const r = rectOf(el), o = rectOf(root);
    const b = { l: r.left - o.left, t: r.top - o.top, r: r.right - o.left, b: r.bottom - o.top };
    return { ...b, w: b.r - b.l, h: b.b - b.t, cx: (b.l + b.r) / 2, cy: (b.t + b.b) / 2 };
  }
  const NORMAL = { l: [-1, 0], r: [1, 0], t: [0, -1], b: [0, 1] };
  function anchor(b, side, frac) {
    const f = frac ?? 0.5;
    if (side === 'l') return [b.l, b.t + b.h * f];
    if (side === 'r') return [b.r + (b.back || 0), b.t + b.h * f];
    if (side === 't') return [b.l + b.w * f, b.t - (b.back || 0)];
    return [b.l + b.w * f, b.b];
  }
  function parseEnd(spec) {
    const m = /^#?([^.@\s]+)(?:\.([lrtb]))?(?:@([\d.]+))?$/.exec((spec || '').trim());
    return m ? { id: m[1], side: m[2] || null, frac: m[3] === undefined ? null : parseFloat(m[3]) } : null;
  }
  function roundedPath(pts, R) {
    let d = `M${f2(pts[0][0])},${f2(pts[0][1])}`;
    for (let i = 1; i < pts.length - 1; i++) {
      const [x0, y0] = pts[i - 1], [x1, y1] = pts[i], [x2, y2] = pts[i + 1];
      const a = Math.hypot(x1 - x0, y1 - y0), b = Math.hypot(x2 - x1, y2 - y1), r = Math.min(R, a / 2, b / 2);
      if (a < 0.01 || b < 0.01) continue;
      d += `L${f2(x1 - ((x1 - x0) / a) * r)},${f2(y1 - ((y1 - y0) / a) * r)}Q${f2(x1)},${f2(y1)} ${f2(x1 + ((x2 - x1) / b) * r)},${f2(y1 + ((y2 - y1) / b) * r)}`;
    }
    const e = pts[pts.length - 1];
    return `${d}L${f2(e[0])},${f2(e[1])}`;
  }
  function roundedPoly(pts, R) {
    const n = pts.length;
    let d = '';
    for (let i = 0; i < n; i++) {
      const [x0, y0] = pts[(i + n - 1) % n], [x1, y1] = pts[i], [x2, y2] = pts[(i + 1) % n];
      const a = Math.hypot(x1 - x0, y1 - y0), b = Math.hypot(x2 - x1, y2 - y1), r = Math.min(R, a / 2, b / 2);
      d += `${i ? 'L' : 'M'}${f2(x1 - ((x1 - x0) / a) * r)},${f2(y1 - ((y1 - y0) / a) * r)}Q${f2(x1)},${f2(y1)} ${f2(x1 + ((x2 - x1) / b) * r)},${f2(y1 + ((y2 - y1) / b) * r)}`;
    }
    return `${d}Z`;
  }
  const wireStyle = { r: 2.5, hl: 6, hw: 4.4, notch: 0.3, base: 0.7 * PT };
  /* Arrowhead with a notched back; returns where the shaft should stop (just inside the notch). */
  function head(tip, dir, lw, style, parent) {
    const len = Math.hypot(dir[0], dir[1]) || 1, ux = dir[0] / len, uy = dir[1] / len;
    const hs = Math.sqrt(lw * wireStyle.base), L = hs * wireStyle.hl, W = hs * wireStyle.hw, bx = tip[0] - ux * L, by = tip[1] - uy * L, k = L * (1 - wireStyle.notch);
    svgEl('path', { d: `M${f2(tip[0])},${f2(tip[1])}L${f2(bx - uy * W / 2)},${f2(by + ux * W / 2)}L${f2(tip[0] - ux * k)},${f2(tip[1] - uy * k)}L${f2(bx + uy * W / 2)},${f2(by - ux * W / 2)}Z`, style: `${style};stroke-linejoin:round` }, parent);
    return [tip[0] - ux * k * 0.92, tip[1] - uy * k * 0.92];
  }
  function shift(p, toward, dist) {
    const dx = toward[0] - p[0], dy = toward[1] - p[1], len = Math.hypot(dx, dy) || 1;
    return [p[0] + (dx / len) * dist, p[1] + (dy / len) * dist];
  }

  /* Returns { pts } for polylines or { curve: [p0, c0, c1, p1] } for a cubic. */
  function routeWire(w, A, B, a, b, obstacles) {
    const dx = B.cx - A.cx, dy = B.cy - A.cy;
    const ovx = Math.min(A.r, B.r) - Math.max(A.l, B.l), ovy = Math.min(A.b, B.b) - Math.max(A.t, B.t);
    const horiz = (s) => s === 'l' || s === 'r';
    let kind = w.getAttribute('route');
    if (!kind) {
      if (a.side && b.side) kind = horiz(a.side) ? (horiz(b.side) ? (a.side === b.side ? 'u' : 'hvh') : 'hv') : horiz(b.side) ? 'vh' : a.side === b.side ? 'u' : 'vhv';
      else if (a.side) kind = horiz(a.side) ? (ovy > 1 ? 'h' : 'hv') : ovx > 1 ? 'v' : 'vh';
      else if (b.side) kind = horiz(b.side) ? (ovy > 1 ? 'h' : 'vh') : ovx > 1 ? 'v' : 'hv';
      else kind = ovy > 1 && Math.abs(dx) > 1 ? 'h' : ovx > 1 ? 'v' : Math.abs(dx) >= Math.abs(dy) ? 'hv' : 'vh';
    }
    const hs = dx >= 0 ? ['r', 'l'] : ['l', 'r'], vs = dy >= 0 ? ['b', 't'] : ['t', 'b'];
    if (kind === 'h' || kind === 'v') {
      const [sa, sb] = kind === 'h' ? hs : vs;
      let p0 = anchor(A, a.side || sa, a.frac), p1 = anchor(B, b.side || sb, b.frac);
      const k = kind === 'h' ? 1 : 0;
      if (a.frac !== null && b.frac === null) p1[k] = p0[k];
      else if (b.frac !== null && a.frac === null) p0[k] = p1[k];
      else if (a.frac === null && b.frac === null) {
        const lo = kind === 'h' ? Math.max(A.t, B.t) : Math.max(A.l, B.l), hi = kind === 'h' ? Math.min(A.b, B.b) : Math.min(A.r, B.r);
        if (hi >= lo) p0[k] = p1[k] = (lo + hi) / 2;
      }
      /* a position given on one end moves the other end with it; if that carries the line off the other element, the wire starts in mid-air */
      const off = (P, q) => (kind === 'h' ? q[1] < P.t - 0.5 || q[1] > P.b + 0.5 : q[0] < P.l - 0.5 || q[0] > P.r + 0.5);
      const detached = off(A, p0) ? 'start' : off(B, p1) ? 'end' : null;
      p0[k] += num(w, 'shift', 0) * PT; p1[k] += num(w, 'shift', 0) * PT;
      return { pts: [p0, p1], detached };
    }
    if (kind === 'hv') {
      const p0 = anchor(A, a.side || hs[0], a.frac), p1 = anchor(B, b.side || vs[1], b.frac);
      return { pts: [p0, [p1[0], p0[1]], p1] };
    }
    if (kind === 'vh') {
      const p0 = anchor(A, a.side || vs[0], a.frac), p1 = anchor(B, b.side || hs[1], b.frac);
      return { pts: [p0, [p0[0], p1[1]], p1] };
    }
    if (kind === 'hvh' || kind === 'vhv') {
      const at = num(w, 'at', 0.5);
      if (kind === 'hvh') {
        const p0 = anchor(A, a.side || hs[0], a.frac), p1 = anchor(B, b.side || hs[1], b.frac), xm = p0[0] + (p1[0] - p0[0]) * at;
        return { pts: [p0, [xm, p0[1]], [xm, p1[1]], p1] };
      }
      const p0 = anchor(A, a.side || vs[0], a.frac), p1 = anchor(B, b.side || vs[1], b.frac), ym = p0[1] + (p1[1] - p0[1]) * at;
      return { pts: [p0, [p0[0], ym], [p1[0], ym], p1] };
    }
    if (kind === 'u') {
      /* Leaves and re-enters on one side, clearing every box that sits between the two ends. */
      const s = w.getAttribute('via') || a.side || b.side || 'l', off = num(w, 'off', 5) * PT;
      const p0 = anchor(A, s, a.frac), p1 = anchor(B, s, b.frac), n = NORMAL[s], k = horiz(s) ? 0 : 1;
      const lo = Math.min(p0[1 - k], p1[1 - k]), hi = Math.max(p0[1 - k], p1[1 - k]);
      let edge = n[k] > 0 ? Math.max(p0[k], p1[k]) : Math.min(p0[k], p1[k]);
      const span = horiz(s) ? [Math.min(A.l, B.l), Math.max(A.r, B.r)] : [Math.min(A.t, B.t), Math.max(A.b, B.b)];
      for (const o of obstacles) {
        const [oa, ob] = horiz(s) ? [o.t, o.b] : [o.l, o.r], [ol, oh] = horiz(s) ? [o.l, o.r] : [o.t, o.b];
        if (ob < lo || oa > hi || oh < span[0] || ol > span[1]) continue;
        edge = n[k] > 0 ? Math.max(edge, oh) : Math.min(edge, ol);
      }
      const out = edge + n[k] * off;
      const q0 = k === 0 ? [out, p0[1]] : [p0[0], out], q1 = k === 0 ? [out, p1[1]] : [p1[0], out];
      return { pts: [p0, q0, q1, p1] };
    }
    if (kind === 'curve') {
      const side = w.getAttribute('side');
      const sa = a.side || side || (Math.abs(dx) >= Math.abs(dy) ? hs[0] : vs[0]), sb = b.side || side || (Math.abs(dx) >= Math.abs(dy) ? hs[1] : vs[1]);
      const p0 = anchor(A, sa, a.frac), p1 = anchor(B, sb, b.frac), chord = Math.hypot(p1[0] - p0[0], p1[1] - p0[1]);
      if (sa === sb) {
        /* An arch on one side: `bend` is its height. The control points sit a quarter of the chord in from each end,
           so the line leaves and arrives at an angle and the whole curve is one round bow, not a flat-topped staple. */
        const h = (w.hasAttribute('bend') ? num(w, 'bend') * PT : Math.min(28 * PT, Math.max(10 * PT, 0.3 * chord))) * (4 / 3), n = NORMAL[sa];
        const q = [(p1[0] - p0[0]) / 4, (p1[1] - p0[1]) / 4];
        return { curve: [p0, [p0[0] + q[0] + n[0] * h, p0[1] + q[1] + n[1] * h], [p1[0] - q[0] + n[0] * h, p1[1] - q[1] + n[1] * h], p1] };
      }
      const bend = w.hasAttribute('bend') ? num(w, 'bend') * PT : Math.max(10 * PT, 0.5 * chord);
      return { curve: [p0, [p0[0] + NORMAL[sa][0] * bend, p0[1] + NORMAL[sa][1] * bend], [p1[0] + NORMAL[sb][0] * bend, p1[1] + NORMAL[sb][1] * bend], p1] };
    }
    /* line: border to border along the centre line, for trees and graphs */
    const clip = (bx, from) => {
      if (bx.w < 0.5 && bx.h < 0.5) return [bx.cx, bx.cy];
      const vx = from[0] - bx.cx, vy = from[1] - bx.cy;
      const round = bx.el && getComputedStyle(bx.el).borderTopLeftRadius.endsWith('%');
      if (round) { const len = Math.hypot(vx, vy) || 1; return [bx.cx + (vx / len) * bx.w / 2, bx.cy + (vy / len) * bx.h / 2]; }
      const s = Math.min(bx.w / 2 / Math.abs(vx || 1e-9), bx.h / 2 / Math.abs(vy || 1e-9));
      return [bx.cx + vx * s, bx.cy + vy * s];
    };
    const p0 = a.side ? anchor(A, a.side, a.frac) : clip(A, [B.cx, B.cy]), p1 = b.side ? anchor(B, b.side, b.frac) : clip(B, [A.cx, A.cy]);
    return { pts: [p0, p1], diagonalOk: true };
  }

  /* ---------- layout pass: shapes, wires, braces, zoom lines ---------- */
  const state = { wires: [] };

  function drawShapes(root) {
    for (const el of $$('.node.trap-r, .node.trap-l, .node.trap-u, .node.trap-d, .node.cyl', root)) {
      el.querySelector(':scope > svg.shape-bg')?.remove();
      /* the shape takes the fill and outline the box would have had, whatever the style */
      el.classList.remove('shape');
      const cs = getComputedStyle(el), lw = parseFloat(cs.borderTopWidth) || 0.55 * PT, i = lw / 2;
      const style = `fill:${cs.backgroundColor};stroke:${parseFloat(cs.borderTopWidth) ? cs.borderTopColor : 'none'};stroke-width:${f2(lw)};stroke-linejoin:round`;
      el.classList.add('shape');
      const rect = rectOf(el), w = rect.width, h = rect.height;
      const svg = svgEl('svg', { class: 'shape-bg', width: f2(w), height: f2(h), viewBox: `0 0 ${f2(w)} ${f2(h)}` });
      if (el.classList.contains('cyl')) {
        const ry = Math.min(3.2 * PT, h * 0.16);
        svgEl('path', { d: `M${i},${ry}V${h - ry}A${w / 2 - i},${ry - i} 0 0 0 ${w - i},${h - ry}V${ry}A${w / 2 - i},${ry - i} 0 0 0 ${i},${ry}A${w / 2 - i},${ry - i} 0 0 0 ${w - i},${ry}`, style }, svg);
      } else {
        const sl = num(el, 'data-slant', 0.2);
        const pts = el.classList.contains('trap-r') ? [[i, i], [w - i, h * sl], [w - i, h * (1 - sl)], [i, h - i]]
          : el.classList.contains('trap-l') ? [[i, h * sl], [w - i, i], [w - i, h - i], [i, h * (1 - sl)]]
          : el.classList.contains('trap-u') ? [[w * sl, i], [w * (1 - sl), i], [w - i, h - i], [i, h - i]]
          : [[i, i], [w - i, i], [w * (1 - sl), h - i], [w * sl, h - i]];
        svgEl('path', { d: roundedPoly(pts, 2 * PT), style }, svg);
      }
      el.prepend(svg);
    }
  }

  function strokeStyle(el, lw) {
    const kind = el.getAttribute('kind') || 'flow';
    const color = el.dataset.c ? 'var(--edge)' : kind === 'faint' ? 'var(--ink-3)' : 'var(--line)';
    const dash = kind === 'dash' ? `;stroke-dasharray:${f2(lw * 4)} ${f2(lw * 3)}` : kind === 'dot' ? `;stroke-dasharray:${f2(lw * 0.2)} ${f2(lw * 3)};stroke-linecap:round` : '';
    return { line: `fill:none;stroke:${color};stroke-width:${f2(lw)};stroke-linejoin:${wireStyle.r ? 'round' : 'miter'}${dash}`, fill: `fill:${color};stroke:none` };
  }

  /* A symbol in a circle, chip or cell is centred on its ink: the font's line box puts "+", "×" and digits visibly high. */
  const pen = document.createElement('canvas').getContext('2d');
  function centreInk(root) {
    for (const el of $$('.op, .var, .chip, .tok', root)) {
      const leaves = [];
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      for (let n = walker.nextNode(); n; n = walker.nextNode()) if (n.nodeValue.trim() && !n.parentElement.closest('.katex-mathml')) leaves.push(n);
      if (!leaves.length) continue;
      let ink = el.querySelector(':scope > .ink');
      if (!ink) { ink = document.createElement('span'); ink.className = 'ink'; ink.append(...el.childNodes); el.appendChild(ink); }
      ink.style.transform = 'none';
      let l = Infinity, t = Infinity, r = -Infinity, b = -Infinity;
      for (const n of leaves) {
        const cs = getComputedStyle(n.parentElement), text = n.nodeValue, lead = text.length - text.trimStart().length;
        pen.font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
        const m = pen.measureText(text.trim()), range = document.createRange();
        range.setStart(n, lead); range.setEnd(n, lead + text.trim().length);
        const rect = rectOf(range);
        /* the baseline is read from the layout (a zero-size probe sits on it); font metrics from the canvas differ from the rounded ones the layout uses */
        const probe = document.createElement('span');
        probe.style.cssText = 'display:inline-block;width:0;height:0;vertical-align:baseline';
        n.before(probe);
        const base = rectOf(probe).bottom;
        probe.remove();
        l = Math.min(l, rect.left - m.actualBoundingBoxLeft); r = Math.max(r, rect.left + m.actualBoundingBoxRight);
        t = Math.min(t, base - m.actualBoundingBoxAscent); b = Math.max(b, base + m.actualBoundingBoxDescent);
      }
      const box = rectOf(el);
      ink.style.transform = `translate(${f2((box.left + box.right) / 2 - (l + r) / 2)}px, ${f2((box.top + box.bottom) / 2 - (t + b) / 2)}px)`;
    }
  }

  function layout(root) {
    drawShapes(root);
    centreInk(root);
    $$(':scope > svg.wires', root).forEach((s) => s.remove());
    const W = Math.ceil(rectOf(root).width), H = Math.ceil(rectOf(root).height);
    const svg = svgEl('svg', { class: 'wires', width: W, height: H, viewBox: `0 0 ${W} ${H}` }, root);
    const cs = getComputedStyle(root), cssNum = (name, dflt) => { const v = parseFloat(cs.getPropertyValue(name)); return Number.isFinite(v) ? v : dflt; };
    const lwBase = cssNum('--wire-w', 0.7) * PT, gapBase = 1 * PT;
    Object.assign(wireStyle, { r: cssNum('--wire-r', 2.5), hl: cssNum('--head-l', 6), hw: cssNum('--head-w', 4.4), notch: cssNum('--head-notch', 0.3), base: lwBase });
    const obstacles = $$('.node, .obj, .op, .var, fig-tokens, fig-matrix, .card, .img', root).map((el) => ({ ...boxOf(el, root), el }));
    const paths = {};
    state.wires = []; state.strokes = [];
    const endBox = (end) => {
      if (paths[end.id]) {
        const p = paths[end.id], pt = p.getPointAtLength(p.getTotalLength() * (end.frac ?? 0.5));
        return { box: { l: pt.x, r: pt.x, t: pt.y, b: pt.y, w: 0, h: 0, cx: pt.x, cy: pt.y }, el: null, frac: null };
      }
      const el = document.getElementById(end.id);
      /* a stacked box has copies behind it, up and to the right: a wire on those sides leaves from the outermost copy */
      const back = el && el.matches('.node.stack, .obj.stack') ? (el.classList.contains('two') ? 2 : 3.4) * PT : 0;
      return el && root.contains(el) ? { box: { ...boxOf(el, root), el, back }, el, frac: end.frac } : null;
    };
    for (const w of $$('fig-wire', root)) {
      const a = parseEnd(w.getAttribute('from')), b = parseEnd(w.getAttribute('to'));
      const A = a && endBox(a), B = b && endBox(b);
      const rec = { el: w, from: w.getAttribute('from'), to: w.getAttribute('to'), ok: !!(A && B) };
      state.wires.push(rec);
      if (!rec.ok) continue;
      const lw = lwBase * num(w, 'weight', 1), st = strokeStyle(w, lw), g = svgEl('g', {}, svg);
      if (w.dataset.c) g.dataset.c = w.dataset.c;
      const heads = w.getAttribute('head') || 'end', gap = w.hasAttribute('gap') ? num(w, 'gap') * PT : gapBase;
      /* an end with a head keeps a hair of air before its target; a plain end sits flush on its box, so the line reads as attached */
      const gapA = w.hasAttribute('gap') || heads === 'start' || heads === 'both' ? gap : 0, gapB = w.hasAttribute('gap') || heads === 'end' || heads === 'both' ? gap : 0;
      const r = routeWire(w, A.box, B.box, { ...a, frac: A.frac }, { ...b, frac: B.frac }, obstacles.filter((o) => o.el !== A.el && o.el !== B.el));
      let d, labelAt, labelDir;
      if (r.curve) {
        let [p0, c0, c1, p1] = r.curve;
        /* a bow arrives at an angle, so its head needs a little more air than a straight arrow to clear the edge */
        p0 = shift(p0, c0, A.el ? gapA * 1.8 : 0); p1 = shift(p1, c1, B.el ? gapB * 1.8 : 0);
        if (heads === 'end' || heads === 'both') p1 = head(p1, [p1[0] - c1[0], p1[1] - c1[1]], lw, st.fill, g);
        if (heads === 'start' || heads === 'both') p0 = head(p0, [p0[0] - c0[0], p0[1] - c0[1]], lw, st.fill, g);
        d = `M${f2(p0[0])},${f2(p0[1])}C${f2(c0[0])},${f2(c0[1])} ${f2(c1[0])},${f2(c1[1])} ${f2(p1[0])},${f2(p1[1])}`;
        rec.pts = Array.from({ length: 13 }, (_, i) => { const t = i / 12, m = 1 - t; return [0, 1].map((k) => m * m * m * p0[k] + 3 * m * m * t * c0[k] + 3 * m * t * t * c1[k] + t * t * t * p1[k]); });
        rec.curve = true; labelAt = rec.pts[6]; labelDir = 'curve';
      } else {
        const pts = r.pts.map((p) => [...p]), n = pts.length;
        rec.detached = r.detached || null;
        pts[0] = shift(pts[0], pts[1], A.el ? gapA : 0); pts[n - 1] = shift(pts[n - 1], pts[n - 2], B.el ? gapB : 0);
        rec.pts = pts.map((p) => [...p]); rec.diagonalOk = !!r.diagonalOk;
        if (heads === 'end' || heads === 'both') pts[n - 1] = head(pts[n - 1], [pts[n - 1][0] - pts[n - 2][0], pts[n - 1][1] - pts[n - 2][1]], lw, st.fill, g);
        if (heads === 'start' || heads === 'both') pts[0] = head(pts[0], [pts[0][0] - pts[1][0], pts[0][1] - pts[1][1]], lw, st.fill, g);
        d = roundedPath(pts, wireStyle.r * PT);
        let best = 0, bestLen = -1;
        for (let i = 0; i + 1 < n; i++) { const len = Math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]); if (len > bestLen + 0.5) { best = i; bestLen = len; } }
        const seg = w.hasAttribute('lseg') ? num(w, 'lseg') : best, lp = num(w, 'lp', 0.5);
        labelAt = [pts[seg][0] + (pts[seg + 1][0] - pts[seg][0]) * lp, pts[seg][1] + (pts[seg + 1][1] - pts[seg][1]) * lp];
        labelDir = Math.abs(pts[seg + 1][0] - pts[seg][0]) >= Math.abs(pts[seg + 1][1] - pts[seg][1]) ? 'h' : 'v';
      }
      const path = svgEl('path', { d, style: st.line }, g);
      if (w.id) paths[w.id] = path;
      if (w.hasAttribute('dot') && !A.el) svgEl('circle', { cx: f2(A.box.cx), cy: f2(A.box.cy), r: f2(lw * 1.5), style: st.fill }, g);
      const lab = w._label;
      if (lab) {
        const side = w.getAttribute('ls') || (labelDir === 'h' ? 't' : 'r'), off = 2.2 * PT;
        const tf = { t: ['-50%', '-100%', 0, -off], b: ['-50%', '0', 0, off], l: ['-100%', '-50%', -off, 0], r: ['0', '-50%', off, 0], on: ['-50%', '-50%', 0, 0] }[side];
        lab.classList.toggle('on', side === 'on');
        lab.style.left = `${f2(labelAt[0] + tf[2])}px`; lab.style.top = `${f2(labelAt[1] + tf[3])}px`;
        lab.style.transform = `translate(${tf[0]}, ${tf[1]})`;
      }
    }
    for (const z of $$('fig-zoom', root)) {
      const A = document.getElementById(z.getAttribute('from')), B = document.getElementById(z.getAttribute('to'));
      if (!A || !B) { state.wires.push({ el: z, from: z.getAttribute('from'), to: z.getAttribute('to'), ok: false }); continue; }
      const a = boxOf(A, root), b = boxOf(B, root), style = `fill:none;stroke:var(--ink-3);stroke-width:${f2(lwBase * 0.8)};stroke-dasharray:${f2(lwBase * 4)} ${f2(lwBase * 3)}`;
      const lines = Math.abs(b.cx - a.cx) >= Math.abs(b.cy - a.cy)
        ? (b.cx > a.cx ? [[a.r, a.t, b.l, b.t], [a.r, a.b, b.l, b.b]] : [[a.l, a.t, b.r, b.t], [a.l, a.b, b.r, b.b]])
        : (b.cy > a.cy ? [[a.l, a.b, b.l, b.t], [a.r, a.b, b.r, b.t]] : [[a.l, a.t, b.l, b.b], [a.r, a.t, b.r, b.b]]);
      for (const [x0, y0, x1, y1] of lines) { svgEl('path', { d: `M${f2(x0)},${f2(y0)}L${f2(x1)},${f2(y1)}`, style }, svg); (state.strokes = state.strokes || []).push([[x0, y0], [x1, y1]]); }
    }
    for (const br of $$('fig-brace', root)) {
      const els = list(br, 'of').map((id) => document.getElementById(id.replace(/^#/, ''))).filter(Boolean);
      if (!els.length) { state.wires.push({ el: br, from: br.getAttribute('of'), to: '', ok: false }); continue; }
      const bs = els.map((e) => boxOf(e, root)), u = { l: Math.min(...bs.map((b) => b.l)), r: Math.max(...bs.map((b) => b.r)), t: Math.min(...bs.map((b) => b.t)), b: Math.max(...bs.map((b) => b.b)) };
      const side = br.getAttribute('side') || 'b', dep = 2.4 * PT, off = 1.6 * PT, sgn = side === 'b' || side === 'r' ? 1 : -1;
      const horiz = side === 'b' || side === 't';
      const [s0, s1] = horiz ? [u.l, u.r] : [u.t, u.b], base = (side === 'b' ? u.b : side === 't' ? u.t : side === 'r' ? u.r : u.l) + sgn * off, m = (s0 + s1) / 2;
      const P = (s, depth) => (horiz ? `${f2(s)},${f2(base + sgn * depth)}` : `${f2(base + sgn * depth)},${f2(s)}`);
      const d = `M${P(s0, 0)}Q${P(s0, dep)} ${P(s0 + dep, dep)}L${P(m - dep, dep)}Q${P(m, dep)} ${P(m, 2 * dep)}Q${P(m, dep)} ${P(m + dep, dep)}L${P(s1 - dep, dep)}Q${P(s1, dep)} ${P(s1, 0)}`;
      svgEl('path', { d, style: `fill:none;stroke:var(--line);stroke-width:${f2(lwBase * 0.9)}` }, svg);
      if (br._label) {
        const tip = base + sgn * (2 * dep + 1.2 * PT), lab = br._label;
        lab.style.left = `${f2(horiz ? m : tip)}px`; lab.style.top = `${f2(horiz ? tip : m)}px`;
        lab.style.transform = `translate(${horiz ? '-50%' : side === 'r' ? '0' : '-100%'}, ${horiz ? (side === 'b' ? '0' : '-100%') : '-50%'})`;
      }
    }
    for (const k of $$('.wk', root)) {
      k.replaceChildren();
      const s = svgEl('svg', { class: 'glyph', width: '14pt', height: '6pt', viewBox: '0 0 14 6' }, k);
      const fake = { getAttribute: (n) => (n === 'kind' ? k.dataset.kind : null), dataset: k.dataset };
      const st = strokeStyle(fake, 0.6);
      const end = head([13.6, 3], [1, 0], 0.6, st.fill, s);
      svgEl('path', { d: `M0.4,3L${f2(end[0])},3`, style: st.line }, s);
    }
  }

  /* ---------- checks ---------- */
  function name(el) {
    if (el.id) return `#${el.id}`;
    const copy = el.cloneNode(true);
    copy.querySelectorAll('.katex-mathml').forEach((m) => m.remove());
    const text = copy.textContent.trim().replace(/\s+/g, ' ').slice(0, 24);
    return `${el.tagName.toLowerCase()}${el.classList.length ? '.' + [...el.classList].join('.') : ''}${text ? ` "${text}"` : ''}`;
  }
  function report(root) {
    const issues = [], add = (level, code, msg) => issues.push({ level, code, msg });
    const R = boxOf(root, root), minPt = num(root, 'data-min-pt', 6);
    /* text sizes and word count */
    const sizes = [];
    let words = 0;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const mathSeen = new Set();
    for (let n = walker.nextNode(); n; n = walker.nextNode()) {
      const text = n.nodeValue.trim(), el = n.parentElement;
      if (!text || el.closest('script, style, .katex-mathml, fig-wire, fig-brace, fig-zoom')) continue;
      const math = el.closest('.katex');
      if (math) { if (mathSeen.has(math)) continue; mathSeen.add(math); }
      const pt = parseFloat(getComputedStyle(math || el).fontSize) / PT;
      sizes.push(pt);
      words += math ? 1 : (text.match(/[\p{L}\p{N}]+/gu) || []).length;
      if (pt < 5 - 0.01) add('error', 'text-size', `${f2(pt)} pt text in ${name(math ? math.parentElement : el)} (below 5 pt)`);
      else if (pt < minPt - 0.01) add('warn', 'text-size', `${f2(pt)} pt text in ${name(math ? math.parentElement : el)} (below ${minPt} pt)`);
    }
    sizes.sort((a, b) => a - b);
    /* bounds and overflow */
    const solid = $$('.node, .obj, .op, .var, .pt, .at, fig-tokens, fig-matrix, .card, .img, .label, .title, .wire-label, .cap, .key, svg.glyph, .gl, .hc', root)
      .filter((el) => el.getClientRects().length && !el.closest('.wk'));
    const boxes = solid.map((el) => ({ el, ...boxOf(el, root) }));
    for (const b of boxes) if (b.l < -0.6 || b.t < -0.6 || b.r > R.w + 0.6 || b.b > R.h + 0.6) add('error', 'out-of-bounds', `${name(b.el)} extends outside the figure`);
    for (const g of $$('.group:not(.bare)', root)) { const b = boxOf(g, root); if (b.l < -0.6 || b.t < -0.6 || b.r > R.w + 0.6 || b.b > R.h + 0.6) add('error', 'out-of-bounds', `${name(g)} extends outside the figure (its content is wider than the space it has)`); }
    for (const el of $$('.node, .obj, .card, .group, .panel', root)) {
      const o = rectOf(el);
      const spill = [...el.children].some((ch) => {
        if (ch.matches('.badge, .gl, .tab, .cap, svg.shape-bg') || getComputedStyle(ch).position === 'absolute') return false;
        const r = rectOf(ch);
        return r.width > 0 && (r.left < o.left - 1 || r.top < o.top - 1 || r.right > o.right + 1 || r.bottom > o.bottom + 1);
      });
      if (spill) add('error', 'overflow', `content overflows ${name(el)}`);
    }
    /* a wire with both ends inside one .plane is a stroke of that drawing: its label may lie on the plane, and its style needs no key */
    const planeOf = (w) => { const ps = [w.from, w.to].map((q) => { const e = parseEnd(q), el = e && document.getElementById(e.id); return el && el.closest('.plane'); }); return ps[0] && ps[0] === ps[1] ? ps[0] : null; };
    const drawn = new Map(state.wires.filter((w) => w.el._label && planeOf(w)).map((w) => [w.el._label, planeOf(w)]));
    /* overlaps between unrelated items */
    for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
      const a = boxes[i], b = boxes[j];
      if (a.el.contains(b.el) || b.el.contains(a.el) || drawn.get(a.el) === b.el || drawn.get(b.el) === a.el) continue;
      if (a.el.closest('[data-overlap="ok"]') || b.el.closest('[data-overlap="ok"]') || a.el.closest('.badge') || b.el.closest('.badge')) continue;
      const ox = Math.min(a.r, b.r) - Math.max(a.l, b.l), oy = Math.min(a.b, b.b) - Math.max(a.t, b.t);
      if (ox > 1 && oy > 1) add('warn', 'overlap', `${name(a.el)} overlaps ${name(b.el)}`);
    }
    /* a label that straddles the edge of a container it does not belong to */
    for (const lab of boxes.filter((b) => b.el.matches('.label, .wire-label, .hc, .cap, .title'))) for (const g of $$('.group:not(.bare)', root)) {
      if (g.contains(lab.el)) continue;
      const q = boxOf(g, root), ox = Math.min(lab.r, q.r) - Math.max(lab.l, q.l), oy = Math.min(lab.b, q.b) - Math.max(lab.t, q.t);
      const inside = lab.l >= q.l && lab.r <= q.r && lab.t >= q.t && lab.b <= q.b;
      if (ox > 0.5 && oy > 0.5 && !inside) add('warn', 'label-on-edge', `${name(lab.el)} sits across the edge of ${name(g)}`);
    }
    /* wires */
    const hitTargets = $$('.node, .obj, .op, .var, .at, fig-tokens, fig-matrix, .card, .img, .label, .title, .wire-label, .hc', root).map((el) => ({ el, ...boxOf(el, root) }));
    const styles = new Set(), crossed = new Set();
    for (const w of state.wires) {
      if (!w.ok) { add('error', 'wire-target', `${w.el.tagName.toLowerCase()} ${w.from} → ${w.to}: element not found`); continue; }
      if (!w.pts) continue;
      if (w.el.tagName === 'FIG-WIRE' && w.el.getAttribute('kind') !== 'faint' && !w.el.hasAttribute('label') && !planeOf(w)) styles.add(`${w.el.getAttribute('kind') || 'flow'}|${w.el.dataset.c || ''}`);
      const ends = [parseEnd(w.from), parseEnd(w.to)].map((e) => document.getElementById(e.id));
      const length = w.pts.slice(1).reduce((a, q, i) => a + Math.hypot(q[0] - w.pts[i][0], q[1] - w.pts[i][1]), 0) / PT;
      /* a label that lies on its own line (a long label inside a shallow bow) */
      if (w.el._label && w.el.getAttribute('ls') !== 'on' && w.el._label.getClientRects().length) {
        const q = boxOf(w.el._label, root);
        let on = false;
        for (let i = 0; i + 1 < w.pts.length && !on; i++) for (let k = 0; k <= 8 && !on; k++) {
          const x = w.pts[i][0] + ((w.pts[i + 1][0] - w.pts[i][0]) * k) / 8, y = w.pts[i][1] + ((w.pts[i + 1][1] - w.pts[i][1]) * k) / 8;
          on = x > q.l + 0.5 && x < q.r - 0.5 && y > q.t + 1 && y < q.b - 1;
        }
        if (on) add('warn', 'label-on-wire', `the label of wire ${w.from} → ${w.to} lies on its own line (raise bend, shorten the label or move it with ls)`);
      }
      if (w.detached) add('warn', 'wire-detached', `wire ${w.from} → ${w.to}: its ${w.detached} lies off the element it leaves from (the position given on the other end is outside this element's span; align the two or use a bend)`);
      if (w.el.tagName === 'FIG-WIRE' && length < 8 && (w.el.getAttribute('head') || 'end') !== 'none' && !planeOf(w)) add('warn', 'wire-short', `wire ${w.from} → ${w.to} is ${f2(length)} pt long, mostly arrowhead (leave at least 10 pt between the boxes)`);
      if (w.pts.some(([x, y]) => x < 0 || y < 0 || x > R.w || y > R.h)) add('error', 'out-of-bounds', `wire ${w.from} → ${w.to} leaves the figure (add padding on that side)`);
      for (let i = 0; i + 1 < w.pts.length; i++) {
        const [x0, y0] = w.pts[i], [x1, y1] = w.pts[i + 1];
        if (!w.diagonalOk && !w.curve && Math.abs(x1 - x0) > 0.8 && Math.abs(y1 - y0) > 0.8)
          add('warn', 'wire-diagonal', `wire ${w.from} → ${w.to} has a diagonal segment (align the boxes or set route)`);
        for (const t of hitTargets) {
          if (ends.some((e) => e && (e === t.el || e.contains(t.el) || t.el.contains(e))) || t.el === w.el._label) continue;
          const l = t.l + 1, r = t.r - 1, tp = t.t + 1, bt = t.b - 1;
          if (Math.max(x0, x1) < l || Math.min(x0, x1) > r || Math.max(y0, y1) < tp || Math.min(y0, y1) > bt) continue;
          let hit = false;
          for (let s = 0; s <= 8 && !hit; s++) { const x = x0 + ((x1 - x0) * s) / 8, y = y0 + ((y1 - y0) * s) / 8; hit = x > l && x < r && y > tp && y < bt; }
          const msg = `wire ${w.from} → ${w.to} passes through ${name(t.el)}`;
          if (hit && !crossed.has(msg)) { crossed.add(msg); add('warn', 'wire-crossing', msg); }
        }
      }
    }
    /* a bent wire needs room on every leg: a short last leg leaves only the head at the corner, a short middle leg reads as a kink */
    for (const w of state.wires) {
      if (!w.pts || w.curve || w.el.tagName !== 'FIG-WIRE' || w.pts.length < 3) continue;
      const heads = w.el.getAttribute('head') || 'end', n = w.pts.length;
      for (let i = 0; i + 1 < n; i++) {
        const len = Math.hypot(w.pts[i + 1][0] - w.pts[i][0], w.pts[i + 1][1] - w.pts[i][1]) / PT;
        const headed = (i === n - 2 && (heads === 'end' || heads === 'both')) || (i === 0 && (heads === 'start' || heads === 'both'));
        if (len < (headed ? 8 : 4)) { add('warn', 'wire-leg', `wire ${w.from} → ${w.to} has a ${f2(len)} pt ${headed ? 'last leg, so only the arrowhead shows after the bend' : 'leg, which reads as a kink'} (move the boxes apart, or line them up and use a straight wire)`); break; }
      }
    }
    /* text or an object that crosses a panel rule or leaves its panel collides with the neighbouring panel */
    for (const rule of $$('.vr, .hr', root)) {
      if (!rule.getClientRects().length) continue;
      const q = boxOf(rule, root), vertical = rule.classList.contains('vr');
      for (const b of boxes) {
        const across = vertical ? (q.l > b.l + 0.5 && q.l < b.r - 0.5 && b.b > q.t && b.t < q.b) : (q.t > b.t + 0.5 && q.t < b.b - 0.5 && b.r > q.l && b.l < q.r);
        if (across) add('warn', 'on-rule', `${name(b.el)} crosses the rule between panels (shorten it, let it wrap, or widen the panel)`);
      }
    }
    for (const panel of $$('.panel', root)) {
      const q = boxOf(panel, root);
      for (const b of boxes) if (panel.contains(b.el) && (b.l < q.l - 1 || b.r > q.r + 1)) add('warn', 'panel-overflow', `${name(b.el)} is wider than its panel and runs into the next one`);
      for (const g of $$('.group:not(.bare)', panel)) { const b = boxOf(g, root); if (b.l < q.l - 1 || b.r > q.r + 1) add('warn', 'panel-overflow', `${name(g)} is wider than its panel and runs into the next one`); }
    }
    /* boxes at one level carry one text size: a smaller box among its siblings looks like a mistake, not a hierarchy */
    for (const c of new Set($$('.node', root).map((n) => n.parentElement))) {
      const sizes = new Set([...c.children].filter((k) => k.matches('.node') && k.getClientRects().length).map((k) => Math.round((parseFloat(getComputedStyle(k).fontSize) / PT) * 4) / 4));
      if (sizes.size > 1) add('warn', 'text-level', `boxes side by side in ${name(c)} use different text sizes (${[...sizes].sort((a, b) => a - b).join(', ')} pt); give one level one size`);
    }
    /* zoom lines are strokes too: one that runs through a piece of text is a collision */
    for (const [[x0, y0], [x1, y1]] of state.strokes || []) for (const el of $$('.key, .label, .hc, .cap, .title, .wire-label, .gl', root)) {
      if (!el.getClientRects().length) continue;
      const q = boxOf(el, root);
      let hit = false;
      for (let k = 0; k <= 60 && !hit; k++) { const x = x0 + ((x1 - x0) * k) / 60, y = y0 + ((y1 - y0) * k) / 60; hit = x > q.l + 0.5 && x < q.r - 0.5 && y > q.t + 0.5 && y < q.b - 0.5; }
      if (hit) add('warn', 'wire-crossing', `a zoom line passes through ${name(el)}`);
    }
    { const mm = metrics(root);
      if (mm.slack > 0.24) add('warn', 'empty-space', `${Math.round(mm.slack * 100)} % of the drawn area is farther than 6 pt from anything drawn (dense published figures: 11 to 15 %, sparse ones up to 29 %); enlarge the objects, shorten the gaps or make the figure smaller`);
      if (mm.largest_empty > 0.12 && mm.largest_empty_mm) add('warn', 'empty-space', `an empty area of ${mm.largest_empty_mm[2]} x ${mm.largest_empty_mm[3]} mm at ${mm.largest_empty_mm[0]} mm from the left, ${mm.largest_empty_mm[1]} mm from the top (${Math.round(mm.largest_empty * 100)} % of the drawn area)`); }
    if (styles.size > 1 && !root.querySelector('.legend .wk')) add('warn', 'wire-key', `${styles.size} unlabelled wire styles and no key (.legend with .wk)`);
    for (const el of $$('fig-icon[data-missing]', root)) add('error', 'icon', `unknown icon "${el.getAttribute('name')}"`);
    /* colour roles and use of the width */
    const roles = new Set($$('[data-c]', root).map((el) => el.dataset.c).filter((c) => c !== 'gray' && c !== 'none'));
    if (roles.size > 4) add('warn', 'colour-roles', `${roles.size} colour roles (${[...roles].join(', ')}); four is the usual ceiling`);
    const content = [...boxes.filter((b) => !b.el.classList.contains('wire-label')), ...$$('.group', root).map((el) => boxOf(el, root))];
    const used = content.length ? (Math.max(...content.map((b) => b.r)) - Math.min(...content.map((b) => b.l))) / R.w : 0;
    if (used < 0.9) add('warn', 'width-use', `content spans ${Math.round(used * 100)} % of the width`);
    if (words > 70) add('warn', 'words', `${words} words in the figure (reference figures: 6 to 110, most under 60)`);
    return {
      width_mm: +(R.w / MM).toFixed(2), height_mm: +(R.h / MM).toFixed(2), width_px: R.w, height_px: R.h, zoom: ZOOM,
      min_text_pt: sizes.length ? +sizes[0].toFixed(2) : null, median_text_pt: sizes.length ? +sizes[sizes.length >> 1].toFixed(2) : null,
      words, nodes: $$('.node, .obj', root).length, wires: state.wires.filter((w) => w.el.tagName === 'FIG-WIRE').length,
      colour_roles: [...roles], wire_styles: styles.size, metrics: metrics(root),
      errors: issues.filter((i) => i.level === 'error').length, warnings: issues.filter((i) => i.level === 'warn').length, issues,
    };
  }

  /* ---------- measured layout metrics (scored by scripts/score.py) ---------- */
  function metrics(root) {
    const R = boxOf(root, root), tol = 0.8;
    /* a .plane is one layout item; what is placed freely inside it is a drawing, not part of the grid */
    const all = $$('.node, .obj, .op, .var, .plane, fig-tokens, fig-matrix, .card, .img, fig-dist, fig-noise, fig-net, fig-points, fig-bars, fig-blob', root)
      .filter((el) => el.getClientRects().length && !el.closest('.legend') && !(el.parentElement && el.parentElement.closest('.plane'))).map((el) => ({ el, ...boxOf(el, root) }));
    const items = all.filter((a) => !all.some((b) => b !== a && a.el.contains(b.el)));
    const near = (a, b) => Math.abs(a - b) <= tol;
    let any = 0, both = 0;
    const loose = [];
    for (const a of items) {
      const x = items.some((b) => b !== a && (near(a.l, b.l) || near(a.cx, b.cx) || near(a.r, b.r)));
      const y = items.some((b) => b !== a && (near(a.t, b.t) || near(a.cy, b.cy) || near(a.b, b.b)));
      any += x || y; both += x && y;
      if (!x && !y) loose.push(name(a.el));
    }
    /* spacing rhythm: gaps between consecutive children of every flex container with three or more children */
    const cvs = [], gapSet = new Set();
    for (const c of $$('.row, .col, .panels, .group', root)) {
      const kids = [...c.children].filter((k) => k.getClientRects().length && getComputedStyle(k).position !== 'absolute' && !k.matches('fig-wire, fig-brace, fig-zoom, .vr, .hr'));
      if (kids.length < 2) continue;
      const col = getComputedStyle(c).flexDirection.startsWith('column');
      const bs = kids.map((k) => boxOf(k, root)).sort((a, b) => (col ? a.t - b.t : a.l - b.l));
      const gaps = bs.slice(1).map((b, i) => (col ? b.t - bs[i].b : b.l - bs[i].r)).filter((g) => g > -0.5);
      gaps.forEach((g) => gapSet.add(Math.round(g / PT)));
      if (gaps.length >= 2) { const m = gaps.reduce((a, g) => a + g, 0) / gaps.length; if (m > 0.5) cvs.push(Math.sqrt(gaps.reduce((a, g) => a + (g - m) ** 2, 0) / gaps.length) / m); }
    }
    /* occupancy grid: covered cells, largest empty rectangle, centroid */
    const cell = 3, gw = Math.max(1, Math.ceil(R.w / cell)), gh = Math.max(1, Math.ceil(R.h / cell));
    const grid = Array.from({ length: gh }, () => new Uint8Array(gw));
    const mark = (l, t, r, b) => { for (let y = Math.max(0, Math.floor(t / cell)); y <= Math.min(gh - 1, Math.floor(b / cell)); y++) for (let x = Math.max(0, Math.floor(l / cell)); x <= Math.min(gw - 1, Math.floor(r / cell)); x++) grid[y][x] = 1; };
    for (const el of $$('.node, .obj, .op, .var, .pt, .at, fig-tokens, fig-matrix, .card, .img, svg.glyph, .label, .title, .cap, .gl, .key, .wire-label, .hc', root)) { if (!el.getClientRects().length) continue; const b = boxOf(el, root); mark(b.l, b.t, b.r, b.b); }
    for (const el of $$('.group:not(.bare), .vr, .hr', root)) { if (!el.getClientRects().length) continue; const b = boxOf(el, root); mark(b.l, b.t, b.r, b.t); mark(b.l, b.b, b.r, b.b); mark(b.l, b.t, b.l, b.b); mark(b.r, b.t, b.r, b.b); }
    for (const pts of [...state.wires.filter((w) => w.pts).map((w) => w.pts), ...(state.strokes || [])]) for (let i = 0; i + 1 < pts.length; i++) { const [x0, y0] = pts[i], [x1, y1] = pts[i + 1]; const n = Math.ceil(Math.hypot(x1 - x0, y1 - y0) / cell) + 1; for (let k = 0; k <= n; k++) { const x = x0 + ((x1 - x0) * k) / n, y = y0 + ((y1 - y0) * k) / n; mark(x, y, x, y); } }
    /* everything below is measured inside the bounding box of what is drawn, so the page margin does not count */
    let bx0 = gw, by0 = gh, bx1 = -1, by1 = -1;
    for (let y = 0; y < gh; y++) for (let x = 0; x < gw; x++) if (grid[y][x]) { bx0 = Math.min(bx0, x); bx1 = Math.max(bx1, x); by0 = Math.min(by0, y); by1 = Math.max(by1, y); }
    if (bx1 < 0) { bx0 = 0; by0 = 0; bx1 = gw - 1; by1 = gh - 1; }
    const bw = bx1 - bx0 + 1, bh = by1 - by0 + 1, total = bw * bh;
    let covered = 0, sx = 0, sy = 0, best = 0, hole = null;
    const heights = new Int32Array(gw);
    for (let y = by0; y <= by1; y++) {
      for (let x = bx0; x <= bx1; x++) { if (grid[y][x]) { covered++; sx += x; sy += y; heights[x] = 0; } else heights[x]++; }
      const stack = [];
      for (let x = bx0; x <= bx1 + 1; x++) { const h = x <= bx1 ? heights[x] : 0; let start = x; while (stack.length && stack[stack.length - 1][1] >= h) { const [sx0, sh] = stack.pop(); if (sh * (x - sx0) > best) { best = sh * (x - sx0); hole = [sx0, y - sh + 1, x - sx0, sh]; } start = sx0; } stack.push([start, h]); }
    }
    /* slack: white space beyond what separates objects, the share of that box farther than about 6 pt from anything drawn */
    const reach = Math.round((6 * PT) / cell);
    let far = 0;
    for (let y = by0; y <= by1; y++) for (let x = bx0; x <= bx1; x++) {
      let near = false;
      for (let v = Math.max(0, y - reach); v <= Math.min(gh - 1, y + reach) && !near; v++) for (let u = Math.max(0, x - reach); u <= Math.min(gw - 1, x + reach) && !near; u++) near = grid[v][u] === 1;
      if (!near) far++;
    }
    /* wires: crossings, bends, backtracking against the main direction */
    const polys = state.wires.filter((w) => w.pts && w.el.tagName === 'FIG-WIRE');
    const segs = polys.flatMap((w, wi) => w.pts.slice(1).map((q, i) => ({ wi, a: w.pts[i], b: q })));
    const ccw = (p, q, r) => (r[1] - p[1]) * (q[0] - p[0]) - (q[1] - p[1]) * (r[0] - p[0]);
    let crossings = 0;
    for (let i = 0; i < segs.length; i++) for (let j = i + 1; j < segs.length; j++) {
      const s = segs[i], u = segs[j];
      if (s.wi === u.wi) continue;
      const d1 = ccw(s.a, s.b, u.a), d2 = ccw(s.a, s.b, u.b), d3 = ccw(u.a, u.b, s.a), d4 = ccw(u.a, u.b, s.b), e = 4;
      if (((d1 > e && d2 < -e) || (d1 < -e && d2 > e)) && ((d3 > e && d4 < -e) || (d3 < -e && d4 > e))) crossings++;
    }
    let dx = 0, dy = 0, pos = 0, neg = 0, bends = 0;
    for (const w of polys) { if (!w.curve) bends += w.pts.length - 2; const a = w.pts[0], b = w.pts[w.pts.length - 1]; dx += Math.abs(b[0] - a[0]); dy += Math.abs(b[1] - a[1]); }
    const k = dx >= dy ? 0 : 1;
    for (const w of polys) { const d = w.pts[w.pts.length - 1][k] - w.pts[0][k]; if (d >= 0) pos += d; else neg -= d; }
    const sizes = new Set(), heightsSet = new Set();
    const tw = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    for (let n = tw.nextNode(); n; n = tw.nextNode()) { const el = n.parentElement; if (!n.nodeValue.trim() || el.closest('script, style, .katex, fig-wire, fig-brace, fig-zoom')) continue; sizes.add(Math.round((parseFloat(getComputedStyle(el).fontSize) / PT) * 4) / 4); }
    for (const el of $$('.node:not(.sm):not(.lg)', root)) heightsSet.add(Math.round(rectOf(el).height / PT));
    const r3 = (v) => Math.round(v * 1000) / 1000;
    return {
      items: items.length, aligned_any: items.length ? r3(any / items.length) : 1, aligned_both: items.length ? r3(both / items.length) : 1, unaligned: loose,
      gap_cv: cvs.length ? r3(cvs.reduce((a, v) => a + v, 0) / cvs.length) : 0, gap_sizes: gapSet.size,
      occupancy: r3(covered / total), largest_empty: r3(best / total), slack: r3(far / total),
      largest_empty_mm: hole ? hole.map((v) => Math.round((v * cell / PT) * 0.3528 * 10) / 10) : null,
      centroid_dx: covered ? r3((sx / covered + 0.5) / gw - 0.5) : 0, centroid_dy: covered ? r3((sy / covered + 0.5) / gh - 0.5) : 0,
      wire_crossings: crossings, bends_per_wire: polys.length ? r3(bends / polys.length) : 0,
      backtrack: pos + neg > 0 ? r3(Math.min(pos, neg) / (pos + neg)) : 0, main_axis: k === 0 ? 'horizontal' : 'vertical',
      text_sizes: [...sizes].sort((a, b) => a - b), node_heights: heightsSet.size,
    };
  }

  /* ---------- boot ---------- */
  async function boot() {
    const root = document.querySelector('.fig');
    const render = new URLSearchParams(location.search).has('render');
    if (!render) document.documentElement.classList.add('screen');
    const setZoom = (z) => { ZOOM = z; document.documentElement.style.zoom = z; };
    setZoom(render ? 8 : 2);
    const width = root.dataset.width || 'neurips';
    root.style.width = WIDTHS[width] || width;
    for (const [tag, fn] of Object.entries(expand)) for (const el of $$(tag, root)) fn(el);
    for (const el of $$('.node:not(.col):not(.row), .key, .card, .obj', root)) {
      const keep = el.classList.contains('key') ? '.sw, .wk, .chip, fig-icon'
        : el.classList.contains('obj') ? '.badge, img, svg, fig-tokens, fig-matrix, fig-dist, fig-noise, fig-net, fig-points, fig-bars, fig-blob, .row, .col' : '.badge, .gl, .tab';
      const flow = [...el.childNodes].filter((n) => !(n.nodeType === 1 && n.matches(keep)));
      if (!flow.some((n) => n.nodeType === 3 && n.nodeValue.trim())) continue;
      const span = document.createElement('span');
      span.className = 'flow';
      flow[0].before(span);
      span.append(...flow);
    }
    for (const w of $$('fig-wire[label], fig-brace[label]', root)) {
      const lab = document.createElement('div');
      lab.className = 'wire-label';
      if (w.dataset.c) lab.dataset.c = w.dataset.c;
      lab.innerHTML = w.getAttribute('label');
      root.appendChild(lab);
      w._label = lab;
    }
    if (window.renderMathInElement) window.renderMathInElement(root, { delimiters: [{ left: '$', right: '$', display: false }], throwOnError: false });
    await document.fonts.ready;
    await Promise.all($$('img', root).map((img) => (img.complete ? null : new Promise((res) => { img.onload = img.onerror = res; }))));
    layout(root);
    await document.fonts.ready;
    layout(root);
    const page = document.createElement('style');
    page.textContent = `@page { size: ${(rectOf(root).width / 96).toFixed(4)}in ${(Math.ceil(rectOf(root).height + 1) / 96).toFixed(4)}in; margin: 0 }`;
    document.head.appendChild(page);
    window.addEventListener('resize', () => layout(root));
    if (!render) {
      window.addEventListener('beforeprint', () => { setZoom(1); layout(root); });
      window.addEventListener('afterprint', () => { setZoom(2); layout(root); });
    }
    window.figRelayout = () => { layout(root); return report(root); };
    return report(root);
  }
  window.figReady = new Promise((resolve) => {
    const go = () => boot().then(resolve, (err) => resolve({ errors: 1, warnings: 0, issues: [{ level: 'error', code: 'kit', msg: String(err && err.stack || err) }] }));
    if (document.readyState === 'complete') go(); else window.addEventListener('load', go);
  });
})();

/* Shared helpers for canvas animations: seeded RNG, palette, easing, a DPR-aware canvas surface
   and a few drawing primitives. Canvas coordinates are stage pixels (the canvas width/height attributes). */
(function () {
  'use strict';

  function mulberry32(seed) {
    let a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function makeRng(seed) {
    const u = mulberry32(seed || 1);
    let spare = null;
    return {
      u,
      uniform: (a, b) => a + (b - a) * u(),
      int: n => Math.floor(u() * n),
      normal: () => {
        if (spare !== null) { const s = spare; spare = null; return s; }
        let x, y, s;
        do { x = 2 * u() - 1; y = 2 * u() - 1; s = x * x + y * y; } while (s >= 1 || s === 0);
        const m = Math.sqrt(-2 * Math.log(s) / s);
        spare = y * m; return x * m;
      },
      pick: arr => arr[Math.floor(u() * arr.length)]
    };
  }

  // palette: keep in sync with the CSS custom properties in css/deck.css
  const C = {
    bg: '#FAF8F3', card: '#FFFFFF', ink: '#1F2933', inkSoft: '#52606D', muted: '#8A96A3', faint: '#E3E7EB', grid: '#ECEFF2',
    navy: '#1D3A5F', teal: '#2A9D8F', tealDark: '#1F7A6F', blue: '#4C72B0', orange: '#F0A23A', coral: '#E76F51',
    violet: '#6B5E9B', copper: '#C8692E', yellow: '#E9C46A', gold: '#D9A21B', steel: '#8E9AA6'
  };
  function hexToRgb(hex) {
    const h = hex.replace('#', ''), v = h.length === 3 ? h.split('').map(c => c + c).join('') : h;
    return [parseInt(v.slice(0, 2), 16), parseInt(v.slice(2, 4), 16), parseInt(v.slice(4, 6), 16)];
  }
  function rgba(hex, a) { const [r, g, b] = hexToRgb(hex); return `rgba(${r},${g},${b},${a})`; }
  function mix(h1, h2, t) {
    const a = hexToRgb(h1), b = hexToRgb(h2), c = a.map((v, i) => Math.round(v + (b[i] - v) * t));
    return `rgb(${c[0]},${c[1]},${c[2]})`;
  }

  const E = {
    clamp: (x, a = 0, b = 1) => Math.max(a, Math.min(b, x)),
    smooth: t => { t = E.clamp(t); return t * t * (3 - 2 * t); },
    smoother: t => { t = E.clamp(t); return t * t * t * (t * (6 * t - 15) + 10); },
    inOut: t => { t = E.clamp(t); return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; },
    out: t => { t = E.clamp(t); return 1 - Math.pow(1 - t, 3); },
    seg: (t, a, b) => E.clamp((t - a) / (b - a))
  };

  // logical size comes from the width/height attributes; backing store follows stage scale × DPR
  function surface(canvas) {
    const w = +canvas.getAttribute('width'), h = +canvas.getAttribute('height');
    canvas.style.width = w + 'px'; canvas.style.height = h + 'px';
    const ctx = canvas.getContext('2d');
    const s = { canvas, ctx, w, h, k: 1 };
    s.resize = function (stageScale) {
      const dpr = Math.min(window.devicePixelRatio || 1, 2.5);
      s.k = Math.max(0.5, stageScale * dpr);
      canvas.width = Math.round(w * s.k); canvas.height = Math.round(h * s.k);
    };
    s.clear = function (color) {
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      if (color) { ctx.fillStyle = color; ctx.fillRect(0, 0, canvas.width, canvas.height); }
      else ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.setTransform(s.k, 0, 0, s.k, 0, 0);
    };
    return s;
  }

  const FONT = '"Pretendard Variable", Pretendard, "Inter", "Helvetica Neue", Arial, sans-serif';
  const SERIF = '"Source Serif 4 Variable", Georgia, serif';
  function font(px, weight = 500, italic = false, family = FONT) { return `${italic ? 'italic ' : ''}${weight} ${px}px ${family}`; }
  function circle(ctx, x, y, r, fill, stroke, lw) {
    ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2);
    if (fill) { ctx.fillStyle = fill; ctx.fill(); }
    if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw || 1; ctx.stroke(); }
  }
  // soft shaded ball with a white rim
  function ball(ctx, x, y, r, color, alpha = 1) {
    ctx.save(); ctx.globalAlpha *= alpha;
    const g = ctx.createRadialGradient(x - r * 0.35, y - r * 0.4, r * 0.1, x, y, r);
    g.addColorStop(0, mix(color, '#FFFFFF', 0.45)); g.addColorStop(0.55, color); g.addColorStop(1, mix(color, '#000000', 0.18));
    ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fillStyle = g; ctx.fill();
    ctx.lineWidth = Math.max(0.6, r * 0.08); ctx.strokeStyle = 'rgba(255,255,255,0.85)'; ctx.stroke();
    ctx.restore();
  }
  function roundRect(ctx, x, y, w, h, r, fill, stroke, lw, dash) {
    ctx.beginPath();
    ctx.moveTo(x + r, y); ctx.lineTo(x + w - r, y); ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r); ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h); ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r); ctx.quadraticCurveTo(x, y, x + r, y); ctx.closePath();
    if (fill) { ctx.fillStyle = fill; ctx.fill(); }
    if (stroke) { ctx.save(); ctx.strokeStyle = stroke; ctx.lineWidth = lw || 1; if (dash) ctx.setLineDash(dash); ctx.stroke(); ctx.restore(); }
  }
  function arrow(ctx, x1, y1, x2, y2, color, lw = 2, head = 10, dash) {
    const a = Math.atan2(y2 - y1, x2 - x1);
    ctx.save(); ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = lw; ctx.lineCap = 'round';
    if (dash) ctx.setLineDash(dash);
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2 - Math.cos(a) * head * 0.6, y2 - Math.sin(a) * head * 0.6); ctx.stroke();
    ctx.setLineDash([]);
    ctx.beginPath(); ctx.moveTo(x2, y2);
    ctx.lineTo(x2 - head * Math.cos(a - 0.42), y2 - head * Math.sin(a - 0.42));
    ctx.lineTo(x2 - head * Math.cos(a + 0.42), y2 - head * Math.sin(a + 0.42));
    ctx.closePath(); ctx.fill(); ctx.restore();
  }
  function text(ctx, str, x, y, o = {}) {
    ctx.save();
    ctx.font = o.font || font(o.size || 22, o.weight || 500, o.italic, o.family || FONT);
    ctx.fillStyle = o.color || C.ink; ctx.textAlign = o.align || 'left'; ctx.textBaseline = o.baseline || 'alphabetic';
    if (o.alpha !== undefined) ctx.globalAlpha *= o.alpha;
    ctx.fillText(str, x, y);
    ctx.restore();
  }
  // smooth pseudo-random signal in [-amp, amp]
  function wiggle(seed, t, amp = 1) {
    return amp * (Math.sin(2.1 * t + seed * 1.7) * 0.5 + Math.sin(3.7 * t + seed * 4.1) * 0.3 + Math.sin(6.3 * t + seed * 2.3) * 0.2);
  }

  window.U = { makeRng, C, rgba, mix, hexToRgb, E, surface, font, FONT, SERIF, circle, ball, roundRect, arrow, text, wiggle };
  window.ANIMS = window.ANIMS || {};
})();

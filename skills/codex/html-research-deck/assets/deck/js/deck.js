/* HTML deck engine (starter, dependency-free). Written 2026-10-30 after reverse-engineering the
   structure of yuanqidu.github.io/blog/a-new-era-of-molecular-simulation (same ideas, own code).

   Keys : → Space PgDn click = next build · ← PgUp Backspace = previous · Home / End
          S presenter window (notes, timer, next) · O overview · F fullscreen · B black screen
          Shift+P pause canvas animations · 12 ⏎ jump to slide 12 · ? help
   URL  : #/12/3 deep link (slide 12, build 3) · ?short skip data-optional slides · ?export no transitions
          ?print every slide stacked at 1920×1080 for PDF capture · ?embed (used by the presenter window)
   Slide : <section class="slide" data-title="..." data-section="..." [data-optional] [data-backup]>
   Build : any element with data-f="n" appears at build n; data-f-out="m" hides it again at build m;
           add class "fade" (no slide-up) or "dim-past" (dim instead of hide once passed).
   Anim  : <canvas class="abs" style="left:..;top:.." width=".." height=".." data-anim="name" data-opts='{...}'>
           window.ANIMS.name = (surface, opts) => ({ enter, leave, step(build), frame(dt, t), draw, resize, ff })
   Notes : <aside class="notes">...</aside> inside a slide, shown in the presenter window. */
(function () {
  'use strict';
  const W = 1920, H = 1080;
  const q = new URLSearchParams(location.search);
  const MODE = q.has('presenter') ? 'presenter' : q.has('print') ? 'print' : q.has('embed') ? 'embed' : 'main';
  const SHORT = q.has('short');
  const EXPORT = q.has('export') || MODE === 'print';
  const MATH = {
    delimiters: [{ left: '\\[', right: '\\]', display: true }, { left: '$', right: '$', display: false }],
    throwOnError: false, strict: false, trust: true,
    macros: { '\\dd': '\\mathrm{d}', '\\E': '\\mathbb{E}', '\\R': '\\mathbb{R}' }
  };

  let slides = [], order = [], pos = 0, frag = 0, scale = 1, paused = false, last = 0;
  const instances = new Map();
  let stage, progressEl, overviewEl, helpEl, blackEl, presenterWin = null, gotoBuf = '', gotoTimer = null;

  // ---------- slides ----------
  function nfragOf(root) {
    let m = 0;
    root.querySelectorAll('[data-f]').forEach(f => { m = Math.max(m, +f.dataset.f || 0, +(f.dataset.fOut || 0)); });
    return m;
  }
  function collect() {
    stage = document.querySelector('.stage');
    slides = Array.from(stage.querySelectorAll(':scope > section.slide'));
    slides.forEach(s => { s._nfrag = nfragOf(s); });
    order = slides.map((s, i) => i).filter(i => !(SHORT && slides[i].hasAttribute('data-optional')));
  }
  function number() {
    let main = 0, backup = 0;
    const total = order.filter(i => !slides[i].hasAttribute('data-backup')).length;
    order.forEach(i => {
      const s = slides[i];
      let n = s.querySelector(':scope > .slide-num');
      if (!n) { n = document.createElement('div'); n.className = 'slide-num'; s.appendChild(n); }
      if (s.hasAttribute('data-backup')) { backup++; n.textContent = 'B' + backup; }
      else { main++; n.textContent = s.classList.contains('title-slide') ? '' : `${main} / ${total}`; }
      s._label = n.textContent;
    });
  }
  function renderMath(root) { if (window.renderMathInElement) window.renderMathInElement(root, MATH); }
  function setFrags(s, f) {
    s.querySelectorAll('[data-f]').forEach(el => {
      const a = +el.dataset.f || 0, b = el.dataset.fOut !== undefined ? +el.dataset.fOut : Infinity;
      el.classList.toggle('f-vis', f >= a && f < b);
      el.classList.toggle('f-past', f >= b);
    });
    s.dataset.step = f;
  }

  // ---------- canvas animations ----------
  function ensure(c, k) {
    if (instances.has(c)) return instances.get(c);
    const factory = (window.ANIMS || {})[c.dataset.anim];
    if (!factory) { console.warn('missing anim', c.dataset.anim); return null; }
    const surf = window.U.surface(c); surf.resize(k);
    let opts = {};
    try { opts = c.dataset.opts ? JSON.parse(c.dataset.opts) : {}; } catch (e) { console.warn('bad data-opts', e); }
    const rec = { inst: factory(surf, opts) || {}, surf, t: 0, active: false };
    instances.set(c, rec);
    return rec;
  }
  const canvasesOf = s => Array.from(s.querySelectorAll('canvas[data-anim]'));
  function enterAnims(s) { canvasesOf(s).forEach(c => { const r = ensure(c, scale); if (!r) return; r.active = true; r.inst.enter && r.inst.enter(); r.inst.draw && r.inst.draw(); }); }
  function leaveAnims(s) { canvasesOf(s).forEach(c => { const r = instances.get(c); if (!r) return; r.active = false; r.inst.leave && r.inst.leave(); }); }
  function stepAnims(s) { canvasesOf(s).forEach(c => { const r = instances.get(c); if (r && r.inst.step) { r.inst.step(frag); r.inst.draw && r.inst.draw(); } }); }
  function ff(r, sec) { if (!r.inst.frame) return; const n = Math.round(sec * 60); for (let i = 0; i < n; i++) { r.t += 1 / 60; r.inst.frame(1 / 60, r.t); } r.inst.draw && r.inst.draw(); }
  function fastForward(sec) { canvasesOf(slides[order[pos]]).forEach(c => { const r = instances.get(c); if (r) ff(r, r.inst.ff !== undefined ? r.inst.ff : sec); }); }
  function loop(now) {
    let dt = Math.min(0.05, (now - last) / 1000); last = now;
    if (paused || document.hidden) dt = 0;
    if (dt > 0) instances.forEach(r => { if (r.active && r.inst.frame) { r.t += dt; r.inst.frame(dt, r.t); } });
    requestAnimationFrame(loop);
  }

  // ---------- layout & navigation ----------
  function layout() {
    const vw = window.innerWidth, vh = window.innerHeight;
    scale = Math.min(vw / W, vh / H);
    stage.style.transform = `translate(${(vw - W * scale) / 2}px, ${(vh - H * scale) / 2}px) scale(${scale})`;
    instances.forEach(r => { r.surf.resize(scale); r.inst.resize && r.inst.resize(); r.inst.draw && r.inst.draw(); });
  }
  function parseHash() {
    const m = location.hash.match(/^#\/(\d+)(?:\/(\d+))?/);
    if (!m) return [0, 0];
    return [Math.max(0, Math.min(order.length - 1, +m[1] - 1)), +(m[2] || 0)];
  }
  function go(p, f) {
    p = Math.max(0, Math.min(order.length - 1, p));
    const sNew = slides[order[p]];
    const changed = p !== pos || !sNew.classList.contains('active');
    if (changed) {
      const sOld = slides[order[pos]];
      if (sOld && sOld !== sNew) { sOld.classList.remove('active'); leaveAnims(sOld); }
      sNew.classList.add('active');
      pos = p;
    }
    frag = Math.max(0, Math.min(sNew._nfrag, f === undefined ? 0 : f));
    setFrags(sNew, frag);
    if (changed) enterAnims(sNew);
    stepAnims(sNew);
    if (EXPORT) fastForward(4); // static capture: show a representative frame instead of frame zero
    const mains = order.filter(i => !slides[i].hasAttribute('data-backup'));
    const mi = mains.indexOf(order[pos]);
    progressEl.style.width = (mi < 0 ? 100 : 100 * mi / Math.max(1, mains.length - 1)) + '%';
    const h = `#/${pos + 1}${frag ? '/' + frag : ''}`;
    if (MODE === 'main' && location.hash !== h) history.replaceState(null, '', h);
    broadcast();
  }
  function next() { const s = slides[order[pos]]; if (frag < s._nfrag) go(pos, frag + 1); else if (pos < order.length - 1) go(pos + 1, 0); }
  function prev() { if (frag > 0) go(pos, frag - 1); else if (pos > 0) go(pos - 1, slides[order[pos - 1]]._nfrag); }
  function toggleFullscreen() { if (!document.fullscreenElement) document.documentElement.requestFullscreen().catch(() => {}); else document.exitFullscreen(); }

  function onKey(e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const k = e.key;
    if (overviewEl.classList.contains('open')) { if (k === 'Escape' || k === 'o' || k === 'O') toggleOverview(false); return; }
    if (helpEl.classList.contains('open') && (k === 'Escape' || k === '?')) { helpEl.classList.remove('open'); return; }
    if (/^[0-9]$/.test(k)) { gotoBuf += k; clearTimeout(gotoTimer); gotoTimer = setTimeout(() => { gotoBuf = ''; }, 1500); return; }
    if (k === 'Enter' && gotoBuf) { go(+gotoBuf - 1, 0); gotoBuf = ''; e.preventDefault(); return; }
    switch (k) {
      case 'ArrowRight': case 'ArrowDown': case 'PageDown': case ' ': case 'n': e.preventDefault(); next(); break;
      case 'ArrowLeft': case 'ArrowUp': case 'PageUp': case 'Backspace': case 'p': e.preventDefault(); prev(); break;
      case 'Home': go(0, 0); break;
      case 'End': go(order.length - 1, 0); break;
      case 'f': case 'F': toggleFullscreen(); break;
      case 'o': case 'O': toggleOverview(true); break;
      case 's': case 'S': openPresenter(); break;
      case 'b': case 'B': case '.': blackEl.classList.toggle('on'); break;
      case 'P': paused = !paused; document.body.classList.toggle('paused', paused); break;
      case '?': case 'h': helpEl.classList.toggle('open'); break;
    }
  }

  // ---------- overlays ----------
  function buildOverview() {
    overviewEl = document.createElement('div'); overviewEl.className = 'overview';
    const grid = document.createElement('div'); grid.className = 'ov-grid'; overviewEl.appendChild(grid);
    order.forEach((i, p) => {
      const s = slides[i], card = document.createElement('button'); card.className = 'ov-card';
      if (s.hasAttribute('data-backup')) card.classList.add('ov-backup');
      if (s.hasAttribute('data-optional')) card.classList.add('ov-optional');
      card.innerHTML = `<span class="ov-num">${s._label || ''}</span><span class="ov-sec">${s.dataset.section || ''}</span><span class="ov-title">${s.dataset.title || ''}</span>`;
      card.addEventListener('click', e => { e.stopPropagation(); toggleOverview(false); go(p, 0); });
      grid.appendChild(card);
    });
    document.body.appendChild(overviewEl);
  }
  function toggleOverview(open) {
    overviewEl.classList.toggle('open', open);
    if (open) overviewEl.querySelectorAll('.ov-card').forEach((c, p) => c.classList.toggle('ov-cur', p === pos));
  }
  function buildHelp() {
    helpEl = document.createElement('div'); helpEl.className = 'help';
    helpEl.innerHTML = `<div class="help-card"><h3>Keyboard</h3><table>
      <tr><td>→ Space PgDn click</td><td>next build / slide</td></tr><tr><td>← PgUp Backspace</td><td>previous</td></tr>
      <tr><td>S</td><td>presenter window: notes, timer, next slide</td></tr><tr><td>O</td><td>overview (Esc closes)</td></tr>
      <tr><td>F</td><td>fullscreen</td></tr><tr><td>B or .</td><td>black screen</td></tr><tr><td>Shift+P</td><td>pause animations</td></tr>
      <tr><td>12 Enter</td><td>jump to slide 12</td></tr><tr><td>?short in URL</td><td>skip optional slides</td></tr>
      <tr><td>?print in URL</td><td>all slides stacked (PDF capture)</td></tr></table></div>`;
    helpEl.addEventListener('click', () => helpEl.classList.remove('open'));
    document.body.appendChild(helpEl);
  }
  function showHint() {
    if (document.body.dataset.hint === 'off') return;
    const h = document.createElement('div'); h.className = 'web-hint';
    h.textContent = '→ or click: next · ←: back · F: fullscreen · O: all slides · ?: keys';
    document.body.appendChild(h);
    const hide = () => h.classList.add('gone');
    document.addEventListener('keydown', hide, { once: true });
    document.addEventListener('click', hide, { once: true });
    setTimeout(hide, 9000);
  }

  // ---------- presenter link (main side) ----------
  function openPresenter() {
    if (presenterWin && !presenterWin.closed) { presenterWin.focus(); broadcast(); return; }
    const url = location.href.split('#')[0].split('?')[0] + '?presenter' + (SHORT ? '&short' : '');
    presenterWin = window.open(url, 'deck-presenter', 'width=1400,height=860');
    setTimeout(broadcast, 800); setTimeout(broadcast, 2000);
  }
  function broadcast() { if (presenterWin && !presenterWin.closed) presenterWin.postMessage({ type: 'deck-state', pos, frag, total: order.length }, '*'); }
  function onMessage(e) {
    const d = e.data || {};
    if (d.type === 'deck-nav') { if (d.dir === 'next') next(); else if (d.dir === 'prev') prev(); }
    if (d.type === 'deck-goto') go(d.pos, d.frag || 0);
    if (d.type === 'deck-hello' && e.source) { presenterWin = presenterWin || e.source; broadcast(); }
  }

  // ---------- presenter window (same file, ?presenter) ----------
  function buildPresenter() {
    const all = Array.from(document.querySelectorAll('.stage > section.slide'));
    const ord = all.map((s, i) => i).filter(i => !(SHORT && all[i].hasAttribute('data-optional')));
    const notes = ord.map(i => { const n = all[i].querySelector('aside.notes'); return n ? n.innerHTML : ''; });
    const titles = ord.map(i => all[i].dataset.title || '');
    const nfr = ord.map(i => nfragOf(all[i]));
    const base = location.href.split('?')[0], extra = SHORT ? '&short' : '';
    document.body.className = 'presenter';
    document.body.innerHTML = `<div class="pv">
        <div class="pv-main"><div class="pv-label">Current</div><div class="pv-frame"><iframe id="pvCur" src="${base}?embed${extra}"></iframe></div></div>
        <div class="pv-side">
          <div class="pv-label">Next</div><div class="pv-frame"><iframe id="pvNext" src="${base}?embed${extra}"></iframe></div>
          <div class="pv-timer"><span id="pvClock">00:00</span><button id="pvReset">reset</button><button id="pvPause">pause</button><span id="pvNum"></span></div>
          <div class="pv-title" id="pvTitle"></div>
          <div class="pv-notes" id="pvNotes"></div>
        </div></div>`;
    const cur = document.getElementById('pvCur'), nxt = document.getElementById('pvNext');
    let state = { pos: 0, frag: 0 }, t0 = Date.now(), pausedAt = null;
    function tick() {
      const el = (pausedAt || Date.now()) - t0, m = Math.floor(el / 60000), s = Math.floor(el / 1000) % 60;
      document.getElementById('pvClock').textContent = `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }
    setInterval(tick, 500);
    document.getElementById('pvReset').onclick = () => { t0 = Date.now(); if (pausedAt) pausedAt = t0; tick(); };
    document.getElementById('pvPause').onclick = e => {
      if (pausedAt) { t0 += Date.now() - pausedAt; pausedAt = null; e.target.textContent = 'pause'; }
      else { pausedAt = Date.now(); e.target.textContent = 'resume'; }
    };
    function render() {
      const p = state.pos;
      document.getElementById('pvNotes').innerHTML = notes[p] || '<em>(no notes)</em>';
      document.getElementById('pvTitle').textContent = titles[p] || '';
      document.getElementById('pvNum').textContent = `slide ${p + 1}/${ord.length} · build ${state.frag}/${nfr[p]}`;
      try { cur.contentWindow.postMessage({ type: 'deck-goto', pos: p, frag: state.frag }, '*'); } catch (e) {}
      let np = p, nf = state.frag + 1;
      if (nf > nfr[p]) { np = Math.min(ord.length - 1, p + 1); nf = np === p ? state.frag : 0; }
      try { nxt.contentWindow.postMessage({ type: 'deck-goto', pos: np, frag: nf }, '*'); } catch (e) {}
    }
    window.addEventListener('message', e => { const d = e.data || {}; if (d.type === 'deck-state') { state = d; render(); } });
    cur.addEventListener('load', render); nxt.addEventListener('load', render);
    document.addEventListener('keydown', e => {
      if (!window.opener) return;
      if (['ArrowRight', 'ArrowDown', 'PageDown', ' '].includes(e.key)) { e.preventDefault(); window.opener.postMessage({ type: 'deck-nav', dir: 'next' }, '*'); }
      if (['ArrowLeft', 'ArrowUp', 'PageUp', 'Backspace'].includes(e.key)) { e.preventDefault(); window.opener.postMessage({ type: 'deck-nav', dir: 'prev' }, '*'); }
    });
    if (window.opener) window.opener.postMessage({ type: 'deck-hello' }, '*');
  }

  // ---------- print mode: every slide becomes its own 1920×1080 page ----------
  function buildPrint() {
    collect(); number(); renderMath(stage);
    document.body.classList.add('print', 'export');
    const vp = document.querySelector('.viewport');
    order.forEach(i => {
      const s = slides[i], pg = document.createElement('div');
      pg.className = 'stage page';
      pg.appendChild(s); s.classList.add('active');
      setFrags(s, s._nfrag);
      const bar = document.createElement('div'); bar.className = 'progress';
      const mains = order.filter(j => !slides[j].hasAttribute('data-backup')), mi = mains.indexOf(i);
      bar.style.width = (mi < 0 ? 100 : 100 * mi / Math.max(1, mains.length - 1)) + '%';
      pg.appendChild(bar);
      vp.appendChild(pg);
    });
    stage.remove();
    document.querySelectorAll('canvas[data-anim]').forEach(c => {
      const r = ensure(c, 2); if (!r) return;
      r.inst.enter && r.inst.enter();
      r.inst.step && r.inst.step(nfragOf(c.closest('section')));
      ff(r, r.inst.ff !== undefined ? r.inst.ff : 4);
      r.inst.draw && r.inst.draw();
    });
    window.__deck = { count: () => order.length, mode: 'print' };
    document.body.dataset.ready = '1';
  }

  // ---------- boot ----------
  function init() {
    collect(); number();
    progressEl = document.createElement('div'); progressEl.className = 'progress'; stage.appendChild(progressEl);
    buildOverview(); buildHelp();
    blackEl = document.createElement('div'); blackEl.className = 'blackout'; document.body.appendChild(blackEl);
    if (MODE === 'embed') document.body.classList.add('embed');
    if (EXPORT) document.body.classList.add('export');
    renderMath(stage);
    window.addEventListener('resize', layout);
    layout();
    const [s0, f0] = parseHash();
    go(s0, f0);
    window.addEventListener('hashchange', () => { const [s, f] = parseHash(); if (s !== pos || f !== frag) go(s, f); });
    document.addEventListener('keydown', onKey);
    if (MODE === 'main' && !EXPORT) {
      document.querySelector('.viewport').addEventListener('click', e => {
        if (e.target.closest('a, button, input, .overview, .help, [data-noclick]')) return;
        if (e.clientX < window.innerWidth * 0.18) prev(); else next();
      });
      showHint();
    }
    window.addEventListener('message', onMessage);
    document.addEventListener('visibilitychange', () => { last = performance.now(); });
    last = performance.now();
    if (!EXPORT) requestAnimationFrame(loop);
    window.__deck = {
      count: () => order.length, pos: () => pos, frag: () => frag, go: (p, f) => go(p, f),
      nfrag: p => slides[order[p]]._nfrag, titleOf: p => slides[order[p]].dataset.title || '', fastForward, next, prev, mode: MODE
    };
    document.body.dataset.ready = '1';
  }

  document.addEventListener('DOMContentLoaded', MODE === 'presenter' ? buildPresenter : MODE === 'print' ? buildPrint : init);
})();

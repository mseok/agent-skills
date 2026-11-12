/* Presenter aids on top of the deck engine (loads after js/deck.js; user decision 2026-11-12).
   L  laser pointer (a red dot follows the mouse, the cursor is hidden)
   Z  zoom 2x at the cursor, Z or Esc again to leave
   T  show or hide the section tracker
   None of this runs in ?print, ?presenter or ?embed, so PNG and PDF exports are unchanged. */
(function () {
  'use strict';
  const q = new URLSearchParams(location.search);
  if (q.has('print') || q.has('presenter') || q.has('embed')) return;
  let x = window.innerWidth / 2, y = window.innerHeight / 2, zoomed = false, dot = null, vp = null;
  function place() { if (dot) dot.style.transform = `translate(${x}px, ${y}px)`; }
  function zoom(on) {
    zoomed = on;
    vp.classList.add('zoomed');
    vp.style.transformOrigin = `${x}px ${y}px`;
    vp.style.transform = on ? 'scale(2)' : '';
  }
  document.addEventListener('DOMContentLoaded', () => {
    vp = document.querySelector('.viewport');
    dot = document.createElement('div'); dot.className = 'laser-dot'; document.body.appendChild(dot); place();
  });
  document.addEventListener('mousemove', e => { x = e.clientX; y = e.clientY; place(); });
  document.addEventListener('keydown', e => {
    if (e.metaKey || e.ctrlKey || e.altKey || !vp) return;
    if (e.key === 'l' || e.key === 'L') document.body.classList.toggle('laser');
    else if (e.key === 'z' || e.key === 'Z') zoom(!zoomed);
    else if (e.key === 't' || e.key === 'T') document.body.classList.toggle('no-tracker');
    else if (e.key === 'Escape' && zoomed) zoom(false);
  });
})();

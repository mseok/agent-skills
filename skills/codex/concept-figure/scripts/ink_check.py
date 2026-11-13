#!/usr/bin/env python3
"""Check from the pixels that symbols sit in the middle of their circles and chips (.op, .var, .chip).

usage: ink_check.py figure.html figure.png [crop_dir]     (needs Pillow; figure.png is the 600 dpi render of figure.html)

Prints, for every symbol, the offset of its ink bounding box from the circle's centre in pt, and exits 1 when any offset
exceeds 0.2 pt. With crop_dir it also saves enlarged crops of the symbols and of the curve specimens of the kit sheet.
Run it on assets/examples/kit-sheet.html after changing the kit: the layout code centres symbols by calculation, and this
is the independent measurement of what was actually painted.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import render  # noqa: E402  (sibling script, imported after the path is set)
from PIL import Image  # noqa: E402

html, png = sys.argv[1:3]
out = sys.argv[3] if len(sys.argv) > 3 else None

c = render.Chrome(render.find_chrome())
try:
    t = c.send("Target.createTarget", url="about:blank")["targetId"]
    c.session = c.send("Target.attachToTarget", targetId=t, flatten=True)["sessionId"]
    c.send("Page.enable")
    c.send("Emulation.setDeviceMetricsOverride", width=1400, height=1000, deviceScaleFactor=1, mobile=False)
    c.send("Page.navigate", url=pathlib.Path(html).resolve().as_uri() + "?render=1")
    c.wait(lambda m: m.get("method") == "Page.loadEventFired")
    render.evaluate(c, "window.figReady.then(() => 1)")
    d = json.loads(render.evaluate(c, """(() => { const Z = parseFloat(document.documentElement.style.zoom) || 1; const R = (e) => { const r = e.getBoundingClientRect(); return {left: r.left / Z, top: r.top / Z, right: r.right / Z, width: r.width / Z, height: r.height / Z}; };
      return JSON.stringify({
      ops: [...document.querySelectorAll('.op, .var, .chip')].filter(e => e.textContent.trim() && !e.closest('.legend')).map(e => { const r = R(e); const k = e.querySelector('.katex-html'); return [e.className, (k ? k.innerText : e.textContent).trim().slice(0, 3), r.left, r.top, r.width, r.height]; }),
      curve: (() => { const a = document.getElementById('e1'), b = document.getElementById('f1'); if (!a || !b) return null; const p = R(a), q = R(b); return [p.left - 14, p.top - 46, q.right + 14 - (p.left - 14), 92]; })()
    }); })()"""))
finally:
    c.close()
S = 600 / 96
im = Image.open(png).convert("RGB")
ops = d["ops"]
plain = [o for o in ops if "chip" not in o[0]]
if plain and out:
    x0 = min(o[2] for o in plain) - 6; x1 = max(o[2] + o[4] for o in plain) + 6; y0 = min(o[3] for o in plain) - 6; y1 = max(o[3] + o[5] for o in plain) + 6
    im.crop((int(x0 * S), int(y0 * S), int(x1 * S), int(y1 * S))).save(pathlib.Path(out) / "crop-ops.png")
if d["curve"] and out:
    ex, ey, ew, eh = d["curve"]
    im.crop((int(ex * S), int(ey * S), int((ex + ew) * S), int((ey + eh) * S))).save(pathlib.Path(out) / "crop-curves.png")
print("element      text   dx(pt)  dy(pt)   ink bounding-box centre minus circle centre; + = right / down")
worst = 0.0
for cls, text, l, t, w, h in ops:
    box = im.crop((round(l * S), round(t * S), round((l + w) * S), round((t + h) * S))); W, H = box.size; px = box.load()
    solid = "chip" in cls
    rr = (min(W, H) / 2) * 0.8
    xs, ys = [], []
    for y in range(H):
        for x in range(W):
            if (x + 0.5 - W / 2) ** 2 + (y + 0.5 - H / 2) ** 2 > rr * rr:
                continue
            v = sum(px[x, y]) / 3
            if (v > 215) if solid else (v < 150):
                xs.append(x); ys.append(y)
    if xs:
        dx = ((min(xs) + max(xs) + 1) / 2 - W / 2) / S * 0.75
        dy = ((min(ys) + max(ys) + 1) / 2 - H / 2) / S * 0.75
        worst = max(worst, abs(dx), abs(dy))
        print(f"{cls.split()[0]:12s} {text:5s} {dx:+.2f}   {dy:+.2f}")
print(f"largest offset {worst:.2f} pt")
sys.exit(1 if worst > 0.2 else 0)

#!/usr/bin/env python3
"""Render a concept-figure HTML file with headless Chrome: layout checks, vector PDF, PNG proof, PNG preview.

usage: render.py figure.html [--out DIR] [--dpi 600] [--preview-dpi 220] [--check-only]

Writes <stem>.pdf, <stem>.png, <stem>.preview.png, <stem>.report.json, zoomed <stem>.tiles/ and an unticked
<stem>.inspection.md (the inspection gate, references/inspection.md) beside the HTML file (or in DIR)
and prints the report. Exit status: 0 clean or warnings only, 1 layout errors, 2 Chrome or kit failure.
Chrome comes from $CHROME, the macOS application path, or google-chrome / chromium on PATH.
pdfinfo and pdffonts (Poppler) add the page size and the embedded fonts to the report when installed.
"""
import argparse
import base64
import fcntl
import json
import math
import os
import pathlib
import select
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib

MAC_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def find_chrome():
    names = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]
    for cand in [os.environ.get("CHROME"), MAC_CHROME, *map(shutil.which, names)]:
        if cand and os.access(cand, os.X_OK):
            return cand
    sys.exit("Chrome not found: set CHROME=/path/to/chrome")


class Chrome:
    """Headless Chrome driven over --remote-debugging-pipe (commands on fd 3, replies on fd 4, NUL-separated JSON)."""

    def __init__(self, binary):
        self.profile = tempfile.mkdtemp(prefix="concept-figure-chrome.")
        cmd_r, self.w = os.pipe()
        self.r, out_w = os.pipe()

        def wire():
            a = fcntl.fcntl(cmd_r, fcntl.F_DUPFD, 10)
            b = fcntl.fcntl(out_w, fcntl.F_DUPFD, 10)
            os.dup2(a, 3)
            os.dup2(b, 4)

        self.proc = subprocess.Popen(
            [binary, "--headless=new", "--remote-debugging-pipe", f"--user-data-dir={self.profile}", "--no-first-run",
             "--no-default-browser-check", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files", "about:blank"],
            preexec_fn=wire, pass_fds=(3, 4), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.close(cmd_r)
        os.close(out_w)
        self.buf, self.backlog, self.n, self.session = b"", [], 0, None

    def read(self, timeout):
        while b"\0" not in self.buf:
            if not select.select([self.r], [], [], timeout)[0]:
                raise TimeoutError(f"no reply from Chrome within {timeout} s")
            chunk = os.read(self.r, 1 << 20)
            if not chunk:
                raise ConnectionError("Chrome closed the debugging pipe")
            self.buf += chunk
        raw, self.buf = self.buf.split(b"\0", 1)
        return json.loads(raw)

    def wait(self, match, timeout=60):
        for i, msg in enumerate(self.backlog):
            if match(msg):
                return self.backlog.pop(i)
        while True:
            msg = self.read(timeout)
            if match(msg):
                return msg
            self.backlog.append(msg)

    def send(self, method, **params):
        self.n += 1
        msg = {"id": self.n, "method": method, "params": params}
        if self.session:
            msg["sessionId"] = self.session
        os.write(self.w, json.dumps(msg).encode() + b"\0")
        n = self.n
        reply = self.wait(lambda m: m.get("id") == n)
        if "error" in reply:
            raise RuntimeError(f"{method}: {reply['error'].get('message')}")
        return reply["result"]

    def close(self):
        self.proc.terminate()
        self.proc.wait(timeout=10)
        shutil.rmtree(self.profile, ignore_errors=True)


def with_dpi(png, dpi):
    """Insert a pHYs chunk after IHDR so viewers and LaTeX read the physical size."""
    ppm = round(dpi / 0.0254)
    chunk = b"pHYs" + struct.pack(">IIB", ppm, ppm, 1)
    return png[:33] + struct.pack(">I", 9) + chunk + struct.pack(">I", zlib.crc32(chunk)) + png[33:]


def evaluate(chrome, expression):
    res = chrome.send("Runtime.evaluate", expression=expression, awaitPromise=True, returnByValue=True)
    if "exceptionDetails" in res:
        raise RuntimeError(res["exceptionDetails"].get("exception", {}).get("description") or res["exceptionDetails"]["text"])
    return res["result"].get("value")


def screenshot(chrome, w, h, zoom, dpi, clip=None):
    """The page is laid out `zoom` times larger than print size (see figure.js), so the device scale is divided by it.
    `clip` is (x, y, width, height) in CSS px of the print-size figure; None takes the whole figure."""
    chrome.send("Emulation.setDeviceMetricsOverride", width=math.ceil(w * zoom), height=math.ceil(h * zoom), deviceScaleFactor=dpi / 96 / zoom, mobile=False)
    evaluate(chrome, "window.figRelayout() && new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
    x, y, cw, ch = clip or (0, 0, w, h)
    shot = chrome.send("Page.captureScreenshot", format="png", captureBeyondViewport=True,
                       clip={"x": x * zoom, "y": y * zoom, "width": cw * zoom, "height": ch * zoom, "scale": 1})
    return with_dpi(base64.b64decode(shot["data"]), dpi)


TILE_DPI = 440
CHECKLIST = [
    ("text", "Every piece of text is clear of lines, box edges, pictures, panel rules and other text; nothing is clipped or cut by a frame."),
    ("arrows", "Every arrow starts on its source and ends on its target; each leg is clearly longer than its head; no head sits at a bend; none runs through an unrelated object or label."),
    ("levels", "Boxes at one level share text size, height and style; arrows of one kind share weight and head."),
    ("alignment", "What should share an axis or a baseline does; equal gaps look equal; symbols are centred in their circles."),
    ("colour", "Each colour has a meaning the figure states; the contribution is the most salient thing; nothing faded reads as empty."),
    ("white space", "No empty band or corner, no object small in a large frame, no arrow longer than its label needs."),
    ("content", "The drawing does not misstate the method: inputs, order, what flows on each arrow, what is trained or frozen."),
    ("whole figure", "At print size (the preview at 100 %) the reading order is obvious and the smallest text is readable."),
]


def tiles(chrome, w, h, zoom, out, stem):
    """Zoomed crops that together cover the figure, for the inspection gate: two columns with an overlap, rows as needed."""
    folder = out / f"{stem}.tiles"
    folder.mkdir(exist_ok=True)
    for old in folder.glob("*.png"):
        old.unlink()
    tw = w * 0.56
    th = min(h, tw * 0.62)
    rows = max(1, math.ceil((h - th * 0.1) / (th * 0.9)))
    names = []
    for r in range(rows):
        y = 0 if rows == 1 else (h - th) * r / (rows - 1)
        for c, x in enumerate((0, w - tw)):
            name = f"r{r + 1}c{c + 1}.png"
            (folder / name).write_bytes(screenshot(chrome, w, h, zoom, TILE_DPI, (x, y, tw, th)))
            names.append(name)
    return folder, names


def inspection_template(path, stem, folder, names):
    """A fresh render invalidates the last inspection: the receipt starts unticked again."""
    lines = [f"# Inspection of {stem}", "",
             "Tick a line only after looking; write what was found and fixed. Read references/inspection.md for the procedure.", "",
             "Inspector: ", "", "## Views", "", f"- [ ] {stem}.preview.png at 100 %"]
    lines += [f"- [ ] {folder.name}/{n}" for n in names]
    lines += ["", "## Checklist", ""] + [f"- [ ] {key}: {text}" for key, text in CHECKLIST]
    lines += ["", "## Defects found in this version", "", "- "]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def poppler(pdf):
    info = {}
    if shutil.which("pdfinfo"):
        for line in subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout.splitlines():
            if line.startswith("Page size:"):
                parts = line.split()
                info["page_pt"] = [float(parts[2]), float(parts[4])]
            if line.startswith("Pages:"):
                info["pages"] = int(line.split()[1])
    if shutil.which("pdffonts"):
        rows = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
        info["fonts"] = [{"name": r.split()[0], "embedded": r.split()[-5] == "yes", "type3": "Type 3" in r} for r in rows if r.strip()]
    return info


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html")
    ap.add_argument("--out")
    ap.add_argument("--dpi", type=float, default=600)
    ap.add_argument("--preview-dpi", type=float, default=220)
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()
    src = pathlib.Path(args.html).resolve()
    out = pathlib.Path(args.out).resolve() if args.out else src.parent
    out.mkdir(parents=True, exist_ok=True)
    chrome = Chrome(find_chrome())
    try:
        target = chrome.send("Target.createTarget", url="about:blank")["targetId"]
        chrome.session = chrome.send("Target.attachToTarget", targetId=target, flatten=True)["sessionId"]
        chrome.send("Page.enable")
        chrome.send("Emulation.setDeviceMetricsOverride", width=8000, height=4000, deviceScaleFactor=1, mobile=False)
        chrome.send("Page.navigate", url=src.as_uri() + "?render=1")
        chrome.wait(lambda m: m.get("method") == "Page.loadEventFired")
        try:
            report = json.loads(evaluate(chrome, "window.figReady.then(r => JSON.stringify(r))"))
        except (RuntimeError, TypeError) as err:
            print(f"kit did not run in {src.name}: {err}", file=sys.stderr)
            return 2
        if not args.check_only and "width_px" in report:
            w, h, zoom = report["width_px"], report["height_px"], report.get("zoom", 1)
            (out / f"{src.stem}.preview.png").write_bytes(screenshot(chrome, w, h, zoom, args.preview_dpi))
            (out / f"{src.stem}.png").write_bytes(screenshot(chrome, w, h, zoom, args.dpi))
            pdf = chrome.send("Page.printToPDF", printBackground=True, preferCSSPageSize=False, paperWidth=w / 96, paperHeight=(h + 0.5) / 96,
                              marginTop=0, marginBottom=0, marginLeft=0, marginRight=0, pageRanges="1", scale=1 / zoom)
            pdf_path = out / f"{src.stem}.pdf"
            pdf_path.write_bytes(base64.b64decode(pdf["data"]))
            report["pdf"] = poppler(pdf_path)
            report["png"] = {"dpi": args.dpi, "width_px": round(w * args.dpi / 96), "height_px": round(h * args.dpi / 96)}
            folder, names = tiles(chrome, w, h, zoom, out, src.stem)
            report["tiles"] = [f"{folder.name}/{n}" for n in names]
            inspection_template(out / f"{src.stem}.inspection.md", src.stem, folder, names)
    finally:
        chrome.close()
    (out / f"{src.stem}.report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    if "width_mm" in report:
        print(f"{src.name}: {report['width_mm']} x {report['height_mm']} mm, text {report['min_text_pt']}-pt minimum "
              f"({report['median_text_pt']} median), {report['words']} words, {report['nodes']} boxes, {report['wires']} wires, "
              f"colour roles: {', '.join(report['colour_roles']) or 'none'}")
    fonts = report.get("pdf", {}).get("fonts")
    if fonts is not None:
        print("PDF fonts: " + ", ".join(f["name"] + ("" if f["embedded"] else " (NOT embedded)") + (" (Type 3)" if f["type3"] else "") for f in fonts))
    for issue in report["issues"]:
        print(f"  {issue['level'].upper():5s} {issue['code']}: {issue['msg']}")
    print(f"{report['errors']} errors, {report['warnings']} warnings")
    if report.get("tiles"):
        print(f"inspection gate: view {src.stem}.preview.png and the {len(report['tiles'])} tiles in {src.stem}.tiles/, then tick {src.stem}.inspection.md")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())

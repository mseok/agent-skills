#!/usr/bin/env python3
"""Deterministic physical-geometry, live-text typography, font-embedding, and spec-consistency audit for nature-figure exports.

Standard library + optional Poppler (pdfinfo, pdffonts) only — zero PyMuPDF / CairoSVG / lxml dependency.
Usage:
  python3 check_figure_export.py --svg figure.svg [--pdf figure.pdf] [--png figure.png] [--spec figure-spec.json]
                                 [--min-pt 6.0] [--require-groups] [--json report.json]
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import shutil
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET

SVG_NS = "{http://www.w3.org/2000/svg}"
UNIT_TO_PT = {"pt": 1.0, "px": 72.0 / 96.0, "in": 72.0, "mm": 72.0 / 25.4, "cm": 72.0 / 2.54, "": 1.0}


def parse_length_pt(raw: str | None) -> tuple[float | None, str]:
    if not raw:
        return None, ""
    m = re.match(r"^\s*([+-]?(?:\d+\.?\d*|\.\d+))\s*([a-zA-Z%]*)\s*$", raw)
    if not m or m.group(2) not in UNIT_TO_PT:
        return None, (m.group(2) if m else raw)
    return float(m.group(1)) * UNIT_TO_PT[m.group(2)], m.group(2)


def transform_scale(attr: str | None) -> float:
    """Uniform/geometric scale factor contributed by an SVG transform attribute."""
    if not attr:
        return 1.0
    scale = 1.0
    for fn, args_s in re.findall(r"([a-zA-Z]+)\(([^)]*)\)", attr):
        nums = [float(x) for x in re.split(r"[\s,]+", args_s.strip()) if x]
        if fn == "scale" and nums:
            sx = abs(nums[0])
            sy = abs(nums[1]) if len(nums) > 1 else sx
            scale *= math.sqrt(sx * sy)
        elif fn == "matrix" and len(nums) >= 4:
            a, b, c, d = nums[:4]
            det = abs(a * d - b * c)
            if det > 0:
                scale *= math.sqrt(det)
    return scale


def style_map(el: ET.Element) -> dict[str, str]:
    out = {}
    raw = el.attrib.get("style", "")
    for part in raw.split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip().lower()] = v.strip()
    return out


def parse_font_size_user(val: str | None) -> float | None:
    if not val:
        return None
    m = re.match(r"^\s*([+-]?(?:\d+\.?\d*|\.\d+))\s*(pt|px|mm|cm|in|)?\s*$", val)
    if not m:
        return None
    num = float(m.group(1))
    unit = m.group(2) or ""
    # Inside SVG user coordinates (e.g. Matplotlib writes viewBox in pt and font-size: 7.5px meaning 7.5 user units):
    if unit in ("", "px", "pt"):
        return num
    return num * UNIT_TO_PT[unit]


def check_svg(svg_path: pathlib.Path, min_pt: float, require_groups: bool) -> dict:
    findings: list[dict] = []
    root = ET.parse(svg_path).getroot()
    w_pt, w_unit = parse_length_pt(root.attrib.get("width"))
    h_pt, h_unit = parse_length_pt(root.attrib.get("height"))
    vb_raw = root.attrib.get("viewBox", "")
    vb = [float(x) for x in re.split(r"[\s,]+", vb_raw.strip()) if x] if vb_raw else []
    if w_pt is None or h_pt is None or w_unit == "" or h_unit == "":
        findings.append({"level": "error", "code": "svg-physical-size", "msg": f"SVG width/height must carry explicit physical units (got width={root.attrib.get('width')!r}, height={root.attrib.get('height')!r})"})
    user_to_pt = (w_pt / vb[2]) if (w_pt and len(vb) == 4 and vb[2] > 0) else 1.0

    # Traverse tree tracking cumulative scale and inherited font-size / family
    text_nodes = 0
    tspan_nodes = 0
    use_glyphs = 0
    measured_pts: list[tuple[float, str, str]] = []
    families: set[str] = set()
    named_groups: list[str] = []

    def walk(el: ET.Element, cum_scale: float, inh_fs: float | None, inh_fam: str | None) -> None:
        nonlocal text_nodes, tspan_nodes, use_glyphs
        s = cum_scale * transform_scale(el.attrib.get("transform"))
        st = style_map(el)
        fs = parse_font_size_user(st.get("font-size") or el.attrib.get("font-size")) or inh_fs
        fam = (st.get("font-family") or el.attrib.get("font-family") or inh_fam or "").strip("'\" ")
        if el.tag == f"{SVG_NS}g":
            gid = el.attrib.get("id", "")
            if gid.startswith(("panel_", "label_", "legend_")):
                named_groups.append(gid)
        elif el.tag == f"{SVG_NS}use":
            href = el.attrib.get("{http://www.w3.org/1999/xlink}href") or el.attrib.get("href") or ""
            if "DejaVu" in href or "Arial" in href or href.startswith("#glyph"):
                use_glyphs += 1
        elif el.tag in (f"{SVG_NS}text", f"{SVG_NS}tspan"):
            if el.tag == f"{SVG_NS}text":
                text_nodes += 1
            else:
                tspan_nodes += 1
            txt = (el.text or "").strip()
            if txt and fs is not None:
                pt = round(fs * s * user_to_pt, 3)
                measured_pts.append((pt, el.tag.replace(SVG_NS, ""), txt[:32]))
                if fam:
                    families.add(fam)
        for ch in el:
            walk(ch, s, fs, fam)

    walk(root, 1.0, None, None)

    if text_nodes == 0:
        findings.append({"level": "error", "code": "svg-outlined-text", "msg": f"0 live <text> elements found ({use_glyphs} glyph <use> refs); set svg.fonttype='none'"})
    elif use_glyphs > 0:
        findings.append({"level": "error", "code": "svg-outlined-glyphs", "msg": f"{use_glyphs} outlined glyph <use> refs found alongside <text>"})

    below = [(pt, tag, txt) for pt, tag, txt in measured_pts if pt < min_pt - 0.02]
    if below:
        worst = min(below, key=lambda r: r[0])
        samples = ", ".join(f"<{tag}> {txt!r} ({pt:.2f} pt)" for pt, tag, txt in below[:5])
        findings.append({"level": "error", "code": "min-text-pt", "msg": f"{len(below)} text/tspan run(s) below {min_pt:.1f} pt floor (min {worst[0]:.2f} pt): {samples}"})

    non_arial = [f for f in sorted(families) if f and "arial" not in f.lower()]
    if non_arial:
        findings.append({"level": "error", "code": "svg-font-family", "msg": f"Non-Arial SVG font-family detected: {non_arial}"})

    if require_groups and not any(g.startswith("panel_") for g in named_groups):
        findings.append({"level": "warn", "code": "svg-named-groups", "msg": "No named panel_* groups found in SVG (Figma handoff expects named panel/label groups)"})

    return {
        "width_pt": round(w_pt, 3) if w_pt else None,
        "height_pt": round(h_pt, 3) if h_pt else None,
        "width_mm": round(w_pt * 25.4 / 72.0, 2) if w_pt else None,
        "height_mm": round(h_pt * 25.4 / 72.0, 2) if h_pt else None,
        "text_elements": text_nodes,
        "tspan_elements": tspan_nodes,
        "min_pt": min((r[0] for r in measured_pts), default=None),
        "max_pt": max((r[0] for r in measured_pts), default=None),
        "distinct_pts": sorted({round(r[0], 2) for r in measured_pts}),
        "families": sorted(families),
        "named_groups": named_groups,
        "findings": findings,
    }


def check_pdf(pdf_path: pathlib.Path) -> dict:
    findings: list[dict] = []
    info: dict = {}
    if shutil.which("pdfinfo"):
        out = subprocess.run(
            ["pdfinfo", str(pdf_path)], capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
        ).stdout
        for line in out.splitlines():
            if line.startswith("Page size:"):
                parts = line.split()
                info["page_pt"] = [float(parts[2]), float(parts[4])]
                info["page_mm"] = [round(float(parts[2]) * 25.4 / 72.0, 2), round(float(parts[4]) * 25.4 / 72.0, 2)]
    if shutil.which("pdffonts"):
        rows = subprocess.run(
            ["pdffonts", str(pdf_path)], capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
        ).stdout.splitlines()[2:]
        fonts = []
        for r in rows:
            if not r.strip():
                continue
            toks = r.split()
            emb = toks[-5] == "yes"
            t3 = "Type 3" in r
            name = toks[0]
            fonts.append({"name": name, "embedded": emb, "type3": t3})
            if not emb:
                findings.append({"level": "error", "code": "pdf-font-unembedded", "msg": f"PDF font {name} is not embedded"})
            if t3:
                findings.append({"level": "error", "code": "pdf-type3-font", "msg": f"PDF font {name} is Type 3 (set pdf.fonttype=42)"})
            if "DejaVu" in name or "Liberation" in name:
                findings.append({"level": "error", "code": "pdf-font-fallback", "msg": f"Silent fallback font {name} embedded in PDF instead of Arial"})
        info["fonts"] = fonts
    info["findings"] = findings
    return info


def check_png(png_path: pathlib.Path, width_mm: float | None, height_mm: float | None) -> dict:
    findings: list[dict] = []
    data = png_path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return {"findings": [{"level": "error", "code": "png-invalid", "msg": "Not a valid PNG file"}]}
    w_px, h_px = struct.unpack(">II", data[16:24])
    phys_dpi = None
    pos = 8
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        if ctype == b"pHYs" and length == 9:
            px_u, py_u, unit = struct.unpack(">IIB", data[pos + 8:pos + 17])
            if unit == 1:
                phys_dpi = [round(px_u * 0.0254, 2), round(py_u * 0.0254, 2)]
            break
        if ctype == b"IEND":
            break
        pos += 12 + length
    eff_dpi = None
    if width_mm and height_mm:
        eff_dpi = [round(w_px / (width_mm / 25.4), 2), round(h_px / (height_mm / 25.4), 2)]
        if min(eff_dpi) <= 300.0:
            findings.append({"level": "error", "code": "png-low-dpi", "msg": f"Effective PNG DPI {eff_dpi} is not strictly above 300 dpi"})
    return {"pixels": [w_px, h_px], "phys_dpi": phys_dpi, "effective_dpi": eff_dpi, "findings": findings}


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--svg", type=pathlib.Path, required=True)
    ap.add_argument("--pdf", type=pathlib.Path)
    ap.add_argument("--png", type=pathlib.Path)
    ap.add_argument("--spec", type=pathlib.Path)
    ap.add_argument("--min-pt", type=float, default=6.0)
    ap.add_argument("--require-groups", action="store_true")
    ap.add_argument("--json", type=pathlib.Path)
    args = ap.parse_args(argv)

    svg_res = check_svg(args.svg, args.min_pt, args.require_groups)
    all_findings = list(svg_res["findings"])
    report: dict = {"svg": svg_res}

    if args.pdf and args.pdf.exists():
        pdf_res = check_pdf(args.pdf)
        report["pdf"] = pdf_res
        all_findings.extend(pdf_res["findings"])

    if args.png and args.png.exists():
        png_res = check_png(args.png, svg_res.get("width_mm"), svg_res.get("height_mm"))
        report["png"] = png_res
        all_findings.extend(png_res["findings"])

    if args.spec and args.spec.exists():
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        # Cross-check pixel dimensions if declared in spec
        spec_px = None
        for key in ("png_pixels", "pixels", "proof_pixels"):
            if isinstance(spec.get(key), list):
                spec_px = spec[key]
        if spec_px is None and isinstance(spec.get("exports"), dict):
            png_exp = spec["exports"].get("png") or spec["exports"].get("figure.png")
            if isinstance(png_exp, dict):
                spec_px = png_exp.get("pixels") or (
                    [png_exp["width_px"], png_exp["height_px"]] if "width_px" in png_exp and "height_px" in png_exp else None
                )
        if spec_px is None and isinstance(spec.get("qa_checks"), dict):
            qpx = spec["qa_checks"].get("png_dimensions_px")
            if isinstance(qpx, list):
                spec_px = qpx
        if spec_px and "png" in report and spec_px != report["png"].get("pixels"):
            all_findings.append({
                "level": "error",
                "code": "spec-png-mismatch",
                "msg": f"figure-spec.json lists PNG pixels {spec_px}, but rendered PNG is {report['png'].get('pixels')}",
            })

    errors = [f for f in all_findings if f["level"] == "error"]
    warns = [f for f in all_findings if f["level"] == "warn"]
    report["summary"] = {"errors": len(errors), "warnings": len(warns), "findings": all_findings}
    if args.json:
        args.json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{args.svg}: {svg_res['width_mm']} x {svg_res['height_mm']} mm | min_pt={svg_res['min_pt']} | distinct={svg_res['distinct_pts']} | errors={len(errors)} warnings={len(warns)}")
    for f in all_findings:
        print(f"  {f['level'].upper():5s} {f['code']}: {f['msg']}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

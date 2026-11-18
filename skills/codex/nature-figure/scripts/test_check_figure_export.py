#!/usr/bin/env python3
"""Unit and smoke tests for check_figure_export.py (stdlib only, LC_ALL=C safe)."""
from __future__ import annotations

import json
import pathlib
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_figure_export as cfe


def _make_png(width: int, height: int) -> bytes:
    def chunk(tag: bytes, payload: bytes) -> bytes:
        crc = zlib.crc32(tag + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    idat = zlib.compress(b"\x00\x00\x00\x00")
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


class CheckFigureExportTests(unittest.TestCase):
    def test_valid_svg_png_and_spec_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = pathlib.Path(tmp)
            svg = d / "figure.svg"
            png = d / "figure.png"
            spec = d / "figure-spec.json"
            svg.write_text(
                '<?xml version="1.0" encoding="utf-8"?>\n'
                '<svg xmlns="http://www.w3.org/2000/svg" width="89mm" height="60mm" viewBox="0 0 252.283 170.079">'
                '<g id="panel_a"><text x="10" y="20" style="font-family: Arial; font-size: 7pt">a \u22121.5 \u03bcM</text></g>'
                "</svg>\n",
                encoding="utf-8",
            )
            png.write_bytes(_make_png(2102, 1417))
            spec.write_text(json.dumps({"png_pixels": [2102, 1417]}), encoding="utf-8")
            rc = cfe.main(["--svg", str(svg), "--png", str(png), "--spec", str(spec), "--require-groups"])
            self.assertEqual(rc, 0)

    def test_detects_small_tspan_non_arial_missing_groups_and_spec_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = pathlib.Path(tmp)
            svg = d / "bad.svg"
            png = d / "bad.png"
            spec = d / "figure-spec.json"
            out = d / "report.json"
            svg.write_text(
                '<?xml version="1.0" encoding="utf-8"?>\n'
                '<svg xmlns="http://www.w3.org/2000/svg" width="89mm" height="60mm" viewBox="0 0 252.283 170.079">'
                '<text x="10" y="20" style="font-family: DejaVu Sans; font-size: 7.5px">log'
                '<tspan style="font-size: 5.25px">\u221210</tspan></text>'
                "</svg>\n",
                encoding="utf-8",
            )
            png.write_bytes(_make_png(700, 470))
            spec.write_text(json.dumps({"png_pixels": [2102, 1417]}), encoding="utf-8")
            rc = cfe.main(["--svg", str(svg), "--png", str(png), "--spec", str(spec), "--require-groups", "--json", str(out)])
            self.assertEqual(rc, 1)
            codes = {f["code"] for f in json.loads(out.read_text(encoding="utf-8"))["summary"]["findings"]}
            self.assertEqual(codes, {"min-text-pt", "svg-font-family", "svg-named-groups", "png-low-dpi", "spec-png-mismatch"})


if __name__ == "__main__":
    unittest.main()

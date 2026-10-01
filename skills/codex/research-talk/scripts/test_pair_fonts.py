#!/usr/bin/env python3
"""pair_fonts.py rewrites slide XML and the chart XML Artifact Tool writes under ppt/slides/charts/."""
import subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'pair_fonts.py'
RUN = '<a:rPr><a:latin typeface="Apple SD Gothic Neo"/><a:ea typeface="Apple SD Gothic Neo"/><a:cs typeface="Apple SD Gothic Neo"/></a:rPr>'


class PairFontsTests(unittest.TestCase):
    def test_slide_and_chart_parts_are_paired(self):
        parts = ['ppt/slides/slide1.xml', 'ppt/slides/charts/chart1.xml', 'ppt/charts/chart2.xml']
        with tempfile.TemporaryDirectory() as td:
            src, dst = Path(td, 'a.pptx'), Path(td, 'b.pptx')
            with zipfile.ZipFile(src, 'w') as z:
                for p in parts:
                    z.writestr(p, RUN)
            subprocess.run([sys.executable, str(SCRIPT), str(src), str(dst)], check=True, capture_output=True)
            with zipfile.ZipFile(dst) as z:
                for p in parts:
                    xml = z.read(p).decode()
                    self.assertIn('<a:latin typeface="Helvetica Neue"', xml, p)
                    self.assertIn('<a:ea typeface="Apple SD Gothic Neo"', xml, p)


if __name__ == '__main__':
    unittest.main()

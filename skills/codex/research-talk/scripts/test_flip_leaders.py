#!/usr/bin/env python3
"""flip_leaders.py turns a rotated zero-height leader into a flipped bounding-box line with the same end points."""
import subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'flip_leaders.py'
SLIDE = ('<p:sld><p:spTree><p:sp><p:nvSpPr><p:cNvPr id="9" name="figure-leader"/></p:nvSpPr><p:spPr>'
         '<a:xfrm rot="%d" xmlns:a="x"><a:off x="1000" y="2000" /><a:ext cx="2000" cy="0" /></a:xfrm></p:spPr></p:sp></p:spTree></p:sld>')


class FlipLeaderTests(unittest.TestCase):
    def run_one(self, deg):
        with tempfile.TemporaryDirectory() as td:
            src, dst = Path(td, 'a.pptx'), Path(td, 'b.pptx')
            with zipfile.ZipFile(src, 'w') as z:
                z.writestr('ppt/slides/slide1.xml', SLIDE % round(deg * 60000))
            subprocess.run([sys.executable, str(SCRIPT), str(src), str(dst)], check=True, capture_output=True)
            return zipfile.ZipFile(dst).read('ppt/slides/slide1.xml').decode()

    def test_down_right_has_no_flip(self):
        xml = self.run_one(45)
        self.assertNotIn('rot=', xml); self.assertNotIn('flipV', xml)
        self.assertIn('<a:off x="1293" y="1293"', xml)    # centre (2000, 2000), box 1414 x 1414
        self.assertIn('cx="1414" cy="1414"', xml)

    def test_up_right_is_flipped(self):
        xml = self.run_one(-45)
        self.assertIn('flipV="1"', xml); self.assertNotIn('rot=', xml)

    def test_negative_reflex_angle_equals_down_right(self):
        xml = self.run_one(-135)                           # a line pointing up-left is a down-right line
        self.assertNotIn('flipV', xml)


if __name__ == '__main__':
    unittest.main()

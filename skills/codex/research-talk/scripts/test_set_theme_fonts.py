#!/usr/bin/env python3
"""set_theme_fonts.py rewrites the major/minor theme fonts."""
import subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'set_theme_fonts.py'
THEME = ('<a:theme><a:fontScheme><a:majorFont><a:latin typeface="Calibri Light"/><a:ea typeface=""/><a:cs typeface="Calibri Light"/></a:majorFont>'
         '<a:minorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface="Calibri"/></a:minorFont></a:fontScheme></a:theme>')


class ThemeFontTests(unittest.TestCase):
    def test_theme_fonts_replaced(self):
        with tempfile.TemporaryDirectory() as td:
            src, dst = Path(td, 'a.pptx'), Path(td, 'b.pptx')
            with zipfile.ZipFile(src, 'w') as z:
                z.writestr('ppt/theme/theme1.xml', THEME)
            subprocess.run([sys.executable, str(SCRIPT), str(src), str(dst), 'Pretendard'], check=True, capture_output=True)
            xml = zipfile.ZipFile(dst).read('ppt/theme/theme1.xml').decode()
            self.assertNotIn('Calibri', xml)
            self.assertEqual(xml.count('typeface="Pretendard"'), 6)


if __name__ == '__main__':
    unittest.main()

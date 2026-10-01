#!/usr/bin/env python3
"""chart_no_autotitle.py adds autoTitleDeleted before plotArea (and leaves charts that already have a title or the flag alone)."""
import subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'chart_no_autotitle.py'
NS = 'xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart"'


class AutoTitleTests(unittest.TestCase):
    def test_flag_added_once(self):
        parts = {'ppt/slides/charts/chart1.xml': f'<c:chartSpace {NS}><c:chart><c:plotArea><c:barChart/></c:plotArea></c:chart></c:chartSpace>',
                 'ppt/slides/charts/chart2.xml': f'<c:chartSpace {NS}><c:chart><c:title/><c:plotArea/></c:chart></c:chartSpace>',
                 'ppt/slides/charts/chart3.xml': f'<c:chartSpace {NS}><c:chart><c:autoTitleDeleted val="1"/><c:plotArea/></c:chart></c:chartSpace>'}
        with tempfile.TemporaryDirectory() as td:
            src, dst = Path(td, 'a.pptx'), Path(td, 'b.pptx')
            with zipfile.ZipFile(src, 'w') as z:
                for k, v in parts.items():
                    z.writestr(k, v)
            subprocess.run([sys.executable, str(SCRIPT), str(src), str(dst)], check=True, capture_output=True)
            z = zipfile.ZipFile(dst)
            self.assertIn('<c:autoTitleDeleted val="1"/><c:plotArea>', z.read('ppt/slides/charts/chart1.xml').decode())
            self.assertEqual(z.read('ppt/slides/charts/chart2.xml').decode().count('autoTitleDeleted'), 0)
            self.assertEqual(z.read('ppt/slides/charts/chart3.xml').decode().count('autoTitleDeleted'), 1)


if __name__ == '__main__':
    unittest.main()

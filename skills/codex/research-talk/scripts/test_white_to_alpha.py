#!/usr/bin/env python3
"""white_to_alpha.py: white becomes transparent, dark ink stays opaque."""
import subprocess, sys, tempfile, unittest
from pathlib import Path
from PIL import Image

SCRIPT = Path(__file__).resolve().parent / 'white_to_alpha.py'


class WhiteToAlphaTests(unittest.TestCase):
    def test_white_transparent_ink_opaque(self):
        with tempfile.TemporaryDirectory() as td:
            src, dst = Path(td, 'a.png'), Path(td, 'b.png')
            im = Image.new('RGB', (20, 20), 'white'); im.putpixel((5, 5), (20, 20, 20)); im.save(src)
            subprocess.run([sys.executable, str(SCRIPT), str(src), str(dst)], check=True, capture_output=True)
            out = Image.open(dst)
            self.assertEqual(out.mode, 'RGBA')
            self.assertEqual(out.getpixel((0, 0))[3], 0)
            self.assertEqual(out.getpixel((5, 5))[3], 255)


if __name__ == '__main__':
    unittest.main()

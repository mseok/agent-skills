#!/usr/bin/env python3
"""ensure_font.py installs the bundled font automatically when it is missing (tested in a throw-away HOME), and --check-only does not."""
import os, subprocess, sys, tempfile, unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'ensure_font.py'


def run(home, *args):
    env = dict(os.environ, HOME=home, ENSURE_FONT_NO_FC='1')
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env)


@unittest.skipUnless(sys.platform in ('darwin',) or sys.platform.startswith('linux'), 'user font folder test covers macOS/Linux')
class EnsureFontTests(unittest.TestCase):
    def folder(self, home):
        return Path(home) / ('Library/Fonts' if sys.platform == 'darwin' else '.local/share/fonts')

    def test_check_only_does_not_install(self):
        with tempfile.TemporaryDirectory() as home:
            r = run(home, '--check-only')
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertFalse(self.folder(home).exists())

    def test_missing_font_is_installed_automatically(self):
        with tempfile.TemporaryDirectory() as home:
            r = run(home)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            names = sorted(p.name for p in self.folder(home).iterdir())
            self.assertEqual(names, ['Pretendard-Bold.otf', 'Pretendard-Regular.otf'])
            self.assertIn('installed', run(home).stdout)       # second run: already there


if __name__ == '__main__':
    unittest.main()

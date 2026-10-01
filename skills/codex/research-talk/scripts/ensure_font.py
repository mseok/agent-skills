#!/usr/bin/env python3
"""Make sure the deck font (default Pretendard) is installed; install the bundled copy automatically when it is missing.

usage: ensure_font.py [--family Pretendard] [--check-only]
Looks in fontconfig (`fc-list`), then the user/system font folders. When the family is missing it copies assets/fonts/<family>-*.otf into the user's
font folder (user-level, no admin rights; the user approved automatic installation on 2026-10-02):
  macOS   ~/Library/Fonts
  Linux   ~/.local/share/fonts (then `fc-cache -f`)
  Windows %LOCALAPPDATA%\\Microsoft\\Windows\\Fonts plus the per-user registry entries
Exit 0 when the family is available afterwards, 1 when it is not (message says why). --check-only never installs.
Other machines that open the deck need the same font: assets/fonts/README.md."""
import argparse, os, shutil, subprocess, sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--family', default='Pretendard'); ap.add_argument('--check-only', action='store_true')
ap.add_argument('--install', action='store_true', help='kept for old callers; installation is automatic now')
a = ap.parse_args()
FONTS = Path(__file__).resolve().parent.parent / 'assets' / 'fonts'


def folders():
    out = [Path.home() / 'Library/Fonts', Path('/Library/Fonts'), Path('/System/Library/Fonts'), Path.home() / '.local/share/fonts', Path('/usr/share/fonts'), Path('C:/Windows/Fonts')]
    if os.environ.get('LOCALAPPDATA'):
        out.append(Path(os.environ['LOCALAPPDATA']) / 'Microsoft/Windows/Fonts')
    return out


def available():
    if not os.environ.get('ENSURE_FONT_NO_FC') and shutil.which('fc-list') and subprocess.run(['fc-list', a.family, 'family'], capture_output=True, text=True).stdout.strip():
        return True
    for d in folders():
        if d.exists() and any(p.name.lower().startswith(a.family.lower()) for p in d.rglob('*') if p.is_file()):
            return True
    return False


def install(files):
    if sys.platform == 'darwin':
        dest = Path.home() / 'Library/Fonts'
    elif sys.platform.startswith('linux'):
        dest = Path.home() / '.local/share/fonts'
    elif sys.platform == 'win32':
        dest = Path(os.environ.get('LOCALAPPDATA', str(Path.home() / 'AppData/Local'))) / 'Microsoft/Windows/Fonts'
    else:
        return None
    dest.mkdir(parents=True, exist_ok=True)
    for f in files:
        shutil.copy(f, dest / f.name)
    if sys.platform.startswith('linux') and shutil.which('fc-cache'):
        subprocess.run(['fc-cache', '-f', str(dest)], capture_output=True)
    if sys.platform == 'win32':
        try:
            import winreg
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows NT\CurrentVersion\Fonts') as k:
                for f in files:
                    winreg.SetValueEx(k, f'{f.stem} (OpenType)', 0, winreg.REG_SZ, str(dest / f.name))
        except Exception as e:   # the files are in place; the font appears after the next sign-in
            print(f'registry entry failed ({e}); sign out and in once')
    return dest


if available():
    print(f'{a.family}: installed'); sys.exit(0)
files = sorted(FONTS.glob(f'{a.family}-*.otf'))
if a.check_only:
    print(f'{a.family}: NOT installed (bundled: {[f.name for f in files] or "none"}); run without --check-only to install'); sys.exit(1)
if not files:
    print(f'{a.family}: NOT installed and no bundled copy in {FONTS}; install it by hand'); sys.exit(1)
dest = install(files)
if dest is None:
    print(f'{a.family}: unsupported platform; install {FONTS}/*.otf by hand'); sys.exit(1)
print(f'{a.family}: installed {len(files)} files into {dest}')
sys.exit(0 if available() or sys.platform == 'win32' else 1)

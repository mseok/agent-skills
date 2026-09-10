"""Find/register Arial; optionally install legally usable local files per user.

Requires matplotlib. Import ensure_arial() in every rendering process, since
Matplotlib addfont() registrations do not persist across Python processes.
No downloads, system installation, font substitution or cross-host copying.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from matplotlib import font_manager, ft2font


def font_dir():
    return Path(os.environ.get('XDG_DATA_HOME', str(Path.home()/'.local/share'))) / 'fonts/nature-figure'


def ensure_arial(source=None, destination=None):
    dest = Path(destination) if destination else font_dir()
    installed = []
    if source:
        # Caller provides a directory of font files licensed for this host.
        candidates = sorted(Path(source).rglob('*'))
        for src in candidates:
            if src.suffix.lower() not in ('.ttf', '.otf'):
                continue
            face = ft2font.FT2Font(str(src))
            if face.family_name != 'Arial':
                continue
            digest = hashlib.sha256(src.read_bytes()).hexdigest()[:16]
            dest.mkdir(parents=True, exist_ok=True)
            target = dest / f'arial-{digest}{src.suffix.lower()}'
            if not target.exists():
                shutil.copyfile(src, target)
            installed.append(str(target))
        if installed and shutil.which('fc-cache'):
            subprocess.run(['fc-cache', '-f', str(dest)], check=True)
    paths = {f.fname for f in font_manager.fontManager.ttflist if f.name == 'Arial'}
    if dest.exists():
        paths.update(str(p) for p in dest.rglob('*') if p.suffix.lower() in ('.ttf','.otf'))
    arial = []
    for path in sorted(paths):
        face = ft2font.FT2Font(path)
        if face.family_name == 'Arial':
            font_manager.fontManager.addfont(path)
            arial.append(path)
    resolved = {}
    missing = []
    for name,weight in [('regular','normal'),('bold','bold')]:
        entries = [f for f in font_manager.fontManager.ttflist
                   if f.fname in arial and f.name == 'Arial' and f.style == 'normal'
                   and ((font_manager.weight_dict.get(f.weight,f.weight) >= 600) == (weight == 'bold'))]
        if not entries:
            missing.append(name)
        else:
            resolved[name] = entries[0].fname
    return {'status':'ready' if not missing else 'missing-arial',
            'font_paths':resolved, 'missing_faces':missing,
            'installed_files':installed, 'reusable_directory':str(dest),
            'scope':'Current Python process and local font files; Figma availability requires a separate check.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', help='Local directory containing Arial files licensed for use on this host')
    parser.add_argument('--destination', help='Override the persistent per-user font directory')
    args = parser.parse_args()
    result = ensure_arial(args.source,args.destination)
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['status']=='ready' else 2)

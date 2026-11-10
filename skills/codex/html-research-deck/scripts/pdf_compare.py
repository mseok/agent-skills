#!/usr/bin/env python3
"""pdf_compare.py — render an exported deck PDF with two independent renderers and compare them page by page.

usage: python3 pdf_compare.py /abs/deck/qa/deck.pdf [--dpi 48] [--json /abs/deck/qa/pdf-compare.json] [--keep DIR]
                              [--renderers pdftoppm,gs] [--max-strong 0.02] [--max-mean 6]

Chrome wrote the PDF; this checks that it survives other PDF engines: gradients, shadows, clip paths and fonts that one
engine draws and another drops show up as pages where the two renderings disagree. Renderers: pdftoppm (Poppler) and gs
(Ghostscript), both rendered to 8-bit gray at the same dpi (default 48, 960x540 px for a 1440x810 pt slide page).
Whichever are installed are used; with only one, the cross-check is skipped and the sanity checks still run. Per page:
  uniform   the page renders as a single flat tone (blank page, missing content)
  disagree  more than --max-strong of the pixels differ by more than 64 gray levels, or the mean difference exceeds --max-mean
  size      the two renderings differ by more than 1 px in width or height
Also: page count per renderer, and pdffonts (when installed): any font not embedded is an error, no Pretendard is a warning.
Exit 1 when a page is flagged or a font is not embedded, 2 when no renderer is installed. Thresholds are starting values
(see references/qa.md); a flagged page is a prompt to open both renderings, not a verdict. Standard library only.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RENDERERS = {
    'pdftoppm': lambda exe, pdf, dpi, prefix: [exe, '-r', str(dpi), '-gray', str(pdf), str(prefix)],
    'gs': lambda exe, pdf, dpi, prefix: [exe, '-q', '-dNOPAUSE', '-dBATCH', '-dSAFER', '-sDEVICE=pgmraw', f'-r{dpi}',
                                         f'-sOutputFile={prefix}-%03d.pgm', str(pdf)],
}
STRONG = 64


def read_pgm(path):
    data = Path(path).read_bytes()
    tokens, pos = [], 0
    while len(tokens) < 4:
        while data[pos:pos + 1].isspace():
            pos += 1
        if data[pos:pos + 1] == b'#':
            pos = data.index(b'\n', pos)
            continue
        end = pos
        while not data[end:end + 1].isspace():
            end += 1
        tokens.append(data[pos:end])
        pos = end
    if tokens[0] != b'P5' or tokens[3] != b'255':
        raise ValueError(f'{path}: not an 8-bit binary PGM')
    width, height = int(tokens[1]), int(tokens[2])
    return width, height, data[pos + 1:pos + 1 + width * height]


def render(name, pdf, dpi, outdir):
    exe = shutil.which(name)
    if not exe:
        return None
    prefix = Path(outdir) / name
    run = subprocess.run(RENDERERS[name](exe, pdf, dpi, prefix), capture_output=True, text=True, check=False, timeout=600)
    pages = sorted(Path(outdir).glob(f'{name}-*.pgm'))
    if run.returncode or not pages:
        sys.exit(f'{name} failed on {pdf}: {run.stderr.strip()[:300]}')
    return [read_pgm(p) for p in pages]


def crop(page, width, height):
    w, h, px = page
    if (w, h) == (width, height):
        return px
    return b''.join(px[row * w:row * w + width] for row in range(height))


def diff_stats(a, b):
    width, height = min(a[0], b[0]), min(a[1], b[1])
    pa, pb = crop(a, width, height), crop(b, width, height)
    total = strong = 0
    for x, y in zip(pa, pb):
        d = x - y if x > y else y - x
        total += d
        strong += d > STRONG
    n = len(pa)
    return total / n, strong / n


def flat(page):
    px = page[2]
    return max(px) - min(px) < 8


def font_findings(pdf):
    exe = shutil.which('pdffonts')
    if not exe:
        return [], 'pdffonts not installed; fonts not checked'
    run = subprocess.run([exe, str(pdf)], capture_output=True, text=True, check=False)
    errors, names = [], []
    for line in run.stdout.splitlines()[2:]:
        tok = line.split()
        if len(tok) < 8:
            continue
        names.append(tok[0])
        if tok[-5] != 'yes':
            errors.append(f'font not embedded: {tok[0]}')
    if names and not any('Pretendard' in n for n in names):
        errors.append('warn: no Pretendard in the PDF (the theme font)')
    return errors, f'{len(names)} fonts'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pdf')
    ap.add_argument('--dpi', type=int, default=48)
    ap.add_argument('--renderers', default=','.join(RENDERERS))
    ap.add_argument('--max-strong', type=float, default=0.02)
    ap.add_argument('--max-mean', type=float, default=6.0)
    ap.add_argument('--json', default='')
    ap.add_argument('--keep', default='', help='keep the rendered PGM pages in this folder')
    a = ap.parse_args()
    pdf = Path(a.pdf).resolve()
    if not pdf.is_file():
        sys.exit(f'not a file: {pdf}')
    names = [n for n in a.renderers.split(',') if n in RENDERERS and shutil.which(n)]
    if not names:
        print('no PDF renderer installed (looked for: ' + a.renderers + ')', file=sys.stderr)
        return 2
    work = Path(a.keep) if a.keep else Path(tempfile.mkdtemp(prefix='pdf-compare.'))
    work.mkdir(parents=True, exist_ok=True)
    try:
        pages = {n: render(n, pdf, a.dpi, work) for n in names}
    finally:
        if not a.keep:
            shutil.rmtree(work, ignore_errors=True)
    counts = {n: len(p) for n, p in pages.items()}
    findings = []
    if len(set(counts.values())) > 1:
        findings.append({'page': 0, 'kind': 'page-count', 'detail': counts})
    rows = []
    for i in range(min(counts.values())):
        row = {'page': i + 1}
        for n in names:
            if flat(pages[n][i]):
                findings.append({'page': i + 1, 'kind': 'uniform', 'detail': n})
        if len(names) > 1:
            first, second = pages[names[0]][i], pages[names[1]][i]
            if abs(first[0] - second[0]) > 1 or abs(first[1] - second[1]) > 1:
                findings.append({'page': i + 1, 'kind': 'size', 'detail': [first[:2], second[:2]]})
            row['mean'], row['strong'] = diff_stats(first, second)
            if row['strong'] > a.max_strong or row['mean'] > a.max_mean:
                findings.append({'page': i + 1, 'kind': 'disagree', 'detail': {'mean': round(row['mean'], 2), 'strong': round(row['strong'], 4)}})
        rows.append(row)
    fonts, font_note = font_findings(pdf)
    print(f"renderers: {', '.join(names)} · pages: {counts} · dpi {a.dpi} · {font_note}")
    if len(names) < 2:
        print(f'only {names[0]} is installed: cross-renderer comparison skipped, sanity checks only')
    else:
        print('page  mean-diff  strong-share')
        for r in rows:
            print(f"{r['page']:>4}  {r['mean']:>9.2f}  {r['strong']:>12.4f}")
    for f in findings:
        print(f"FLAG  page {f['page']}  {f['kind']}  {f['detail']}")
    for f in fonts:
        print(('WARN  ' if f.startswith('warn') else 'ERROR ') + f)
    bad = len(findings) + sum(not f.startswith('warn') for f in fonts)
    print(f'{len(rows)} pages compared · {len(findings)} flagged pages or counts · {len(fonts)} font findings')
    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps({'renderers': names, 'pages': rows, 'findings': findings, 'fonts': fonts}, indent=1) + '\n', encoding='utf-8')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())

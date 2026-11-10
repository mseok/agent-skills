#!/usr/bin/env python3
"""regression_run.py — replay every recorded user-reported visual defect against the deck checkers.

usage: python3 regression_run.py [--manifest regression/manifest.json] [--only ID,ID] [--list] [--no-render] [--json out.json]

Each case in the manifest is one defect the user reported (format and how to add one: regression/README.md). A case names
the checker that should catch it, a `bad` fixture that must trigger the expected finding and, when the defect can be
fixed in markup, a `fixed` fixture that must not. Fixtures are slide fragments (`<section class="slide">…`); they are
placed into a throw-away deck that links this skill's css, js and vendor folders. Cases with tool `manual` cannot be
measured: they are printed as a checklist for the inspection pass in references/qa.md.

  PASS    the bad fixture triggers the expected finding and the fixed one does not
  FAIL    the checker missed the defect, flagged the fixed fixture, or the case's quote is not in its source file
  MANUAL  inspection item, nothing was run
  SKIP    needs headless Chrome and none was found (or --no-render)

Exit 1 when any case fails. Every `source` must exist inside the skill folder and contain the `quote` verbatim, so a case can
only be seeded from a defect the skill's own files record. Standard library only.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL / 'scripts'
DECK = SKILL / 'assets' / 'deck'
CHROME = os.environ.get('CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
TOOLS = {'check_layout', 'check_deck', 'banned_copy_lint', 'manual'}
NEEDS_CHROME = {'check_layout'}
REQUIRED = ('id', 'date', 'source', 'quote', 'defect', 'tool')


def build_deck(fragment, folder):
    """A throw-away deck: the skill's template with the fragment as its slides, engine folders linked."""
    folder = Path(folder)
    for sub in ('css', 'js', 'vendor'):
        (folder / sub).symlink_to(DECK / sub)
    template = (DECK / 'templates' / 'index.template.html').read_text(encoding='utf-8')
    sprite = (DECK / 'sprite-research.svg').read_text(encoding='utf-8').strip()
    html = template.replace('{{TITLE}}', 'regression').replace('{{LANG}}', 'ko').replace('{{SPRITE}}', sprite).replace('{{SLIDES}}', fragment)
    index = folder / 'index.html'
    index.write_text(html, encoding='utf-8')
    return index


def run_tool(tool, index, out_json):
    """Return the list of finding codes a checker produced on one deck."""
    cmd = [sys.executable, str(SCRIPTS / f'{tool}.py'), str(index), '--json', str(out_json)]
    if tool == 'check_layout':
        cmd.append('--quiet')
    run = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=600)
    if not Path(out_json).is_file():
        raise RuntimeError(f'{tool} wrote no report (exit {run.returncode}): {(run.stderr or run.stdout).strip()[-300:]}')
    doc = json.loads(Path(out_json).read_text(encoding='utf-8'))
    if tool == 'check_layout':
        return [f['kind'] for s in doc['slides'] for f in s['findings']]
    if tool == 'check_deck':
        return list(doc['errors']) + list(doc['warnings'])
    return [f['rule'] for f in doc['findings']]


def matches(tool, expect, codes):
    if tool == 'check_deck':
        return any(expect in c for c in codes)
    return expect in codes


def check_case(case, args):
    problems = [f'missing field {k}' for k in REQUIRED if not case.get(k)]
    if problems:
        return 'FAIL', '; '.join(problems)
    if case['tool'] not in TOOLS:
        return 'FAIL', f"unknown tool {case['tool']}"
    source = (SKILL / case['source']).resolve()
    if SKILL not in source.parents or not source.is_file():
        return 'FAIL', f"source {case['source']} is not a file inside the skill"
    if case['quote'] not in source.read_text(encoding='utf-8'):
        return 'FAIL', f"quote not found verbatim in {case['source']}"
    if case['tool'] == 'manual':
        return 'MANUAL', case.get('check', case['defect'])
    if not case.get('expect') or not case.get('bad'):
        return 'FAIL', 'a measured case needs expect and bad'
    if case['tool'] in NEEDS_CHROME and (args.no_render or not os.access(CHROME, os.X_OK)):
        return 'SKIP', 'needs headless Chrome'
    results = {}
    for variant in ('bad', 'fixed'):
        if not case.get(variant):
            continue
        fixture = (args.manifest.parent / case[variant]).read_text(encoding='utf-8')
        with tempfile.TemporaryDirectory(prefix='regression.') as tmp:
            index = build_deck(fixture, tmp)
            results[variant] = run_tool(case['tool'], index, Path(tmp) / 'report.json')
    if not matches(case['tool'], case['expect'], results['bad']):
        return 'FAIL', f"{case['tool']} did not report {case['expect']} on the bad fixture (got {sorted(set(results['bad'])) or 'nothing'})"
    if 'fixed' in results and matches(case['tool'], case['expect'], results['fixed']):
        return 'FAIL', f"{case['tool']} still reports {case['expect']} on the fixed fixture"
    return 'PASS', case['defect']


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--manifest', type=Path, default=SKILL / 'regression' / 'manifest.json')
    ap.add_argument('--only', default='')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--no-render', action='store_true')
    ap.add_argument('--json', default='')
    args = ap.parse_args()
    args.manifest = args.manifest.resolve()
    cases = json.loads(args.manifest.read_text(encoding='utf-8'))['cases']
    ids = [c.get('id') for c in cases]
    if len(set(ids)) != len(ids):
        sys.exit('duplicate case ids in the manifest')
    only = {x for x in args.only.split(',') if x}
    rows = []
    for case in cases:
        if only and case.get('id') not in only:
            continue
        if args.list:
            print(f"{case.get('id'):<28} {case.get('date')}  {case.get('tool'):<17} {case.get('defect')}")
            continue
        try:
            status, note = check_case(case, args)
        except (RuntimeError, OSError, subprocess.TimeoutExpired) as err:
            status, note = 'FAIL', str(err)
        rows.append({'id': case.get('id'), 'status': status, 'note': note})
        print(f"{status:<6} {case.get('id'):<28} {note}")
    if args.list:
        return 0
    tally = {s: sum(r['status'] == s for r in rows) for s in ('PASS', 'FAIL', 'MANUAL', 'SKIP')}
    print(' · '.join(f'{n} {s}' for s, n in tally.items()))
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps({'cases': rows, 'tally': tally}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return 1 if tally['FAIL'] else 0


if __name__ == '__main__':
    sys.exit(main())

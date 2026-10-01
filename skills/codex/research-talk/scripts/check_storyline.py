#!/usr/bin/env python3
"""Check a build snapshot against the approved flow; cannot authenticate consent."""
import argparse
import hashlib
import json
from pathlib import Path


def flow_digest(snapshot):
    flow = {key: snapshot[key] for key in ('presentation_id', 'brief', 'slides')}
    return hashlib.sha256(json.dumps(flow, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def check(snapshot):
    language = (snapshot.get('brief') or {}).get('language')
    if not isinstance(language, str) or not language.strip() or language.strip().lower() in ('tbd', 'unknown', 'unspecified', 'pending', '미정'):
        raise ValueError('Ask the user for the slide language and record their choice before building.')
    if snapshot.get('status') != 'approved':
        raise ValueError('Discuss and obtain user approval of this flow before building slides.')
    approval = snapshot.get('approval') or {}
    # Brief-driven runs (no interactive approval): `basis: "brief"` + `user_reference` = the brief; a date is not invented when the brief has none.
    if not approval.get('user_reference') or not (approval.get('approved_at') or approval.get('basis') == 'brief'):
        raise ValueError('The actual user approval reference and date are required (brief-driven runs: approval.basis = "brief").')
    if approval.get('flow_sha256') != flow_digest(snapshot):
        raise ValueError('The storyline changed after approval. Resolve the substantive change with the user.')
    for slide in snapshot['slides']:
        for field in ('id', 'role', 'title', 'message', 'visual'):
            if not isinstance(slide.get(field), str) or not slide[field].strip():
                raise ValueError(f'Each slide needs a nonempty {field}; use an explicit missing-input visual plan when needed.')
        if not isinstance(slide.get('evidence'), list):
            raise ValueError('Each slide needs an evidence list, even when empty for a setup slide.')
        missing = slide.get('missing_inputs', [])
        if not isinstance(missing, list) or any(not isinstance(item, str) or not item.strip() for item in missing):
            raise ValueError('missing_inputs must be a list of specific nonempty strings.')
        if slide['role'] in ('result', 'finding', 'benchmark', 'conclusion') and not slide['evidence'] and not slide.get('missing_inputs'):
            raise ValueError('Evidence-bearing slides need recorded evidence or explicit missing_inputs; do not invent results.')
    ids = [slide['id'] for slide in snapshot['slides']]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('Slides need nonempty, unique IDs.')
    source = snapshot.get('input_deck')
    if source and hashlib.sha256(Path(source['path']).read_bytes()).hexdigest() != source['sha256']:
        raise ValueError('The input deck changed. Read the latest user-edited file before revising.')
    return {'status': 'ready', 'flow_sha256': flow_digest(snapshot), 'slides': len(ids)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('--digest', action='store_true')
    args = parser.parse_args()
    snapshot = json.loads(args.snapshot.read_text())
    if args.digest:
        print(flow_digest(snapshot))
    else:
        try:
            print(json.dumps(check(snapshot)))
        except ValueError as error:
            parser.exit(2, str(error) + '\n')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""check_storyline.py accepts a brief-driven approval (basis = "brief") without an invented timestamp, and still rejects a missing reference."""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'check_storyline.py'


def run(snapshot):
    with tempfile.TemporaryDirectory() as td:
        p = Path(td, 's.json')
        p.write_text(json.dumps(snapshot))
        digest = subprocess.run([sys.executable, str(SCRIPT), str(p), '--digest'], capture_output=True, text=True).stdout.strip().split()[-1]
        snapshot['approval']['flow_sha256'] = digest
        p.write_text(json.dumps(snapshot))
        return subprocess.run([sys.executable, str(SCRIPT), str(p)], capture_output=True, text=True)


def base(approval):
    return {'presentation_id': 'x', 'status': 'approved', 'brief': {'language': 'English'}, 'approval': approval,
            'slides': [{'id': 's1', 'role': 'setup', 'title': 'T', 'message': 'm', 'evidence': [], 'visual': 'v'}]}


class BriefApprovalTests(unittest.TestCase):
    def test_brief_basis_without_date_passes(self):
        r = run(base({'user_reference': 'brief.json', 'basis': 'brief'}))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_missing_reference_fails(self):
        r = run(base({'basis': 'brief'}))
        self.assertNotEqual(r.returncode, 0)


if __name__ == '__main__':
    unittest.main()

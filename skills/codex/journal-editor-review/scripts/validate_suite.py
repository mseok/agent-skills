#!/usr/bin/env python3
"""Structural validator for journal-editor-review paired fixtures (inputs.json & rubric.json)."""

import argparse
import json
import re
import sys
from pathlib import Path

EXPECTED_FAMILIES = [f"T0{i}" for i in range(1, 9)]
URL_RE = re.compile(r"https?://([^/\s\"')>\]]+)")


def validate_suite(tests_dir):
    raw_inputs = (tests_dir / "inputs.json").read_text(encoding="utf-8")
    inp = json.loads(raw_inputs)
    rub = json.loads((tests_dir / "rubric.json").read_text(encoding="utf-8"))
    if inp.get("schema_version") != 1 or rub.get("schema_version") != 1:
        raise ValueError("Expected schema_version 1 in both inputs.json and rubric.json")
    cases = inp.get("cases") or []
    if len(cases) != 16:
        raise ValueError(f"Expected 16 cases in inputs.json, got {len(cases)}")
    case_ids = [c.get("id") for c in cases]
    if len(set(case_ids)) != 16:
        raise ValueError("Duplicate or missing case IDs in inputs.json")

    hosts = sorted({m.group(1).lower() for m in URL_RE.finditer(raw_inputs)})
    non_example = [h for h in hosts if not (h == "example.org" or h == "example.com" or h.endswith(".example"))]
    if non_example:
        raise ValueError(f"Non-reserved URLs in synthetic inputs.json: {non_example}")

    families = rub.get("families") or []
    if [f.get("id") for f in families] != EXPECTED_FAMILIES:
        raise ValueError(f"Expected families {EXPECTED_FAMILIES}, got {[f.get('id') for f in families]}")
    rubric_case_ids = []
    for fam in families:
        f_cases = fam.get("case_ids") or []
        if f_cases != [f"{fam['id']}A", f"{fam['id']}B"]:
            raise ValueError(f"Family {fam['id']} must pair {fam['id']}A and {fam['id']}B (got {f_cases})")
        if not fam.get("expectations") or not fam.get("paired_invariant"):
            raise ValueError(f"Family {fam['id']} missing expectations or paired_invariant")
        rubric_case_ids.extend(f_cases)
    if rubric_case_ids != case_ids:
        raise ValueError("Case ID order mismatch between inputs.json and rubric.json")
    return {"structural_status": "valid", "families": len(families), "cases": len(cases), "reserved_hosts": len(hosts)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--tests-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "tests",
    )
    args = ap.parse_args()
    report = validate_suite(args.tests_dir)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, KeyError, OSError) as exc:
        sys.exit(str(exc))

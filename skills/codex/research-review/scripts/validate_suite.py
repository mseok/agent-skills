#!/usr/bin/env python3
"""Validate paired fixtures and optionally prepare blind, gold-free review inputs."""

import argparse
import hashlib
import json
from pathlib import Path
import random
import re
import sys


SKILL = Path(__file__).resolve().parent.parent
FAMILIES = {"T{:02d}".format(i) for i in range(1, 19)}


def load_cases(path):
    data = json.loads(path.read_text())
    if data.get("schema_version") != 1 or not isinstance(data.get("cases"), list):
        raise ValueError("Expected schema_version 1 and a cases list: {}".format(path))
    cases = data["cases"]
    ids = [case.get("id") for case in cases]
    if any(not isinstance(i, str) for i in ids) or len(set(ids)) != len(ids):
        raise ValueError("Missing or duplicate case IDs: {}".format(path))
    return cases


def validate():
    inputs = load_cases(SKILL / "tests" / "inputs.json")
    rubrics = load_cases(SKILL / "tests" / "rubric.json")
    if len(inputs) != 36 or {c["id"] for c in inputs} != {c["id"] for c in rubrics}:
        raise ValueError("Expected 36 input/rubric pairs with matching IDs")
    variants = {family: [] for family in FAMILIES}
    allowed = {"id", "family", "variant", "request", "materials"}
    for case in inputs:
        if set(case) != allowed:
            raise ValueError("Unexpected input fields; keep gold out of inputs: {}".format(case["id"]))
        if re.fullmatch(r"T(?:0[1-9]|1[0-8])-[ab]", case["id"]) is None:
            raise ValueError("Invalid regression ID: {}".format(case["id"]))
        family = case["family"]
        if family not in FAMILIES or not case["id"].startswith(family + "-"):
            raise ValueError("Family/ID mismatch: {}".format(case["id"]))
        if case["variant"] not in {"base", "counter"}:
            raise ValueError("Invalid variant: {}".format(case["id"]))
        variants[family].append(case["variant"])
        if not isinstance(case["request"], str) or not case["request"].strip():
            raise ValueError("Empty request: {}".format(case["id"]))
        if not isinstance(case["materials"], list) or not case["materials"]:
            raise ValueError("Missing source materials: {}".format(case["id"]))
    if any(sorted(v) != ["base", "counter"] for v in variants.values()):
        raise ValueError("Each T01–T18 family requires one base and one counter case")
    for case in rubrics:
        for key in ("assertions", "critical_failures"):
            value = case.get(key)
            if not isinstance(value, list) or not value or any(
                not isinstance(item, str) or not item.strip() for item in value
            ):
                raise ValueError("Invalid rubric {}: {}".format(key, case["id"]))
    return inputs


def prepare(inputs, destination):
    if destination.exists():
        raise ValueError("Evaluation destination exists; choose a new path")
    shuffled = list(inputs)
    random.Random(20261106).shuffle(shuffled)
    batches = [[], []]
    mapping = {}
    for index, case in enumerate(shuffled):
        opaque = "C{:02d}".format(index + 1)
        # Producers get neither family/variant cues nor the expected judgments.
        batches[index % 2].append({
            "case_id": opaque,
            "request": case["request"],
            "materials": case["materials"],
        })
        mapping[opaque] = case["id"]
    hashes = {
        str(p.relative_to(SKILL)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [SKILL / "SKILL.md"] + sorted((SKILL / "references").glob("*.md"))
        + [SKILL / "tests" / "inputs.json", SKILL / "tests" / "rubric.json"]
    }
    destination.mkdir(parents=True)
    for index, cases in enumerate(batches, 1):
        (destination / "inputs-{}.json".format(index)).write_text(
            json.dumps({"synthetic": True, "cases": cases}, ensure_ascii=False, indent=2) + "\n"
        )
    (destination / "evaluation-map.json").write_text(json.dumps(mapping, indent=2) + "\n")
    (destination / "source-hashes.json").write_text(json.dumps(hashes, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-evaluation", type=Path)
    args = parser.parse_args()
    inputs = validate()
    if args.prepare_evaluation:
        prepare(inputs, args.prepare_evaluation.expanduser())
    print(json.dumps({
        "structural_status": "valid", "families": 18, "cases": len(inputs),
        "behavioral_status": "not evaluated by this script",
        "evaluation_directory": str(args.prepare_evaluation) if args.prepare_evaluation else None,
    }))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as exc:
        sys.exit(str(exc))

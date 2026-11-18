#!/usr/bin/env python3
"""Validate a benchmark-comparison verification receipt before reporting tables or figures."""

import argparse
import json
import sys
from pathlib import Path

REQUIRED_BASIS = (
    "factor_of_interest",
    "population_and_splits",
    "checkpoints",
    "evaluator_and_version",
    "budget_and_seeds",
    "selection_rule",
    "metric_and_direction",
    "missingness",
    "authoritative_reference",
    "analysis_parameters",
)
PLACEHOLDERS = {"", "tbd", "todo", "memory", "assumed", "?"}
PROVISIONAL_SOURCES = {"chat", "slack", "slides", "prior_figure"}
NON_STANDARD_SELECTION = {"oracle", "best-of-n", "best_of_n"}


def check_receipt(receipt, manifest_ids=None):
    errors = []
    basis = receipt.get("basis") or {}
    for key in REQUIRED_BASIS:
        val = str(basis.get(key, "")).strip()
        if val.lower() in PLACEHOLDERS:
            errors.append(f"basis.{key}: missing or placeholder value")

    cohorts = receipt.get("cohorts") or {}
    for cname, cohort in cohorts.items():
        expected_n = len(manifest_ids) if manifest_ids is not None else cohort.get("planned_n")
        observed_n = cohort.get("observed_n")
        if not isinstance(observed_n, int) or observed_n <= 0:
            errors.append(f"cohort.{cname}: observed_n must be a positive integer")
            continue
        if isinstance(expected_n, int) and observed_n < expected_n:
            removed = cohort.get("removed_ids")
            source = str(cohort.get("removal_reason_source", "")).strip()
            if not isinstance(removed, list) or len(removed) != expected_n - observed_n:
                errors.append(
                    f"cohort.{cname}: observed_n={observed_n} < expected_n={expected_n} "
                    f"without matching removed_ids (need {expected_n - observed_n})"
                )
            if not source:
                errors.append(f"cohort.{cname}: shrunk cohort requires removal_reason_source (or 'unknown')")

    panels = receipt.get("panels") or []
    cohort_primary_comparators = {}
    for panel in panels:
        pid = panel.get("id", "<unnamed>")
        cname = panel.get("cohort")
        rows = panel.get("rows") or []
        has_conf_selected = any(str(r.get("selection_rule", "")).lower() == "confidence-selected" for r in rows)
        comp_names = [r.get("comparator") for r in rows if r.get("comparator")]
        if cname and cname not in cohort_primary_comparators:
            cohort_primary_comparators[cname] = set(comp_names)
        elif cname and panel.get("kind") == "subgroup":
            missing_comp = cohort_primary_comparators[cname] - set(comp_names)
            declared_excl = set((panel.get("excluded_comparators") or {}).keys())
            undeclared = sorted(missing_comp - declared_excl)
            if undeclared:
                errors.append(f"panel.{pid}: subgroup omits parent cohort comparators without reason: {undeclared}")

        for row in rows:
            label = str(row.get("display_label", ""))
            sel = str(row.get("selection_rule", "")).lower()
            if (
                sel in NON_STANDARD_SELECTION
                and has_conf_selected
                and not row.get("user_bare_label_override")
                and "oracle" not in label.lower()
                and "best" not in label.lower()
                and sel not in label.lower()
            ):
                errors.append(f"panel.{pid}/{row.get('comparator')}: {sel} row needs selection tag in display_label")
            src_kind = str(row.get("source_kind", "raw_output")).lower()
            if src_kind in PROVISIONAL_SOURCES and not panel.get("provisional"):
                errors.append(f"panel.{pid}/{row.get('comparator')}: {src_kind} numbers require provisional=true")

    spots = receipt.get("spot_checks") or []
    if len(spots) < 2:
        errors.append(f"spot_checks: need >= 2 raw-output entity checks (got {len(spots)})")
    for idx, sc in enumerate(spots, 1):
        tol = float(sc.get("tolerance", 1e-6))
        if not sc.get("entity_id") or not sc.get("raw_path"):
            errors.append(f"spot_checks[{idx}]: missing entity_id or raw_path")
            continue
        if abs(float(sc["raw_value"]) - float(sc["reported_value"])) > tol:
            errors.append(f"spot_checks[{idx}] ({sc['entity_id']}): raw_value != reported_value")
    return errors


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("receipt", type=Path)
    ap.add_argument("--manifest", type=Path, help="newline-delimited or JSON list of expected entity IDs")
    args = ap.parse_args()
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    manifest_ids = None
    if args.manifest:
        raw = args.manifest.read_text(encoding="utf-8").strip()
        manifest_ids = json.loads(raw) if raw.startswith("[") else [ln.strip() for ln in raw.splitlines() if ln.strip()]
    errors = check_receipt(receipt, manifest_ids)
    print(json.dumps({"status": "fail" if errors else "ok", "errors": errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

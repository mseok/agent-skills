#!/usr/bin/env python3
"""Unit tests for benchmark-comparison/scripts/check_comparison_receipt.py."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from check_comparison_receipt import check_receipt


def valid_basis():
    return {
        "factor_of_interest": "problem identity disclosure (Informed vs Blind LLM)",
        "population_and_splits": "SVM 30 units (10 datasets x 3 seeds); PID 30 units (6 plants x 5 seeds)",
        "checkpoints": "claude-sonnet-5-5, fixed prompt v1",
        "evaluator_and_version": "poc_summary.py @ commit 713894f",
        "budget_and_seeds": "15 evaluations, shared 3-point Sobol init per seed",
        "selection_rule": "confidence-selected (best observed on validation; tie-break seed then step)",
        "metric_and_direction": "evals_to_target (lower is better), attainment % (higher is better)",
        "missingness": "exclude incomplete campaign runs with log citation",
        "authoritative_reference": "results/pid_poc/v1/summary.md (2026-11-16)",
        "analysis_parameters": "target threshold 1.10x grid_best, Wilson 95% CI",
    }


class CheckComparisonReceiptTests(unittest.TestCase):
    def test_catches_shrunk_cohort_missing_subgroup_comparator_and_bare_oracle_label(self):
        v01 = {
            "basis": valid_basis(),
            "cohorts": {"svm": {"planned_n": 30, "observed_n": 29}},
            "panels": [
                {
                    "id": "panel_b",
                    "cohort": "pid",
                    "kind": "main",
                    "rows": [
                        {"comparator": "botorch_bo", "display_label": "BoTorch", "selection_rule": "confidence-selected"},
                        {"comparator": "oracle_run", "display_label": "ModelX", "selection_rule": "oracle"},
                    ],
                },
                {
                    "id": "panel_c",
                    "cohort": "pid",
                    "kind": "subgroup",
                    "rows": [
                        {"comparator": "oracle_run", "display_label": "ModelX (oracle)", "selection_rule": "oracle"},
                    ],
                },
            ],
            "spot_checks": [
                {"entity_id": "('breast_cancer', True, 0)", "raw_path": "runs.jsonl", "raw_value": 4, "reported_value": 4},
            ],
        }
        errs = check_receipt(v01)
        self.assertTrue(any("cohort.svm" in e for e in errs), errs)
        self.assertTrue(any("panel.panel_b/oracle_run" in e for e in errs), errs)
        self.assertTrue(any("panel.panel_c" in e and "botorch_bo" in e for e in errs), errs)
        self.assertTrue(any("spot_checks: need >= 2" in e for e in errs), errs)

    def test_valid_receipt_passes_cli_under_ascii_locale(self):
        v02 = {
            "basis": valid_basis(),
            "cohorts": {
                "svm": {
                    "planned_n": 30,
                    "observed_n": 29,
                    "removed_ids": ["('wine', False, 0)"],
                    "removal_reason_source": "results/svm_poc/v1_resume.log:2 (중단 기록)",
                },
                "pid": {"planned_n": 30, "observed_n": 30},
            },
            "panels": [
                {
                    "id": "panel_b",
                    "cohort": "pid",
                    "kind": "main",
                    "rows": [
                        {"comparator": "botorch_bo", "display_label": "BoTorch", "selection_rule": "confidence-selected"},
                        {"comparator": "llm_named", "display_label": "Informed LLM", "selection_rule": "confidence-selected"},
                        {"comparator": "oracle_top", "display_label": "Model (best-of-N)", "selection_rule": "best-of-N"},
                    ],
                },
                {
                    "id": "panel_c",
                    "cohort": "pid",
                    "kind": "subgroup",
                    "rows": [
                        {"comparator": "botorch_bo", "display_label": "BoTorch", "selection_rule": "confidence-selected"},
                        {"comparator": "llm_named", "display_label": "Informed LLM", "selection_rule": "confidence-selected"},
                        {"comparator": "oracle_top", "display_label": "Model (best-of-N)", "selection_rule": "best-of-N"},
                    ],
                },
            ],
            "spot_checks": [
                {"entity_id": "('breast_cancer', True, 0)", "raw_path": "runs.jsonl", "raw_value": 4, "reported_value": 4},
                {"entity_id": "('digits', False, 2)", "raw_path": "runs.jsonl", "raw_value": 4, "reported_value": 4},
            ],
        }
        self.assertEqual(check_receipt(v02), [])
        with tempfile.TemporaryDirectory() as tmp:
            rec_path = Path(tmp) / "receipt.json"
            rec_path.write_text(json.dumps(v02, ensure_ascii=False), encoding="utf-8")
            script = Path(__file__).resolve().with_name("check_comparison_receipt.py")
            env = {**os.environ, "LC_ALL": "C", "PYTHONUTF8": "0"}
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(rec_path)],
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            self.assertEqual(json.loads(proc.stdout)["status"], "ok")


if __name__ == "__main__":
    unittest.main()

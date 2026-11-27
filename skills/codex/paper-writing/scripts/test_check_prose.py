#!/usr/bin/env python3
"""Unit tests for paper-writing/scripts/check_prose.py."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from check_prose import check


class CheckProseTests(unittest.TestCase):
    def test_latex_comments_display_math_and_layout_args_do_not_false_positive(self):
        draft = (
            "\\section{Results}\n"
            "% author note: 저자 확인 필요 (99.9%) and TBD marker\n"
            "DNA and RNA duplexes bind ATP in 3D space with 94.7\\% specificity \\citep{smith2024}.\n"
            "\\includegraphics[width=0.95\\textwidth]{fig1.pdf}\n"
            "\\vspace{-2.5mm}\n"
            "\\begin{tabular}{p{4.2cm}rr}\n"
            "\\[\n"
            "  \\mathcal{L}_{\\mathrm{KL}} = \\sum_{i=1}^{100} x_i\n"
            "\\]\n"
        )
        notes = "specificity = 94.7%"
        rep = check(draft, notes=notes, section="results")
        self.assertEqual(rep["report_register"], [])
        self.assertEqual(rep["non_english"], [])
        self.assertEqual(rep["untraced_numbers"], [])
        self.assertEqual(rep["undefined_acronyms"], [])

    def test_markdown_percentages_stay_intact(self):
        draft = "Informed search improved attainment from 60.0% to 94.7% across 30 benchmarks.\n"
        notes = "attainment: 60.0% -> 94.7% across 30 benchmarks"
        rep = check(draft, notes=notes, section="results")
        self.assertEqual(rep["untraced_numbers"], [])
        self.assertEqual(rep["sentences"]["count"], 1)

    def test_cjk_kana_and_hangul_detected_as_non_english(self):
        rep_kanji = check("The model generalizes across 漢字 cohorts.\n")
        self.assertEqual(len(rep_kanji["non_english"]), 1)
        rep_kana = check("The model generalizes across テスト cohorts.\n")
        self.assertEqual(len(rep_kana["non_english"]), 1)
        rep_hangul = check("The model generalizes across 실험 cohorts.\n")
        self.assertEqual(len(rep_hangul["non_english"]), 1)

    def test_acronym_allowlist_and_undefined_detection(self):
        rep = check("Complex VIII and Complex XII bind DNA, RNA and ATP in 2D and 3D views of QWERTY.\n")
        self.assertEqual(rep["undefined_acronyms"], ["QWERTY"])

    def test_results_finding_citations_and_equivalence_and_slop_flags(self):
        draft = (
            "Informed search halved the evaluations required to hit the target (Fig. 2a).\n\n"
            "Informed search (Fig. 2b) is comparable to the baseline and not merely faster, but cleaner.\n"
        )
        rep = check(draft, section="results")
        self.assertEqual(rep["review_layout"], [])
        self.assertTrue(any("comparable to" in h["match"].lower() for h in rep["review_in_context"]))
        self.assertTrue(any("not merely" in h["match"].lower() for h in rep["generic"]))

        rep_methods = check(draft, section="methods")
        self.assertEqual(rep_methods["review_layout"], [])

    def test_results_wrapped_finding_citations_are_not_layout_issues(self):
        draft = (
            "The treatment reduced aggregate formation\n"
            "(Fig. S2a).\n\n"
            "The affinity increased across the tested concentrations\n"
            "(see Fig. 3a and 3b).\n"
        )
        self.assertEqual(check(draft, section="results")["review_layout"], [])

    def test_results_pointer_only_and_presentational_endings(self):
        draft = (
            "The treatment reduced aggregate formation. See Fig. 2.\n\n"
            "(Table S1).\n\n"
            "The results are shown in Fig. 3.\n\n"
            "The left panel shows the comparison.\n"
        )
        hits = check(draft, section="results")["review_layout"]
        self.assertEqual([hit["line"] for hit in hits], [1, 3, 5, 7])
        self.assertIn("See Fig. 2.", hits[0]["match"])
        self.assertIn("layout/process sentence", hits[-1]["match"])
        self.assertEqual(check(draft, section="methods")["review_layout"], [])

    def test_intro_greek_entity_names_are_not_automatically_notation(self):
        for draft in (
            "Aβ and α-synuclein form distinct aggregates.",
            "β-lactam exposure altered the measured response.",
            "CO₂ concentration controls the reaction conditions.",
        ):
            with self.subTest(draft=draft):
                self.assertEqual(check(draft, section="intro")["opening"], [])

    def test_intro_explicit_math_remains_a_review_item(self):
        for draft in (
            "The coefficient $\\alpha$ controls the response.",
            r"The response is defined by \(y = x^2\).",
            "The response follows α = 0.5 under the stated conditions.",
        ):
            with self.subTest(draft=draft):
                hits = check(draft, section="intro")["opening"]
                self.assertTrue(any(hit["issue"] == "notation in the first paragraph" for hit in hits))

    def test_cli_runs_under_ascii_locale(self):
        script = Path(__file__).resolve().with_name("check_prose.py")
        env = {**os.environ, "LC_ALL": "C", "PYTHONUTF8": "0"}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            draft_path = root / "draft.tex"
            notes_path = root / "notes.md"
            draft_path.write_text(
                "% 한글 주석 88.8%\nDNA binding reached 91.2\\% accuracy across 30 targets.\n",
                encoding="utf-8",
            )
            notes_path.write_text("91.2% accuracy on 30 targets\n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(draft_path), "--notes", str(notes_path), "--json"],
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["untraced_numbers"], [])


if __name__ == "__main__":
    unittest.main()

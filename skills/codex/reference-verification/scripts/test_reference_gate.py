"""Behavior checks for finalization with absent, stale or unresolved evidence."""

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from check_reference_gate import METADATA_FIELDS, check_review, inventory


class ReferenceGateTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "main.tex").write_text(
            "\\input{section}\n\\bibliography{refs}\n",
            encoding="utf-8",
        )
        (self.root / "section.tex").write_text("A bounded claim.\\cite{a,b}\n", encoding="utf-8")
        (self.root / "refs.bib").write_text(
            "@article{a, title={Alpha}, author={One, A}, year={2026}}\n"
            "@article{b, title={Beta}, author={Two, B}, year={2026}}\n",
            encoding="utf-8",
        )
        self.current = inventory(self.root, ["main.tex"])
        evidence = [{"url": "https://example.org/paper", "locator": "section 2",
                     "accessed": "2026-11-09"}]
        self.review = {
            "snapshot_sha256": self.current["snapshot_sha256"],
            "references": {key: entry | {"metadata_status": "verified",
                           "evidence": evidence, "reason": "Fixture metadata agrees.",
                           "fields": {field: {"status": "verified" if field in {"title", "authors", "date"} else "not_applicable",
                                      "reason": "Inspected the synthetic source record."} for field in METADATA_FIELDS}}
                           for key, entry in self.current["references"].items()},
            "uses": {uid: {"context_sha256": use["context_sha256"],
                     "references": {key: {"status": "supported", "evidence": evidence,
                                    "reason": "Fixture passage supports this clause."}
                                    for key in use["keys"]}}
                     for uid, use in self.current["uses"].items()},
        }
        self.uid = next(iter(self.current["uses"]))

    def test_complete_current_review_passes(self):
        self.assertEqual(check_review(self.current, self.review), [])

    def test_missing_bibliography_key_blocks(self):
        (self.root / "section.tex").write_text("Claim.\\cite{missing}\n", encoding="utf-8")
        current = inventory(self.root, ["main.tex"])
        self.assertTrue(current["problems"])

    def test_missing_reference_review_blocks(self):
        del self.review["references"]["a"]
        self.assertTrue(check_review(self.current, self.review))

    def test_incomplete_group_review_blocks(self):
        del self.review["uses"][self.uid]["references"]["b"]
        self.assertTrue(check_review(self.current, self.review))

    def test_changed_title_cannot_reuse_review(self):
        path = self.root / "refs.bib"
        path.write_text(path.read_text(encoding="utf-8").replace("Alpha", "Invented title"), encoding="utf-8")
        self.assertTrue(check_review(inventory(self.root, ["main.tex"]), self.review))

    def test_changed_claim_cannot_reuse_review(self):
        path = self.root / "section.tex"
        path.write_text(path.read_text(encoding="utf-8").replace("bounded", "universal"), encoding="utf-8")
        self.assertTrue(check_review(inventory(self.root, ["main.tex"]), self.review))

    def test_recorded_metadata_mismatch_blocks(self):
        self.review["references"]["a"]["metadata_status"] = "mismatch"
        self.assertTrue(check_review(self.current, self.review))

    def test_missing_primary_evidence_blocks(self):
        self.review["references"]["a"]["evidence"] = []
        self.assertTrue(check_review(self.current, self.review))

    def test_partial_support_requires_a_resolved_role(self):
        review = copy.deepcopy(self.review)
        item = review["uses"][self.uid]["references"]["a"]
        item["status"] = "partial"
        item["disposition"] = "unresolved"
        self.assertTrue(check_review(self.current, review))
        item["disposition"] = "covered_by_group"
        item["reason"] = "This source supports clause one; source b supports clause two."
        self.assertEqual(check_review(self.current, review), [])

    def test_blocked_access_cannot_be_cleared(self):
        self.review["uses"][self.uid]["references"]["a"]["status"] = "unverified"
        self.assertTrue(check_review(self.current, self.review))

    def test_metadata_mode_does_not_require_content_reviews(self):
        del self.review["uses"]
        self.assertEqual(check_review(self.current, self.review, "metadata"), [])
        self.assertTrue(check_review(self.current, self.review, "full"))

    def test_metadata_mode_excludes_content_mismatch(self):
        self.review["uses"][self.uid]["references"]["a"]["status"] = "mismatch"
        self.assertEqual(check_review(self.current, self.review, "metadata"), [])
        self.assertTrue(check_review(self.current, self.review, "full"))

    def test_metadata_mode_still_blocks_metadata_mismatch(self):
        self.review["references"]["a"]["metadata_status"] = "mismatch"
        self.assertTrue(check_review(self.current, self.review, "metadata"))

    def test_verified_overall_does_not_hide_unverified_field(self):
        self.review["references"]["a"]["fields"]["authors"]["status"] = "unverified"
        self.assertTrue(check_review(self.current, self.review, "metadata"))

    def test_missing_field_review_blocks(self):
        del self.review["references"]["a"]["fields"]["date"]
        self.assertTrue(check_review(self.current, self.review, "metadata"))

    def test_duplicate_keys_are_rejected(self):
        path = self.root / "refs.bib"
        path.write_text(path.read_text(encoding="utf-8") + "@article{a, title={Other}}\n", encoding="utf-8")
        current = inventory(self.root, ["main.tex"])
        self.assertTrue(any("Duplicate bibliography key: a" in p for p in current["problems"]))
        self.assertTrue(check_review(current, self.review))

    def test_unresolved_include_blocks_inventory(self):
        (self.root / "main.tex").write_text("\\input{absent}\n", encoding="utf-8")
        self.assertTrue(inventory(self.root, ["main.tex"])["problems"])

    def test_citation_placeholder_blocks_inventory(self):
        (self.root / "section.tex").write_text("A claim [CITE: evidence needed].\n", encoding="utf-8")
        self.assertTrue(inventory(self.root, ["main.tex"])["problems"])

    def test_unsupported_citation_command_cannot_silently_pass(self):
        for command in ("\\autocite{a}", "\\cites{a}{b}"):
            with self.subTest(command=command):
                (self.root / "section.tex").write_text(f"A claim.{command}\n", encoding="utf-8")
                self.assertTrue(inventory(self.root, ["main.tex"])["problems"])

    def test_single_citation_cannot_claim_group_support(self):
        (self.root / "section.tex").write_text("A claim.\\cite{a}\n", encoding="utf-8")
        current = inventory(self.root, ["main.tex"])
        uid = next(iter(current["uses"]))
        review = copy.deepcopy(self.review)
        review["snapshot_sha256"] = current["snapshot_sha256"]
        del review["references"]["b"]
        review["uses"] = {uid: review["uses"][self.uid]}
        review["uses"][uid]["context_sha256"] = current["uses"][uid]["context_sha256"]
        del review["uses"][uid]["references"]["b"]
        review["uses"][uid]["references"]["a"].update(status="partial", disposition="covered_by_group")
        self.assertTrue(check_review(current, review))

    def test_capitalized_natbib_commands_are_extracted(self):
        (self.root / "section.tex").write_text(
            "\\Citet{a} showed the bound, \\Citep[see][p.~2]{b} confirmed it, "
            "and \\Citealt{a} with \\Citeauthor{b} agreed.\n",
            encoding="utf-8",
        )
        current = inventory(self.root, ["main.tex"])
        self.assertEqual(current["problems"], [])
        self.assertEqual(set(current["references"]), {"a", "b"})
        self.assertEqual(len(current["uses"]), 4)

    def test_bib_percent_comments_ignored_and_unclosed_entry_recorded(self):
        bib = self.root / "refs.bib"
        bib.write_text(
            "% @article{a, title={Old commented duplicate}}\n"
            "  % @article{unclosed_comment, title={Ignored\n"
            + bib.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        clean_current = inventory(self.root, ["main.tex"])
        self.assertEqual(clean_current["problems"], [])

        bib.write_text(bib.read_text(encoding="utf-8") + "@article{broken, title={Missing brace\n", encoding="utf-8")
        broken_current = inventory(self.root, ["main.tex"])
        self.assertTrue(any("Unclosed bibliography entry: broken" in p for p in broken_current["problems"]))

    def test_utf8_cli_io_under_ascii_locale(self):
        (self.root / "section.tex").write_text("Müller et al. (2020–2026) studied 촉매.\\Citet{a}\n", encoding="utf-8")
        (self.root / "refs.bib").write_text(
            "@article{a, title={Über–Alpha}, author={Müller, A}, year={2026}}\n",
            encoding="utf-8",
        )
        current = inventory(self.root, ["main.tex"])
        uid = next(iter(current["uses"]))
        evidence = [{"url": "https://example.org/muller", "locator": "p. 1–2", "accessed": "2026-11-18"}]
        review = {
            "snapshot_sha256": current["snapshot_sha256"],
            "references": {
                "a": current["references"]["a"]
                | {
                    "metadata_status": "verified",
                    "evidence": evidence,
                    "reason": "Verified Müller metadata.",
                    "fields": {
                        field: {
                            "status": "verified" if field in {"title", "authors", "date"} else "not_applicable",
                            "reason": "Checked UTF-8 record.",
                        }
                        for field in METADATA_FIELDS
                    },
                }
            },
            "uses": {
                uid: {
                    "context_sha256": current["uses"][uid]["context_sha256"],
                    "references": {"a": {"status": "supported", "evidence": evidence, "reason": "Supported."}},
                }
            },
        }
        inv_path = self.root / "inventory.json"
        rev_path = self.root / "review.json"
        rev_path.write_text(json.dumps(review, ensure_ascii=False), encoding="utf-8")
        script = Path(__file__).resolve().with_name("check_reference_gate.py")
        env = {**os.environ, "LC_ALL": "C", "PYTHONUTF8": "0"}
        proc = subprocess.run(
            [
                sys.executable,
                "-B",
                str(script),
                "--source-root",
                str(self.root),
                "--roots",
                "main.tex",
                "--inventory",
                str(inv_path),
                "--review",
                str(rev_path),
                "--mode",
                "full",
            ],
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        self.assertEqual(json.loads(proc.stdout)["status"], "clear")


if __name__ == "__main__":
    unittest.main()

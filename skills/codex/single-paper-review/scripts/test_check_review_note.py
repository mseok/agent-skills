#!/usr/bin/env python3
"""Unit tests for single-paper-review/scripts/check_review_note.py."""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from check_review_note import REQUIRED_ORDER, check_note


class CheckReviewNoteTests(unittest.TestCase):
    def test_template_frontmatter_starts_with_required_order(self):
        template = (Path(__file__).resolve().parent.parent / "assets" / "review_template.md").read_text(encoding="utf-8")
        fm_match = re.match(r"^---\n(.*?)\n---\n", template, re.DOTALL)
        self.assertIsNotNone(fm_match)
        keys = [
            m.group(1)
            for ln in fm_match.group(1).splitlines()
            if (m := re.match(r"^([A-Za-z0-9_-]+):", ln))
        ]
        self.assertEqual(tuple(keys[:4]), REQUIRED_ORDER)

    def test_catches_subfolder_embed_missing_updated_empty_keys_and_cjk(self):
        broken = (
            "---\n"
            'title: "AlphaFold 3"\n'
            "created: 2026-11-18\n"
            "tags:\n"
            "  - kind/paper-review\n"
            "arxiv:\n"
            "doi:\n"
            "categories: [bio]\n"
            "---\n\n"
            "## 본문 그림 모음\n"
            "### Figure 1\n"
            "![[Attachments/af3/fig-1.png]]\n"
            "### Figure 3\n"
            "![[Attachments/af3-fig-3--a1b2c3d4e5f6.png]]\n"
            "漢字 요약\n"
        )
        errs, _ = check_note(broken)
        self.assertTrue(any("frontmatter.updated" in e for e in errs), errs)
        self.assertTrue(any("frontmatter.arxiv: empty field" in e for e in errs), errs)
        self.assertTrue(any("frontmatter.doi: empty field" in e for e in errs), errs)
        self.assertTrue(any("frontmatter.categories: retired" in e for e in errs), errs)
        self.assertTrue(any("invalid embed path" in e for e in errs), errs)
        self.assertTrue(any("non-contiguous" in e for e in errs), errs)
        self.assertTrue(any("CJK/kana" in e for e in errs), errs)

    def test_clean_note_passes_under_ascii_locale_cli(self):
        clean = (
            "---\n"
            'title: "AlphaFold 3"\n'
            "created: 2026-11-18\n"
            "updated: 2026-11-18\n"
            "tags:\n"
            "  - kind/paper-review\n"
            "year: 2024\n"
            "---\n\n"
            "## 본문 그림 모음\n"
            "### Figure 1\n"
            "![[Attachments/af3-fig-1--a1b2c3d4e5f6.png]]\n"
            "### Figure 2\n"
            "![[Attachments/af3-fig-2--0123456789ab.png]]\n"
        )
        errs, paths = check_note(clean)
        self.assertEqual(errs, [])
        self.assertEqual(len(paths), 2)

        with tempfile.TemporaryDirectory() as tmp:
            note_path = Path(tmp) / "note.md"
            note_path.write_text(clean, encoding="utf-8")
            script = Path(__file__).resolve().with_name("check_review_note.py")
            env = {**os.environ, "LC_ALL": "C", "PYTHONUTF8": "0"}
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(note_path)],
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(len(payload["attachment_preview_paths"]), 2)


if __name__ == "__main__":
    unittest.main()

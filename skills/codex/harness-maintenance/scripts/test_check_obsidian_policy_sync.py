#!/usr/bin/env python3
"""Unit tests for check_obsidian_policy_sync.py across synthetic clean/dirty trees and live skills."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_obsidian_policy_sync import audit_skills_root, main


class CheckObsidianPolicySyncTests(unittest.TestCase):
    def test_clean_tree_and_historical_provenance_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            policy = root / "codex" / "obsidian-agent-record" / "references" / "obsidian-policy.md"
            policy.parent.mkdir(parents=True)
            policy.write_text(
                "# Policy\n## 2. 실행된 배치 및 단건 기록 색인 (Evidence Index)\n"
                "`provenance_state`: `retained`, `partial`, `unverified`, `not-applicable`\n",
                encoding="utf-8",
            )
            un = root / "codex" / "obsidian-user-note"
            un.mkdir(parents=True)
            (un / "SKILL.md").write_text(
                '- **Concepts:** use `knowledge_revise(action: "create", path: "Concepts/<title>.md")` '
                "with YAML `title`, `created`, `updated`, `tags`.\n",
                encoding="utf-8",
            )
            deck = root / "codex" / "html-research-deck"
            deck.mkdir(parents=True)
            (deck / "SKILL.md").write_text(
                "Deck workflow (the former `research-talk` skill was merged into this one on 2026-11-12).\n",
                encoding="utf-8",
            )
            hm_cod = root / "codex" / "harness-maintenance" / "references"
            hm_cod.mkdir(parents=True)
            (hm_cod.parent / "SKILL.md").write_text("# Unified multi-harness maintenance\n", encoding="utf-8")
            (hm_cod / "user-decisions.md").write_text("- 2026-11-18: unified.\n", encoding="utf-8")
            gem = root / "gemini"
            gem.mkdir(parents=True)
            (gem / "harness-maintenance").symlink_to("../codex/harness-maintenance")

            router = Path(tmp) / "research-router.md"
            router.write_text("Uses html-research-deck and obsidian-agent-record.\n", encoding="utf-8")
            self.assertEqual(audit_skills_root(root, router), [])
            self.assertEqual(main(["--skills-root", str(root), "--router", str(router)]), 0)

    def test_dirty_tree_catches_all_defect_classes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            policy = root / "codex" / "obsidian-agent-record" / "references" / "obsidian-policy.md"
            policy.parent.mkdir(parents=True)
            policy.write_text(
                "# Policy\n## 2. 실행된 배치 및 단건 기록 색인 (Evidence Index)\n"
                "`provenance_state`: `retained`, `partial`, `unverified`, `not-applicable`\n",
                encoding="utf-8",
            )
            rw = root / "codex" / "research-workflow"
            rw.mkdir(parents=True)
            (rw / "SKILL.md").write_text(
                "Add to ## 2. 실행된 배치 및 단건 기록 색인 (Evidence Index) and run renew-gemini-login or claude rc.\n",
                encoding="utf-8",
            )
            un = root / "codex" / "obsidian-user-note"
            un.mkdir(parents=True)
            (un / "SKILL.md").write_text(
                '- **Concepts:** use `knowledge_revise(action: "create", path: "Concepts/<title>.md")` '
                "with YAML `title`, `created`, `tags`.\n",
                encoding="utf-8",
            )
            hm_cod = root / "codex" / "harness-maintenance" / "references"
            hm_cod.mkdir(parents=True)
            (hm_cod.parent / "SKILL.md").write_text("One scope: never add a second scope.\n", encoding="utf-8")
            (hm_cod / "user-decisions.md").write_text("- 2026-11-10: old.\n", encoding="utf-8")

            hm_gem = root / "gemini" / "harness-maintenance" / "references"
            hm_gem.mkdir(parents=True)
            (hm_gem.parent / "SKILL.md").write_text("# Fork\n", encoding="utf-8")
            (hm_gem / "user-decisions.md").write_text("- 2026-11-18: new.\n", encoding="utf-8")
            (root / "gemini" / "broken-skill").symlink_to("../codex/does-not-exist")

            router = Path(tmp) / "research-router.md"
            router.write_text("Uses research-talk's presentation note.\n", encoding="utf-8")

            issues = audit_skills_root(root, router)
            kinds = {str(item["kind"]) for item in issues}
            self.assertEqual(
                kinds,
                {
                    "broken_gemini_symlink",
                    "duplicate_policy_rule",
                    "missing_updated_field",
                    "retired_reference",
                    "user_decisions_divergence",
                },
            )
            self.assertEqual(main(["--skills-root", str(root), "--router", str(router), "--json"]), 1)

    def test_live_repository_skills_pass(self) -> None:
        skills_root = Path(__file__).resolve().parents[3]
        self.assertEqual(audit_skills_root(skills_root), [])


if __name__ == "__main__":
    unittest.main()

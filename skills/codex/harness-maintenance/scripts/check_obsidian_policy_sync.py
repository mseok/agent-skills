#!/usr/bin/env python3
"""Deterministic checker for Obsidian policy SSOT, retired harness terms, and codex/gemini skill sync.

Implements enforcement-ledger.md row 31 ('Grep skills and the vault for a second copy of a vault
rule when a rule changes') plus cross-harness user-decisions and symlink parity under Python 3.9+.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RETIRED_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("retired skill 'research-talk'", re.compile(r"\bresearch-talk\b")),
    ("retired skill 'obsidian-main-note'", re.compile(r"\bobsidian-main-note\b")),
    ("deleted command 'renew-gemini-login'", re.compile(r"\brenew-gemini-login\b")),
    ("retired 'claude rc' workflow", re.compile(r"\bclaude rc\b")),
    ("obsolete single-scope ban ('never add a second scope')", re.compile(r"never add a second scope", re.IGNORECASE)),
)

HISTORICAL_PROVENANCE_RE = re.compile(r"\bformer\s+`?research-talk`?\s+skill\s+was\s+merged\b", re.IGNORECASE)

DUPLICATE_POLICY_MARKERS: tuple[tuple[str, str], ...] = (
    (
        "2026-11-16 two-section synthesis heading duplicated outside obsidian-policy.md",
        "## 2. 실행된 배치 및 단건 기록 색인 (Evidence Index)",
    ),
    (
        "experiment 4-field enum list duplicated outside obsidian-policy.md",
        "`provenance_state`: `retained`, `partial`, `unverified`, `not-applicable`",
    ),
)


def read_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def emit_utf8(text: str) -> None:
    sys.stdout.buffer.write(text.encode("utf-8"))


def audit_skills_root(skills_root: Path, router_path: Path | None = None) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    codex_dir = skills_root / "codex"
    gemini_dir = skills_root / "gemini"
    policy_path = codex_dir / "obsidian-agent-record" / "references" / "obsidian-policy.md"

    if not policy_path.is_file():
        issues.append({"kind": "missing_policy", "path": str(policy_path), "line": 1, "detail": "obsidian-policy.md missing"})
        return issues

    policy_text = read_utf8(policy_path)

    if gemini_dir.is_dir():
        for entry in sorted(gemini_dir.iterdir()):
            if entry.name.startswith("."):
                continue
            if entry.is_symlink():
                if not entry.exists():
                    issues.append({
                        "kind": "broken_gemini_symlink",
                        "path": str(entry),
                        "line": 1,
                        "detail": "broken relative symlink in skills/gemini",
                    })
                continue
            if not entry.is_dir():
                continue
            gem_ud = entry / "references" / "user-decisions.md"
            cod_ud = codex_dir / entry.name / "references" / "user-decisions.md"
            if (
                gem_ud.is_file()
                and cod_ud.is_file()
                and not gem_ud.is_symlink()
                and read_utf8(gem_ud) != read_utf8(cod_ud)
            ):
                issues.append({
                    "kind": "user_decisions_divergence",
                    "path": str(cod_ud),
                    "line": 1,
                    "detail": f"diverges from {gem_ud}",
                })

    scan_files: list[Path] = sorted(codex_dir.glob("*/SKILL.md"))
    if gemini_dir.is_dir():
        scan_files.extend(
            p / "SKILL.md"
            for p in sorted(gemini_dir.iterdir())
            if p.is_dir() and not p.is_symlink() and (p / "SKILL.md").is_file()
        )
    if router_path and router_path.is_file():
        scan_files.append(router_path)

    for file_path in scan_files:
        lines = read_utf8(file_path).splitlines()
        for lineno, line in enumerate(lines, 1):
            for label, rx in RETIRED_PATTERNS:
                if rx.search(line):
                    if label == "retired skill 'research-talk'" and HISTORICAL_PROVENANCE_RE.search(line):
                        continue
                    issues.append({"kind": "retired_reference", "path": str(file_path), "line": lineno, "detail": label})
            for label, needle in DUPLICATE_POLICY_MARKERS:
                if needle in policy_text and needle in line:
                    issues.append({"kind": "duplicate_policy_rule", "path": str(file_path), "line": lineno, "detail": label})

    user_note_skill = codex_dir / "obsidian-user-note" / "SKILL.md"
    if user_note_skill.is_file():
        for lineno, line in enumerate(read_utf8(user_note_skill).splitlines(), 1):
            if 'knowledge_revise(action: "create", path: "Concepts/' in line and "updated" not in line:
                issues.append({
                    "kind": "missing_updated_field",
                    "path": str(user_note_skill),
                    "line": lineno,
                    "detail": "Concepts create YAML snippet omits 'updated' required by obsidian-policy.md section 5 (2026-11-15)",
                })

    return issues


def main(argv: list[str] | None = None) -> int:
    default_skills_root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skills-root", type=Path, default=default_skills_root)
    parser.add_argument("--router", type=Path, default=None, help="Optional research-router.md file to scan")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    args = parser.parse_args(argv)

    issues = audit_skills_root(args.skills_root, args.router)
    if args.json:
        emit_utf8(json.dumps({"ok": len(issues) == 0, "count": len(issues), "issues": issues}, ensure_ascii=False, indent=2) + "\n")
    else:
        for item in issues:
            emit_utf8(f"{item['path']}:{item['line']}: [{item['kind']}] {item['detail']}\n")
        if not issues:
            emit_utf8("OK: 0 policy-sync or retired-term issues.\n")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())

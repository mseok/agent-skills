#!/usr/bin/env python3
"""Pre-delivery structural and embed validator for single-paper-review Obsidian notes."""

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_ORDER = ("title", "created", "updated", "tags")
RETIRED_KEYS = {"categories", "projects", "review_status", "knowledge_state", "meeting_date", "related_notes", "source_host"}
VALID_ATTACHMENT = re.compile(r"^Attachments/[A-Za-z0-9._-]+--[0-9a-f]{12}\.(?:png|jpg|jpeg|webp|svg|pdf)$")
IMAGE_EMBED = re.compile(r"!\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
UNREPLACED_PLACEHOLDER = re.compile(r"<paper-slug>|<sha12>|\{\{(?:title|date)\}\}|\[Put the formula here\]|\[중요한 claim을")
CJK_OR_KANA = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]")


def check_note(text):
    errors = []
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return ["Missing YAML frontmatter block"], []
    fm = m.group(1)
    body = text[m.end():]
    keys = []
    fm_lines = fm.splitlines()
    for idx, ln in enumerate(fm_lines):
        km = re.match(r"^([A-Za-z0-9_-]+):(.*)$", ln)
        if km:
            key, rest = km.group(1), km.group(2).strip()
            keys.append(key)
            if key in RETIRED_KEYS:
                errors.append(f"frontmatter.{key}: retired key forbidden by obsidian-policy.md")
            # Flag scalar empty keys (not followed by indented list items)
            if rest == "" and key != "tags":
                next_ln = fm_lines[idx + 1] if idx + 1 < len(fm_lines) else ""
                if not re.match(r"^\s+-\s+", next_ln):
                    errors.append(f"frontmatter.{key}: empty field must be omitted rather than left blank")

    for req in REQUIRED_ORDER:
        if req not in keys:
            errors.append(f"frontmatter.{req}: required field missing")
    present_req = [k for k in keys if k in REQUIRED_ORDER]
    if present_req != [k for k in REQUIRED_ORDER if k in present_req]:
        errors.append(f"frontmatter order must begin with {list(REQUIRED_ORDER)} (got {present_req})")
    if "kind/paper-review" not in fm:
        errors.append("frontmatter.tags: missing kind/paper-review")

    for pm in UNREPLACED_PLACEHOLDER.finditer(text):
        errors.append(f"unreplaced template placeholder at L{text.count(chr(10), 0, pm.start()) + 1}: {pm.group(0)}")
    for cm in CJK_OR_KANA.finditer(body):
        errors.append(
            f"CJK/kana character forbidden by obsidian-policy.md at L{text.count(chr(10), 0, m.end() + cm.start()) + 1}: {cm.group(0)}"
        )

    embeds = []
    for em in IMAGE_EMBED.finditer(body):
        target = em.group(1).strip()
        embeds.append(target)
        if not VALID_ATTACHMENT.match(target):
            errors.append(
                f"invalid embed path '{target}': must use attachment_upload returned path "
                f"'Attachments/<stem>--<sha12>.<ext>' (no subfolders or guessed names)"
            )

    atlas = re.search(r"^##\s+본문 그림 모음\b(.*?)(?=^##\s+|\Z)", body, re.MULTILINE | re.DOTALL)
    if not atlas:
        errors.append("missing required '## 본문 그림 모음' section")
    else:
        figs = [int(n) for n in re.findall(r"^###\s+Figure\s+(\d+)\b", atlas.group(1), re.MULTILINE)]
        has_missing_note = bool(re.search(r"누락|생략|없음", atlas.group(1)))
        if not figs and not has_missing_note:
            errors.append("## 본문 그림 모음 contains no '### Figure N' entries")
        elif figs and figs != list(range(1, max(figs) + 1)) and not has_missing_note:
            errors.append(f"## 본문 그림 모음 Figure numbers are non-contiguous without missing-figure note: {figs}")

    return errors, sorted(set(embeds))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("note", type=Path)
    args = ap.parse_args()
    errors, embeds = check_note(args.note.read_text(encoding="utf-8"))
    print(json.dumps({
        "status": "fail" if errors else "ok",
        "errors": errors,
        "attachment_preview_paths": embeds,
    }, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

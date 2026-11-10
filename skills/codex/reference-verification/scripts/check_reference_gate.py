"""Check citation-review coverage and freshness; this is not an entailment judge."""

import argparse
import hashlib
import json
import re
from pathlib import Path

METADATA_FIELDS = ("title", "authors", "date", "venue", "volume", "issue", "pages", "identifier", "version")
FIELD_CLEAR = {"verified", "format_equivalent", "missing_optional", "not_applicable"}


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def active(text):
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in text.splitlines())


def bibliography_entries(text):
    entries = {}
    for match in re.finditer(r"@(\w+)\s*\{\s*([^,]+),", text):
        if match[1].lower() in {"comment", "preamble", "string"}:
            continue
        depth = 1
        end = match.end()
        while depth and end < len(text):
            if end == 0 or text[end - 1] != "\\":
                depth += (text[end] == "{") - (text[end] == "}")
            end += 1
        if depth:
            raise ValueError(f"Unclosed bibliography entry: {match[2]}")
        key = match[2].strip()
        if key in entries:
            raise ValueError(f"Duplicate bibliography key: {key}")
        entries[key] = digest(text[match.start():end])
    return entries


def inventory(source_root, roots):
    source_root = source_root.resolve()
    files, uses, entries, problems = {}, {}, {}, []
    bib_paths = set()

    def resolve(name, parent, suffix):
        name = name if Path(name).suffix else name + suffix
        for candidate in [source_root / name, parent / name]:
            path = candidate.resolve()
            if path.is_file() and path.is_relative_to(source_root):
                return path
        problems.append(f"Unresolved or out-of-root input: {name}")
        return None

    def walk(path, root_name, seen):
        if path in seen:
            return
        seen.add(path)
        relative = str(path.relative_to(source_root))
        raw = path.read_text()
        files[relative] = digest(raw)
        text = active(raw)
        lines = text.splitlines()
        if re.search(r"\[CITE(?:\s*:|\])", text):
            problems.append(f"Unresolved citation placeholder: {relative}")
        commands = set(re.findall(r"\\([A-Za-z]*cite[A-Za-z]*)", text, re.IGNORECASE))
        unsupported = sorted(command for command in commands
                             if (not command.startswith("cite") and command != "nocite") or command.endswith("cites"))
        if unsupported:
            problems.append(f"Citation commands need compiled-document review in {relative}: {', '.join(unsupported)}")
        pattern = r"\\(?:cite\w*|nocite)\*?\s*(?:\[[^\]]*\]\s*){0,2}\{([^}]+)\}"
        for ordinal, match in enumerate(re.finditer(pattern, text), 1):
            line = text[:match.start()].count("\n")
            start = end = line
            while start and lines[start - 1].strip():
                start -= 1
            while end + 1 < len(lines) and lines[end + 1].strip():
                end += 1
            keys = sorted(set(key.strip() for key in match[1].split(",")))
            if "*" in keys:
                problems.append(f"nocite wildcard needs explicit review: {relative}:{line + 1}")
                continue
            context = "\n".join(lines[start:end + 1])
            identifier = f"{root_name}:{relative}:{line + 1}:{ordinal}"
            uses[identifier] = {"file": relative, "line": line + 1, "keys": keys,
                                "context": context, "context_sha256": digest(context)}
        for match in re.finditer(r"\\(subfile|input|include|bibliography|addbibresource)\{([^}]+)\}", text):
            is_bib = match[1] in {"bibliography", "addbibresource"}
            for name in match[2].split(","):
                child = resolve(name.strip(), path.parent, ".bib" if is_bib else ".tex")
                if child is not None:
                    if is_bib:
                        bib_paths.add(child)
                    else:
                        walk(child, root_name, seen)

    for root_name in roots:
        root = resolve(root_name, source_root, ".tex")
        if root is not None:
            walk(root, root_name, set())
    for path in sorted(bib_paths):
        raw = path.read_text()
        files[str(path.relative_to(source_root))] = digest(raw)
        for key, entry_hash in bibliography_entries(raw).items():
            if key in entries:
                problems.append(f"Duplicate bibliography key across files: {key}")
            entries[key] = entry_hash
    cited = {key for use in uses.values() for key in use["keys"]}
    problems.extend(f"Missing bibliography key: {key}" for key in sorted(cited - entries.keys()))
    return {"snapshot_sha256": digest(json.dumps(files, sort_keys=True)), "files": files,
            "references": {key: {"entry_sha256": entries.get(key)} for key in sorted(cited)},
            "uses": uses, "unused_keys": sorted(entries.keys() - cited), "problems": problems}


def has_evidence(record):
    return bool(record.get("reason", "").strip() and record.get("evidence") and
                all(all(source.get(field) for field in ("url", "locator", "accessed"))
                    for source in record["evidence"]))


def check_review(current, review, mode="full"):
    failures = list(current["problems"])
    if review.get("snapshot_sha256") != current["snapshot_sha256"]:
        failures.append("Review is not bound to the current source snapshot")
    for kind in (("references", "uses") if mode == "full" else ("references",)):
        if set(review.get(kind, {})) != set(current[kind]):
            failures.append(f"Incomplete or extra {kind} in review")
    for key, expected in current["references"].items():
        record = review.get("references", {}).get(key, {})
        if record.get("entry_sha256") != expected["entry_sha256"] or not expected["entry_sha256"]:
            failures.append(f"{key}: bibliography review missing or stale")
        if record.get("metadata_status") != "verified" or not has_evidence(record):
            failures.append(f"{key}: metadata not cleared with evidence")
        for field in METADATA_FIELDS:
            decision = record.get("fields", {}).get(field, {})
            if decision.get("status") not in FIELD_CLEAR or not decision.get("reason"):
                failures.append(f"{key}/{field}: metadata field not cleared")
    if mode == "metadata":
        return failures
    allowed = {"supported", "background", "resource", "partial"}
    for identifier, expected in current["uses"].items():
        record = review.get("uses", {}).get(identifier, {})
        if record.get("context_sha256") != expected["context_sha256"]:
            failures.append(f"{identifier}: citation context review missing or stale")
        assessed = record.get("references", {})
        if set(assessed) != set(expected["keys"]):
            failures.append(f"{identifier}: incomplete citation-group review")
        for key in expected["keys"]:
            item = assessed.get(key, {})
            status = item.get("status")
            if status not in allowed or not has_evidence(item):
                failures.append(f"{identifier}/{key}: support not cleared with evidence")
            elif status == "partial" and item.get("disposition") not in {"covered_by_group", "authors_own_work"}:
                failures.append(f"{identifier}/{key}: partial support remains unresolved")
            elif status == "partial" and item.get("disposition") == "covered_by_group" and len(expected["keys"]) < 2:
                failures.append(f"{identifier}/{key}: grouped support requires another citation")
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--roots", nargs="+", required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--mode", choices=("metadata", "full"), required=True)
    args = parser.parse_args()
    current = inventory(args.source_root.resolve(), args.roots)
    args.inventory.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n")
    failures = check_review(current, json.loads(args.review.read_text()), args.mode) if args.review else current["problems"]
    result = {"status": "blocked" if failures else "clear" if args.review else "inventory_only",
              "mode": args.mode,
              "references": len(current["references"]), "citation_locations": len(current["uses"]),
              "reference_use_pairs": sum(len(use["keys"]) for use in current["uses"].values()),
              "snapshot_sha256": current["snapshot_sha256"], "failures": failures,
              "limit": "Checks coverage, source binding and recorded verdicts, not metadata accuracy or scientific truth. Metadata mode excludes citation-support clearance."}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())

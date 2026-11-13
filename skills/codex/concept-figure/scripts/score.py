#!/usr/bin/env python3
"""Score a rendered concept figure out of 100: 40 measured points from the render report, 60 judged points
(36 for clarity, 24 for beauty).

usage: score.py figure.report.json [--judgement judgement.json] [--label v03] [--ledger scores.jsonl]

The measured part needs only the report written by render.py. The judged part reads a judgement file written by
whoever looked at the figure with references/rubric.md: {"judge": "...", "scores": {"M1": 0-3, ...}, "notes": {...}}.
Prints both parts with the points lost per criterion, largest first, and appends one line to the ledger.
"""
import argparse
import datetime
import json
import pathlib
import sys

# criterion: (weight, short name); a criterion is scored 0-3 and is worth 3 * weight points (weights sum to 20)
JUDGED = {
    "M1": (2.0, "message in five seconds"), "M2": (1.5, "focal point and hierarchy"), "M3": (1.0, "concrete example carried through"),
    "M4": (0.5, "stands with its caption"),
    "E1": (1.25, "colour means something"), "E2": (0.75, "conventional shapes, one per meaning"), "E3": (1.0, "arrows unambiguous"),
    "C1": (1.25, "one reading path"), "C2": (1.5, "grouping and spacing"), "C3": (1.25, "proportion and balance"),
    "K1": (1.5, "line and arrow craft"), "K2": (1.5, "type craft"), "K3": (1.0, "finish"),
    "A1": (1.5, "palette harmony and restraint"), "A2": (1.5, "richness without clutter"), "A3": (1.0, "identity"),
}


def ramp(value, full, zero):
    """1 at `full`, 0 at `zero`, linear between (works in either direction)."""
    if full == zero:
        return 1.0
    return max(0.0, min(1.0, (value - zero) / (full - zero)))


def measured(report):
    m = report["metrics"]
    sizes = len(m["text_sizes"])
    rows = [
        ("checks", 6, 0.0 if report["errors"] else max(0.0, 1 - 0.25 * report["warnings"]), f"{report['errors']} errors, {report['warnings']} warnings"),
        ("alignment", 6, ramp(m["aligned_any"], 1.0, 0.75), f"{m['aligned_any']:.0%} of objects share an edge or centre line with another"
         + (f"; loose: {', '.join(m['unaligned'][:6])}" if m.get("unaligned") else "")),
        ("rhythm", 6, 0.6 * ramp(m["gap_cv"], 0.05, 0.6) + 0.4 * ramp(m["gap_sizes"], 5, 11), f"gap variation {m['gap_cv']:.2f}, {m['gap_sizes']} gap sizes"),
        ("white space", 5, ramp(m.get("slack", 0.35), 0.12, 0.35), f"{m.get('slack', float('nan')):.0%} of the drawn area is farther than 6 pt from anything drawn"),
        ("largest hole", 3, ramp(m["largest_empty"], 0.06, 0.18), f"largest empty rectangle {m['largest_empty']:.0%} of the drawn area"),
        ("balance", 3, ramp(max(abs(m["centroid_dx"]), abs(m["centroid_dy"])), 0.03, 0.12), f"centre of mass off by {m['centroid_dx']:+.1%} x, {m['centroid_dy']:+.1%} y"),
        ("text", 6, (ramp(report["min_text_pt"] or 0, 6, 5) + ramp(sizes, 4, 6) + ramp(report["words"], 60, 110)) / 3,
         f"minimum {report['min_text_pt']} pt, {sizes} sizes, {report['words']} words"),
        ("colour roles", 1, ramp(len(report["colour_roles"]), 4, 6), f"{len(report['colour_roles'])} roles"),
        ("wires", 4, 0.5 * ramp(m["wire_crossings"], 0, 2) + 0.5 * ramp(m["bends_per_wire"], 0.5, 1.5), f"{m['wire_crossings']} crossings, {m['bends_per_wire']:.2f} bends per wire"),
    ]
    return [(name, top, round(top * share, 1), note) for name, top, share, note in rows]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report")
    ap.add_argument("--judgement")
    ap.add_argument("--label")
    ap.add_argument("--ledger")
    args = ap.parse_args()
    path = pathlib.Path(args.report).resolve()
    report = json.loads(path.read_text(encoding="utf-8"))
    if "metrics" not in report:
        sys.exit("no metrics in the report: render it again with the current kit")
    rows = measured(report)
    got = sum(r[2] for r in rows)
    print(f"measured {got:.1f} / 40")
    for name, top, pts, note in sorted(rows, key=lambda r: r[2] - r[1]):
        print(f"  {pts:4.1f} / {top:<2d} {name}: {note}")
    entry = {"date": datetime.date.today().isoformat(), "figure": str(path), "label": args.label or path.parent.name,
             "measured": round(got, 1), "measured_parts": {r[0]: r[2] for r in rows}}
    receipt = path.with_name(path.name.replace(".report.json", ".inspection.md"))
    open_items = receipt.read_text(encoding="utf-8").count("- [ ]") if receipt.exists() else None
    entry["inspected"] = open_items == 0
    if open_items != 0:
        print("NOT INSPECTED: " + (f"{open_items} lines of {receipt.name} are unticked" if open_items else f"{receipt.name} is missing; render again")
              + ". View the preview and every tile first (references/inspection.md); a score without it is not a result to report.")
    if args.judgement:
        j = json.loads(pathlib.Path(args.judgement).read_text(encoding="utf-8"))
        scores = j["scores"]
        missing = sorted(set(JUDGED) - set(scores))
        if missing or any(scores[k] not in (0, 1, 2, 3) for k in JUDGED):
            sys.exit(f"judgement needs an integer 0-3 for every criterion; missing or invalid: {missing or 'values'}")
        judged = sum(JUDGED[k][0] * scores[k] for k in JUDGED)
        beauty = sum(JUDGED[k][0] * scores[k] for k in JUDGED if k[0] in "KA")
        print(f"judged {judged:.1f} / 60 (judge: {j.get('judge', 'unnamed')}): clarity {judged - beauty:.1f} / 36 (message, encoding, composition), "
              f"beauty {beauty:.1f} / 24 (craft, aesthetics)")
        for k in sorted(JUDGED, key=lambda k: JUDGED[k][0] * (scores[k] - 3)):
            lost = JUDGED[k][0] * (3 - scores[k])
            if lost:
                print(f"  -{lost:4.2f} {k} {JUDGED[k][1]} = {scores[k]}/3" + (f": {j.get('notes', {}).get(k)}" if j.get("notes", {}).get(k) else ""))
        print(f"total {got + judged:.1f} / 100")
        entry.update(judged=round(judged, 1), clarity=round(judged - beauty, 1), beauty=round(beauty, 1), total=round(got + judged, 1),
                     judge=j.get("judge"), scores=scores)
    ledger = pathlib.Path(args.ledger) if args.ledger else path.parent.parent / "scores.jsonl"
    with ledger.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"ledger: {ledger}")


if __name__ == "__main__":
    main()

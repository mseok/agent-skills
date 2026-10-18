#!/usr/bin/env python3
"""Mechanical checks for manuscript prose written with the paper-writing skill.

Reports report-register phrases, weakness signposts, summary labels, British
spellings, words to review in context, generic openers, non-English text,
undefined acronyms, layout and opening problems, sentence lengths and, with
--notes, numbers that do not occur in the source notes. Numbers repeated in the
Notes to author block are listed as declared computed values for review; the
checker does not verify the computation, nor any number's sign context, unit,
comparator or provenance. Proper names keep their own spelling; ignore British
spelling matches inside them. Exit status is 1 when report-register phrases,
weakness signposts, summary labels, British spellings (with --spelling us, the
default), non-English text or untraced numbers are found.
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPORT_REGISTER = [
    r"\bnot yet (?:been )?(?:confirmed|verified|tested|validated|evaluated|examined|explored|investigated|studied|checked|run)\b",
    r"\b(?:has|have|had) not yet been (?:confirmed|verified|tested|validated|checked|run|evaluated)\b",
    r"\b(?:has|have|had) not been (?:confirmed|verified|tested|validated|checked|run|evaluated) yet\b",
    r"\bremains? to be (?:verified|confirmed|tested|seen|determined|investigated|validated)\b",
    r"\b(?:is|are) still (?:under investigation|being \w+)\b",
    r"\b(?:analysis|evaluation|verification|validation|experiments?) (?:is|are) (?:in progress|pending|underway)\b",
    r"\b(?:needs?|requires?) (?:further |additional )?(?:verification|validation|testing|confirmation)\b",
    r"\b(?:further|additional) (?:analysis|analyses|experiments?|verification|testing) (?:is|are) (?:needed|required|necessary)\b",
    r"\bneeds? to be (?:checked|verified|confirmed|tested)\b",
    r"\bpreliminary (?:results?|experiments?|analys[ie]s|findings?)\b",
    r"\bwe plan to\b",
    r"\bwill be (?:explored|investigated|addressed|studied|examined) in (?:future|later) work\b",
    r"\bfuture work will\b",
    r"\bTBD\b",
    r"\bTODO\b",
    r"\(\?\)",
    r"\bwe first tried\b",
    r"\bafter (?:several|many|some|multiple) attempts\b",
    r"\bit turned out\b",
    r"\bwe then (?:checked|tried|ran|noticed)\b",
    r"\bwe noticed\b",
    r"\bit (?:was|is) (?:confirmed|judged|seen) that\b",
    r"\bit can be (?:seen|confirmed|observed) that\b",
    r"\bas requested\b",
    r"\bbelow,? we (?:summari[sz]e|report|describe|list)\b",
    r"\bthis section (?:reports|summari[sz]es|describes|presents)\b",
    r"\bit should be noted\b",
    r"\bit is worth (?:noting|mentioning)\b",
    r"\binterestingly\b",
    r"\bunfortunately\b",
    r"\balthough not perfect\b",
    r"\bonly slightly (?:worse|lower|higher|better)\b",
    r"\bdespite (?:its|these|the|our) limitations\b",
    r"\bmuch better\b",
    r"\ba lot\b",
    r"\bhuge\b",
    r"\b(?:may|might|could) (?:possibly|potentially|perhaps)\b",
    r"\bkey (?:finding|result|takeaway)s?:",
    r"(?<![\w,]\x20)\b(?-i:I) (?:think|believe|found|ran|used|tried)\b",
]

WEAK_SIGNPOST = [
    r"\b(?:two|three|four|several|some|other|the remaining|further) (?:further |other |remaining )?(?:results?|findings?|comparisons?|evaluations?|experiments?) (?:are|is|were|was) (?:weak|weaker|mixed|less favou?rable|negative(?! control)|disappointing|inconclusive)\b",
    r"\b(?:the )?(?:evidence|results?|picture|findings?) (?:is|are|was|were) (?:more )?(?:mixed|nuanced)\b",
    r"\b(?:the )?(?:gains|improvements?|benefits?|advantages?) (?:are|is|were|was) not (?:uniform|consistent)\b",
    r"\bnot all (?:results?|benchmarks?|tasks?|settings?) (?:are|were|show)\b",
]

SUMMARY_LABEL = re.compile(
    r"^[ \t>]*(?:\*\*|__)?(?:Summary|In summary|To summari[sz]e|Takeaways?|Key (?:findings?|results?|takeaways?)|"
    r"What (?:the|this|our) (?:comparison|results?|evidence|experiments?|data|analysis) (?:supports?|shows?|establish(?:es)?))"
    r"(?:\*\*|__)?\s*[.:,]|^[ \t>]*\*\*(?:Summary|Takeaways?|Key findings?) of [^*\n]{1,60}\*\*|"
    r"(?:(?<=[.!?] )|^)(?:In (?:summary|conclusion)|To (?:conclude|summari[sz]e)),|^#+\s*(?:Summary|Takeaways?|Key findings)\b[^\n]*$",
    re.M | re.I,
)

BRITISH = [
    r"\b(?:un|re|de|mis|non|pre|sub)?(?:organ|optim|normal|recogn|summar|minim|maxim|parallel|discret|token|general|initial|character|regular|"
    r"parameter|parametr|util|emphas|real|special|standard|visual|local|stabil|synthes|hypothes|priorit|categor|"
    r"vector|central|final|random|serial|custom|author|apolog|critic|memor|capital|polar|linear|penal|familiar|"
    r"neutral|quant|marginal|personal|modern|symbol|harmon|equal|mobil|global|individual|conceptual|contextual|"
    r"operational|formal|digit|theor|crystall|ion|magnet|vapor|mechan|homogen|amort|fertil|steril|factor|binar|symmetr|sanit|raster|scrutin|revolution)"
    r"is(?:e|es|ed|ing|ation|ations|ational|er|ers|able|ability)\b",
    r"\b(?:catalys|paralys|analys(?=e|ed|ing|er))(?:e|ed|ing|er|ers)\b",
    r"\b(?:un|re|de|mis|non|pre|sub)?(?:behaviour|colour|favour|flavour|honour|labour|neighbour|rumour|vapour|harbour|humour|"
    r"endeavour|odour|armour|vigour|rigour|tumour|fervour|candour|splendour)"
    r"(?:s|ed|ing|ite|ites|able|ably|al|ally|less|hood|hoods|ful|bar|map)?\b",
    r"\b(?:un|re|de|mis|non|pre|sub)?(?:model|label|travel|cancel|signal|fuel|level|tunnel|channel|total|counsel|marshal|dial|equal|rival|"
    r"spiral|jewel|pencil|parcel|quarrel)l(?:ed|ing|er|ers)\b",
    r"\b(?:kilo|milli|centi|micro|nano)?(?:centre|centres|centred|centring|fibre|fibres|litre|litres|metre|metres|calibre|lustre|spectre|theatre)\b",
    r"\b(?:judgement|judgements|defence|defences|licence|grey|greyscale|programme|programmes|catalogue|catalogues|"
    r"analogue|whilst|amongst|artefacts?|aluminium|sulphur|ageing|acknowledgement|fulfil|fulfilment|skilful|learnt|caesium|practised?|offences?)\b",
]

OPENING_HEDGE = re.compile(r"\b(?:sometimes|often|occasionally|frequently|usually|typically|generally|commonly|"
                           r"in (?:many|some|most) cases)\b", re.I)
RUN_IN_LABEL = re.compile(r"^[ \t>]*(?:\*\*[^*\n]{2,80}?(?:[.:]\*\*|\*\*[.:])|\\paragraph\*?\{)", re.M)
FIGURE_IN_HEADING = re.compile(r"^(?:#+|\\(?:sub)*section\*?\{)[^\n]*\b(?:Fig(?:ure)?s?\.?|Tables?)\s*~?(?:\d|\\ref)", re.M)

# Report register only when they describe the state of the authors' own work.
CONTEXTUAL = [
    r"\bcurrently\b",
    r"\bto date\b",
    r"\bso far\b",
    r"\bat present\b",
    r"\bat this stage\b",
    r"\bfor now\b",
    r"\bongoing\b",
    r"\bnote that\b",
    r"\bshows? no such (?:advantage|gain|improvement|benefit)\b",
    r"\b(?:has|have|had) not been (?:confirmed|verified|tested|validated|checked|run|evaluated)\b",
    r"\b(?:is|are) still (?:unclear|unknown)\b",
    r"\binitial experiments?\b",
    r"[→⇒]",
    r"\b(?:statistically significant|significantly (?:higher|lower|better|worse|improved|reduced|outperforms?))\b",
]

GENERIC = [
    r"\bin recent years\b",
    r"\bover the (?:past|last) (?:few )?(?:years|decades?)\b",
    r"\b(?:has|have) (?:attracted|received|gained|drawn) (?:increasing|growing|considerable|significant|much|wide|widespread) (?:attention|interest)\b",
    r"\bplays? an? (?:crucial|important|vital|key|pivotal|central|essential) role\b",
    r"\bwith the (?:rapid )?(?:development|advancement|advent|rise) of\b",
    r"\bwide range of applications\b",
    r"\b(?:hot|active) (?:topic|research area)\b",
    r"\bnovel\b",
    r"\bstate-of-the-art\b",
    r"\bpaves? the way\b",
    r"\bsheds? (?:new )?light\b",
    r"\bextensive experiments\b",
    r"\bsuperior performance\b",
    r"\bremarkabl[ey]\b",
    r"\bunprecedented\b",
    r"\bdramatic(?:ally)?\b",
]

HANGUL = re.compile(r"[ㄱ-ㆎ가-힣]")
ACRONYM = re.compile(r"\b(?=[A-Z0-9]*[A-Z][A-Z0-9]*[A-Z])[A-Z][A-Z0-9]+s?\b")
ACRONYM_ALLOW = {
    "GPU", "GPUs", "CPU", "CPUs", "RAM", "API", "URL", "PDF", "ID", "IDs",
    "II", "III", "IV", "VI", "VII", "TODO", "TBD", "CITE", "AUTHOR", "USA", "UK", "EU",
}
REFERENCE = re.compile(
    r"(?:Supplementary|Extended Data)?\s*(?:Fig(?:ure)?s?\.?|Tables?|Tab\.|Eqs?\.?|Equations?|Sections?|Sec\.|"
    r"Notes?|Appendix|Algorithm|Alg\.)\s*~?\(?S?\d+(?:\.\d+)*[a-z]?\)?(?:\s*(?:[–-]|to)\s*\(?S?\d+(?:\.\d+)*[a-z]?\)?)?"
)
CITATION = re.compile(r"\[[\d,\s–-]+\]|\\(?:cite[tp]?|ref|eqref|label|tag)\{[^}]*\}|\[(?:CITE|AUTHOR):[^\]]*\]")
NUMBER = re.compile(r"(?<![\w.])[-−+]?(?:\d{1,3}(?:,\d{3})+(?!\d|,\d)(?:\.\d+)?|\d+(?:\.\d+)?|\.\d+)(?:[eE][-−+]?\d+)?")
THOUSANDS = re.compile(r"(?<=\d)(?:\{,\}|\\,|\u2009|\u202f)(?=\d{3})")
ABBREV = re.compile(r"\b(?:e\.g|i\.e|et al|vs|Fig|Figs|Eq|Eqs|Sec|Tab|Ref|Refs|approx|cf)\.", re.I)
NOTES_HEADING = re.compile(r"^-{3,}\s*\n+\s*#*\s*\**(?:Notes to author|저자\s*메모|저자에게)", re.M | re.I)


def split_notes_to_author(text):
    """Return (manuscript, notes_to_author) split at the Notes to author block."""
    m = NOTES_HEADING.search(text)
    return (text[: m.start()], text[m.start():]) if m else (text, "")


def prose_lines(text):
    """Yield prose lines, skipping headings, tables and display math (for sentence statistics)."""
    in_math = False
    for line in text.splitlines():
        s = line.strip().lstrip("> ").strip()
        if in_math:
            if s.endswith("$$") or s.startswith("\\end{"):
                in_math = False
            continue
        if s.startswith("$$"):
            in_math = not (len(s) > 2 and s.endswith("$$"))
            continue
        if s.startswith("\\begin{equation") or s.startswith("\\begin{align"):
            in_math = True
            continue
        if not s or s.startswith(("#", "|", "%")):
            continue
        yield line


def to_float(token):
    try:
        return float(token.replace(",", "").replace("−", "-").lstrip("+"))
    except ValueError:
        return None


def numbers_in(text):
    return {v for v in (to_float(t) for t in NUMBER.findall(THOUSANDS.sub("", text))) if v is not None}


def find_all(patterns, text):
    hits = []
    for pat in patterns:
        for m in re.finditer(pat.replace(" ", r"\s+"), text, re.I):
            hits.append({"line": text.count("\n", 0, m.start()) + 1, "match": " ".join(m.group(0).split())})
    return sorted(hits, key=lambda h: h["line"])


def find_british(text):
    """Return (hits, name_hits); a capitalized match inside a sentence is a possible proper name."""
    hits, names = [], []
    for pat in BRITISH:
        for m in re.finditer(pat, text, re.I):
            word = m.group(0)
            before = text[max(0, m.start() - 3):m.start()]
            line_start = text.rfind("\n", 0, m.start()) + 1
            mid_sentence = text[line_start:m.start()].strip(" #*|->") and not re.search(r"[.!?:]\W*$", before)
            hit = {"line": text.count("\n", 0, m.start()) + 1, "match": word}
            (names if word[0].isupper() and mid_sentence else hits).append(hit)
    return sorted(hits, key=lambda h: h["line"]), sorted(names, key=lambda h: h["line"])


def first_paragraph(body):
    for block in re.split(r"\n\s*\n", body):
        lines = [ln for ln in prose_lines(block)
                 if not re.match(r"\s*(?:\\(?:sub)*section\*?\{[^}]*\}|\*\*[^*]+\*\*)\s*$", ln)]
        if lines:
            return " ".join(s.strip() for s in lines)
    return ""


def opening_issues(body):
    para = first_paragraph(body)
    first = re.split(r"(?<=[.!?])\s+(?=[A-Z])", ABBREV.sub(lambda m: m.group(0)[:-1], para), maxsplit=1)[0] if para else ""
    issues = []
    for m in OPENING_HEDGE.finditer(first):
        issues.append({"issue": "frequency hedge in the first sentence", "match": m.group(0)})
    for m in re.finditer(r"\$[^$]+\$|\\\(.+?\\\)|\b[A-Z][0-9]\b|[₀-₉α-ωΑ-Ω]", para):
        issues.append({"issue": "notation in the first paragraph", "match": m.group(0)[:40]})
    return issues


def check(draft, notes=None, section=None, spelling="us"):
    body, author_notes = split_notes_to_author(draft)
    british, british_names = find_british(body)
    report = {
        "report_register": find_all(REPORT_REGISTER, body),
        "weak_signpost": find_all(WEAK_SIGNPOST, body),
        "summary_label": [{"line": body.count("\n", 0, m.start()) + 1, "match": " ".join(m.group(0).split())}
                          for m in SUMMARY_LABEL.finditer(body)],
        "british_spelling": british if spelling == "us" else [],
        "opening": opening_issues(body) if section == "intro" else [],
        "review_layout": [{"line": body.count("\n", 0, m.start()) + 1, "match": m.group(0).strip()[:60]}
                          for pat in (RUN_IN_LABEL, FIGURE_IN_HEADING) for m in pat.finditer(body)],
        "review_in_context": find_all(CONTEXTUAL, body) + (
            [{"line": h["line"], "match": h["match"] + " (proper name?)"} for h in british_names] if spelling == "us" else []),
        "generic": find_all(GENERIC, body),
        "non_english": [{"line": n, "text": line.strip()[:80]}
                        for n, line in enumerate(body.splitlines(), 1) if HANGUL.search(line)],
        "undefined_acronyms": [], "untraced_numbers": [], "untraced_small_integers": [],
        "declared_computed": [], "sentences": {},
    }

    prose = "\n".join(prose_lines(body))
    plain = re.sub(r"\$[^$]*\$", " ", CITATION.sub(" ", prose))
    seen = set()
    for m in ACRONYM.finditer(plain):
        acr = m.group(0)
        base = acr[:-1] if acr.endswith("s") and acr[:-1].isupper() else acr
        if base in seen or acr in ACRONYM_ALLOW or base in ACRONYM_ALLOW:
            continue
        seen.add(base)
        if plain[max(0, m.start() - 1): m.start()] != "(":
            report["undefined_acronyms"].append(acr)

    if notes is not None:
        known = numbers_in(notes)
        declared = numbers_in(author_notes)
        for tok in NUMBER.findall(THOUSANDS.sub("", CITATION.sub(" ", REFERENCE.sub(" ", re.sub(r"(?m)^(#+[ \t]*)\d+(?:\.\d+)*\.?[ \t]", r"\1", body))))):
            v = to_float(tok)
            if v is None or v in known:
                continue
            if v in declared:
                bucket = "declared_computed"
            elif v.is_integer() and abs(v) <= 10:
                bucket = "untraced_small_integers"
            else:
                bucket = "untraced_numbers"
            if tok not in report[bucket]:
                report[bucket].append(tok)

    text = re.sub(r"\$[^$]*\$", "X", ABBREV.sub(lambda m: m.group(0)[:-1], prose))
    chunks = re.split(r"\n[ \t>]*(?:[-*+]|\d+\.)[ \t]+", text)
    sentences = [s for c in chunks for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(\[\\])", re.sub(r"\s+", " ", c))
                 if len(s.split()) > 2]
    lengths = [len(s.split()) for s in sentences]
    report["sentences"] = {
        "count": len(lengths),
        "mean_words": round(sum(lengths) / len(lengths), 1) if lengths else 0,
        "max_words": max(lengths) if lengths else 0,
        "over_40": [s[:90] for s, k in zip(sentences, lengths) if k > 40],
    }
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("draft", type=Path)
    ap.add_argument("--notes", type=Path, help="source notes for number tracing")
    ap.add_argument("--section", choices=("intro", "methods", "results", "other"), help="enables opening checks for intro")
    ap.add_argument("--spelling", choices=("us", "uk"), default="us", help="us (default) flags British spellings")
    ap.add_argument("--json", action="store_true", help="print the report as JSON")
    args = ap.parse_args()

    try:
        notes = args.notes.read_text(encoding="utf-8") if args.notes else None
        draft = args.draft.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        ap.error(str(exc))
    report = check(draft, notes, args.section, args.spelling)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
    else:
        print(f"== {args.draft} ==")
        for key in ("report_register", "weak_signpost", "summary_label", "british_spelling", "review_in_context",
                    "review_layout", "generic", "non_english"):
            print(f"{key}: {len(report[key])}")
            for hit in report[key]:
                print(f"  L{hit['line']}: {hit.get('match') or hit.get('text')}")
        if report["opening"]:
            print(f"opening (review): {len(report['opening'])}")
            for hit in report["opening"]:
                print(f"  {hit['issue']}: {hit['match']}")
        print(f"undefined_acronyms: {report['undefined_acronyms']}")
        if notes is not None:
            print(f"untraced_numbers: {report['untraced_numbers']}")
            print(f"untraced_small_integers (review): {report['untraced_small_integers']}")
            print(f"declared_computed (verify each computation): {report['declared_computed']}")
        s = report["sentences"]
        print(f"sentences: n={s['count']} mean={s['mean_words']} max={s['max_words']} over_40={len(s['over_40'])}")
        for sent in s["over_40"]:
            print(f"  >40: {sent}")

    failed = any(report[k] for k in ("report_register", "weak_signpost", "summary_label", "british_spelling",
                                     "non_english", "untraced_numbers"))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

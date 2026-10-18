---
name: paper-field-map
description: Learn a new paper field or answer a comparison question from the literature by turning one question into evidence cards, a big-picture map and a reading queue of 8-10 papers. Use for literature surveys, novelty or precedent checks, related work, 논문 조사, 선행연구, 문헌 정리, or whenever several papers must be found, read and compared; novelty claims stay unverified until the precedent check returns. The parent never reads bio-adjacent papers itself (bio-safe-reading). Not for a single paper summary (single-paper-review).
---

# Question to map to reading queue

Goal: the user reads 8-10 papers in full, chosen because they directly support the
question, with every other paper reduced to a verified card. Reuse an existing field
folder when one exists (look for `README.md`, `READING_QUEUE.md`, `papers/`).

## 1. Fix the question and tracks

- State one comparison question and its factor of interest (e.g. single sequence vs MSA).
  Split into 2-4 tracks that have different benchmarks (e.g. variant effect, contact, folding).
- Ask the user only for choices that change scope (which tracks, depth of reading).
  Do not use a large unfiltered citation corpus as the basis for the reading list.
- Check the Obsidian vault first through `obsidian_main` (`knowledge_search`, `investigation_context`).
  Reuse a matching question report; create one with `research-workflow` only for a distinct question.

## 2. Build cards, one agent per track (parallel, background)

Copy `CARD_TEMPLATE.md` to `<field>/papers/` and give each track agent: the question, the track,
the template, the work folder, papers already established, and these rules:

- Download the PDF (`curl -L` to `/tmp/<field>/`), run `pdftotext -layout`, read tables yourself.
  WebFetch cannot read PDF bodies. Never fill numbers from memory or snippets; mark
  "abstract only" or "not obtained" and leave numbers blank.
- Quote numbers exactly with table/figure/page, metric direction, n, cohort and depth definition.
- Matched means one factor varied. Say what else differs (parameters, data, ensemble, templates,
  architecture, evaluator, denominator). Mark preprint vs peer-reviewed. Mark figure-read values.
- Cap about 16 cards per track. Finish with: cards and one-line verdicts, 3-5 must-read papers, what could not be verified.

## 3. Verify before synthesizing

- Agents' reports are claims. Spot-check the numbers the conclusion rests on against the extracted
  text (`grep` the table row), at least the cleanest single-factor comparisons.
- Look for contradictions between cards (for example, a depth effect not matching a taxon effect)
  and record them as open issues instead of resolving them by assumption.
- Do not merge numbers across papers whose cohorts, benchmark versions or depth definitions differ.

## 4. Write the map and the queue

In the field folder:

- `README.md`: one-paragraph conclusion; a table per track with where the weakness is confirmed,
  where it is closed or uncertain, the cleanest evidence, and comparability; interpretive judgments;
  open issues; what could not be verified and which numbers were or were not cross-checked.
- `READING_QUEUE.md`: 8-10 papers in reading order with the exact sections to read, what each gives,
  an optional list, a skip list with reasons, and the unanswered questions.
- `scripts/build_index.py` (copy from this skill) regenerates `papers/INDEX.md` from the cards.

Keep observation, assumption, proposal and adopted decision distinct. Do not present a non-matched
comparison as a performance comparison.

## 5. Record and keep it reusable

- Record the milestone with `research-workflow` (`research_capture`) in the question's report.
- When the user reads a paper and corrects a card, edit the card, rebuild the index and update
  `README.md` and the queue. A new paper joins by adding a card, not by rewriting the map.
- Update the field folder's pointer in project memory if one exists.

## 6. Research questions from a map (2026-10-17 audit)

Before an ideation fan-out, ask one question that fixes the bar (for example a top-venue question, or quick analyses on existing data) and the core question the ideas must answer; a budget instruction such as "max effort" covers cost, not framing. Novelty claims stay unverified until the precedent check returns, and no candidate is called oral-level before it.

---
name: benchmark-comparison
description: Set up, re-aggregate or audit a benchmark comparison between models, methods, checkpoints or settings before any number is reported or plotted. Use when the user asks to compare, re-evaluate, aggregate, bootstrap, rank, rebuild a results table or figure, or check reproducibility (비교, 재평가, 집계, 벤치마크, 성능표, 재현). Not for a single run's status or for manuscript prose.
---

# Benchmark comparison

A comparison is only as good as its matched conditions. Most user corrections in this area were about population, selection rule, evaluator version and aggregation, not about arithmetic.

## 1. Pin the basis before computing

Read the project's facts file (`PROJECT_FACTS.md` or the task-state `decisions`) and write the comparison basis as a table in the working folder before running anything:

| item | value | source |
|---|---|---|
| factor of interest | one factor | user request |
| population and splits | exact ID list or manifest path per cell, with count | manifest file |
| checkpoints and model aliases | name, path, date | facts file |
| evaluator and version | tool, version, settings | facts file |
| budget and seeds | candidates per target, seed pairing, sampling budget | facts file |
| selection rule | confidence-selected, oracle, best-of-N, first | per method |
| metric and direction | name, higher or lower is better, denominator | facts file |
| missingness | drop, impute, report separately | user decision |

If any row is unknown, ask once with a recommendation; do not fill it from memory. If the facts file does not exist, create it from the answers and record it in the task state so the next thread reads it.

## 2. Compute with receipts

- Derive membership from the manifest; never hardcode a historical count. Report the population of every cell (n per method per subset) in a denominator table next to the results.
- Recompute every reported number from raw outputs per the benchmark's own evaluation definition; label each table and figure with checkpoint, evaluator version, cohort size and selection rule. Report primary endpoints before favorable secondary metrics; numbers copied from chat, Slack, slides or older figures appear only in panels labelled provisional.
- Preserve source, run, metric direction, numerator, denominator and the dependency unit through every aggregation.
- Keep data, selection or aggregation, evaluator and cohort as separate axes; changing one is a different experiment and gets its own row, never a silent switch.
- Label oracle or best-of-N selections in the table and legend, and never under the bare model name beside confidence-selected baselines. When asked to look for alternative metrics or subsets, keep the full list of variants tried and report the one adopted with the rest.
- Seed subsets and bootstraps use the same seed pairing across methods; state the unit of every count (targets, seed combinations, complexes).
- Input preparation follows each model's official pipeline; cite the code read, not the documentation summary.

## 3. Verify before reporting

- Spot-check at least two cells against raw outputs (the score file, not the aggregated CSV).
- Compare against the previously reported numbers for the same cell and explain every difference by one of the axes above.
- A result that differs from the manuscript or a prior figure is a finding to flag in the first line, not to absorb quietly.
- Write a short verification receipt (basis table, denominator table, spot checks, differences explained) beside the outputs; a figure or table rebuild ships with that receipt and the exact data version.

## 4. Deliver

Draft the table or figure in the working folder with a versioned name; show it inline; apply to a manuscript or shared deck only on explicit instruction (`paper-writing`, `nature-figure`). Record the comparison as a milestone with `research-workflow` when it changes a judgment, and as an `experiment-ledger` entry when it is a terminal comparable result.

## Verified additions (2026-10-17 audit)

- Basis table rows to add: `authoritative reference` (the latest collaborator-posted table, figure or method note for this benchmark, with date and where it was posted) and `analysis parameters` (value and why: tool default, literature, or a convergence check with n). Settle factual rows (which inputs, seeds and variants exist per dataset and how they correspond) from the files first, then ask the remaining choices in one round.
- In a data × method 2×2, fix the population on the new-data × new-method cell unless the user says otherwise; "old" means the published numbers. The manifest marks exactly one cohort per benchmark as current; superseded cohorts appear only in the provenance document. When a population shrinks, report what was removed (counts, IDs) separately from why; the why needs a cited message, commit or document, otherwise say it is unknown.
- Selection rules state a deterministic tie-break (seed, then sample index), never file or completion order. If the user still asks for a bare model name on an oracle or best-of-N result, state the mismatch once, comply, and keep the selection rule in every exported caption and legend.
- Before saying prepared inputs match a model's official handling, run that model's installed loader or featurizer on every prepared input and compare its output with the intended features; until then the match is unverified. Input preparation for a comparison (입력 준비, benchmark inputs) is in scope of this skill.
- Reproduce the latest collaborator-posted numbers for the same benchmark before calling any text manuscript-ready; until they match or each difference is explained, label the text provisional. Trace at least two selected rows to the evaluator's native per-item output and confirm the value belongs to the intended entity and reference copy ("reproduces the stored table" is not validation). Before calling something a defect, search captions, READMEs and the SI for a documented exception.
- When proposing a new or redefined metric, state whether it implies or is implied by an existing one and which claim it cannot support before showing rankings on it.

## Found defects (2026-10-17 audit)

When you find a defect in scoring, extraction or aggregation code, write it to the project facts file in the same turn with the affected tables, list the delivered work built on them (manuscript text, figures, handoffs to colleagues) and ask one yes/no question about auditing that work; a "rest not checked" caveat is not a finding.

---
name: experiment-ledger
description: Preserve a separately comparable terminal research result and connect it to its question report through obsidian_main. Use for durable experiments whose outcomes will be compared, cited or used for decisions; routine polling, short checks and disposable debugging stay in the source task.
---

# Retain the experiment and its meaning

Read the [Obsidian vault policy](../obsidian-agent-record/references/obsidian-policy.md) once
per task before using this workflow; reuse it if already loaded. All vault and
recording rules live there; this skill holds the procedure.

Keep hypotheses and consequential choices in the question report using
`research-workflow` via `obsidian_main` (`migrated-settings_obsidian_main` in
Antigravity). Planned/running job state stays in the execution system; an
important decision about such a job may still be a question milestone.

Before a durable experiment, state its purpose, comparison and the decision it
will change. Run from committed source in the current checkout: commit the files
you changed for the run, by path, before launch (AGENTS.md, Environment and tools;
a local commit needs no request, a push always does). Record `HEAD`
only with a clean tracked index/tree and no execution-affecting untracked file.
Preserve unrelated changes; never reset, stash, push or make a worktree just
to satisfy bookkeeping, and never commit changes that are not yours: a tree still
dirty from them is recorded as the source with its diff hash. Ask about unrelated
changes only when they actually block launch.

Retain the exact code revision, execution-affecting config, data/checkpoint
identity, launch method, measured comparison population and output location.
Use W&B/job/step identifiers when they help recover or compare the result. Keep
large data and detailed environment/config artifacts in their proper stores;
host-local paths must name the execution host and access state. Add concise
pseudocode bound to the source revision when a changed algorithm matters.

At `completed`, `failed`, `inconclusive` or `cancelled`, inspect actual results
before interpreting them. Use `investigation_context` and search the retained
run/artifact identity for an existing result. `record_create` accepts a stable
`evidence_key` (run/artifact plus comparison/analysis scope), `investigation_id`
and exact `source_refs`. Reuse the same key across servers/tasks; a new run or
independently comparable analysis gets a distinct key.

Follow policy §7's batch and evidence rules: write one record and one
`evidence_key` per batch, sweep or screening round (with a table or an
`attachment_upload` file, never one record per item), link any `Writing/` or
`Notes/` user note that builds on the run, and preserve primary null findings
alongside exploratory signals while distinguishing failure boundaries from
unmeasured endpoints. Lead with what was learned, the observed result, its
interpretation and the current choice. Supply canonical `project`/`tags` (`kind/experiment`),
the four flat terminal-experiment fields (`experiment_status`,
`provenance_state`, `evidence_access`, `claim_state`) and any `superseded_by`
link as defined in policy §5 (never on synthesis/strategy notes or in bulk on
legacy notes).

Finally call `research_capture` with the result note's `evidence_paths` and
`report_patch` to add the run to the question report's policy §7 evidence-index
table. Subsequent interpretation changes are dated milestones in that report;
use gateway revision/history tools (policy §2) for authorized corrections and
retain failed deliveries in the external outbox (`obsidian-research`, policy §7)
without direct vault file or Git fallbacks.

## User decisions

The dated decisions behind these rules, in the user's own words, are in [references/user-decisions.md](references/user-decisions.md). Read it before editing this skill or when a rule's origin or scope is in doubt; record a new decision there and state the resulting rule in plain words in this file.

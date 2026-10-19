---
name: experiment-ledger
description: Preserve a separately comparable terminal research result and connect it to its question report through obsidian_main. Use for durable experiments whose outcomes will be compared, cited or used for decisions; routine polling, short checks and disposable debugging stay in the source task.
---

# Retain the experiment and its meaning

Read the [shared recording policy](../research-workflow/references/research-recording.md) once
per task before using this workflow; reuse it if already loaded. Detailed
recording rules live there rather than in every project's AGENTS.md.

Keep hypotheses and consequential choices in the question report using
`research-workflow`. Planned/running job state stays in the execution system;
an important decision about such a job may still be a question milestone.

Before a durable experiment, state its purpose, comparison and the decision it
will change. Run from committed source in the current checkout. Record `HEAD`
only with a clean tracked index/tree and no execution-affecting untracked file.
Preserve unrelated changes; never reset, stash, commit, push or make a worktree just
to satisfy bookkeeping: a dirty tree is recorded as the source with its diff hash,
and committing happens only when the user asks. Ask about unrelated changes only
when they actually block launch.

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

For `kind/experiment`, supply canonical project/tags and four flat fields:

- `experiment_status`: actual terminal state.
- `provenance_state`: `retained`, `partial`, `unverified`, `not-applicable`.
- `evidence_access`: `durable`, `local-only`, `mixed`, `unknown`.
- `claim_state`: `current`, `bounded`, `superseded`, `inconclusive`.

`superseded_by` is only for an exact later note that changes the claim. Do not
bulk-add experiment fields to unrelated legacy notes. A synthesis or proposed
training strategy is a report/decision, not a completed training experiment.

Lead with what was learned and its implication. Explain the observed result,
interpretation and current choice; preserve primary null findings alongside
exploratory signals. Missing provenance is a recovery issue, not automatic
scientific inconclusiveness. Mention a missing field only when it matters to
reproduction or the next judgment. Do not demand exhaustive ablations to retain
a useful working assumption. A run that never reached the relevant measurement
can establish a failure boundary, but cannot supply that measurement.

Finally call `research_capture` with the result note's `evidence_paths` to
update the cumulative question report. Subsequent interpretation changes are
dated milestones in that report. Use the gateway's revision/history facilities
for authorized corrections. On delivery failure, retain the external outbox
and resume later; never write a scratch vault file or use Git as a fallback.

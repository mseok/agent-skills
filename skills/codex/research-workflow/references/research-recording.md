<!-- BEGIN obsidian-research (managed by obsidian-main/scripts/deploy-research.py) -->
## Research continuity through Obsidian

For research work, use `research-workflow` automatically at a meaningful
hypothesis, implementation, result interpretation, adopted decision, or change
of direction. Keep one cumulative report per question across local, messi and
gpu22. Read `investigation_context` once per task, which returns the synthesis
and recent events, and reuse each capture receipt's `sha256` afterwards; use
`research_capture` with `report_patch` for the sections that changed to retain
the milestone, original source identifiers and dated judgment history.
Do not ask permission again for ordinary research milestones covered by this
policy. Routine coding, polling and unsettled chat do not each earn a note.

Lead with the current judgment and next action. Explain why the question
matters, the hypothesis, core method, observed result and interpretation.
Separate observation, working assumption, proposal and adopted decision.
Converging circumstantial evidence can justify a bounded working assumption.
State only limitations that change the decision; missing provenance is a
separate recovery issue, not a blanket reason to dismiss the scientific result.
Never invent the original hypothesis or turn an agent proposal into a
user-adopted decision. Preserve user corrections and dates of changed
interpretations. Add ablations when they could change the next decision.

Write records, report bodies and judgment summaries in Korean or English only,
in complete sentences with normal spacing. Never compress prose by dropping
spaces or by switching to Japanese or Chinese characters.

Use `experiment-ledger` for separately comparable terminal results. Source
code, launch configuration, run tracking and large artifacts stay in their
proper stores; retain exact, host-qualified recovery locators in the record.
Use an `evidence_key` for the same run/artifact/comparison, and reuse an existing
result from another task. A new interpretation is a new milestone in the same
question, not a second copy of the experiment.

All vault access uses the host-local `obsidian_main` bridge and Mac mini
single-writer gateway. `knowledge_revise` preserves the same path and prior
versions with an expected SHA. Registered question reports are shared; human
notes and other-host legacy records need an explicitly scoped local maintenance
run. Keep record identity and original creation date; revision authorship is
recorded separately. Never write vault files, publish branches, use `un note`,
or synchronize vault Git. Mac mini Git remains backup-only. Attachments use
raw-byte uploads from approved files.

Pass the hook context's session and turn IDs as `session_id` and `turn_id` in
every `research_capture`. When the Stop hook asks for the end-of-turn check and
no milestone was captured, mark `no-material-change` with the host-local MCP
`research_disposition` tool and those IDs; the hook asks only for turns long
enough for research work and at most once per interval per session. This check
needs no vault note or shell write approval. Failed delivery stays
in the host-local outbox outside the vault. On resume, inspect/replay pending
requests; a SHA conflict needs a fresh read and a new request, never a forced
overwrite. Recording failures must not block a scientific job.
<!-- END obsidian-research -->

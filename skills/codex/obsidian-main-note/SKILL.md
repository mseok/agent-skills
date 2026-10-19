---
name: obsidian-main-note
description: Save a reusable project outcome or an explicitly requested note through the canonical Obsidian gateway. For ongoing research milestones use research-workflow to update the question report; use this skill for independently reusable records and authorized existing-note revisions.
---

# Save a useful outcome

Read the [shared recording policy](../research-workflow/references/research-recording.md) once
per task before using this workflow; reuse it if already loaded. Detailed
recording rules live there rather than in every project's AGENTS.md.

Use `obsidian_main` for every vault read/write. Search first and reuse existing
records. Explain the current judgment, why it matters, the supporting
observations and the next decision. Keep raw prompts, transcripts, code,
configs, datasets, logs and credentials in their source systems.

For research milestones use `research-workflow`: update a question report with
`research_capture`. For an independently reusable outcome, use `record_create`
with a specific title, compact body, canonical tags/project and an operation ID.
Add exact source references and, when applicable, `investigation_id` and a stable
`evidence_key`. Reuse operation IDs only for identical retries. An evidence key
identifies the original run/artifact/comparison, so another task can reuse it.

For a terminal experiment use `experiment-ledger` and its four state fields.
Keep source recovery state separate from the scientific judgment. State
material limits precisely; do not replace interpretation with a boilerplate
list of missing evidence. Preserve user corrections and distinguish agent
proposals from adopted decisions.

Upload a small approved supporting file with `attachment_upload`; pass the
returned attachment ID to the record. Raw bytes travel through HTTPS, never
MCP JSON or base64. Embed a figure once.

Use `knowledge_revise` with current SHA, reason and source references for an
authorized same-path revision. History and exact-content restoration are
available through that tool. Human notes and other-host legacy records require
the explicitly scoped local maintenance run. `record_append` remains limited
to unchanged same-host gateway records. On conflict, read current content and
resolve only the affected note. Never force an overwrite or edit vault files.

Failed deliveries remain in the bridge's external outbox. Inspect/replay them
with `obsidian-research`; do not claim that pending content was saved. Git and
the retired UniversalNotes publisher are not fallback writers.

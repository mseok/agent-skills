---
name: obsidian-agent-record
description: Create or revise reusable agent records in Inbox/Agents so later agents can retrieve work outcomes, evidence and decisions. Use for agent-facing records, even when explicitly requested by the user. For the user's concept notes, meeting notes or personal writing, use obsidian-user-note; research question reports and comparable experiments use their dedicated skills.
---

# Obsidian agent records: Inbox/Agents

Use this skill for records that later agents search and reuse: what was established, the evidence, the judgment and its implications. For example, “record this outcome so the next agent can reuse it” belongs here. An explicit request to revise an existing agent record stays here as well.

For concept references, meeting notes or personal prose the user wants to read and edit, use [obsidian-user-note](../obsidian-user-note/SKILL.md). Select by the requested artifact's purpose, not by whether the request is explicit or arrives through Chat, Codex or Claude. These are workflow skills; a connector supplies the tools and does not by itself load either skill. An ordinary chat explanation does not authorize a vault write.

Read the [Obsidian vault policy](references/obsidian-policy.md) once
per task before using this workflow; reuse it if already loaded. All vault and
recording rules live there; this skill holds the procedure.

Apply policy section 7 when recording or reusing failures: keep dated incident
facts separate from authority, and do not turn them into future-work prohibitions.

Use `obsidian_main` for every vault read/write. Search first and reuse existing
records. Explain the current judgment, why it matters, the supporting
observations and the next decision. Keep raw prompts, transcripts, code,
configs, datasets, logs and credentials in their source systems.

`Inbox/Agents/` is the layer that later agents search and fetch; the user does
not read every record. Write each record so a search finds it: a specific title,
canonical `kind/*`, `project/*` and `topic/*` tags (policy section 5), and the
canonical `project`. When a record is a key experiment or
decision behind something the user writes in `Writing/` or `Notes/`, link that
note from the record. A screening, sweep or batch over many items is one record
per batch with a table or an attached file, never one record per item.

For research milestones use `research-workflow`: update a question report with
`research_capture`. For an independently reusable outcome, use `record_create`
with a specific title, compact body, canonical tags/project and an operation ID.
Add exact source references and, when applicable, `investigation_id` and a stable
`evidence_key`. Reuse operation IDs only for identical retries. An evidence key
identifies the original run/artifact/comparison, so another task can reuse it.

For a terminal experiment use `experiment-ledger`; the recording policy covers
judgment, provenance and user corrections.

Upload a small approved supporting file with `attachment_upload`; pass the
returned attachment ID to the record. Raw bytes travel through HTTPS, never
MCP JSON or base64. Embed a figure once.

Use `knowledge_revise` with current SHA, reason and source references for an
agent-record revision within the policy's permissions (section 2); on the Mac mini the tool also
creates, moves, deletes and undeletes notes. History and exact-content
restoration are available through that tool. `record_append` remains limited
to unchanged same-host gateway records. On conflict, read current content and
resolve only the affected note. Never force an overwrite or edit vault files.

Failed deliveries remain in the bridge's external outbox. Inspect/replay them
with `obsidian-research`; do not claim that pending content was saved. Git and
the retired UniversalNotes publisher are not fallback writers.

## User decisions

The dated decisions behind these rules, in the user's own words, are in [references/user-decisions.md](references/user-decisions.md). Read it before editing this skill or when a rule's origin or scope is in doubt; record a new decision there and state the resulting rule in plain words in this file.

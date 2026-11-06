---
name: obsidian-main-note
description: Save a reusable project outcome or authorized existing-note revision through the canonical Obsidian gateway. For ongoing research milestones use research-workflow; route explicit concept explanations and personal writing through obsidian-writing-note to Concepts and Writing respectively.
---

# Save a useful outcome

For an explicit Obsidian note request, use [obsidian-writing-note](../obsidian-writing-note/SKILL.md): reusable definitions, mechanisms and background explanations belong in `Concepts/`; the user's own essays, reflections, meeting records and personal synthesis belong in `Writing/`. For mixed requests, link concept references to the user's writing. Infer the destination from the purpose of the text, and honor any explicit destination. An ordinary chat explanation does not authorize a vault write.

Read the [Obsidian vault policy](references/obsidian-policy.md) once
per task before using this workflow; reuse it if already loaded. All vault and
recording rules live there; this skill holds the procedure.

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

Use `knowledge_revise` with current SHA, reason and source references for a
revision within the policy's permissions (section 2); on the Mac mini it also
creates, moves, deletes and undeletes notes. History and exact-content
restoration are available through that tool. `record_append` remains limited
to unchanged same-host gateway records. On conflict, read current content and
resolve only the affected note. Never force an overwrite or edit vault files.

Failed deliveries remain in the bridge's external outbox. Inspect/replay them
with `obsidian-research`; do not claim that pending content was saved. Git and
the retired UniversalNotes publisher are not fallback writers.

## User decisions

- 2026-11-06 (voice transcript): `"내가 그 모든 노트를 사실 다 읽을 수 있을 거라고 생각하지는 않고 기본적으로 그 LLC들이 자기네들의 서툰 기반으로서 이제 피지하면 했으면 좋겠다는 생각도 좀 있어. 그래서 그런 역할을 하는 게 사실 이 박스에서 원래 의도를 했던 거고"` (Inbox/Agents is meant for LLM search and fetch) and `"핵심 실험 같은 것들이 있으면 그거는 좀 어느 정도 내가 쓰는 노트랑 좀 연결시켜서 적으면 좋다 생각을 하는데"` (link key experiments to the user's own notes).
- 2026-11-06: the user adopted the proposal to keep a large screening as one record per batch with a table or attachment (`"너의 제안 중에 이번도 좀 반영해 주면 좋을 것 같고"`, proposal 2 of the 2026-11-05 vault evaluation).

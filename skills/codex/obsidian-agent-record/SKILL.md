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

Use `obsidian_main` (`migrated-settings_obsidian_main` in Antigravity top-level
sessions; `~/.local/bin/obsidian-main-mcp` over stdio or a coordinator-staged
`scratch/` snapshot when `swarm` workers lack MCP access, per policy §1) for
every vault read and write—never open or edit vault files directly. Search first
and reuse existing records. State the current judgment, why it matters, the
supporting observations and the next decision; keep raw prompts, transcripts,
code, configs, datasets, logs and credentials in their source systems, and
record failures strictly as dated incident observations under policy §7.

Write each `Inbox/Agents/` record for later agent search and fetch: use a
specific title, canonical `kind/*`, `project/*`, `topic/*` tags and `project`
(with `updated` stamped per policy §5), and follow policy §7 on keeping one
record per batch/sweep/screening round and linking related `Writing/` or
`Notes/` user notes.

Route ongoing research milestones to `research-workflow` (`research_capture`)
and comparable terminal runs to `experiment-ledger`. For an independently
reusable outcome, call `record_create` with a specific title, compact body,
canonical tags/project, exact `source_refs`, a fresh `operation_id` (reused
only for identical retries), and—when applicable—`investigation_id` and a stable
`evidence_key`. When the record belongs to an active question report, pass its
path in `evidence_paths` and patch the report's policy §7 evidence-index section
via `report_patch`. When delegating analysis, verification or follow-up work to
subagents (`spawn_agent`, Claude `Agent`, Antigravity `invoke_subagent` or
`swarm`) or peer threads, pass the relevant `Inbox/Agents/` paths (or stage
read-only snapshots / use `~/.local/bin/obsidian-main-mcp` stdio for MCP-blocked
`swarm` workers, per policy §7; omit only for blind isolation).

Upload small approved supporting files via `attachment_upload` (raw HTTPS bytes,
never base64 or MCP JSON; embed once) and revise existing records via SHA-checked
`knowledge_revise` or same-host `record_append` within policy §2 permissions.
Inspect and replay failed deliveries through the external `obsidian-research`
outbox (policy §7); never claim pending writes were saved or fall back to Git or
retired publishers.

## User decisions

The dated decisions behind these rules, in the user's own words, are in [references/user-decisions.md](references/user-decisions.md). Read it before editing this skill or when a rule's origin or scope is in doubt; record a new decision there and state the resulting rule in plain words in this file.

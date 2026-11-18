---
name: research-workflow
description: Maintain a cumulative Obsidian research report across tasks and hosts when an important hypothesis, implementation, result interpretation or direction decision occurs. Recover related question context on resume and check recording omissions at turn end. Routine polling and disposable debugging do not create records.
---

# Keep the research question continuous

Read the [Obsidian vault policy](../obsidian-agent-record/references/obsidian-policy.md) once
per task before using this workflow; reuse it if already loaded. All vault and
recording rules live there; this skill holds the procedure.

Use `obsidian_main` throughout (`migrated-settings_obsidian_main` in Antigravity
top-level sessions; for Antigravity `swarm` workers where MCP tools are blocked,
read via `~/.local/bin/obsidian-main-mcp` over stdio or a coordinator-staged
snapshot in `scratch/`, per policy §1 and §7—never direct vault `read_file`).
When a task starts or resumes, read the question once. If the `investigation_id`
is already known—from startup hook context, a handoff, the previous capture, or
(when no SessionStart hook ran, such as in Antigravity) the deepest matching
`cwd` entry under `project_bindings` in `~/.config/obsidian-research/host.json`—call
`investigation_context` with that ID: it returns the synthesis without the
history block, its `sha256` and the last five compact events. If the question
remains unknown, call `investigation_context(project, query)` instead; each
candidate comes with its `sha256`, a synthesis excerpt and its latest event,
which is enough to add a milestone or patch a section. Read the chosen ID
afterwards only when the whole synthesis is needed (for example to restructure
it with `report_body`). Raise `events_limit` or pass `content=full` only when
older judgments or source references are needed, `content=none` when only the
current `sha256` is needed, and `content_offset` to continue past one page.
Reuse the same ID across repositories and servers for the same question, or
register a separate phase ID on a subdirectory (`obsidian-research register
--root /absolute/project/subdir --project CanonicalProject --investigation-id
new-phase-id`, policy §7); inspect candidates before adopting one, as shared
words or project names alone do not establish identity.

When resuming or capturing a failure, apply policy §7's incident rule: treat
past tool errors and refusals as scoped dated observations, assess the current
request under current instructions, and never write or adopt a future-work
prohibition.

When initializing an approved research project, register its directory with
`obsidian-research register --root /absolute/project --project CanonicalProject
--investigation-id existing-question-id` (omit `--investigation-id` only for a
new question). A research tool call in an inbox activates only the invoking
session; do not register the whole inbox as research.

At a meaningful milestone, call `research_capture` with `investigation_id`,
canonical `project`, `source_refs`, when it happened, a stable `event_id` and
`operation_id`. In Codex and Claude Code, the `PreToolUse` hook supplies
`session_id` and `turn_id` (use only the active hook context's IDs; conflicting
IDs are rejected). In Antigravity—where no `obsidian-research` hook runs—pass
the current session's `Conversation ID` from `<user_information>` as
`session_id` and a current-turn label (for example `agy-turn-1`) as `turn_id`
so online captures never warn `unassigned` and any offline `outbox.mjs` item
remains replayable with `obsidian-research replay --session-id <conversation-id>`.
Never borrow IDs from another task or session, and never resend an already saved
milestone under a new `operation_id`. Use `expected_sha256` from the latest
capture receipt in this session (or `investigation_context` when none exists),
re-reading only on `revision_conflict`, after compaction, or after concurrent
host writes. Supply `question`, a specific `title` and `report_body` for a new
report, or `report_path` and its SHA to adopt an authorized existing report.

Keep the synthesis (`report_body` / `report_patch`) strictly in the objective
two-section layout defined in policy §7 (section 1 adopted user rules; section 2
executed-run and evidence-record index table), and follow policy §6's
Korean/English-only prose rule (no Han characters or kana; normal spacing).
Update those two sections via `report_patch` (`{heading, body}` items; matching
headings replace, new headings append, `Parent::Child` qualifies repeated
titles) whenever a user rule is adopted or a batch/evidence record is created so
records stay indexed after `events` rolls past five. Send `report_body` only to
create or restructure the whole synthesis while preserving existing material.

Keep hypotheses, interpretations and proposed next steps in each dated event
`summary`: state status (`observation`, `working-assumption`, `proposed`, or
`adopted`—adopted only when supported by the user's statement or actual choice,
with original and revised interpretations dated), then motivation, hypothesis,
method, observed result and interpretation (plus pseudocode only when an
implementation difference matters). Apply policy §7's evidence rules on bounded
assumptions, provenance recovery, and primary vs exploratory populations.

`source_refs` contains `{host, kind, locator, anchor?, sha256?}` (`task`,
`artifact`, `code`, `run`, `note`, `user`). Use exact spans and run/artifact
identities after inspecting underlying results; keep raw transcripts and large
data at their source and name the host on server-local locators. Set `event_id`
from the original milestone (not a prose hash), reusing it across tasks for the
same event and minting a new ID for a revised interpretation; reuse
`operation_id` only for identical retries (`event_kind=result` deduplicates an
evidence surface; `interpretation` records a changed reading). Retain comparable
terminal runs with `experiment-ledger`, pass their `evidence_paths` to
`research_capture`, and patch the policy §7 evidence-index table. Follow policy
§7 when delegating to subagents (`spawn_agent`, `Agent`, `invoke_subagent`,
`swarm`) or peer threads.

On SHA conflict, re-read current context, merge concurrent material and send a
new `operation_id` with the current SHA. Use `knowledge_revise` only within
policy §2 permissions.

Call `research_disposition` (`status=no-material-change`, brief `reason`, and
hook `session_id`/`turn_id`) **only** when a Stop hook explicitly prompts for an
omission check on a turn without a milestone—never call it unprompted in
Antigravity, where no Stop hook runs. Keep Plan-mode recordings as proposed
actions. Inspect and replay offline outbox entries per session (`obsidian-research
status --session-id SESSION`, `obsidian-research replay --session-id SESSION
[--dry-run]`, policy §7); never report queued items as saved or fall back to
direct vault files or Git.

## User decisions

The dated decisions behind these rules, in the user's own words, are in [references/user-decisions.md](references/user-decisions.md). Read it before editing this skill or when a rule's origin or scope is in doubt; record a new decision there and state the resulting rule in plain words in this file.

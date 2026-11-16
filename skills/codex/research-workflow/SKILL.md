---
name: research-workflow
description: Maintain a cumulative Obsidian research report across tasks and hosts when an important hypothesis, implementation, result interpretation or direction decision occurs. Recover related question context on resume and check recording omissions at turn end. Routine polling and disposable debugging do not create records.
---

# Keep the research question continuous

Read the [Obsidian vault policy](../obsidian-agent-record/references/obsidian-policy.md) once
per task before using this workflow; reuse it if already loaded. All vault and
recording rules live there; this skill holds the procedure.

Use `obsidian_main` throughout. When a task starts or resumes, read the
question once. If the `investigation_id` is already known (the hook context
lists prior question IDs; a handoff or the previous capture names it), call
`investigation_context` with that ID: it returns the synthesis without the
history block, its `sha256` and the last five compact events. If the question
is unknown, call `investigation_context(project, query)` instead; each
candidate comes with its `sha256`, a synthesis excerpt and its latest event,
which is enough to add a milestone or patch a section. Read the chosen ID
afterwards only when the whole synthesis is needed, for example to restructure
it with `report_body`. Raise `events_limit` or pass `content=full` only when
older judgments or source references are actually needed, `content=none` when
only the current `sha256` is needed, and `content_offset` to continue a
synthesis longer than one page. A question can span repositories and servers.
Reuse its ID and report for the same question; create and register a new stable
ID when the work enters a distinct research phase or subdirectory (for example,
`obsidian-research register --root /abs/project/subdir --project CanonicalProject
--investigation-id new-phase-id`) so earlier phase logs do not bloat active
context. Inspect candidate reports before adopting one. Shared words or a
common project alone do not establish that questions are the same.

When resuming, interpret past tool errors and refusals as scoped incident
observations under vault policy section 7. Assess the current request under
current instructions; do not adopt a note's inferred future-work prohibition.
When capturing a failure, preserve what happened and what remains unverified
without issuing a new prohibition to later agents.

When initializing an approved research project, register its directory with
`obsidian-research register --root /absolute/project --project CanonicalProject
--investigation-id existing-question-id`; omit the last option only for a new
question. This preserves other host settings and makes the question available
in startup context. A research tool call activates only the invoking session
when working in an inbox; do not register the whole inbox as research.

At a meaningful milestone, call `research_capture` with the investigation ID,
canonical project, source references, when it happened, a stable event ID and
operation ID. The trusted PreToolUse handler supplies the invoking session and
turn IDs. If supplying IDs yourself, use only those from the current hook
context; conflicting IDs are rejected. Never infer them from another source
task or the most recently active session. `recording_context.status=unassigned`
means the report was saved but the turn check cannot see it. Restore invocation
binding before the next capture; do not resend a saved milestone under a new
operation ID merely to attach it to the current turn.
For `expected_sha256` use the `sha256` from the latest capture
receipt in this session, or from `investigation_context` when there is none.
Do not re-read the report before every capture; re-read only after a
`revision_conflict`, after context compaction, or when another host may have
written meanwhile. For a new report supply `question`, a specific `title` and
`report_body`; an authorized existing report can be adopted with `report_path`
and its SHA.

The synthesis is the report body without frontmatter or the gateway's managed
history. To avoid anchoring later agents on an earlier agent's subjective
judgment or proposed next action, keep the synthesis strictly objective with
two level-2 headings: `## 1. 사용자 확정 조건 (Adopted User Rules)` (dated
rules and constraints explicitly approved by the user) and
`## 2. 실행된 배치 및 단건 기록 색인 (Evidence Index)` (a compact table of
executed batches/runs, verified metrics/costs, and `[[Inbox/Agents/...]]` or
`[[Writing/...]]` links). Update these two sections with `report_patch` whenever
a user rule is adopted or a batch/experiment record is created so that every
record stays indexed even after `events` rolls past the latest five. To update
it, prefer `report_patch`, a list of
`{heading, body}` items: a matching heading has its section replaced and a new
heading is appended, while other sections stay as they are; qualify a repeated
title as `Parent::Child`. Send `report_body`
only to restructure the whole synthesis or create a new report, and preserve
relevant existing material when doing so. Keep hypotheses, interpretations and
proposed next steps in the dated event `summary` rather than as standing
directives in the synthesis. The gateway keeps the dated event history
separately.

Write in Korean or English only, using connected, compact paragraphs with
normal spacing. This applies to `report_body`, record bodies and every
`summary`. Never shorten text by dropping spaces or by switching to Japanese or
Chinese; the gateway rejects a `summary` that contains kana or Han characters.
Order and separate the content as follows:

- In the synthesis: adopted user rules first, then the evidence index table of
  executed runs and linked records. In each event `summary`: state the
  decision/observation status, then motivation, hypothesis, method, observed
  result and interpretation. Include algorithm/pseudocode only when
  it explains an important implementation difference.
- Keep `observation`, `working-assumption`, `proposed` and `adopted` distinct.
  A proposal is adopted only when the user's statement or subsequent actual
  choice supports that reading. Keep original and revised interpretations dated.
- Combine related evidence into a practical judgment with its applicable scope.
  Missing source information belongs in provenance recovery, and does not erase
  an observed result. Explain only uncertainty that changes the next decision.
- Preserve primary and exploratory findings together, with their distinct
  comparison populations. Analysis completion does not prove a proposed
  training method's effect. Suggest extra experiments only when they discriminate
  between decisions that matter now.

`source_refs` contains `{host, kind, locator, anchor?, sha256?}`. Kinds are
`task`, `artifact`, `code`, `run`, `note`, `user`. Use exact retained task/turn
or source spans and run/artifact identity; inspect underlying results before
turning an earlier assistant answer into evidence. Keep raw transcripts and
large data at their source. A server-local locator explicitly names its host.

Set `event_id` from the original task milestone, not a prose hash. Reuse it for
the same event across tasks and use a new ID for a new interpretation. Reuse
`operation_id` only for an identical request. `event_kind=result` deduplicates
the same evidence surface; use `interpretation` for a changed reading of it.
Use `experiment-ledger` to retain separately comparable terminal evidence, then
pass those `evidence_paths` to the question report and add the new record row
to `## 2. 실행된 배치 및 단건 기록 색인 (Evidence Index)` via `report_patch`.
When delegating analysis, verification or follow-up work to a subagent
(`spawn_agent`) or peer thread, pass the relevant `Inbox/Agents/` record paths
and `investigation_id` so the recipient reads primary records directly via
`knowledge_read` or `investigation_context` instead of relying only on a
free-text summary (except during intentionally isolated blind reviews).

On SHA conflict, re-read current context, incorporate the concurrent material
and send a new operation ID with the current SHA. Do not replay stale
replacement prose with a new SHA. Use `knowledge_revise` only within the permissions in the policy; history
and restore retain original identity and the exact prior content.

At turn end, the successful capture receipt satisfies the omission check. When
the hook asks for the check and there was no milestone, call
`research_disposition` with `status=no-material-change`, a brief `reason`, and
the `session_id` and `turn_id` from hook context. This MCP tool writes only
host-local state and remains usable when the gateway is offline. The hook asks
at most once per turn, only for a turn that ran long enough for research work
and at most once per interval per session; a turn it does not ask about needs
no disposition. The check never justifies creating a routine note. In Plan
mode, keep any recording as a proposed action.

The bridge retains failed deliveries outside the vault. `obsidian-research
status --session-id SESSION` lists pending IDs. Preview with `obsidian-research
replay --session-id SESSION --dry-run`, then remove `--dry-run` to retry only
that session's exact payloads. Unassigned requests require provenance recovery;
never guess their session or turn. Replay stops at a conflict or delivery error.
Resolve semantic/SHA conflicts in context. Never report a queued request as
saved, and never use a direct vault file or Git fallback.

## User decisions

The dated decisions behind these rules, in the user's own words, are in [references/user-decisions.md](references/user-decisions.md). Read it before editing this skill or when a rule's origin or scope is in doubt; record a new decision there and state the resulting rule in plain words in this file.

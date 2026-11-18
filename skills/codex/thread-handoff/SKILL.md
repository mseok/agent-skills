---
name: thread-handoff
description: Hand work between threads, sessions, harnesses (Antigravity, Codex, Claude Code) and hosts, resume from a handoff, and run subagent, native swarm, workflow, or bulk thread operations safely. Use when a conversation is long or compacted (/compact), when the user says 인계, 이어서, 새 스레드에서, 핸드오프, resume, continue in Codex/Claude/AGY, or before spawning multiple subagents or swarm workers or archiving many threads.
---

# Thread handoff, swarm, and delegation

## Write the handoff (`codex-task-state`)

1. Keep the current-state file in the task's artifact folder with `~/dot/bin/codex-task-state` (`read` first, pass `--expected-sha` on rewrite) so Antigravity, Codex, and Claude Code share one schema: `goal`; `completion_criterion` (optional: the user's stopping test verbatim with nothing added; the final reply says met, not met with the reason, or blocked with the one user action); `scope` (permitted changes, forbidden changes, and exclusions); `decisions` (dated verbatim user decisions and fixed numbers); `sources` (exact paths, hosts, checkpoints, data and figure versions); `active_operations` (job and process IDs with hosts); `completed_checks`; `pending_questions`; `status`; `next_action`.
2. Create it at the first compaction (`/compact`), before the first external-account change or bulk write, and before switching harnesses; refresh at material transitions, after about five compactions (then offer a fresh thread), on context reset, and before archiving. Record decisions, not chat history or exploration logs.
3. Keep it current, not cumulative. When `read` includes a `history` key, remove reversed decisions, finished operations, answered questions, and unused sources in the same write (archived verbatim to `<name>.history.jsonl`); keep old entries only on an older tool without `history`. Never paraphrase, merge, or narrow an active user decision without asking.
4. Preserve `[kNN]` prefixes on `completed_checks`, append new checks at the end, and cite `[kNN]` in decisions, questions, or next actions resting on them. Over 12,000 bytes the tool moves the oldest checks to `<name>.history.jsonl`, retaining the newest ten and every cited check; clean up remaining bloat at the next write, and read the history only when a decision is disputed or the handoff flags a gap.
5. Record tool errors, access failures, model refusals, or runner policies only as dated incidents for that run (affected step, observed result, unfinished checks, usable outputs), never as standing prohibitions on future work. Preserve only explicit user scope exclusions and actual safeguards as authority.
6. Cite the file's absolute path and SHA when creating it, handing off, or asking the user to act on it; keep routine refreshes silent.

## Resume and cross-harness transitions

1. Read only the handoff and the files it points to; do not re-read raw transcripts unless the handoff flags a gap. If `read` reports `copy_of` while the original folder exists, ask which one is current before writing either.
2. Start in the directory the handoff names and verify host, branch, and data version before acting. Standing permissions must appear explicitly in `decisions`; otherwise ask once.
3. Restate goal, scope, and next action in two lines, then proceed; quote the recorded decision (or `.history.jsonl`) first if a decision is disputed.
4. **Cross-harness routing**:
   - Between Antigravity, Codex, and Claude Code, pass the `codex-task-state` file path rather than pasting chat transcripts; in Codex desktop, recover missing browser bindings via `~/dot/ai/codex/references/codex-browser.md`.
   - `conversation://<id>` resolves only inside Antigravity, and private UI thread links from another harness cannot be opened directly—say so immediately, or for local Claude Code / `claude.ai/code` sessions locate the transcript under `~/.claude/projects/<cwd-key>/` on the host that ran it (over SSH when needed).

## Subagent, swarm, and workflow fan-out preflight

1. **Choose the host's native delegation tool**:
   - **Codex**: `spawn_agent` with explicit `model` and `reasoning_effort`.
   - **Claude Code**: `Agent` tool (`effort`); use `claude -p --effort` only where no native subagent tool exists (such as a plain terminal or external workflow).
   - **Antigravity**: `invoke_subagent` for a single bounded helper; `swarm` (`action: "add"`, `read_board`, `post_message`, `swarm_wait`) for multi-worker collaboration or independent verification (`workspace: "share"` when multiple workers edit/build repository code concurrently; `inherit` for readers/verifiers); `run_workflow` for homogeneous fan-outs or staged pipelines (read `run-workflow` first). Leave worker `model` unset to inherit the active model unless the user asked for a specific model; if no supported route exists, say so before launching.
   - **Preflight line**: state agent count, model, effort, expected cost/quota (`~/dot/bin/fanout-preflight --agents N --model M --effort E [--chars C]` prints one non-blocking line with live quota; inside Antigravity, `swarm{action: "models", all: true}` also reports live Gemini/Claude/GPT remaining quotas with zero model inference), search cap per agent, and output files. Stop launching if a usage warning appears, or size the first wave to one third when remaining budget is unreadable (and when a reset time is near, launch after it or state the risk).
2. **Mandatory worker brief invariants**: no nested subagents by default (`local tools only`), exact question, user-approved inputs and exclusions (ask before adding extra sources), disjoint output paths, host shell traps from `~/.codex/host-context.md` (`/bin/ls` instead of `ls`, `python3`, move unwanted files to scratch instead of `rm -f` / `rm -rf`, no GNU `timeout` assumptions), relevant Obsidian `Inbox/Agents/` paths or `investigation_id` when research context applies (for Antigravity `swarm` workers where MCP is blocked, stage a read-only snapshot in `scratch/` or use `~/.local/bin/obsidian-main-mcp` stdio—never direct vault `read_file`), and this exact verbatim English sentence (neither translated nor widened to outputs):
   `"Do not put the user's email address, phone number or account IDs into any external request (web search, URL, API call)."`
3. **Waiting and salvage**:
   - In Antigravity, subagents and background tasks wake the turn automatically and `swarm_wait(since=<last_read_seq>)` sleeps at zero token cost—never poll in a shell `sleep` loop, `@mention` only the next acting peer on peer-to-peer swarm handoffs rather than CC'ing `@coordinator`, and `swarm{action: "kill"}` helpers you spawned after landing their work.
   - In CLI/file fan-outs without reactive wakeup, have each worker write a marker file beside its completed output and reply with one status line; wait on the markers in one bounded loop (`< 2 min` steps) and read outputs only after completion. Give workers structured JSON sidecar files (one verdict/record object per case) beside prose reports so the parent aggregates deterministically by script, and filter possibly null results in workflow scripts. Salvage finished outputs as workers complete.
4. **Parent verification**: check worker claims (citations, numbers, diffs, rendered artifacts) against primary sources before relaying them, and never surface raw inter-agent status posts as the final reply.

## Bootstrap template for a thread that must only wait

```
Already verified: guidance sha <x> on <hosts>. Do not re-verify or connect to other hosts; read your handoff file, confirm readiness in one line, and wait.
```

## Bulk thread and server operations

Produce a dry-run list first, protect active skill/evaluation threads and threads with running jobs, confirm, then archive, rename, restart, or delete one batch (or one live server) at a time and verify each. Under the 2026-10-17 audit rule, a restored or replacement thread counts as "back" only when visible in the user's sidebar/mobile UI (threads created via app-server tools are hidden—create replacements in the GUI or state that they are hidden), and imported cross-harness threads must be checked against `completed_checks` for gaps before continuing.

## Verified additions (2026-10-17 & 2026-11-10 audits)

- Hand off when accumulated images or large tool outputs slow or blank turn history (a fresh thread + handoff fixes it; forking does not). Record source-confirmed facts that downstream numbers depend on under `decisions` with source and page, and quote the user's original words before acting on any decision relayed from another thread or folder.
- Sibling sessions on one host designate a single GUI owner (browser, Figma, computer use, Hancom / `hwp-browser`); siblings work on local files and route GUI steps silently through the owner. Each session owns its output directory—if foreign files appear there, move new outputs to a fresh subdirectory, note it once, and credit the other session's outputs accurately.
- When `create_session` cannot set the working directory for another project folder, start the session directly inside that target directory (a first-run folder-trust prompt needs the user's keypress). An inter-thread mailbox post is not delivery until you send direct input or wake the sibling and confirm work started.

## User decisions

The dated decisions behind these rules, in the user's own words, are in [references/user-decisions.md](references/user-decisions.md). Read it before editing this skill or when a rule's origin or scope is in doubt; record a new decision there and state the resulting rule in plain words in this file.

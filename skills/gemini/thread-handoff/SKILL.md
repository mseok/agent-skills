---
name: thread-handoff
description: Hand work between threads, sessions, harnesses (Antigravity, Codex, Claude Code) and hosts, resume from a handoff, and run Antigravity subagent, native swarm, or workflow fan-outs safely. Use when a conversation is long or compacted (/compact), when the user says 인계, 이어서, 새 스레드에서, 핸드오프, resume, continue in Codex/Claude/AGY, or before spawning multiple subagents or swarm workers.
---

# Thread handoff, swarm, and delegation (Antigravity)

## Write the handoff (`codex-task-state`)

1. Keep the cross-harness state file in the task's artifact folder with `~/dot/bin/codex-task-state` (`read` first, pass `--expected-sha` on `write`) so Antigravity, Codex, and Claude Code read the exact same schema: `goal`, `completion_criterion` (optional: the user's stopping test verbatim), `scope` (permitted/forbidden changes and exclusions), `decisions` (dated verbatim user decisions and fixed numbers), `sources` (exact paths, hosts, checkpoints, data/figure versions), `active_operations` (job/process IDs with hosts), `completed_checks` (`[kNN]` IDs), `pending_questions`, `status`, `next_action`.
2. Create it before compacting (`/compact`), before the first external-account change or bulk write, and before switching harnesses; refresh at material transitions. Record decisions, not chat history.
3. Keep it current: when `read` shows a `history` key, remove reversed decisions, finished operations, and answered questions in the same write (archived automatically to `<name>.history.jsonl`). Never paraphrase or narrow an active user decision without asking.
4. Record tool errors, access blocks, or model refusals only as dated incidents for that run (affected step, observed error, usable outputs), never as standing prohibitions on future work.
5. Cite the absolute path and SHA when creating the handoff or handing off to the user; keep routine refreshes silent.

## Resume and cross-harness transitions

1. Read only `task-state.json` and the files it points to; do not re-read raw transcripts unless the handoff flags a gap. If `read` reports `copy_of` while the original exists, ask which folder is current before writing either.
2. Verify host, branch, and data version before acting. Standing permissions must be explicitly recorded in `decisions`; otherwise ask once.
3. Restate goal, scope, and next action in two lines, then proceed. Links to another harness's private UI thread (`codex://`, Claude remote threads) cannot be opened directly inside Antigravity (`conversation://<id>` links only AGY conversations); say so immediately or read local files/handoffs directly.

## Antigravity subagent, swarm, and workflow fan-out preflight

1. **Pick the right AGY primitive**:
   - Single bounded helper task -> `invoke_subagent`.
   - Multi-worker collaboration with peer handoffs or independent verification -> `swarm` (`action: "add"`, `read_board`, `post_message`, `swarm_wait`). Pass `workspace: "share"` when multiple workers edit/build repository code concurrently; readers and verifiers keep `inherit`.
   - Many homogeneous items or staged map-reduce pipelines -> `run_workflow` (read the `run-workflow` skill first).
2. **Preflight line**: before launching multiple workers, state in one concise block the worker count, model (leave unset to inherit the active model unless the user requested a specific model; ask before substituting an unavailable user-named model), expected cost/quota (`~/dot/bin/fanout-preflight --agents N --model M --effort high` informs without blocking), search cap, and output paths.
3. **Mandatory worker brief invariants**:
   - No nested subagents by default (`local tools only; do not spawn nested subagents`).
   - Disjoint owned output paths per worker (shared project inputs strictly read-only when benchmarking or auditing).
   - Host shell traps from `~/.codex/host-context.md` (on this Mac mini: `/bin/ls` instead of `ls`, `python3` instead of `python`, move unwanted files to scratch instead of `rm -f` / `rm -rf`, no destructive git).
   - Relevant Obsidian `Inbox/Agents/` paths or `investigation_id` when research context applies (omit only for intentionally blind review).
   - Paste this exact English identifier rule verbatim (neither translated nor widened to outputs):
     `Do not put the user's email address, phone number or account IDs into any external request (web search, URL, API call).`
4. **Reactive waiting (zero polling)**: Antigravity resumes automatically when a subagent or background task finishes, and `swarm_wait(since=<last_read_seq>)` sleeps at zero token cost. Never poll in a shell `sleep` loop, and on peer-to-peer swarm handoffs (`author -> @verifier`) `@mention` only the next acting peer rather than CC'ing `@coordinator`.
5. **Parent verification**: verify worker claims (numbers, citations, file diffs, rendered PNG/PDF outputs) against primary sources before relaying them, and never surface raw board chatter as the user reply. Kill any helper workers you spawned yourself (`swarm{action:"kill"}`) after landing their work and before finishing.

## Sibling sessions and GUI ownership

When multiple sessions run on one host, only one designated owner drives foreground/GUI or browser tools (Figma, HWP `hwp-browser`, screen sharing); other sessions work on local files. If unexpected files appear in your output directory, move new outputs to a fresh subfolder, note it once, and credit the other session's outputs accurately.

## User decisions

The dated decisions behind these rules, in the user's own words, are in [references/user-decisions.md](references/user-decisions.md). Read it before editing this skill or when a rule's origin or scope is in doubt; record a new decision there and state the resulting rule in plain words in this file.

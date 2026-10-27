---
name: thread-handoff
description: Hand work between threads, sessions, harnesses (Codex, Claude Code) and hosts, resume from a handoff, and run subagent fan-outs or bulk thread operations safely. Use when a thread is long or compacted, when the user says 인계, 이어서, 새 스레드에서, 핸드오프, resume, continue in Codex/Claude, or before spawning several agents or archiving many threads.
---

# Thread handoff and delegation

## Write the handoff

1. Keep the current-state file in the task's artifact location with `~/dot/bin/codex-task-state` (read it first, pass `--expected-sha` on rewrite). The tool accepts only its documented fields, so put each item where it belongs: `goal`; `scope` (permitted changes, forbidden changes, and the exclusions the user ruled out); `decisions` (dated entries, including every user-fixed threshold or number with the user's wording when it was a correction); `sources` (exact paths, hosts, checkpoints, data and figure versions); `active_operations` (job and process IDs with hosts); `completed_checks`; `pending_questions`; `status`; `next_action`.
2. Create it at the first compaction or before the first external-account change or bulk write; refresh it at material transitions, after about five compactions (then offer a fresh thread), when the user resets context, and before the thread is archived. A handoff carries decisions, not history: no chat summary, no exploration log.
3. Name the file in the reply with its absolute path and the SHA from the tool's output.

## Resume

1. Read only the handoff and the files it points to; do not re-read raw history or earlier threads unless the handoff names a gap.
2. Start in the directory the handoff names; verify host, branch and data version before acting. A handoff is not permission: standing authorizations must be listed in it explicitly, otherwise ask once.
3. Restate goal, scope and next action in two lines, then continue. If the user disputes a decision, quote the handoff's recorded decision before answering.

## Cross-harness

- Codex → Claude: write the handoff file, then start the new thread with its path; do not paste the Codex transcript.
- Claude → Codex: same file; Codex worker threads created through an API lack browser context, so browser work stays in the GUI thread.
- Links to another harness's thread cannot be opened; say so immediately instead of trying.

## Subagent fan-out preflight

1. Before launching, state in one block: number of agents, model, effort (pass the requested model and effort through the host's own subagent tool: ChatGPT app `spawn_agent` with explicit `model` and `reasoning_effort`, Claude Code Agent `effort`; use `claude -p --effort` only where no native subagent tool exists, such as a plain terminal or Workflow; if no route supports it, say so before launching), expected token cost, search cap per agent, and output files. Check the remaining usage budget first; stop launching when a usage warning appears.
2. No nested subagents by default. Each prompt carries: the exact question, input paths, the output path, "local tools only", and the identifier restriction (no emails, phone numbers, account IDs in requests or outputs).
3. The parent verifies subagent claims (citations, numbers, "done") against sources before relaying them, and never lets an inter-thread status message be the final reply to the user.
4. Partial results are salvaged into files as agents finish; a crashed workflow must not lose finished work.

## Bootstrap template for a thread that must only wait

```
Already verified: guidance sha <x> on <hosts>. Do not re-verify or connect to other hosts; read your handoff file, confirm readiness in one line, and wait.
```

## Bulk thread operations

Archiving, renaming, restarting or deleting many threads or sessions: produce the dry-run list first, keep a protected set (active skill or evaluation threads, threads with running jobs), confirm, then act one batch at a time and verify each is back or gone. Restarting live agent servers follows the same rule: list affected sessions, restart one at a time, verify each.

## Verified additions (2026-10-17 audit)

- Links to a `claude rc` or claude.ai/code session have their transcript on the host that runs it: find that host and folder and read `~/.claude/projects/<cwd-key>/` there by id and time (over SSH when needed) before asking the user to log in anywhere; only cloud-only sessions or another person's threads cannot be opened, and that is said at once.
- Hand off also when the thread has accumulated many images or large tool outputs: slow or empty turn history is the trigger; a handoff plus a fresh thread preserves the old one, a fork does not help. Facts confirmed from a source that later numbers depend on go under `decisions` with the source and page. A decision relayed from another thread or read from a work folder authorizes only what the user's own words there authorized; quote that source before acting.
- Sibling threads on one host: each handoff names the single thread that owns the host's GUI (browser, Figma, computer use, Hancom); the others work on local files and route GUI requests through the owner, and that request never appears in the user-facing reply. Each thread writes outputs to a directory it owns; if files you did not write appear there, continue in a new directory, say so once, and credit another session's results to it.
- Fan-out: each agent gets its own working and download directory (shared folders are read-only to agents) and the host's shell traps from host-context (for example `/bin/ls` instead of `ls`, no GNU `timeout`); read a subagent's output only after its completion notification or wait call returns, since an existing file may still be rewritten; in Workflow scripts treat every agent result as possibly null and filter before reading its fields. Claude Code cannot read plan usage: before a fan-out of more than about five agents ask once for the user's usage figures, and when a reset time is near, launch after it or state the risk in the launch line.
- To continue in another project folder on the Mac mini, start the session there with the host-context procedure (herdr workspace with `--cwd`, then `claude rc`); `create_session` cannot set the working directory, and a first-run folder-trust prompt needs the user's keypress.

## Bulk operations: what "back" means (2026-10-17 audit)

A restored or replacement thread counts as back only when it is visible where the user looks (sidebar and mobile); threads created through app-server tools are hidden there, so create replacements from the GUI or say that they are hidden. After importing a thread into another harness, compare the imported history with the handoff's completed checks and report any gap before continuing.

## User decisions

- 2026-10-27 (ChatGPT app, Claude chat 01a17beb-b6e8-7861-8906-b61838d2e8b1, continued in 01a17c0d-815e-76b0-b8aa-0a33e0754199): a fan-out passes model and effort through the host's own subagent tool and uses `claude -p --effort` only where no native subagent tool exists (step 1 above). User's words: "ㅇㅇ 둘다 적용 ㄱㄱ" and "둘 다 적용하면 될 듯?".

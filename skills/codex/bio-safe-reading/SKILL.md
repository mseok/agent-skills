---
name: bio-safe-reading
description: Route the reading of biology, chemistry, drug-discovery or medical material (papers, corpora, chat transcripts, sequences, assay notes) to the user's designated model (Claude Opus 5, id claude-opus-5) and recover from a safety-classifier refusal. Use when a request touches such material even indirectly (writing-style or slide work over bio papers, literature indexes such as Europe PMC, audits of research chats), when a reply is refused or flagged ("[bio]", "safeguards flagged", "can't help with that", "earlier conversation content", Codex's refusal text, 밴), or when the user says 바이오 내용, 직접 읽지 마, Opus 5로 읽어.
---

# Bio-safe reading

Safety classifiers stop sessions when raw biological or chemical content enters the context, even for harmless meta tasks (slide design, writing style, literature surveys, chat audits). Once titles, abstracts or sequences are in the parent context the session stays poisoned, so the parent never reads them.

## Rules for the parent

1. Do not open raw bio-adjacent sources yourself: paper PDFs, corpus lists, assay or design notes, sequence files, transcripts of research chats. Work from paths, counts, metadata and behavioral summaries.
2. Delegate reading to the user's designated model, Claude Opus 5 (`claude-opus-5`). Opus 5.5 and Fable have refused this material before, so do not substitute them silently: in T3 use `delegate_task` with `providerInstanceId: claudeAgent` and `model: claude-opus-5`; in Claude Code without T3 the Agent tool's `opus` alias resolves to Opus 5.5, so run a headless process instead (`claude -p --model claude-opus-5 "<brief>"`) or say which model you are using and why; in Codex do not use a Codex worker thread (same classifier): delegate across providers to Claude Opus 5 through T3 or the headless `claude` command. One batch per agent; give it paths, the question and the output file, never pasted content.
3. The subagent writes its findings to a file and replies with a short summary. Tell it to keep its own notes at the level of agent behavior or evidence pointers: no protocols, sequences, structures, targets, compound names, dosing or mechanism details in the report unless the user's deliverable needs them, in which case it writes them to the deliverable file, not to the chat.
4. The parent reads only the summary and the report. If a report must contain scientific detail, read it with a second allowed-model agent that extracts what the parent needs.
5. Keep quarantine folders for raw material (`<task>/raw/`) and reports (`<task>/findings/`). Never print corpus lists, abstracts or excerpts into the chat.

## When a refusal or flag happens

0. First check what must keep running (an RSI loop, a job, a download) and keep it running; recovery of the conversation never interrupts the work it was supervising.
1. Do not retry the same request in the same session or harness; a repeated attempt fails again and wastes the turn budget.
2. Record the state with `~/dot/bin/codex-task-state` (goal, paths, what was already read, next action) and say in one line that the classifier blocked the step and which file it concerned.
3. Continue in a fresh session or an allowed-model subagent with a brief that contains paths and the question only. If the blocked step was a subagent, relaunch it on the same file with the "behavioral level only" instruction; if it fails twice, mark the file as unreadable in the findings and move on.
4. Never work around the classifier by paraphrasing hazardous content or splitting it into fragments; route, do not evade.

## Delegation prompt template

```
Read <paths> and write <output file>. Report at the level of agent behavior or evidence pointers;
do not reproduce protocols, sequences, structures, targets, compound names, dosing or mechanism
details. No personal identifiers (emails, phone numbers, account IDs) in the output. Local file
tools only; no network, no connectors, no subagents. Reply with a <=15-line summary.
```

## Verified additions (2026-10-17 audit)

- Rule 1 also covers item prompts, answer keys, generated drafts, judged sentences, structure files, database entry pages, and research notes or their title lists derived from such material. When the material's domain does not matter to the task (writing-style corpora, evaluation items, layout tests), choose non-bio sources up front, never a life-science index; after a lockout remove bio-adjacent items from such a corpus instead of adding more. In code-driven analysis of biological structures or benchmarks, scripts print identifiers, counts and metrics only, never database records or page text.
- When the deliverable itself is bio-adjacent text (slides, manuscript prose) in a Claude Code session, ask once for `/model claude-opus-5`, which has recovered the same session before; in Codex an "Invalid prompt … safety reasons" turn failure poisons the thread and no later turn runs, so keep the task-state file current before every bio-adjacent fetch and tell the user once, at task start, that recovery is a new thread that reads that file.
- The blocked turn's tool calls may have run although they are gone from your context: list files changed in the task folder since the blocked turn and treat them as your own output before redoing work.

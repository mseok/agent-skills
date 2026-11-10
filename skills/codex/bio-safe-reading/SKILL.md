---
name: bio-safe-reading
description: Apply the user's model-specific preference for reading biology, chemistry, drug-discovery or medical material. Astra, Sol, Claude Sonnet 5.5 and Claude Opus 5 may read directly; route Claude Fable or Opus 5.5 reading to Claude Sonnet 5.5 (effort high by default) before it starts. Use for such material, an explicit reading-model instruction, or safe state preservation after a refusal. Model changes never override a safety refusal.
---

# Bio-safe reading

This is a model-specific reading preference, not a universal requirement to delegate biology content. Astra, Sol, Claude Sonnet 5.5 and Claude Opus 5 may read sources directly. The routing rules below apply only when the parent is Claude Fable or Opus 5.5, or the user explicitly requests that routing.

## User decisions

The dated decisions behind these rules, in the user's own words, are in [references/user-decisions.md](references/user-decisions.md). Read it before editing this skill or when a rule's origin or scope is in doubt; record a new decision there and state the resulting rule in plain words in this file.

## When the parent is Claude Fable or Opus 5.5

1. Do not open raw bio-adjacent sources yourself: paper PDFs, corpus lists, assay or design notes, sequence files, transcripts of research chats. Work from paths, counts, metadata and behavioral summaries.
2. Delegate reading to Claude Sonnet 5.5 (`claude-sonnet-5-5`) at effort high unless the user names another model or effort: in the ChatGPT app pass both to `spawn_agent` (`model`, `reasoning_effort`), in Claude Code give the Agent tool the exact model ID and the effort. Claude Opus 5 (`claude-opus-5`) remains an allowed reader when the user asks for it: in Claude Code use the exact model ID rather than an `opus` alias that may resolve to Opus 5.5, and in the ChatGPT app, where `spawn_agent` does not offer it, run it as the headless `claude -p --model claude-opus-5` worker described in host-context and say so before launching. One batch per agent; give it paths, the question and the output file, never pasted content. Astra and Sol parents may instead read directly or use a suitable worker when delegation is useful.
3. The subagent writes its findings to a file and replies with a short summary. Tell it to keep its own notes at the level of agent behavior or evidence pointers: no protocols, sequences, structures, targets, compound names, dosing or mechanism details in the report unless the user's deliverable needs them, in which case it writes them to the deliverable file, not to the chat.
4. The parent reads only the summary and the report. If a report must contain scientific detail, read it with a second allowed-model agent that extracts what the parent needs.
5. Keep quarantine folders for raw material (`<task>/raw/`) and reports (`<task>/findings/`). Never print corpus lists, abstracts or excerpts into the chat.

## When a refusal or flag happens

0. First check what must keep running (an RSI loop, a job, a download) and keep it running; recovery of the conversation never interrupts the work it was supervising.
1. Do not retry the same request in the same session or harness; a repeated attempt fails again and wastes the turn budget.
2. Record the state with `~/dot/bin/codex-task-state` (goal, paths, what was already read, next action) and say in one line that the classifier blocked the step and which file it concerned.
3. Continue only work that is permitted by the refusal's scope. Do not relaunch the denied request under another model, session or harness to obtain the blocked content.
4. Never work around a refusal by paraphrasing hazardous content or splitting it into fragments. A reading-model preference is not permission to bypass safeguards.

## Delegation prompt template

```
Read <paths> and write <output file>. Report at the level of agent behavior or evidence pointers;
do not reproduce protocols, sequences, structures, targets, compound names, dosing or mechanism
details. No personal identifiers (emails, phone numbers, account IDs) in the output. Local file
tools only; no network, no connectors, no subagents. Reply with a <=15-line summary.
```

## Verified additions (2026-10-17 audit)

- Rule 1 also covers item prompts, answer keys, generated drafts, judged sentences, structure files, database entry pages, and research notes or their title lists derived from such material. When the material's domain does not matter to the task (writing-style corpora, evaluation items, layout tests), choose non-bio sources up front, never a life-science index; after a lockout remove bio-adjacent items from such a corpus instead of adding more. In code-driven analysis of biological structures or benchmarks, scripts print identifiers, counts and metrics only, never database records or page text.
- When the deliverable itself is bio-adjacent text (slides, manuscript prose) and the active reader is Claude Fable or Opus 5.5, use the default reader (Sonnet 5.5, effort high) before reading or ask once for a model switch if delegation is unavailable. Astra and Sol require no switch solely because the topic is biological. Preserve the current task state after an actual turn failure without promising that a fresh session will bypass it.
- The blocked turn's tool calls may have run although they are gone from your context: list files changed in the task folder since the blocked turn and treat them as your own output before redoing work.

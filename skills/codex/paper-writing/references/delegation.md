# Packaging the work for a writer

A writer agent or model sees only what it is given. The package must let a writer with no other context produce the text the plan describes, and no part of it may be a summary that loses a number, a condition or a placement.

## The package

Put the files in one folder. Keep facts in notes.md and editorial decisions (tiers, placements, framing) in plan.md.

- **`notes.md`**: the facts, in any language, with a source locator for each (file, table, run). Every number with its unit, comparator, condition, basis, aggregation and uncertainty, and its figure or table number if one exists, copied from its source, never rounded or paraphrased here. Keep conflicting values, missing definitions, the author's interpretations ("저자 정리: …") and unrun work, each marked as such. Leave out only what bears on no claim: keep every result that tests, bounds or contradicts a claim or belongs to a reported aggregate.
- **`plan.md`**, when there is one: the plan (`planning.md`) with its status. An "accepted" plan carries the author's words of acceptance; an unreviewed plan says "provisional". Without a plan, leave the file out, and the writer makes the decisions privately.
- **`brief.md`**: the target venue; the sections to write, their file names and the scope of each ("the Results subsection reporting the main comparison"); target lengths if known; spelling; output format; citation placeholders; the language of Notes to author; and whether figure and table numbers in the notes are the paper's own.
- **`prompt.txt`**: the prompt below with every brace filled in, saved beside the package together with the skill snapshot's path and hash and the model and reasoning effort requested, so the run can be repeated or audited.

## The prompt

Fill in the braces and give the writer this prompt, adjusted only where the harness differs:

```
You are drafting parts of a research paper. No one will answer questions before the text is due: do not stop to ask, and do not return a plan instead of the files.

Inputs: read only {DIR}/brief.md, {DIR}/plan.md and {DIR}/notes.md, plus the skill folder named below. Open nothing else under {ROOT}, and in particular nothing under {FORBIDDEN}. Do not browse the web, and put no personal identifier (name, email address) into any request.

Read the writing skill directly from {SKILL}: SKILL.md first, then references/register.md and the references for the sections you write. Do not invoke the Skill tool, do not read references/planning.md or references/delegation.md, and use no other installed skill or MCP tool. Skip the skill's planning step: follow plan.md as far as its status allows (an accepted plan binds the direction; a provisional plan is a proposal), except where it conflicts with notes.md or with the skill's non-negotiables; there, follow those and list the departure in Notes to author.

If a shell is available, run python3 -I {SKILL}/scripts/check_prose.py DRAFT --notes {DIR}/notes.md --section SECTION on each draft, with SECTION one of intro, methods, results or other. Reread every item it reports and fix the real problems; a review item or a listed computed number is a prompt to check, not an instruction to delete.

Write at the level of the strongest papers at the target venue named in brief.md. Create {OUT} and write {OUT}/<section>.md for each section that brief.md lists. Each file holds manuscript text only; anything for the author goes after a line --- under the heading Notes to author.

Final reply: the file paths and their word counts, nothing else.
```

- Before launching, check that the writer can read every input path and the skill path and can write `{OUT}`; nothing may depend on implicit skill discovery, a slash command or another session's history.
- `{SKILL}` is an absolute path the writer can read. For a comparison, make it a frozen copy of the skill for this run and record its path and a hash of its files, so every writer reads the same version. `{ROOT}` is the project folder; `{FORBIDDEN}` names every folder the writer must not see, such as the source papers of a test.
- Without an accepted plan, drop plan.md from the inputs line and end the skill paragraph with: "Skip the skill's planning step: make its four decisions privately from notes.md and write the sections."
- For a condition without the skill, replace the skill and checker paragraphs with "Do not use any installed skill: do not invoke the Skill tool and do not read skill files from ~/.claude/skills, ~/.codex/skills or ~/agent-skills." Keep every other line identical, and give plan.md only if the comparison is meant to include it. In Codex, that condition must not have the skill installed under `~/.codex/skills`, and `{OUT}` must lie inside the session's writable roots.
- Use the same model and reasoning effort for every compared condition, give every writer the same package and prompt except for the factor being compared, and write each output to its own folder. In a test, plan.md is written from notes.md alone, by someone who has not read the source paper.
- For a chat interface without file access, send one message that contains brief.md, plan.md and notes.md inline, followed by the skill's SKILL.md and the references for the requested sections (or attach those files), and ask for the manuscript text and the Notes to author block.
- Read each returned draft against notes.md and plan.md before using it: the numbers with their basis, the scope words, and everything the plan placed in the Supplementary or left out.

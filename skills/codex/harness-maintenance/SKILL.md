---
name: harness-maintenance
description: Maintain the agent harness itself across hosts: the shared AGENTS.md/CLAUDE.md source in ~/dot, the agent-skills repository, host-context files, hooks, memory notes and the Obsidian research gateway, and run instruction or skill A/B evaluations. Use when the user says 지침, AGENTS, CLAUDE.md, 스킬 정리, dotfiles, hook, 동기화, 하네스, 평가 harness, or when a rule or skill must change or reach another host. Not for ordinary project work.
---

# Harness maintenance

## Where things live

- Shared guidance: `~/dot/ai/codex/AGENTS.md` (every host links `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md` to it). The research block at its top is managed by `obsidian-main/scripts/deploy-research.py` from `policies/research-router.md`; edit both the router source and AGENTS.md identically, or redeploy, never one alone.
- Shared skills: `~/agent-skills/skills/codex` (both harnesses) and `~/agent-skills/skills/claude` (Claude only); `~/dot/bin/install_codex.sh` and `~/dot/bin/install_claude.sh` link them into `~/.codex/skills` and `~/.claude/skills`. The research skills (`research-workflow` with its recording policy under `references/`, `experiment-ledger`, `obsidian-main-note`) live here too; the obsidian-main deployer manages only the research block and hooks. Host-local skill directories are never edited by hand.
- Host facts: `~/.codex/host-context.md` on each host. Hooks and settings: `~/.claude/settings.json`, `~/.codex/hooks.json`, host-local.
- Memory: Claude auto-memory under `~/.claude/projects/<cwd-key>/memory/`, Codex memory under `~/.codex/memories/`. Mandatory behavior never lives only in memory; promote it to AGENTS.md, a skill or host-context, then delete the memory note.

## Change a rule or skill

1. Start from evidence: the failure or correction, with thread and turn, and the sentence that should have prevented it. Do not adopt a rule set wholesale from a video or a repository; add the clause that earns its place and remove clauses that measured as unfollowed.
2. Keep AGENTS.md scoped: chat-reply style applies to chat only; procedures go to a skill or a reference file; host facts go to host-context. Target under 15k characters.
3. Edit the source checkout, not a linked copy. `git status` first; preserve other uncommitted work. Commit only when the user asks; never push without a request.
4. Propagate: fetch and fast-forward each host's `~/dot` and `~/agent-skills`, run the guidance-only installer, then grep skills, automations and per-project instruction files on every host for the old path or rule. A running session does not reload guidance; say that a new session is needed.
5. Verify on each host: the links resolve, the skill list loads (`ls ~/.claude/skills`, `ls ~/.codex/skills`), no `AGENTS.override.md` shadows the common file, and host-context has the facts the change relies on.

## Skills that encode user decisions

When the user adopts a rule for a skill or automation, record it verbatim with its date in the skill's `User decisions` section, read that section before editing or running the skill, and never drop or narrow an entry without asking. Edit skills in place (no delete-and-recreate), make automation prompts point to the skill instead of copying its rules, and before moving, renaming or deleting a skill or helper, search live automations and other skills for its path and update them in the same change.

## Evaluate an instruction or skill change

- Run A/B arms from a clean working directory with the candidate file loaded by an explicit path; include an empty-baseline arm and a probe that reports which file was loaded. Preflight the tool list of the client under test, log every tool call (not only shell commands), give every arm the same repetitions, quote the cost before starting, and add no arm without approval.
- Send-capable connectors (mail, Slack, calendar) and research recording are disabled for every arm; evaluation prompts carry the identifier restriction.
- Factuality is a hard gate; model judges are not human calibration. Report per-arm counts with the exact prompts and keep the arms under `inbox/<project>/arms/` with a task-state file.
- Stop when the completion criterion is met; score-chasing beyond it is waste.

## Instruction-source integrity

At session start on any host, `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md` must be symlinks to `~/dot/ai/codex/AGENTS.md` and `~/.codex/AGENTS.override.md` must not exist (Codex loads an override instead of, not alongside, the common file). `~/dot/bin/guidance-check` prints the state; wire it as a SessionStart hook on each host so drift is reported once per session. Codex auto-loads only the AGENTS.md chain with no imports; Claude Code loads CLAUDE.md plus its imports; rules that must always apply live in the AGENTS.md body, because skills and side files are read only when the model decides to.

## Health checks (model-free first)

- Obsidian gateway: `tailscale serve status` and `tailscale funnel status` on the home hub must show the Funnel binding recorded in host-context (443 to the gateway port); then one `investigation_context` read from each host; then `obsidian-research status` for a pending outbox. Replay only with a session filter.
- Tunnels and services: Zotero MCP, html-preview relay, KVPN monitor status (KAIST VPN Monitor app, `tools/kaist-vpn-monitor`). Record outages and root causes in host-context, not only in memory.
- Memory hygiene: delete notes that are wrong or superseded, keep one fact per note, and keep the index line consistent with the note.

## Verified additions (2026-10-17 audit)

- Evaluation results lead with per-arm wins, losses, ties and invalid judgments and the rule that decided adoption ("no candidate met <rule>", never "keep the original"); an adoption rule you set yourself is shown to the user with its expected pass rate before you spend on it. Rank arms with a blind pairwise judge that sees both orders, calibrated on a few of the user's own blind picks; counts of length, bullets or fences are regression guards, never the ranking; rerun one arm against itself for the noise band and confirm a winner once on held-out items. Inside a user-set goal or budget, add arms and report spend after each stage; ask only before a protocol change such as an acceptance-rule edit. Strip internal labels and field names from writer inputs and search drafts for them; trace where a reported defect came from before the next round.
- Gateway, plugin and hook changes: edit only in their git checkouts and deploy to the live service from a merged commit unless the user asks for a hotfix; before restarting, run the build in an isolated copy against recent real requests and new-feature cases (several sections, multi-line bodies, code fences); a bot-review loop gets its stop rule before the first push (fix findings touching the requested feature or data integrity; after two rounds, defer the rest and list them). Gateway maintenance may measure vault files and the journal read-only; every write still goes through `obsidian_main`.
- Memory: task progress, to-do lists and repair status go in a task-state file; a memory note may point to it but never holds it, and work unrelated to the folder's project gets no memory note there.

## Skill parity across hosts (2026-10-17 audit)

After any skill change, list `~/.claude/skills` and `~/.codex/skills` on every host and diff the names against the shared repository; a host missing a shared skill (manuscript-writing was absent on the lab server for a month) is fixed by the installer, never by an ad-hoc copy or by letting the agent fall back to an archived skill.

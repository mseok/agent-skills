---
name: harness-maintenance
description: "Maintain the agent harness across Antigravity (Gemini), Codex, and Claude Code: the dedicated AGY track in ~/dot/ai/gemini + ~/agent-skills/skills/gemini alongside the shared Codex/Claude track in ~/dot/ai/codex + ~/agent-skills/skills/codex, host-context files, hooks, and the Obsidian research gateway, and run instruction or skill A/B evaluations. Use when the user says 지침, AGENTS, CLAUDE.md, 플러그인, 스킬 정리, dotfiles, hook, 동기화, 하네스, 평가 harness, or when a rule or skill must change or reach another host. Not for ordinary project work."
---

# Harness maintenance (Antigravity + Codex/Claude)

## Where things live

- **Two guidance tracks (`~/dot`)**:
  - **Codex & Claude Code**: `~/dot/ai/codex/AGENTS.md` (linked from `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md` via `bin/install_codex.sh` and `bin/install_claude.sh`). Its top research block is managed by `obsidian-main/scripts/deploy-research.py` from `policies/research-router.md`.
  - **Antigravity / Gemini**: `~/dot/ai/gemini/` (`plugin.json`, plain-Markdown always-on `rules/AGENTS.md` at ~5–6 KB, progressive `trigger: model_decision` rule files under `rules/*.md`, plugin-root `hooks.json` + `hooks/agy_agent_guard.py`, and `mcp_config.template.json`), installed into `~/.gemini/config/plugins/migrated-settings/` via `~/dot/bin/install_gemini.sh` without ever touching `~/.gemini/config/config.json`. Keep the research-continuity invariants in `ai/gemini/rules/AGENTS.md` aligned whenever `policies/research-router.md` changes.
- **Skill scopes (`~/agent-skills/skills/`)**:
  - `skills/codex/` is the shared source for Codex and Claude (`skills/claude` is a link to `codex`).
  - `skills/gemini/` is the Antigravity skill scope (per the 2026-11-18 user decision): unchanged domain skills (`paper-writing`, `concept-figure`, `nature-figure`, `benchmark-comparison`, `html-research-deck`, `obsidian-*`, `research-workflow`, `experiment-ledger`, etc.) are **relative symlinks `../codex/<skill>`** so edits never fork across harnesses; Codex/Claude-only refusal workarounds (`bio-safe-reading`) and Claude TUI mods (`usage-progress`) are omitted; AGY-divergent harness skills (`harness-maintenance`, `thread-handoff`) live in `skills/gemini/<skill>/SKILL.md` while sharing `enforcement-ledger.md`.
  - `hwp-agent-edit` lives only in `/Volumes/ExternalSSD/inbox/hwp-local-editor/skills/hwp-agent-edit`; `install_gemini.sh` links it when that checkout is present on the host.
  - Every Obsidian vault rule lives only in `obsidian-agent-record/references/obsidian-policy.md`. Retired skills are deleted from Git, not archived. Host-local skill directories are never edited by hand.
- **Host facts & hooks**: `~/.codex/host-context.md` on each host (shared across all harnesses). Hooks and settings remain host-local (`~/.claude/settings.json`, `~/.codex/hooks.json`, `~/.gemini/config/hooks.json`); AGY plugin hooks live at `<plugin_dir>/hooks.json` using AGY's camelCase `toolCall.{name, args}` contract.

## Change a rule or skill

1. Start from evidence: the failure or correction, with conversation/turn and the clause that should have prevented it. Add only clauses that earn their place; remove clauses measured as unfollowed.
2. Pick the strongest enforcer first: architecture (one source of truth, relative symlinks, templates) -> hook or permission rule (`~/dot/bin/agent-guard` + `agy_agent_guard.py`) -> check script -> prose in `rules/AGENTS.md`, a `trigger: model_decision` rule, or a skill last. Prove a new hook or check fires on the recorded failure before adopting it, and update [references/enforcement-ledger.md](references/enforcement-ledger.md) in the same change.
3. Keep always-on guidance scoped: in AGY, `ai/gemini/rules/AGENTS.md` stays plain Markdown (no YAML frontmatter, ~4–6 KB, well inside the 24 KB per-file cap and 20,000-token `defaultRulesBudget`); situational procedures go to `trigger: model_decision` rules (YAML frontmatter `trigger: model_decision` + `description`) or skills; host facts go to `~/.codex/host-context.md`. Edit `ai/codex/AGENTS.md` too when a general user rule applies to Codex/Claude.
4. Edit the source checkouts (`~/dot`, `~/agent-skills`), never linked copies under `~/.gemini/config/plugins/`. Check `git status` first and preserve unrelated uncommitted work. Commit only when the user asks; never push without a request.
5. Propagate and verify:
   - Run `~/dot/bin/install_gemini.sh` (or `--guidance-only` for rules/hooks only). Never hand-edit `~/.gemini/config/config.json` or call restricted LS mutation RPCs (`JetboxWriteState`, `DeletePlugin`, `InstallCustomization`); surface `[Research Harness (AGY)](customization://migrated-settings)` when the user needs to toggle UI state.
   - Verify AGY plugin ingestion via the Language Server Connect endpoint (`lsrpc GetAllPlugins ... | jq`, **never** unfiltered, since unfiltered `GetAllPlugins` inlines every `SKILL.md`), confirming all rules, skills, hooks and MCP servers resolve with zero broken links.
   - When shared skills or rules also changed for Codex/Claude, fast-forward peer hosts (`git fetch origin` + `git merge --ff-only origin/main`), run `install_codex.sh --guidance-only` and `install_claude.sh --guidance-only`, and check `guidance-check` + `harness-status`.
6. Make no sidecar `.bak` backups beside harness files: Git tracks `~/dot` and `~/agent-skills`, and host-local changes record rollback details in the task's change record / restore manifest.

## Skills that encode user decisions

Record each user-adopted rule verbatim with its date in the skill's `references/user-decisions.md`, state the resulting rule plainly in `SKILL.md`, read `user-decisions.md` before editing any skill, and never drop or narrow an entry without asking. Keep domain skills as single-source entries in `skills/codex/<skill>` linked from `skills/gemini/<skill> -> ../codex/<skill>` unless AGY's native runtime genuinely diverges.

## Evaluate an instruction or skill change

- Run A/B arms from clean isolated directories with explicit instruction paths, an empty-baseline arm, equal repetitions, logged tool calls, and upfront cost quotes; disable send-capable connectors and research recording across arms, and include the verbatim English identifier restriction from `thread-handoff`.
- Spot-check automatic scorer pass/fail outputs before reporting rates; rank subjective quality with a calibrated order-swapped blind pairwise judge rather than length/bullet counts; stop once the completion criterion is met.

## Health checks (model-free first)

- Antigravity: Language Server `/healthz` + `GetAllPlugins | jq` inventory, symlink resolution under `~/.gemini/config/plugins/`, and verification that `~/.orca` dead hooks in `~/.gemini/config/hooks.json` are disabled so `PreToolUse` does not force `"decision": "ask"` on every tool call.
- Obsidian gateway & services: `tailscale serve status`, `tailscale funnel status` (Funnel 10000 -> 39123), `investigation_context` read via `obsidian_main`, `obsidian-research status` outbox check (session-filtered replay only), Zotero MCP, and `html-preview`.

## User decisions

The dated decisions behind these rules, in the user's own words, are in [references/user-decisions.md](references/user-decisions.md). Read it before editing this skill or when a rule's origin or scope is in doubt; record a new decision there and state the resulting rule in plain words in this file.

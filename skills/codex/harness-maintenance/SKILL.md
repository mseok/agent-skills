---
name: harness-maintenance
description: "Maintain the agent harness across Antigravity (Gemini), Codex, and Claude Code: the shared Codex/Claude track in ~/dot/ai/codex + ~/agent-skills/skills/codex alongside the dedicated Antigravity track in ~/dot/ai/gemini + ~/agent-skills/skills/gemini, host-context files, hooks, memory notes, and the Obsidian research gateway, and run instruction or skill A/B evaluations. Use when the user says 지침, AGENTS, CLAUDE.md, 플러그인, 스킬 정리, dotfiles, hook, 동기화, 하네스, 평가 harness, or when a rule or skill must change or reach another host. Not for ordinary project work."
---

# Harness maintenance

## Where things live

- **Two guidance tracks (`~/dot`)**:
  - **Codex & Claude Code**: `~/dot/ai/codex/AGENTS.md` (every host links `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md` to it via `~/dot/bin/install_codex.sh` and `~/dot/bin/install_claude.sh`). Its top research block is managed by `obsidian-main/scripts/deploy-research.py` from `policies/research-router.md`; edit both the router source and `AGENTS.md` identically, or redeploy, never one alone.
  - **Antigravity (Gemini)**: `~/dot/ai/gemini/` (`plugin.json`, plain-Markdown always-on `rules/AGENTS.md` at ~4–6 KB with no YAML frontmatter, progressive `trigger: model_decision` rule files under `rules/*.md`, plugin-root `hooks.json` + `hooks/agy_agent_guard.py`, and `mcp_config.template.json`), linked into `~/.gemini/config/plugins/migrated-settings/` via `~/dot/bin/install_gemini.sh` without ever reading or modifying `~/.gemini/config/config.json`. Keep research-continuity invariants in `ai/gemini/rules/AGENTS.md` aligned whenever `policies/research-router.md` changes.
- **Skill scopes (`~/agent-skills/skills/`)**:
  - `skills/codex/` is the canonical single source for shared skills (`skills/claude` is a link to `codex` so older Claude paths resolve); `install_codex.sh` and `install_claude.sh` link every skill into `~/.codex/skills` and `~/.claude/skills`.
  - `skills/gemini/` manages the Antigravity skill set separately (2026-11-18 user decision): all included skills are **relative symlinks `../codex/<skill>`** so procedures stay single-source across harnesses, while Codex/Claude-only entries (`bio-safe-reading`, `usage-progress`) are omitted. Whenever adding, renaming, or retiring a skill, update `skills/gemini/` in the same change and verify with `~/dot/bin/install_gemini.sh --check` and `scripts/check_obsidian_policy_sync.py`.
  - `hwp-agent-edit` lives only in the `hwp-local-editor` checkout (`skills/hwp-agent-edit`), which links it into `~/.codex/skills` and `~/.claude/skills` with `node scripts/install-skill.mjs --link` and into Antigravity via `install_gemini.sh` on hosts that carry that checkout; its absence elsewhere is expected.
  - Every Obsidian vault rule lives only in `obsidian-agent-record/references/obsidian-policy.md`; `obsidian-main` deploys only the research block and hooks. Retired skills are deleted from Git, not archived. Host-local skill directories are never edited by hand.
- **Host facts & hooks**: `~/.codex/host-context.md` on each host (shared across all harnesses). Hooks and settings stay host-local (`~/.claude/settings.json`, `~/.codex/hooks.json`, `~/.gemini/config/hooks.json`); Antigravity plugin hooks live at `<plugin_dir>/hooks.json` using camelCase `toolCall.{name, args}`.
- **Memory**: Claude auto-memory under `~/.claude/projects/<cwd-key>/memory/`, Codex memory under `~/.codex/memories/`. Mandatory behavior never lives only in memory; promote it to `AGENTS.md`, a skill, or `host-context.md`, then delete the memory note.

## Change a rule or skill

1. Start from evidence: the failure or correction, with thread/conversation and turn, and the clause that should have prevented it. Do not adopt a rule set wholesale from a video or repository; add only clauses that earn their place and remove clauses measured as unfollowed.
2. Pick the strongest enforcer before writing prose: architecture (one source of truth, relative symlinks, a template or tool, a persistent signing identity) -> hook or permission rule (`~/dot/bin/agent-guard` + `agy_agent_guard.py`) -> deterministic test or check script (`scripts/check_obsidian_policy_sync.py`, skill `scripts/check_*.py`) -> prose in `AGENTS.md`, a `trigger: model_decision` rule, or a skill last. Prove a new hook or check fires on the recorded failure before adopting it, update [references/enforcement-ledger.md](references/enforcement-ledger.md) in the same change, and delete prose that an enforcer made redundant.
3. Keep always-on guidance scoped: chat-reply style applies to chat only; situational procedures go to `trigger: model_decision` rules (in AGY) or skills/references; host facts go to `~/.codex/host-context.md`. Keep `ai/codex/AGENTS.md` under 15k characters and `ai/gemini/rules/AGENTS.md` plain Markdown (~4–6 KB, well inside AGY's 24 KB per-file cap and 20,000-token `defaultRulesBudget`).
4. Edit the source checkouts (`~/dot`, `~/agent-skills`), never linked copies. Run `git status` first and preserve unrelated uncommitted work. Commit only when the user asks; never push without a request.
5. Propagate across hosts: fast-forward each host's `~/dot` and `~/agent-skills` (`git fetch origin` + `git merge --ff-only origin/main`), run `install_codex.sh --guidance-only`, `install_claude.sh --guidance-only`, `migrate_agent_skills.sh`, and `install_gemini.sh` (or `--guidance-only`), then grep skills, automations, and per-project instruction files for any retired path or rule. Never hand-edit `~/.gemini/config/config.json` or call restricted Language Server mutation RPCs (`JetboxWriteState`, `DeletePlugin`, `InstallCustomization`); surface `[Research Harness (AGY)](customization://migrated-settings)` when the user needs to toggle UI state, and note when a new session is required to reload guidance.
6. Verify on each host: links resolve (`~/dot/bin/guidance-check`, `~/dot/bin/install_gemini.sh --check`, `~/dot/bin/harness-status`), skill directories load (`/bin/ls ~/.claude/skills`, `/bin/ls ~/.codex/skills`, and in AGY `lsrpc GetAllPlugins ... | jq`—**never** unfiltered, because unfiltered `GetAllPlugins` inlines every `SKILL.md`), no `~/.codex/AGENTS.override.md` exists, `scripts/check_obsidian_policy_sync.py` exits `0`, and `host-context.md` records the facts the change relies on.
7. Make no sidecar `.bak` backups of harness changes: Git tracks `~/dot` and `~/agent-skills`, and host-local file edits record rollback details in the task's change record or restore manifest instead of copying files beside live config.

## Skills that encode user decisions

When the user adopts a rule for a skill or automation, record the decision verbatim with its date in the skill's `references/user-decisions.md`, state the resulting rule plainly in `SKILL.md`, read `user-decisions.md` before editing the skill, and never drop or narrow an entry without asking. Edit skills in place (no delete-and-recreate), keep `skills/gemini/<skill> -> ../codex/<skill>` relative symlinks in sync, make automation prompts point to the skill instead of copying rules, and search live automations and skills before moving, renaming, or deleting any skill or helper.

## Evaluate an instruction or skill change

- Run A/B arms from clean isolated working directories with the candidate file loaded by explicit path; include an empty-baseline arm and a file-loaded probe, preflight the client's tool list, log every tool call (not only shell commands), give every arm equal repetitions, quote cost upfront, and add no unapproved arm outside a user-set budget.
- Disable send-capable connectors (mail, Slack, calendar) and research recording for every arm, set `AGY_UNATTENDED=1` in Antigravity runs so the `gmail` CLI plugin hard-blocks outbound mutations, and paste the verbatim English identifier restriction from `thread-handoff`.
- Factuality is a hard gate; spot-check pass and fail outputs of any automatic scorer before reporting counts or rates (until then the number is a draft). Keep arms under `inbox/<project>/arms/` with `codex-task-state`, and stop once the completion criterion is met.

## Instruction-source integrity

At session start on any host, `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md` must symlink to `~/dot/ai/codex/AGENTS.md`, `~/.codex/AGENTS.override.md` must not exist, and (where Antigravity is installed) `~/.gemini/config/plugins/migrated-settings/` must pass `~/dot/bin/install_gemini.sh --check`. `~/dot/bin/guidance-check` checks session-start links; rules that must always apply belong in `AGENTS.md` (`ai/codex/AGENTS.md` and `ai/gemini/rules/AGENTS.md`), because skills and `model_decision` rules load on demand.

## Health checks (model-free first)

- Antigravity: Language Server `/healthz` + `lsrpc GetAllPlugins ... | jq` inventory, `~/dot/bin/install_gemini.sh --check`, and confirmation that dead `~/.orca` hooks in `~/.gemini/config/hooks.json` remain `enabled: false` so `PreToolUse` does not force `"decision": "ask"` on every tool call.
- Obsidian gateway & services: `tailscale serve status` and `tailscale funnel status` on the home hub (Funnel `10000` -> gateway `39123`), one `investigation_context` read per host, `obsidian-research status` outbox check (session-filtered replay only), Zotero MCP, `html-preview`, and KVPN monitor (`tools/kaist-vpn-monitor`). Record outages and root causes in `host-context.md`, not only in memory.
- Memory hygiene: delete wrong or superseded notes, keep one fact per note, and keep the index line consistent with the note.

## Verified additions (2026-10-17 audit)

- Evaluation reports lead with per-arm wins, losses, ties, invalid judgments, and the rule that decided adoption (`"no candidate met <rule>"`, never `"keep the original"`); show self-set adoption rules with expected pass rates before spending. Rank subjective quality with a calibrated order-swapped blind pairwise judge (length, bullets, and fences are regression guards, never rankings); rerun one arm against itself for the noise band and confirm a winner once on held-out items. Within a user-set budget, report spend after each stage and ask only before protocol changes. Strip internal labels and field names from writer inputs, search drafts for them, and trace defects before the next round.
- Gateway, plugin, and hook changes: edit only in git checkouts and deploy from merged commits unless the user asks for a hotfix; test in an isolated copy against recent real requests and multi-section, multi-line, code-fence cases before restarting; set a two-round bot-review stop rule before the first push (fix feature or data-integrity findings, then defer and list the rest). Maintenance may measure vault files and the journal read-only while writes still go through `obsidian_main`.
- Memory: task progress, to-do lists, and repair status belong in `codex-task-state` (a memory note may point to it, never hold it), and unrelated work gets no memory note in a project folder.

## Skill parity across hosts (2026-10-17 & 2026-11-18)

After any skill change, run `/bin/ls ~/.claude/skills`, `/bin/ls ~/.codex/skills`, `~/dot/bin/install_gemini.sh --check`, and `~/dot/bin/harness-status` across hosts to confirm parity against `~/agent-skills/skills/{codex,gemini}`; fix missing links through the maintained installers, never ad-hoc copies.

## User decisions

The dated decisions behind these rules, in the user's own words, are in [references/user-decisions.md](references/user-decisions.md). Read it before editing this skill or when a rule's origin or scope is in doubt; record a new decision there and state the resulting rule in plain words in this file.

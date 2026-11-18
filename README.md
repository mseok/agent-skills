# Personal agent skills

Source repository for reusable personal skills. Edit these files here; installed
skill directories and legacy dot paths point to this checkout.

For the shareable macOS KAIST VPN automation, see
[KAIST VPN Monitor Community](tools/kaist-vpn-monitor/README.md)
for setup, requirements, and validation limits.

- `skills/codex/`: shared skill source installed for both Codex and Claude, including `nature-figure` and `html-research-deck` (talk storylines and HTML slide decks; PPTX decks in the dissertation style on request, with the Pretendard font bundled under `assets/pptx/fonts` and installed automatically).
- `skills/codex/usage-progress/`: a Claude Code plugin, not a skill; it has no `SKILL.md`, so only the link in `~/.claude/skills` loads it.
- `skills/claude`: a link to `skills/codex`, kept so that older paths resolve across the shared Codex/Claude scope.
- `skills/gemini/`: dedicated Antigravity (Gemini) skill scope (since 2026-11-18). Unchanged domain skills are relative symlinks (`../codex/<skill>`) to `skills/codex` so domain edits never fork across harnesses; Antigravity-divergent harness skills (`harness-maintenance`, `thread-handoff`) live here directly while linking shared references, and Codex/Claude-only entries (`bio-safe-reading`, `usage-progress`) are omitted.
- Retired skills are deleted, not archived; recover one from the Git history when it is needed again.
- `skills/codex/verification-before-completion/`: adapted from obra/superpowers at commit `8ca22db` (MIT; its `LICENSE` is kept beside the skill). Since 2026-11-13 the upstream general sections are condensed into one paragraph and one table; the tables below them are this repository's own.
- `hwp-agent-edit` is not in this repository (since 2026-11-13). Its only source is `skills/hwp-agent-edit` in the hwp-local-editor checkout, which links it into `~/.codex/skills` and `~/.claude/skills` with `node scripts/install-skill.mjs --link` (and into Antigravity via `~/dot/bin/install_gemini.sh`); a host has the skill only where that checkout is installed.

Codex and Claude share one scope (`skills/codex`, since 2026-11-10), while `skills/gemini/` manages the Antigravity scope separately (since 2026-11-18) using relative symlinks for shared domain skills.

## Install or migrate

With the companion dot checkout available:

```bash
~/dot/bin/migrate_agent_skills.sh --destination ~/agent-skills --dry-run
~/dot/bin/migrate_agent_skills.sh --destination ~/agent-skills
```

For Antigravity (Gemini), link and verify `skills/gemini/` with:

```bash
~/dot/bin/install_gemini.sh
~/dot/bin/install_gemini.sh --check
```

The installer links individual skills under `~/.codex/skills` and
`~/.claude/skills` and removes links left by deleted or moved skills. It preserves host-owned `.system` skills and unrelated
plugins. `AGENT_SKILLS_HOME` overrides the default source checkout location.
The normal dot Codex installer invokes the same migration.

For another machine, clone the public repository first, then run migration:

```bash
git clone https://github.com/mseok/agent-skills.git ~/agent-skills
~/dot/bin/migrate_agent_skills.sh
```
Without this checkout, dot can bootstrap its formerly tracked skills from its
own local Git history, but cannot recover skills that were never committed on
that machine. The public source is https://github.com/mseok/agent-skills.

## Repository boundary

Commit skill instructions, helper source, reference documents, and lightweight
test fixtures. Keep actual research outputs in their projects/artifact stores.
Do not commit app-managed system skills, plugin caches, credentials, installed
fonts, Python environments, or generated font caches.

Initial extraction includes the two untracked personal Codex skills
`ivanti-daily-login` and `nature-figure`. Original files are backed up in the
host-local `~/.local/state/agent-skills-migration/` directory. The original
tracked history remains in dot; this repository begins with an extracted
snapshot, not a rewritten copy of that history.

# Personal agent skills

Source repository for reusable personal skills. Edit these files here; installed
skill directories and legacy dot paths point to this checkout.

For the shareable macOS KAIST VPN automation, see
[KAIST VPN Monitor Community](tools/kaist-vpn-monitor/README.md)
for setup, requirements, and validation limits.

- `skills/codex/`: every skill, installed for both Codex and Claude, including `nature-figure` and `research-talk` (slide decks in the dissertation style; Pretendard font bundled under `assets/fonts`, installed automatically).
- `skills/codex/usage-progress/`: a Claude Code plugin, not a skill; it has no `SKILL.md`, so only the link in `~/.claude/skills` loads it.
- `skills/claude`: a link to `skills/codex`, kept so that older paths resolve. There is one scope; do not add a second directory.
- Retired skills are deleted, not archived; recover one from the Git history when it is needed again.
- `skills/codex/verification-before-completion/`: copied unchanged from obra/superpowers at commit `8ca22db` (MIT; its `LICENSE` is kept beside the skill).

Skills are not grouped by agent (since 2026-11-10): a skill that only one harness can
use says so in its own description.

## Install or migrate

With the companion dot checkout available:

```bash
~/dot/bin/migrate_agent_skills.sh --destination ~/agent-skills --dry-run
~/dot/bin/migrate_agent_skills.sh --destination ~/agent-skills
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

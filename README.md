# Personal agent skills

Source repository for reusable personal skills. Edit these files here; installed
skill directories and legacy dot paths point to this checkout.

- `skills/codex/`: 7 personal Codex skills, including `nature-figure`.
- `skills/claude/`: 12 personal Claude skills.

Keep the existing agent-specific grouping during migration. Shared capabilities
can be consolidated later after checking their instructions and callers.

## Install or migrate

With the companion dot checkout available:

```bash
~/dot/bin/migrate_agent_skills.sh --destination ~/agent-skills --dry-run
~/dot/bin/migrate_agent_skills.sh --destination ~/agent-skills
```

The installer links individual skills under `~/.codex/skills` and
`~/.claude/skills`. It preserves host-owned `.system` skills and unrelated
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

# User decisions

Dated decisions of the user behind this skill's rules, in the user's own words. Read this file before editing the skill or when the origin or scope of a rule is in doubt. Add each new decision here with its date; never drop or narrow an entry without asking the user.

## User decisions

- 2026-11-10 (ChatGPT app, Claude chat 01a1c3bb-3572-7cd3-990c-7dccc5a119e4): one skill scope. User's words: "codex/, claude/ skill 을 굳이 나누지말고 한 쪽을 다른쪽의 shallow link 로 대체하는게 좋을 것 같은데." It followed the finding that a skill kept in the Claude-only scope was invisible to Claude models running in the ChatGPT app.
- 2026-11-10 (same chat): unused skills are deleted. User's words: "skill 중에 안 쓰는건 지워도될거같고". Applied to the retired skills under `archive/`; every installed skill had been opened at least once since 2026-10-17 and stayed.
- 2026-11-10 (same chat): no sidecar backups for harness changes. User's words: "백업 굳이 안해도될듯. 기존에 많이 있던 백업도 다 없애주라 이거관련된거만". Files under Git (dot, agent-skills) roll back through Git; a change to a host-local file (hook settings, host-context) is described in the task's change record instead of being copied beside the file.
- 2026-11-10 (same chat): decision records live in references/user-decisions.md. Asked whether to move the decision sections out of SKILL.md into a reference file per skill (about 8% less text on every skill load, records kept for edits), the user answered: "추천 ㄱㄱ".

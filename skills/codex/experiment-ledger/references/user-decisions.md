# User decisions

Dated decisions of the user behind this skill's rules, in the user's own words. Read this file before editing the skill or when the origin or scope of a rule is in doubt. Add each new decision here with its date; never drop or narrow an entry without asking the user.

## User decisions

- 2026-11-13: until this date the skill said "committing happens only when the user asks". After a review of the user's research code found script copies kept where a commit would have preserved the code state, the user was asked whether agents may commit the files they changed locally without a request, with pushes still on request, and answered: "좋아. 그렇게 하자. 그리고 git directory가 너가말한거처럼 쓸데없는 파일들로 인해서 너무 커지지 않도록 잘 조절하는 것도 조건으로 넣자." The agent therefore commits the files it changed for a run, by path, before launch; a push needs a request; the repository stays small under the rule in AGENTS.md (Environment and tools).

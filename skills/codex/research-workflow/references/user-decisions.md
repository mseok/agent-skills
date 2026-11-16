# User decisions

Dated decisions of the user behind this skill's rules, in the user's own words. Read this file before editing the skill or when the origin or scope of a rule is in doubt. Add each new decision here with its date; never drop or narrow an entry without asking the user.

## User decisions

- 2026-11-16: On why `Inbox/Agents/` was created and how question reports should avoid biasing later agents while remaining useful across sessions and subagents: `"애초에 inbox/  는 agent 들이 읽게 하는걸 목표로 하고 있었어. 그게 잘 되고 있냐는거지."` `"내 질문에 답하거나 자기들끼리 얘기할 때 잘 사용하는지가 궁금하다는 것."` On leading the top synthesis with `## 현재 판단과 다음 행동`: `"이런거에 너무 bias 걸릴거같아서 그랬엇는데."` On splitting `investigation_id` when a project moves to a new stage/subdirectory and passing `Inbox/Agents/` paths to subagents/peer sessions: `"이런건 실제로 필요해보이네."` `"그래 둘다해봐"`. Keep the question report synthesis bias-free (`사용자 확정 조건` + `실행된 배치 및 단건 기록 색인`), keep agent interpretations/proposals in dated events, split `investigation_id` by distinct stage or subdirectory, and pass `Inbox/Agents/` record paths or `investigation_id` when delegating to subagents or peer threads (unless blind isolation is required).
- 2026-11-11: "그 기록 때문에 다음 에이전트도 작업을 포기하면 안 되잖아." "그리고 앞으로 obsidian 에 작업 금지에 대한 내용은 적어두지 않는다고 skill? 도 수정해줘." Apply the canonical incident-recording rule in obsidian-agent-record/references/obsidian-policy.md section 7 when resuming and capturing research work.
- 2026-11-05: "ㅇㅇ 그럼 1~3번부터 적용하고 검증까지 ㄱㄱ." Apply project/question linking, invocation-bound recording and session-filtered replay on Mac mini and messi. Server-context execution gates are outside this change.

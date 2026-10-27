# User decisions

Read this file before editing the skill; never drop or narrow an entry without asking the user. Entries are verbatim, with their date. Writers do not need this file.

- 2026-10-18, goal: "완전히 from scratch부터 논문 writing skill or instruction 만들기. Nature 계열(바이오는 보지 마)이나 3대 AI 학회 오랄급 논문들."
- 2026-10-18, requirements:
  1. "nature 계열 논문들에서 뻔한 흐름보다 확실한 차이점을 강조하면서도 읽기 쉽게 작성되어야"
  2. "디테일한 것과 그렇지 않은 것을 잘 구분해야함."
  3. "보고서 같은 말투 (e.g. 이런건 아직 확인되지 않음 ..) 이런건 절대 쓰면 안되지 학술 논문에."
  4. "결과를 좋은 건 엄청 좋고, 안 좋은건 좀 드러나지 않도록 써야함."
- 2026-10-18: "기본적으로 미국식 영어를 써주도록 해 앞으로는."
- 2026-10-18, on the planning and briefing steps: "내 생각에는 너가 작성 agent 들에게 준 prompt 를 만들 수 있는 skill 이 있으면 좋을듯. 그리고 지금 우리 슬라이드 스킬처럼 논문의 방향을 같이 논의하는 순간이 있으면 좋겠음 그런거 할 때."
- 2026-10-18, on replacing manuscript-writing: "2번으로 하면 될듯. 그리고 manuscript writing 없애고 paper writing 만 남겨서 사용하자." The revision and live-manuscript rules of manuscript-writing (its 2026-10-17 audit additions included) were ported into references/revision.md.
- Acceptance test used for this skill: blind pairwise picks by the user, passing at "9쌍 중 7쌍 이상에서 스킬 쪽 선택(비김은 스킬 선택으로 세지 않음)". Round 3 on held-out papers: 9 of 9.
- 2026-10-18, on the retained-config rule ported from manuscript-writing: "1번은 동의 초안에도 넣어야할듯." The rule is in references/methods.md (new drafts) and references/revision.md (revisions).
- 2026-10-27, on the three Results-writing improvements: "그럼 그 세 가지를 paper-writing 스킬에 반영해줘. 원고는 건드리지 말고, 항체 사례를 예시로 개선 전후 차이도 보여줘." The accepted proposal covers paragraph-level Results planning, the explanation a case adds beyond aggregate performance, and semantic review separate from the prose checker. The antibody example is an illustration for the user, not authorization to edit the manuscript or a requirement to make the shared skill biology-specific.
- 2026-10-28, on integrating the paper and learning editorial choices from examples: "하나의 논문, 그에 대한 얘기하고 싶은 논문의 한 문장 요약을 기준으로 이제 모든 내용들이 다 같이 얼라인될 수 있게 하는 게 제일 좋겠다"; "지금 너가 보고서식 논문식 이렇게 예시 들어준 게 제일 좋은 것 같아서 저런 예시 같은 거를 그냥 그 스킬을 쓸 때마다 좀 참고할 수 있게". Approval: "좋아. 그러면 그렇게 업데이트를 해보면 될 것 같은데 스킬을." This adopts a final whole-paper integration pass, selection of facts and limitations by their role in the actual argument, and four required contrasting examples with facts, report-like prose, paper-like prose and the editorial decision explained. Manuscript editing is outside this approval.

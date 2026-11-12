# 스토리라인도 직접 쓰는 빌드 (추가 지시, 위 지시문보다 우선)

이번 시험에는 승인된 스토리라인이 없다. 논문을 이 모델이 직접 읽고 `work/storyline-v1.json`을 먼저 쓴 뒤, 같은 내용을 `work/storyline.json`으로 복사하고 덱을 만든다. 위 지시문의 "승인된 스토리라인"과 `work/storyline*.json` 수정 금지는 이 두 파일을 처음 쓰는 일에는 적용되지 않는다. 다 쓴 뒤에는 장의 `id`, `role`, `evidence`를 바꾸지 않는다. 사용자 승인 단계는 이 시험에서 건너뛴다.

- 청중과 길이: 연구실 논문 세미나, AI·구조생물학·신약개발 연구자, 언어 한국어, **20장**. 표지에는 논문 제목과 저자, "논문 세미나 · 문석현"을 적는다.
- 파일 형식: `references/storyline-format.md`의 필드에 `closing`(마무리줄)과 `glossary`를 더한다. `slides[]`는 `id`(s01…s20), `role`, `title`, `message`, `evidence`, `visual`, `closing`, `transition`을 갖는다. `role`은 title, question, background, method, setup, result, limitation, conclusion 가운데서 고른다. `evidence`에는 논문 위치(§, eq., Table, Fig., Appendix)를 적는다. `status`는 "approved", `approval`은 {"user_reference": "빌더 자체 작성, 승인 없음"}으로 둔다.
- 흐름: `message-style.md`를 따른다. 청중이 아는 상황으로 여는 고리, 왜 이 청중에게 중요한가, 방법의 뼈대, 발견의 축적, 조건과 한계, 우리에게 주는 뜻 순서다. 킥커의 섹션은 6개 이내다.
- `glossary`: 이 논문의 핵심 용어 10개 이상을 항목마다 `use`(논문의 영어 표기), `avoid`(쓰지 않을 번역어 목록), `why`로 적는다.
- 마지막 장의 질문 패널은 사용자가 발표마다 직접 쓰는 자리이므로 그 장에 `"owner": "user"`를 두고, 내용 헤더와 질문 2–3개만 둔다.
- 사용자 지시(2026-11-02) "그냥 각 모델로 해주라": 이 시험에서는 논문을 이 모델이 직접 읽는다. 생물·화학 자료를 다른 모델에 넘겨 읽게 하는 위임을 적용하지 않고, 하위 에이전트도 쓰지 않는다. 안전 거부가 나오면 우회하지 말고 어느 파일에서 멈췄는지 보고한다.
- 보고에 스토리라인을 어떤 순서로 짰는지와 뺀 내용을 두 줄로 덧붙인다.

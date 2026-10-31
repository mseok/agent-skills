# 빌더 실행 지시문 — 메시지 goal (Claude Opus 5.5 max)

당신은 `html-research-deck` 스킬로 만든 HTML 발표 덱의 **문구**를 `references/rubric-message.md`에서 더 높은 점수로 끌어올리는 빌더다. 디자인은 사용자가 "이제 좋네"라고 했으므로 그림·격자·글자 크기는 건드리지 않는 것이 원칙이고, 디자인 점수(`deck/qa/score.json`, `rubric.md`)가 90 아래로 떨어지면 그 반복은 실패다. 먼저 `references/message-style.md`를 읽는다 — 레퍼런스 덱이 어떤 말투로 어떤 것을 강조하는지와 우리 덱에 옮기는 규칙 10개가 거기 있다.

작업 폴더에 `work/build.py`(덱 조립; 모든 문구와 노트가 여기 있음), `deck/index.html`(산출물), `deck/qa/score-message.json`(최근 메시지 점수와 세부 측정값: 어느 장의 제목이 왜 깎였는지, 풀이 없는 용어가 무엇인지), `deck/qa/judge-msg-*.json`(독립 심사 — 가장 최근 파일의 `judge.slides[].evidence`, `judge.deck`), `deck/qa/score.json`(디자인 점수), `deck/qa/judge-*.json`(디자인 심사), `work/storyline.json`(스토리라인; id·역할·증거는 고정, 제목·메시지·마무리줄은 바꿀 수 있음), `paper/text-flow.txt`·`paper/tables.txt`(논문 본문·표)가 있다. 스킬은 `~/.claude/skills/html-research-deck/`.

절차:
1. `deck/qa/score-message.json`의 `detail`에서 만점이 아닌 측정 항목과 그 장을 확인하고, 가장 최근 `judge-msg-*.json`의 장별 근거와 덱 단위 근거(N3 서사, N5 정직)를 읽는다. 디자인 심사의 G(한 장 한 메시지)·J(글 양) 근거도 읽는다 — 문구를 바꾸면 그 둘이 움직인다.
2. 감점이 큰 순서로 고친다. 대상은 킥커, 제목, 레인 헤더, 장면 안 라벨, 마무리줄, 인용줄, 노트다.
   - 제목: 주제 + 요점, 명사구, 34자 이내, 절 이름 접두사("결과 1:")와 변수 나열 금지. 콜론형 허용.
   - 킥커: "섹션 · 소주제", 섹션은 6개 이내로 덱 전체가 목차가 되게.
   - 마무리줄: 교훈 한 문장 또는 증거 숫자 하나, 12–48자, 숫자 2개 이하, 제목 되풀이 금지, 굵은 구절 하나까지(`<b>…</b>` 허용).
   - 용어: 첫 등장 장에서 괄호·`=`로 한국어 풀이. 루브릭 코드는 말로. 논문 위치 표기는 인용줄에만.
   - 길잡이: 2–4장 안에 "이 발표: …" 약속 문장, 2–3장 안에 청중 고리(우리 연구실의 데이터도 생존자 표본이라는 식), 마지막 장은 "우리에게 주는 뜻".
   - 정직: 모식·좌표값·발표자 해석은 화면에 표시. 논문 범위(30개 모델, 14개 시나리오, 이 게임)를 넘는 일반화 금지. 저자 주장과 발표자 생각을 섞지 않는다.
   - 노트: 출처 인용은 유지하고, 그 장을 말할 첫 문장과 다음 장으로 넘어가는 문장을 덧붙인다.
3. 그림 요소의 라벨을 바꿀 때는 글자 수가 늘어 패널 밖으로 나가거나 겹치지 않게 한다. 레이아웃을 바꿔야 한다면 최소로, `check_layout.py` 0 오류·0 경고를 유지한다.
4. `work/build.py`만 고친다. 그런 다음 반드시 실행: `python3 work/build.py`, `python3 ~/.claude/skills/html-research-deck/scripts/check_deck.py deck/index.html`, `python3 ~/.claude/skills/html-research-deck/scripts/check_layout.py deck/index.html --quiet`, `python3 ~/.claude/skills/html-research-deck/scripts/score_message.py deck/index.html --out /tmp/score-message-check.json --storyline-v1 work/storyline-v1.json`(측정 항목만 — 심사 없이 측정 50점 중 몇 점인지와 detail을 본다), `sh ~/.claude/skills/html-research-deck/scripts/shots.sh deck/index.html deck/qa/shots-full 1`. 고친 장의 PNG를 열어 눈으로 확인한다.
5. 마지막에 바꾼 장과 문구(제목·마무리줄 전후), 측정 점수 줄, 남은 경고를 짧게 보고한다. 심사와 최종 점수는 호출자가 한다(직접 점수를 주장하지 않는다).

금지: `references/`, `scripts/`, `deck/qa/judge*.json`, `deck/qa/score*.json`, `work/storyline*.json` 수정(스토리라인은 호출자가 덱에서 다시 스냅샷한다); 슬라이드 삭제·병합·추가; 출처 없는 수치 추가; 노트에 없는 숫자를 화면에 추가; 그림 재설계(문구 때문에 꼭 필요한 최소 조정만); 하위 에이전트 생성; 네트워크·GUI 사용.

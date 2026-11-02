# 빌더 실행 지시문 — 처음부터 만들기 (동등성 시험용; 모델 무관)

당신은 `html-research-deck` 스킬로 논문 세미나 덱을 **처음부터** 만드는 빌더다. 스킬 폴더와 작업 폴더의 절대 경로는 호출자가 이 지시문 아래에 적는다. 같은 지시문·같은 입력으로 여러 모델이 각자 덱을 만들고, 호출자가 같은 채점표와 같은 심사자로 잰다 — 그러니 지시문에 없는 것을 추측해 더하지 말고, 스킬 문서의 규칙을 그대로 따른다.

먼저 읽을 것(순서대로, 한 번씩): `SKILL.md`, `references/design-system.md`, `references/qa.md`, `references/message-style.md`, `references/rubric.md`와 `references/rubric-message.md`의 **측정 항목** 표(심사 항목은 호출자가 별도 모델로 잰다 — 점수를 스스로 주장하지 않는다).

입력(작업 폴더 안):
- `paper/` — 논문 PDF·HTML, `text-flow.txt`(본문), `tables.txt`(표와 그림 캡션), `pages/`(쪽 PNG), `context-for-judge.txt`(초록). 모든 숫자는 여기 인쇄값에서만 가져온다. 그림 좌표에서 읽은 값은 인용줄에 "그림 좌표에서 읽음"으로 표시한다.
- `work/storyline-v1.json` — 승인된 스토리라인. 장 수와 각 장의 `id`·`role`·`evidence`는 고정(장을 지우거나 합치거나 더하지 않는다). `title`·`message`·`closing`·`visual`은 `message-style.md`에 맞게 다듬을 수 있다. `glossary`의 `use` 표기만 쓰고 `avoid` 표기는 화면에 두지 않는다. `owner: user`인 장은 내용 헤더와 질문 2–3개만 둔다("여기부터는 발표자 생각" 같은 헤더 금지 — 사용자가 발표마다 직접 쓰는 자리).

산출(작업 폴더 안):
- `work/build.py` — 덱 조립 스크립트. 모든 문구·숫자·노트가 여기에 있고, 실행하면 `deck/index.html`을 다시 쓴다.
- `deck/` — `scripts/new_deck.py`로 스캐폴드한 뒤 `build.py`가 채운 결과(`css/`, `js/`, `vendor/`, `assets/figs/`, `index.html`).
- `deck/qa/` — `check.json`, `layout.json`, `shots/`(0.5배), `shots-full/`(1배), `contact.png`, `deck.pdf`, `copy.txt`·`copy.json`, `copy-lint.txt`, `fact-check.md`(장별로 화면에 보이는 숫자·비교·주장과 그 출처 위치).

규칙(스킬 문서가 우선; 여기는 요약):
- 언어는 스토리라인의 언어(한국어). 단 맥락 의존 학술 용어(prior, score, drift, ELBO, interpolant, encoder, gradient 등)는 논문이 쓰는 영어 원어로 쓰고 번역어나 비유로 바꾸지 않는다(`message-style.md` 규칙 4; 라벨도 같다, 조사는 영어 발음에 맞춘다). 제목은 명사구 폭 34자 이내(라틴 글자와 숫자는 0.6자로 셈), 콜론 구문("A: B")과 숫자 없는 괄호 태그 금지, 저자·발표자·모식·번역 표시는 인용줄에만. 마무리줄은 한 문장 폭 12–48자, 숫자 2개 이하.
- 그림은 흰 패널 없이 따뜻한 무대 위에 바로 놓는다(`design-system.md` Stage first). `panel`은 투명하고, 흰색은 수식 하나(`.fx.box`), 여러 칸 중 작은 차트 하나(`.panel.card`), 마무리줄처럼 한 항목만 담는 카드에만 쓴다.
- 유도나 정의를 말하는 장에는 논문의 식을 화면에 둔다. 단계 이름만 적은 상자 사슬로 바꾸지 않는다. 한 관계식은 한 줄에 쓴다. 카드를 넓히거나 24 px까지 줄이고, 줄바꿈은 서로 다른 식 사이에서만 한다(`design-system.md` Formulas).
- 수식·첨자·그리스 문자는 KaTeX `.fx` 블록(유니코드 첨자를 SVG 글자에 넣지 않는다). 분포는 `scripts/density.py`의 `cloud()`, 경로는 `bridge()`로 계산해 그린다(손으로 그린 블롭, 점선 타원, 분포를 두른 선 금지; `design-system.md` Distributions). 분자·PDB 구조는 이 덱에 없으면 넣지 않는다.
- 장면 글자 ≥ 22px(회색 참고 표기는 19px 이상, 색은 테마 `--muted`), 패널당 설명 줄 ≤ 3, 슬라이드당 설명 글자 ≤ 220자, 모든 내용 장에 그림 패널(그림이 패널 안면적의 30% 이상). 사슬의 화살표마다 변화 라벨, 같은 행위자는 같은 모양·색, 차트는 숫자로 그리고 값 라벨을 단다.
- 인용줄은 내용 장마다 출처 위치(§·Table·Fig.·Appendix)를 적고, 노트는 수치 출처 인용(200자 이상)과 말할 대본 첫 문장·전환 문장을 담는다.

절차:
1. `python3 <스킬>/scripts/new_deck.py <작업 폴더>/deck --title "…" --lang ko --slides title,figure,closing`으로 스캐폴드.
2. 스토리라인을 읽고 장마다 "이 그림 하나가 보여 줘야 할 것"(등장 인물·상태 변화 2–3칸)을 정한 뒤 `work/build.py`를 쓴다. 기존 덱의 빌더 패턴(`fx()`·`tex()`·`panel()`·`dens()`)은 `references/design-system.md`에 설명돼 있다.
3. `python3 work/build.py` → `python3 <스킬>/scripts/check_deck.py deck/index.html --json deck/qa/check.json` → `python3 <스킬>/scripts/check_layout.py deck/index.html --json deck/qa/layout.json`: **오류 0**이 될 때까지 고친다. 경고는 고치거나 보고에 사유를 적는다.
4. `sh <스킬>/scripts/shots.sh deck/index.html deck/qa/shots-full 1`로 전장 PNG를 만들고 **모든 장을 직접 열어 본다** — 글자가 선과 겹치거나 튀어나오는 곳, 렌더링 안 된 `$…$`, 빈 띠, 어긋난 정렬을 고치고 다시 찍는다.
5. `sh <스킬>/scripts/shots.sh deck/index.html deck/qa/shots 0.5`, `sh <스킬>/scripts/contact_sheet.sh deck/qa/shots deck/qa/contact.png 5`, `sh <스킬>/scripts/export_pdf.sh deck/index.html deck/qa/deck.pdf`, `python3 <스킬>/scripts/deck_copy.py deck/index.html --json deck/qa/copy.json --text deck/qa/copy.txt`, `python3 <스킬>/scripts/copy_lint.py --json deck/qa/copy.json > deck/qa/copy-lint.txt`.
6. `deck/qa/fact-check.md`를 쓴다: 장마다 화면의 숫자·비교·주장 → 논문 위치. 출처가 없는 숫자는 화면에서 뺀다.
7. 보고: 만든 장 수, check_deck/check_layout 마지막 줄, 남은 경고와 사유, 눈 검토에서 고친 것, 시간이 모자라 못 한 것.

금지: 게시(`publish.py`)·네트워크·웹 검색; 하위 에이전트; 스킬 폴더(`scripts/`, `references/`, `assets/`) 수정; `work/storyline*.json` 수정; 점수 파일(`score*.json`, `judge*.json`) 생성; 출처 없는 수치. 시간 예산은 2시간 30분 — 넘길 것 같으면 검사 통과 상태로 마무리하고 미완을 보고한다.

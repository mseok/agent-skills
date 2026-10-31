# 메시지·문구 기준: 레퍼런스 덱에서 읽어 낸 발표 말투 (2026-10-31)

레퍼런스: Yuanqi Du, *A New Era of Molecular Simulation via Neural Samplers* (yuanqidu.github.io/blog/a-new-era-of-molecular-simulation/, 40장, 2026). 아래 인용은 그 덱의 HTML에서 그대로 뽑은 것이다(`extract_copy.py` 덤프 기준). 사용자 피드백(2026-10-31): "멘트같은것들이 내가보기에는 너무 technical 해보이고 academic paper or work 를 발표하는 스타일은 아닌거같은데" — 즉 지금 덱은 논문 요약 말투이고, 발표 말투가 아니다. 이 문서는 레퍼런스가 무엇을 어떻게 말하는지 정리하고, 거기서 우리 덱(한국어, 논문 세미나)에 옮길 규칙을 고정한다. 점수화는 `rubric-message.md`.

## 1. 레퍼런스가 하는 일 (관찰)

**구조.** 표지 → 공동 저자(논문 2편의 제목·저자·arXiv) → 로드맵("Today", 다섯 부분마다 한 줄짜리 *왜*: "why ensembles stay expensive, even with machine-learned potentials") → 문제 3장 → 방법 10장 → Part I (논문 1) → Part II (논문 2) → 요약 표 → 한 문장 결론 → 열린 문제 → 감사. 킥커는 늘 "섹션 · 소주제"("ATLAS · validation", "Neural samplers · path weights", "JANUS · discovery")라서 킥커만 읽어도 목차가 된다.

**제목(h2) = 그 장의 요점.** 36장 중 섹션 표지를 빼면 제목은 4–10단어이고, 절반이 "주제: 요점"의 콜론형이다. 모두 *무엇이 어떻다*를 말한다.
- "The bottleneck: local moves get trapped"
- "Machine-learned potentials made each step cheap, not the walk short"
- "Fixed-point training: the model proposes, the physics corrects"
- "Forces find the modes; path weights fix their weights"
- "Train on 64 particles, sample 512"
- "Free energy and entropy with >500× fewer energy evaluations"
- "A new era: simulation becomes a query"
- 질문형도 쓴다: "How do we train it? How the field got here", "What is the discrete analogue of a force?"
- 없는 것: "Result 1", "Method", "Experimental setup" 같은 논문 절 이름, 변수 나열("14 scenarios × 30 models × 2 modes × 3 runs"), 괄호 안 배점 목록.

**마무리줄(takeaway) = 교훈 한 문장 또는 숫자 하나.** 6–21단어, 굵은 글씨는 한 구절.
- 교훈: "Learning a diffusion model = learning the **score** ∇log p_t at every noise level." / "**No retraining**: one base sampler reaches any tilted target."
- 숫자가 곧 증거: "Glass at T=0.2: free-energy error 2×10⁻³." / "Zero-shot on a new composition already beats the best from-scratch run."
- 대구·반전: "**Train once, query many**: simulation becomes a query." / "made each step cheap, not the walk short"
- 다음 장으로 넘기는 손잡이: "…the **path weight** fixes the mode weights. Next: where it comes from."
- 이 발표의 약속: "**This talk:** neural samplers address this problem / Fewer evaluations × cheaper evaluations: the two efficiency gains multiply."

**본문 = 굵은 두세 단어 라벨 + 한 절.** "**Slow mixing.** Crossing a barrier Δ takes ~e^{βΔ}" / "**No amortization.** Every temperature, pressure or composition is a new run." / "**Why they matter**: … **Why they are hard**: … **No data**: …" / "**Task**: … **Result**: … **Design rules**: …". 한 장에 이런 줄이 3–5개, 아니면 수식 하나와 문장 하나. 설명을 문단으로 쓰지 않는다.

**용어는 첫 등장에서 바로 풀이.** "the natural prior is **uniform** (an ideal gas), not a Gaussian" / "path weight … $W=-\log w$ is the work" / "**SMC** uses the work to **reweight** … **APT** uses the work to **swap**". 약어·기호가 먼저 나오고 설명이 뒤따르는 일이 없다.

**숫자는 적게, 크게, 비교형으로.** ">500× fewer", "~10³× fewer", "36 GPU-h / ~20 GPU-h per composition / ~300× less compute over 480 compositions"(큰 숫자 타일 + 한 줄 라벨). 표의 30개 값을 다 읽게 하지 않는다.

**다른 사람의 연구는 "맞는 생각 + 그러나".** 역사 장("How do we train it? How the field got here")은 "2018 · Boltzmann generators … **But** invertible layers limit expressiveness" → "2024 · PDDS → iDEM: **the right idea** … **But** the debiasing sits inside the label … **High variance → fails at scale**" → "2025–26 · fixed-point matching"으로 이어지고, 마무리줄이 "ATLAS · JANUS = fixed-point matching **+** the 2022–24 path-weight loss"로 자기 기여를 그 계보 위에 놓는다. 선행연구마다 공을 한 줄, 한계를 한 줄.

**청중이 아는 성공으로 동기 부여.** 확산 모델 장은 "The generative models behind a decade of breakthroughs: Images & video · Protein design (RFdiffusion) · Biomolecular structure (AlphaFold 3) · Materials (MatterGen) · Weather (GenCast)" 표로 시작한다. 방법을 설명하기 전에 "당신이 이미 아는 그것"에 건다.

**LLM 에이전트는 어떻게 말했나.** 레퍼런스는 1인칭 연구 발표라 LLM 에이전트가 주제가 아니라 두 장의 *응용*으로 나온다. 그 두 장의 문구가 기준이다.
- 27장 "Agentic inverse design: LLM agent × ATLAS × universal MLIP" — "**Task**: ≤5 of 8 elements; MACE-MPA-0; objectives B, G, B/G." / "**Result**: Pareto front converges within **480** ATLAS evaluations." / "**Design rules**: Co, Ni, Ti in every Pareto alloy." 인용줄: "left: schematic of the asynchronous agent loop · candidates are model-guided hypotheses for higher-fidelity validation".
- 35장 "Steering and agentic design of alloys" — "**LLM agent proposes Δμ** (Ag–Al–Au–Cu–Ni) for stiffness, ductility and reflectance; hypervolume saturates in ~**120** evaluations."
- 36장(탐색 루프) — "**Sampler**: … **Screen**: 8,000 samples → enriched pairs and triplets → hybrid DFT. **Found**: known centres re-emerge (Si E centre, Ge–V); new: **S–Ti** (Si), **B–O–O** (diamond)." 인용줄: "candidates require excited-state validation".
- 패턴: 에이전트는 루프 속 도구이고, 강조되는 것은 (a) 비싼 평가를 몇 번 만에 끝냈는가(480, 120), (b) 사람이 읽을 수 있는 발견(설계 규칙, 새 결함), (c) 인용줄의 정직한 단서("가설이다", "검증 필요"). 과장 없이 숫자 하나와 규칙 하나.

**정직 표기는 인용줄에.** "left: schematic three-well landscape · right: real run of the fixed-point rule on a 1D toy" / "right panel: exact transport for this mixture (an ideally trained sampler)" / "reference: converged PT-MCMC with ≈4.5×10⁸ evaluations". 모식과 실측, 기준선의 비용을 그림 바로 아래 한 줄로 적는다. 자기 논문은 저자명에 **Du** 굵게.

## 2. 우리 덱(한국어 논문 세미나)에 옮기는 규칙

장르 차이: 레퍼런스는 자기 연구의 1인칭 발표이고, 논문 세미나는 남의 논문을 3인칭으로 소개하며 발표자의 생각을 따로 얹는다. 그래서 규칙 하나가 더 붙는다 — **저자의 주장과 발표자의 해석을 보이게 구분한다**(레퍼런스의 "candidates are model-guided hypotheses" 단서와 같은 자리, 인용줄 또는 '발표자 해석' 라벨).

1. **제목 = 주제 + 요점, 명사구, 34자 이내.** 콜론형("주제: 요점") 허용. "결과 1:", "방법:", "프로토콜:" 같은 절 이름 접두사와 변수 나열형 제목 금지. 한국어 명사구 규칙(research-talk `korean-slide-copy.md`)은 유지하되, 명사구가 요점을 담아야 한다. 예시(강제 문구가 아니라 방향): "결과 2: 높은 생존율 ≠ 인과 이해" → "이기고도 이유를 모르는 에이전트"; "14개 시나리오 × 30개 모델 × 2개 실행 모드 × 3회" → "같은 예산으로 30개 모델을 14개 시나리오에서 비교"; "프로토콜: 탐색 10회 → 최종 설계 1,000대 평가 → 설명 보고서" → "열 번 실험하고, 한 번 제출하고, 이유를 설명하는 게임".
2. **킥커 = "섹션 · 소주제".** 섹션은 6개 이내(예: 왜 · 게임 · 함정 · 결과 · 들여다보기 · 우리에게), 소주제는 그 장의 자리. 킥커만 읽어도 목차가 되게.
3. **마무리줄 = 그 장의 교훈 한 문장 또는 증거가 되는 숫자 하나.** 12–48자, 숫자 2개 이하, 제목을 되풀이하지 않음, 굵은 글씨 한 구절까지. 논문 절·표·그림 번호, 루브릭 코드 금지. 다음 장으로 넘기는 손잡이("다음: …")는 허용.
4. **용어는 첫 등장에서 풀이.** 게임 용어(SCM, DEF, EMI, 문턱, 궤적, 세션, 가족…)와 에이전트 용어(Agentic/Prompting, ReAct, OpenCode, 스캐폴딩, 베이스라인, ICC, Spearman, pp)는 처음 나오는 장에서 괄호나 "=" 로 한국어 풀이를 붙인다("승리 기준(문턱 75%)", "SCM = 숨은 인과 모형"). 루브릭 코드(CR1·ED1…)는 화면에 쓰지 않고 말로 쓴다("기전 식별", "실험 설계"). 논문 위치 표기(§, Table, Fig., Appendix, Observation)는 인용줄에만.
5. **숫자는 적게, 크게, 비교형으로.** 제목·킥커·마무리줄·레인 헤더의 숫자는 장당 3개 이하. 차트 눈금은 예외. 핵심 수치는 비교로("최적보다 14pp 아래", "유출되면 +18.5pp").
6. **길잡이 문장.** 앞 네 장 안에 "이 발표: …"(레퍼런스의 "This talk:")가 있고, 앞 세 장 안에 청중의 일과 잇는 고리가 있다(스크리닝 히트, 발현 데이터, 구조 데이터베이스처럼 *우리가 보는 데이터도 생존자 표본*이라는 식). 마지막 장은 "우리에게 주는 뜻"으로 끝난다.
7. **본문은 라벨 + 한 절.** 설명은 "**관측**: …", "**함정**: …", "**해법**: …"처럼 굵은 라벨 뒤 한 절. 문단 금지(디자인 채점표 C1·C2와 같은 방향).
8. **선행·관련 연구는 "맞는 생각 + 그러나".** 기존 벤치마크 비교 장은 표 15행이 아니라, 각 계열의 공 한 줄과 빠진 것 한 줄, 그리고 이 논문이 더한 것 한 줄.
9. **정직 표기는 화면에.** 모식 차트는 "모식", 벡터 좌표에서 읽은 값은 "값은 그림 좌표에서 읽음", 발표자의 해석·번역·가설은 "발표자 해석"을 인용줄이나 라벨로. 논문의 범위를 넘는 일반화("LLM은 인과 추론을 못 한다") 금지 — 논문은 30개 모델·14개 시나리오에서의 관찰이다.
10. **발표자 노트 = 말할 대본.** 노트는 출처 인용(기존 규칙)에 더해, 그 장을 말할 때의 첫 문장과 다음 장으로 넘어가는 문장을 담는다.

## 3. 적용 범위와 금지

- 이 규칙은 보이는 문구(킥커·제목·레인 헤더·라벨·마무리줄·인용줄)와 노트에만 적용된다. 그림·격자·글자 크기는 `design-system.md`와 `rubric.md`가 다스리고, 메시지 수정은 그 점수를 떨어뜨리면 안 된다.
- 슬라이드 수와 승인된 스토리라인의 id·역할·증거는 유지한다. 제목·메시지·마무리줄·전환 문구는 바꿀 수 있고(사용자 지시 2026-10-31 "이제 메시지만 좀 조절하면 되겠다"), 바뀐 스토리라인은 `work/storyline.json`에 새 스냅샷으로 남기고 사용자 검토로 넘긴다.
- 숫자는 늘 논문 인쇄값. 문구를 바꾸면서 새 수치를 더하지 않는다.

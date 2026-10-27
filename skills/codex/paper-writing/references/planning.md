# Planning the paper with the author

The materials show what was done; the author knows what the paper is for. Agree on the direction before drafting, so the prose argues the paper the author wants to publish and no draft has to be rewritten because its premise was wrong.

## When

- Before the first draft of a paper or of a new set of sections, and whenever the author asks to settle the direction first ("방향부터 같이 정하자").
- Skip it for a revision of one passage, when the author has already accepted a plan for these sections (continue from it without asking again), or when the inputs include a writer package (`plan.md` with `brief.md`).
- Skip it in any run where no one can answer before the text is due (SKILL.md, Workflow step 1): make the decisions and the paragraph outline privately, write the sections, and list each open decision with the choice made in Notes to author. Such a draft is provisional; never record its decisions as accepted.
- Handing the work to another agent does not waive the discussion: if the author asked to settle the direction first, the plan goes back to the author before any prose.

## Read the materials first

Read everything supplied: notes, result tables, logs, drafts, earlier versions. Sort what you read into facts (a measured value with its unit, comparator, condition and source), the author's interpretations, hypotheses and plans, and items marked as not run or unconfirmed. The plan is built from the facts; an interpretation enters as the author's framing, labeled as such. Map every result that supports, tests, bounds or contradicts a proposed claim, including the components of an aggregate, and classify it by its role in the paper's question, not by an informal label in the notes: a result the notes call weak may answer the central question. Do not propose new experiments or analyses unless the author asks; when a planned claim needs evidence the materials lack, say how the claim narrows without it.

## The plan

Write the plan in the author's language, but quote the difference, the headline claims, their scope words, the proposed sentences and the Results headings in English, as they will appear in the manuscript. Show it in two passes, so the author settles the direction before reading any table.

**First pass, one screen.**

1. **Story.** Three to five lines: what the paper shows, in the order the Introduction will argue it.
2. **Direction.** The closest prior work and what it achieves; the difference as one sentence naming both sides; its scope words; the insight, if the materials contain one. Make this sentence the paper's central message: what the reader should newly understand from the work, not just what was built. Use the same sentence as the reference for the final integration pass (`integration.md`). Beside it, the proposed English first sentence of the Introduction and the Turn sentence. When the materials support more than one framing, show the two best supported side by side, each with its first sentence and the headline it would lead to, and recommend one.
3. **Headlines.** The one or two headline results with comparator and number, and the weak results that narrow them, with the scope words they add.
4. **Questions.** Only gaps that change the text: which result leads when two compete, a missing acronym expansion or value, two numbers that disagree, a figure number. At most three, each a single decision with your recommended answer.

Ask about the direction only.

**Second pass, after the direction is accepted.**

5. **Evidence.** Full rows (claim supported, comparator and number, figure or table, tier, placement) for headline, weak and unverified results and for any placement the author may want to change; supporting results in one line per section.
6. **Outline.** The Introduction in full: one row per paragraph with its job, the content and numbers it carries, and its closing point (what its last sentence lands on, as a phrase). For Results, map each core paragraph's reader question, observation, supported implication and role in the paper's central claim, as described in `results.md`, then show subsection order, headings (a full-sentence finding for nature-family, a short question or experiment for ml-conference) and where each weak result sits. Supporting-only paragraphs can name the claim they support. For Methods, show only the rows where a choice is made: main text or Supplementary and the tier (novel, critical, routine, environment).
7. **Format**, only where it differs from the defaults or is unknown: venue profile, target length, spelling, output format, citation placeholders.

Before asking for acceptance, check the load of the outline: a paragraph that must carry two claims, an Introduction preview with more than two headline numbers, or a Methods subsection that mixes a novel component with routine settings gets a proposed split, and the author decides.

## Discussion

- After a revision, show only what changed.
- When the author fixes how a method, dataset or result must be described, add the wording to the project facts file in the same turn, as well as to the plan.
- Keep the author's wording for the difference and the headline when it is accurate. When it overstates the evidence, show the accurate version beside it and name the result that bounds it. The author chooses the framing and the emphasis; the scope words the evidence requires are not a choice, and the plan records the scoped version. An author's confirmation makes an interpretation the paper's framing, not evidence: it is still stated at the strength its support allows, and an item marked as not run stays unverified.
- "Left out" and "Supplementary" are placements only for unverified items and for weak results outside the scope of every headline claim. A result that bounds or contradicts a headline claim is placed beside that claim in Results, and the claim narrows, whatever placement is preferred.
- End each pass with one explicit question: whether to draft the named sections with this plan. Apart from the proposed first sentence and Turn sentence, draft prose only after the author accepts. A request to explore, silence, a timeout or the existence of a plan file is not acceptance while the author can answer.
- After acceptance, every section follows the plan without asking again. A substantive departure (a new headline, a dropped result, a changed scope) goes back to the author; wording and fit do not. A plan never overrides the materials: where it conflicts with them or with the non-negotiables, follow those and tell the author.
- Save the accepted plan as `plan.md` beside the draft, with its status ("accepted"), the sections it covers, the date and the author's words of acceptance, so that a later session or another writer works from the same plan. A plan the author has not reviewed is saved with the status "provisional".

## Example of a first pass (synthetic; the system and numbers are invented)

> **줄거리**
> 1. 잡음 속 음성 인식은 같은 발화라도 잡음 조건에 따라 오류가 크게 달라짐.
> 2. 잡음 증강 학습은 잡음 조건의 오류를 낮추지만, 깨끗한 버전과 잡음 버전의 예측을 서로 맞추는 학습 신호는 없음.
> 3. 우리는 두 버전의 frame posterior를 맞추는 일관성 항을 CTC 손실에 더함.
> 4. 잡음 조건 평균 오류가 기존 최고 모델 대비 12.9%에서 8.4%로 내려가고, 차이는 가장 시끄러운 조건에서 가장 큼.
>
> **방향**
> - 가장 가까운 선행 연구: 잡음 증강 학습. 잡음 조건의 오류를 낮추지만 두 버전의 예측을 맞추도록 학습하지는 않음.
> - 차이: "Rather than only adding noisy copies to the training data, we train the recognizer to give the same frame-level predictions for an utterance and its noisy copy."
> - 범위 단어: "in noisy conditions". 깨끗한 음성에서는 차이가 0.1포인트라 헤드라인 범위에 넣지 않음.
> - 첫 문장 후보: "Even the strongest recognizer we compare makes about four times as many word errors on noisy speech as on clean speech."
>
> **헤드라인**
> - 평균 WER, 잡음 조건 전체: 기존 최고 모델 12.9% → 8.4% (Table 2).
> - 범위를 정하는 약한 결과: 깨끗한 음성 3.2% 대 3.1%. 헤드라인에 "in noisy conditions"를 붙임.
>
> **질문**
> 1. 헤드라인을 평균 WER로 둘까요, −5 dB 결과(21.3% → 12.6%)로 둘까요? 추천: 평균 WER. 모든 잡음 조건을 대표하고, −5 dB는 그 안에서 차이가 가장 큰 조건으로 바로 뒤에 둡니다.

The first-sentence candidate rests on the strongest baseline's 3.2% on clean speech and 12.9% averaged over the noise conditions, both in the notes; the ratio of about four is a computed number and goes to Notes to author.

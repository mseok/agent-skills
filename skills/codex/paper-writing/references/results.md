# Results

The reader finishes each subsection convinced of one claim, with the strongest evidence first and its meaning spelled out. Weak results are visible to a careful reader but never carry the narrative.

## Tiers and placement

| Tier | Where | How |
|---|---|---|
| headline | the claim of a subsection or paragraph, stated by its second sentence, or by its third when a question and a setup sentence come first; also the abstract, the Introduction preview and a main figure | claim with its scope words, comparator, exact number, figure or table reference close by |
| supporting | body of the paragraph, ablations, analyses | number, and what it shows |
| weak | after the strong result it qualifies, in the same paragraph; on secondary settings outside the scope of every headline claim, the Supplementary with a pointer | compact, exact, with its condition and direction |
| unverified | nowhere in the manuscript | Notes to author |

A trade-off, null or adverse result that answers the paper's question is a finding and is placed as one, even when it is negative.

## Opening a Results section

Before drafting, map each core paragraph to the reader's question, the observation that answers it, the implication supported by that observation and its role in the paper's central claim. Keep this map in the writing plan, or make it privately when planning is skipped; for a local revision, map the target passage in its surrounding argument. A supporting-only paragraph can name the claim it supports. These are reasoning prompts, not four compulsory sentences: use the order the reader needs, and do not invent an implication to fill a slot. A benchmark name or metric alone is not a scientific question.

Open the section, and each major subsection whose question changes, the way a good Introduction paragraph opens: one sentence on the question the experiment answers, one on how it was set up if the reader needs it, then the headline answer with its number. The reader should know what to look for before the details arrive. Do not open on a description of a table, and do not repeat the Introduction's motivation. The headline in the opening already carries its scope words ("at signal-to-noise ratios below 10 dB"), so that no later sentence has to narrow it; the numbers of weak results come later, beside the claims they qualify. When an ml-conference Experiments section begins with a setup subsection, this opening belongs to the first results subsection.

## Making strong results land

- **Claim first, figure second.** "The decoder lowers the logical error rate by a factor of 3.1 (Fig. 2a)", not "Fig. 2a shows the logical error rates of both decoders." When the reader needs the question or the experiment first, give it in one sentence, then the claim.
- **Size in its most telling honest form.** Absolute and relative when both mean something ("from 12.1% to 7.5%, a 38% reduction"); against the strongest baseline, not the weakest; as a fraction of the gap to an oracle or upper bound, or in units of prior progress, when the inputs allow.
- **Breadth amplifies.** "on all 12 benchmarks", "at every lead time from 1 to 10 days", "across three orders of magnitude in compute", always within the tested range. An aggregate does not show that every case improves.
- **Then say what it means.** End a claim with what its result implies for the paper's question, after any qualification, so that the implication already accounts for it: "The improvement therefore concentrates in the noisy conditions that the consistency objective targets"; "The two decoders therefore differ only where errors arrive in bursts." An implication says where, when or on which measure the result holds and what that means for the question; it needs only the data just shown, so state it plainly. A cause is not an implication and follows the next bullet. A paragraph that only adds supporting numbers to the previous claim needs no meaning sentence of its own, and none is appended for symmetry. A results section that only reports numbers leaves its most interesting material unsaid.
- **Mechanisms at the strength the evidence allows.** An ablation shows what removing a component does under its controls; say what was held fixed and whether variants were retrained when the inputs say so. Call something a mechanism only when an analysis isolates it; otherwise use "suggests" once, or leave the cause out while keeping the implication.
- **Numbers carry the intensity.** At most one evaluative adverb per paragraph ("substantially"), and only next to a number. No "remarkable", "unprecedented" or "dramatic".
- **Proportion.** Each paragraph carries one claim, its evidence and its meaning. Per-item numbers that a table already lists appear in the text only when the sentence uses them. A subsection that reports one main comparison usually reads best at about 400–600 words; above that, cut per-item numbers, secondary comparisons that bound no headline claim, and repeated setup before cutting any sentence that says what a result means.

## What a case adds

A case should explain something the aggregate comparison leaves unresolved: which scientific object or process was recovered, where a prediction failed, or which relevant distinction a summary metric conceals. State that difference in the domain's terms, with measurements close by. Explain what a change in coordinates, error or score means for the question rather than stopping at the measurement. If the case adds only another win, shorten it to supporting evidence instead of forcing a separate interpretation.

Distinguish an observed failure mode from why a model produced it. Explain the former directly when the source supports it; connect it to the paper's proposed approach at the strength allowed by the evidence. Attributing success to a component, or failure to a comparator's design, needs evidence that separates that cause. When this evidence is absent, keep the observed distinction and its scientific implication; do not invent a cause or erase the explanation.

## Semantic review

Read the draft for meaning separately from running the prose checker:

- Temporarily hide numerical values and method names. Can a reader still identify the scientific question, the observed difference and its role in the paper's argument? Keep quantities and named methods wherever they are needed in the final text; this is a diagnostic for result lists, not a reason to remove evidence or repeat the central claim in every paragraph.
- For a case, what explanatory information would disappear if it were removed? If nothing beyond another favorable score disappears, revise its role using the available evidence or shorten it to support the existing claim.
- For each "therefore", "thus" or equivalent inference, identify the premises in the preceding text. Supply a supported missing premise or narrow the conclusion. Check whether the conclusion describes an observation, an implication or a causal explanation, and preserve useful interpretation at the level the evidence supports.

## Placing weak results

Legitimate devices, in order of preference:

1. **Subordinate after strength.** The main clause carries the strong result; the weak one follows in a trailing clause or the next sentence, with its condition. "The gain holds at every tested noise level and is largest at −5 dB (41%); on clean speech the new model's error rate is 0.1 points lower (3.1% versus 3.2%)."
2. **Honest aggregation.** "improves on 10 of 12 benchmarks (Table 1)", with the full table available. Name the exceptions in one clause and give the number of the largest gap when it bounds a headline claim; the table holds the rest.
3. **Condition, not failure.** State the regime where the method does not help as the boundary of the claim. Give a reason only when the inputs support one (a ceiling effect, a regime outside the training distribution).
4. **Supplementary with a pointer**, for weak results on secondary settings outside the scope of every headline claim (not a component of a headline aggregate): "Results on the two coastal stations are in Supplementary Table S4."
5. **Exact, neutral wording.** "is 0.4 points lower", "narrows to 1.2 points", "trails the baseline by 0.1 points (s.d. 0.2 over three runs)"; always say which system is higher. Equivalence words ("comparable", "on par", "matches") need an equivalence analysis or interval in the inputs; overlapping error bars are not one.

When a weak result bounds a headline claim, state it beside that claim and narrow the claim, in the abstract and Introduction too: "lowers the error on noisy recordings" rather than "lowers the error".

Never:

- alter or round a number to hide it;
- omit a result that bounds or contradicts a headline claim;
- call a loss "comparable" or "competitive";
- switch metrics or baselines partway through a section to avoid a weak number;
- give a weak result a heading, a figure title, a topic sentence or a paragraph of its own;
- announce weakness as a topic: "Two further results are weak", "The evidence is mixed", "The gains are not uniform";
- end a section or subsection with a paragraph that only lists caveats. A boundary that qualifies a specific inference stays beside that inference, even when it is the last claim; the scope of the whole study goes to the Discussion or Limitations, or to Notes to author when neither is being written;
- apologize ("unfortunately"), excuse, or speculate about causes the inputs do not support;
- describe a weakness in report register ("this issue has not yet been resolved").

## Layout

- **nature-family.** Subsection headings are full-sentence findings within the evidence, with their scope: "Correlation-aware decoding suppresses burst-induced failures", not "Decoder performance". Inside a subsection, paragraphs are continuous prose without bold run-in labels. Figures are cited inline in parentheses, "(Fig. 2a)", never in a heading or label.
- **ml-conference.** Experiments are organized around the paper's questions. A short bold label naming a question or experiment may open a paragraph ("**Transfer to unseen chips.**").
- **Both.** No closing summary paragraph or label ("Summary.", "In summary,", "Key findings:", "Takeaways"): the opening already gave the answer, and the Discussion draws the conclusions.

## Tables

Captions and headers make a table readable on its own: metric and its direction, units, evaluation set, aggregation and what ± means. Mark published versus reproduced baseline numbers, and separate rows run under different protocols or budgets. Bold the best comparable value (ties included) under a stated rule. Present favorable and unfavorable columns identically.

## One way to build a paragraph (an option, not a template)

Question or claim → the claim with number and reference → how it was measured, if not obvious → breadth or consistency → qualification (the weak result, exact and scoped, in a trailing clause) → what it means for the question, accounting for the qualification → transition to the next claim.

## Example (synthetic; the system and numbers are invented)

Notes:

> 새 모델 평균 WER 8.4 vs 기존 best 12.9 (Table 2) / SNR −5 dB에서 차이 제일 큼: 21.3 → 12.6 / clean에선 새 모델 3.1 vs 기존 3.2로 거의 같음 / 화자 수 늘려도 개선 유지되는 듯 (Fig. 3b, 50명 → 500명에서 상대 개선 33–36%) / 사투리 음성은 아직 안 돌려봄

Results:

> We first ask whether consistency training lowers recognition errors in noise. Across all noise conditions, the consistency-trained model lowers the average word error rate from 12.9% to 8.4% relative to the strongest baseline (Table 2). The relative reduction ranges from 33% to 36% across the tested training-pool sizes of 50 to 500 speakers (Fig. 3b). The margin is largest in the noisiest condition: at −5 dB, the error rate falls from 21.3% to 12.6%, a 41% reduction, whereas on clean speech the consistency-trained model is 0.1 points lower (3.1% versus 3.2%). The improvement therefore concentrates in the noisy conditions that the consistency objective targets.

What changed: the question opens and the claim with the strongest comparison follows at once; the breadth across training-pool sizes comes next; the clean-speech result is exact, attributed and placed in a trailing clause that reads as the low-noise end of the contrast; the closing sentence says what the pattern means and already accounts for it; "유지되는 듯" became the measured range with its tested conditions, not a claim of independence; the 41% and 0.1 are computed from the notes and listed in Notes to author; the untested dialectal speech is absent from the text and listed in Notes to author.

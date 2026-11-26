# Register: write as the paper, never as a report

A paper develops a scientific argument through its questions, findings and interpretation. A report narrates status to someone. Write in the language of the scientific subject, not the language of the writing or verification process.

State supported findings directly. Keep evidence checking in the working notes, and use its outcome to choose accurate words. A measured effect can simply reduce, increase or change a scientific quantity; it does not need to be introduced as "evidence that establishes only …". An interpretation keeps the degree of confidence its basis warrants, and an untested result never becomes a finding.

## Select facts for the argument

Write the clearest, strongest claim the evidence supports, with the conditions that make it true. Organize facts by what they let the reader understand; do not give every observation, untested setting or possible objection equal space. Keep the source notes complete while selecting, combining and placing material in the manuscript. Preserve exceptions and contrary results that change a claim's meaning; put other details in their agreed location.

Before adding a qualification, ask what scientific meaning would change without it. Keep a consequential condition or contrary finding where the reader needs it. Once the experimental or theoretical setting is clear, let that context carry through the argument; repeat a condition only when the context changes or the statement will be read independently. An accurately stated finding needs no routine inventory of untested settings, no "does not establish" afterthought and no repeated "in this study". Keep necessary study-level limitations in the appropriate Discussion or required section, with their scientific consequence.

## Same facts, different editorial decisions

Read these contrasts before drafting and compare your draft's choices with them before returning. All are independent synthetic examples, not findings from real studies. The excerpts illustrate editorial decisions; a real paper keeps its supporting figure references and necessary uncertainty. Transfer the decisions, not the vocabulary or a fixed sentence template.

### 1. A list of results becomes a finding

**Facts:** Word error rate changed from 12.9% to 8.4% on noisy recordings and from 3.2% to 3.1% on clean recordings.

**Report-like:** On noisy recordings, word error rate decreased from 12.9% to 8.4%. On clean recordings, it decreased from 3.2% to 3.1%. The degree of improvement differed between conditions.

**Paper-like:** The reduction in word error rate was concentrated in noisy recordings, where it fell from 12.9% to 8.4%, compared with 3.2% to 3.1% on clean recordings.

**Decision:** Both comparisons remain. Their pattern becomes the finding, so the reader learns where the approach helps without a separate verdict that the gains are uneven.

### 2. A technical metric becomes a scientific distinction

**Facts:** In one navigation trial, controller A selected the correct corridor and ended 0.2 m from the target. Controller B entered a different corridor and ended 2.4 m from the target.

**Report-like:** Controller A had a final position error of 0.2 m, whereas controller B had an error of 2.4 m. The controllers selected different corridors.

**Paper-like:** In this trial, controller A selected the correct corridor and reached within 0.2 m of the target, whereas controller B entered a different corridor and finished 2.4 m away. The error involved route selection, beyond fine adjustment of the final position.

**Decision:** The measurement now explains the observed failure mode. The trial identifies what went wrong, without claiming which architectural component caused it.

### 3. A generic caveat becomes a scoped claim

**Facts:** The question concerns single-device inference at batch size 1. Fusion reduced latency from 12 ms to 8 ms under those conditions. Multi-device execution was not evaluated.

**Report-like:** Fusion reduced latency from 12 ms to 8 ms on one device at batch size 1. However, evaluation was restricted to this setup, and applicability to multi-device execution remains unclear.

**Paper-like:** For single-device inference at batch size 1, fusion reduced latency from 12 ms to 8 ms.

**Decision:** The result carries its actual conditions. No multi-device claim is made, so the untested setting does not need a defensive sentence here. If scaling becomes a headline claim or an intended application, its boundary becomes material and must be addressed.

### 4. A consequential exception stays with the finding

**Facts:** The application requires a response within 10 ms. Measured latency was 8 ms at the tested normal load and 20 ms at peak load.

**Report-like:** Latency was 8 ms at normal load and 20 ms at peak load. The requirement was 10 ms. Performance was therefore mixed, and the system still has limitations.

**Paper-like:** The system met the 10-ms response deadline at the tested normal load (8 ms), but exceeded it at peak load (20 ms).

**Decision:** The deadline makes the peak-load result essential to interpreting the application claim. Keep the exception and both measurements beside the finding, without adding a vague judgment about the quality of the work.

### 5. A scientific finding replaces a verification disclaimer

**Facts:** In a cell-free aggregation assay, peptide P reduced tau fibril formation by 40% relative to vehicle. The study contains no cellular or animal experiments.

**Report-like:** These results establish only a reduction in fibril formation in a cell-free assay; they do not establish cellular efficacy or therapeutic benefit.

**Paper-like:** Peptide P reduced tau fibril formation by 40% relative to vehicle in the cell-free assay.

**Decision:** The sentence names the process, effect and experimental setting. It makes no cellular or therapeutic claim, so a list of unmeasured outcomes adds no scientific information. A paper that argues for such an application must address the relevant evidence in that argument. Nearby sentences about the same assay need not repeat its scope.

## Banned in manuscript text

| Report register | Instead |
|---|---|
| "has not yet been confirmed / verified / tested", "has not been run yet", "remains to be verified", "is still under investigation", "analysis is in progress", "requires further verification", "additional experiments are needed" | State the supported finding directly. Leave unfinished work out of the manuscript; flag it to the author only when it requires a decision. Include a material experimental condition or limitation where it changes the scientific interpretation (`results.md`). |
| Routine proof-status contrasts: "establishes only X, not Y", "does not prove", "cannot establish", "is not sufficient evidence for" after an already accurate finding | Remove the bookkeeping and state the finding in the field's terms. Keep a distinction of this kind only when resolving it is part of the scientific question or correcting an inference the argument otherwise invites. |
| Internal labels: "verified artifact", "eligible claim", "evidence ledger", "validation gate", run status or checklist verdicts | Name the scientific object, operation and observation. Such terms belong in the manuscript only when they are actual subjects of the research. |
| "preliminary results suggest", "initial experiments show" | Report the result with its actual support, or leave it out. |
| "we plan to", "will be explored in future work", "TBD", "TODO", "(?)" | Remove from Results and Methods; at most one forward-looking sentence with scientific content in the Discussion. |
| Process narration: "we first tried", "after several attempts", "it turned out that", "we then checked", "we noticed that" | Describe the final procedure and the evidence. |
| Frames carried over from Korean report style: "It was confirmed that X", "It is judged that X", "It can be seen that X", "It was observed that X" | State X, with its evidence: "X (Fig. 2)". |
| Messages to the reader or requester: "as requested", "below we summarize", "this section reports", "it should be noted that", "it is worth noting", "interestingly" | Delete the frame; state the content. |
| Weakness announced as a topic: "Two further results are weak", "The evidence is mixed", "The gains are not uniform", "Not all results are favorable" | The condition and the number, in a clause after the strong result it qualifies (`results.md`, weak results). |
| Summary labels and closing recaps in Results: "Summary.", "In summary,", "In conclusion,", "Key finding:", "Takeaways" | Delete. The opening of the section states the answer; the Discussion draws conclusions. |
| Apology and defense: "unfortunately", "although not perfect", "only slightly worse", "despite its limitations" | The number and its condition, stated neutrally (`results.md`, weak results). |
| Vague magnitude: "much better", "a lot", "huge" | The number. |
| Hedge stacks: "may possibly suggest", "could potentially" | One calibrated verb (below). |
| Chat-style formatting, arrows in ordinary prose, emoji, or headings that narrate the author's work | Use the paragraph, heading and list conventions of the target article type established in `venue-adaptation.md`. A list or short label earns its place by helping the scientific argument, not by the agent's reporting habits. |
| First-person singular, chatty asides, rhetorical questions | "We" for the authors; declarative sentences. A Results subsection opens by motivating its question in a declarative (`results.md`). |

## Words that depend on context

"currently", "to date", "so far", "at present", "at this stage", "ongoing" and "note that" are report register when they describe the state of the authors' own work ("we have so far tested two datasets"). They are fine in other roles: the time scope of prior literature ("to date, no decoder meets …"), a physical condition ("ongoing thermal fluctuations"), mathematical exposition ("note that $f$ is convex"). Rewrite the first kind; keep the others.

"Significant" and "significantly" mean statistical significance to most readers. Use them only for an inferential claim with its named test and result; otherwise give the magnitude ("substantially", or better, the number).

Give the effect size with its uncertainty beside any test result: a small p-value is not a large effect.

Review "sometimes", "often" and "in many cases" for vague padding. State a meaningful condition when the evidence identifies one; preserve genuine frequency or conditionality when it is the accurate scientific claim. Never delete a qualifier merely to make a statement sound universal.

## Calibrated verbs

Choose a verb that expresses the scientific result at the strength its evidence supports. Prefer the result itself ("binds", "reduces", "increases", "is associated with") to a running commentary on its evidential status:

- direct measurement or controlled comparison: "shows", "reduces", "outperforms", or a plain "is";
- a test designed to establish exactly the claim, whose outcome does: "establishes", "confirms", "validates";
- consistent indirect evidence: "indicates", "is consistent with", "supports";
- interpretation from an analysis: "suggests", once per point and never stacked with "may".

State an exploratory pattern as an observation from the analysis that found it; reserve validation language for a suitable independent test. Keep prediction, association and causation distinct through accurate nouns and verbs, rather than attaching a disclaimer to each result.

Universal words ("every", "each", "always", "unchanged", "any") need evidence of universality; otherwise say "can" or give the tested range.

Never express uncertainty about the authors' own procedure ("we believe we used …").

## Spelling

American English by default: analyze, organize, optimize, normalize, modeling, labeled, behavior, color, favorable, center, judgment, defense. Use British spelling only when the author's draft or the venue uses it, and then consistently.

## Converting notes (Korean or English)

| Note | In the paper |
|---|---|
| "~인 것 같음", "~로 보임", "seems to" | First decide what the evidence is. A measurement: state it with its number and the tested conditions. An interpretation of indirect evidence: one calibrated verb. Never turn an observed range into independence, causality or generality. |
| "아직 확인 안 됨", "아직 안 돌려봄", "추가 실험 필요", "not run yet" | Omit from manuscript prose; flag to the author only when it changes the selected claim or requires action. |
| "애매함", "미묘함", "mixed" | Exact numbers with their condition (`results.md`, weak results). |
| "원인은 아마 ~", "probably because" | A mechanism only when an analysis supports it ("is consistent with …"); otherwise omit the cause and keep what the result implies. |
| "기존 방법은 별로임", "baselines are bad" | The specific shortfall of the closest work, cited. |
| "이건 중요하지 않음", "minor detail" | Methods triage (`methods.md`): routine or environment. |

## Limitations without report register

State a limitation when it changes the interpretation, reliability or application of a finding, in the location where that consequence matters. Preserve contrary scientific results. Keep routine verification records and lists of unattempted work out of the manuscript.

- Report: "Finite systems have not yet been tested."
- Paper: "The simulations use periodic boundary conditions."

The second sentence gives the actual scientific setting. If finite-system behavior is part of the paper's claim, explain the relevant consequence there; otherwise it needs no additional disclaimer. Rephrasing must not invent a failure mechanism or remedy.

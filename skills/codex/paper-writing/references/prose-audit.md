# Prose review after argument revision

Apply these diagnostics to an already coherent manuscript. Their purpose is to preserve meaning while removing the writer’s reporting habits. A sound passage is not improved merely by changing its vocabulary. American English is the default unless the author or venue specifies otherwise.

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
| Weakness announced as a topic: "Two further results are weak", "The evidence is mixed", "The gains are not uniform", "Not all results are favorable" | The scientific pattern with the conditions and measurements that make it meaningful. Let contrary evidence determine the claim and its scope before deciding where the comparison belongs (`results.md`). |
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


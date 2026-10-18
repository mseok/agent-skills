# Register: write as the paper, never as a report

A paper states what was established. A report narrates status to someone. Report register makes solid work sound unfinished and the authors unsure, and reviewers read it that way.

Removing report register never changes what the evidence supports. Translate each note by its evidential meaning: an established measurement is stated directly with its conditions; a tentative interpretation keeps one calibrated verb; an untested claim leaves the paper.

## Banned in manuscript text

| Report register | Instead |
|---|---|
| "has not yet been confirmed / verified / tested", "has not been run yet", "remains to be verified", "is still under investigation", "analysis is in progress", "requires further verification", "additional experiments are needed" | Leave the unverified claim out (Notes to author). If the boundary matters to the reader, state it once as a boundary of the evidence in the Discussion: "Our experiments cover X; Y lies outside the evaluated scope." A boundary that narrows a specific claim stays beside that claim instead (`results.md`). |
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
| Report formatting: bold run-in labels in nature-family Results, bullet lists in Results or Discussion, arrows in prose, emoji | Prose paragraphs. Only an ml-conference contributions list may be bulleted, and only ml-conference Experiments may use short bold paragraph labels. |
| First-person singular, chatty asides, rhetorical questions | "We" for the authors; declarative sentences. A question that frames an experiment ("We first ask whether …") is fine. |

## Words that depend on context

"currently", "to date", "so far", "at present", "at this stage", "ongoing" and "note that" are report register when they describe the state of the authors' own work ("we have so far tested two datasets"). They are fine in other roles: the time scope of prior literature ("to date, no decoder meets …"), a physical condition ("ongoing thermal fluctuations"), mathematical exposition ("note that $f$ is convex"). Rewrite the first kind; keep the others.

"Significant" and "significantly" mean statistical significance to most readers. Use them only for an inferential claim with its named test and result; otherwise give the magnitude ("substantially", or better, the number).

"Sometimes", "often" and "in many cases" weaken an opening sentence without adding information. State the fact and the condition under which it holds instead; deleting the hedge without the condition would claim universality.

## Calibrated verbs

One verb per claim, matched to the evidence:

- direct measurement or controlled comparison: "shows", "reduces", "outperforms", or a plain "is";
- a test designed to establish exactly the claim, whose outcome does: "establishes", "confirms", "validates";
- consistent indirect evidence: "indicates", "is consistent with", "supports";
- interpretation from an analysis: "suggests", once per point and never stacked with "may".

Universal words ("every", "each", "always", "unchanged", "any") need evidence of universality; otherwise say "can" or give the tested range.

Never express uncertainty about the authors' own procedure ("we believe we used …").

## Spelling

American English by default: analyze, organize, optimize, normalize, modeling, labeled, behavior, color, favorable, center, judgment, defense. Use British spelling only when the author's draft or the venue uses it, and then consistently.

## Converting notes (Korean or English)

| Note | In the paper |
|---|---|
| "~인 것 같음", "~로 보임", "seems to" | First decide what the evidence is. A measurement: state it with its number and the tested conditions. An interpretation of indirect evidence: one calibrated verb. Never turn an observed range into independence, causality or generality. |
| "아직 확인 안 됨", "아직 안 돌려봄", "추가 실험 필요", "not run yet" | Omit; Notes to author. |
| "애매함", "미묘함", "mixed" | Exact numbers with their condition (`results.md`, weak results). |
| "원인은 아마 ~", "probably because" | A mechanism only when an analysis supports it ("is consistent with …"); otherwise omit the cause and keep what the result implies. |
| "기존 방법은 별로임", "baselines are bad" | The specific shortfall of the closest work, cited. |
| "이건 중요하지 않음", "minor detail" | Methods triage (`methods.md`): routine or environment. |

## Limitations without report register

Limitations are boundaries of the evidence, stated where they matter: beside the claim they qualify when they change it, and in the Discussion or the Limitations section a venue requires.

- Report: "Finite systems have not yet been tested."
- Paper: "All simulations use periodic boundary conditions, which limits the evidence for finite systems."

Rephrasing a limitation must not add a failure mechanism, a necessity claim or a remedy that the evidence does not contain.

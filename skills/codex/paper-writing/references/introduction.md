# Introduction

The reader leaves the Introduction understanding the scientific question, why it matters, and what this work adds. Use the target readership, article type, contribution and central message established in `venue-adaptation.md`. A limitation of existing methods is one possible reason for the study; an unexplained observation, competing explanations, an unmeasured regime or a need for a reliable resource can be equally good reasons.

## The first sentence and the first paragraph

Readers and editors decide in the first paragraph whether to keep reading, so it gets the most care.

- **The opening** establishes the scientific setting and why the problem deserves attention, at the intended reader's level. A general statement can do useful work when the paragraph develops it into a consequential question. A concrete phenomenon or example can also work when its significance is apparent. Choose the progression that makes this study intelligible; do not require the first sentence to identify this paper alone, introduce its variables or describe a control experiment. Retain uncertainty where it carries scientific meaning.
- **The first paragraph** starts from what this readership can reasonably be expected to know and supplies the context needed to understand the question. Explain unfamiliar concepts and use established field terms. Choose the breadth from the scientific motivation, without inflating the contribution or prematurely reducing it to an experimental setup.
- **Its ending** gives the next paragraph a reason to follow. This may be the unresolved question, a distinction or the next piece of background; there is no compulsory closing sentence or paragraph count.
- **Examples are optional.** Use an illustration when it clarifies a problem whose importance the reader can understand. Do not add a worked number, named system or imagined comparison merely to make the opening concrete. If a hypothetical example is useful, label its premises as hypothetical, keep its arithmetic exact and retain the calculation in working notes; never present it as a measurement.

Synthetic contrast:

- Weak: "Quantum processors sometimes exhibit correlated errors $e_{ij}$ between syndrome bits."
- Better when the paper addresses decoding latency: "A surface-code quantum processor must decode each round of syndrome measurements before the next round arrives, roughly every microsecond." The deadline explains the problem's consequence. Its specificity alone does not make it a better opening for a different scientific question.

## Make the argument specific

The familiar flow "X is important → many methods exist → they have limitations → we propose Y → experiments show it works" can suit a methods paper. Its generic sentences obscure the contribution, and its structure does not suit every study. Select the reasoning this paper needs, using matched published examples to judge what the target reader needs to hear.

| Obvious step | Specific replacement |
|---|---|
| "X is important in many applications." | The scientific understanding, measurement or practical decision that this question affects. Use a concrete consequence or example when it clarifies the importance. |
| "Many studies have examined X [1–20]." | What the closest work established and what remains unresolved for this question. Group broader work only where the grouping is accurate and useful. |
| "However, they have limitations." | The actual uncertainty, disagreement or limitation that motivates this study. Do not invent a failure of prior work. |
| "We propose a novel framework Y." | What this work adds, stated in the same scientific terms as its question. |
| "Extensive experiments demonstrate …" | The decisive finding, with the comparison and quantities needed to understand it. |

## Moves

Use the moves the argument needs, in the order it needs them.

- **Anchor.** Open on the phenomenon, scientific uncertainty or practical problem at the level relevant to the target reader.
- **Closest work.** Explain what is already known or possible. Credit the nearest studies precisely so the reader can see what this work adds.
- **Unresolved question.** Identify the missing understanding, conflicting observations, unexplored conditions or methodological limitation that matters here. Explain a shared assumption or failure mechanism only when the sources establish it.
- **Contribution.** State the new understanding, measurement, resource or capability in the question's own terms. Use a contrast when it clarifies an actual distinction; do not force every contribution into "Rather than …, we …".
- **Insight** (when the inputs have one). Why the change is possible or why it works: a property, an observation, an identity.
- **Alternative explanation** (when it matters to the argument). Explain the competing account or interpretation that makes the question consequential and how the study distinguishes it. Do not interrupt the Introduction with a routine defense against hypothetical objections.
- **Approach** (when the contribution is a multistage procedure). Its functional steps in a short prose sequence: what enters each step, what leaves it, and who makes any judgment ("The approach has three steps. First, …"). This is how the idea works, not a list of implementation components.
- **Evidence preview.** Give the decisive results when the target article type and argument call for them. Use a study objective or approach at the close when that is the more appropriate progression; a results preview and a contributions list are options, not requirements.
- **Consequence.** What the result makes possible within the tested domain, in one grounded sentence.

## Make the contribution clear

- State the contribution as early as the reader has the background to understand it. Let the argument determine its position and whether a later statement adds anything. Keep the scientific objects consistent while varying the wording naturally; do not repeat a contrast just to satisfy a template.
- **State the result accurately.** Describe what the work delivers. Include a condition or dependence when omitting it would change the meaning. Within a continuous argument, established context carries forward without repeating qualifiers such as "in this study" or "under the tested conditions". A title, abstract or heading that can be read independently must remain accurate on its own.
  - Overclaim, then retraction: "The probe measures soil moisture without calibration. … Each soil type still needs one reference sample."
  - Scoped once: "The probe measures soil moisture from one reference sample per soil type, instead of the laboratory calibration curve that current probes require."
- Keep one central message. Place supporting contributions where they advance it, without making them compete as unrelated stories.
- Explain the scientific contribution rather than merely naming a component swap. For a methods paper, the important difference may be an assumption, representation or objective. For another contribution, it may be the phenomenon explained, the quantity measured or the distinction resolved.
- Express the contribution at its supported strength. Explain what changes and why it matters; use a contrast or number when it helps, without requiring either to carry the emphasis.
- "First" claims appear only when the inputs establish them; otherwise describe the specific capability.
- Use a contributions list only when it suits the article type and target practice. Each item names a distinct contribution; routine implementation steps and a second copy of the results paragraph do not earn items.

## The evidence preview

When the Introduction previews results, select the findings that establish the central contribution. Do not compress every result into the closing paragraph.

- Give the decisive observation or result, with a comparator and number when they carry the scientific meaning. Include an essential denominator, cost or trade-off; do not choose numbers to meet a quota.
- State the finding in terms familiar to the target reader, rather than as an abstract verdict about the evidence ("the picture is nuanced", "the two criteria diverge").
- Keep secondary metrics and per-task scores in Results. A special condition belongs in the preview when it defines the scientific finding; do not present a favorable special case as typical performance.
- Introduce an unfamiliar dataset, benchmark or prior experiment by its role ("one of the calibration runs", "the strongest physics-based forecast"); give its name only when the reader needs it to identify the comparison. Names of people and individual datasets that readers of the venue do not know stay in Results.
- Express a necessary boundary in the finding itself, such as "on noisy recordings", rather than following it with an inventory of what was not shown. Retain a contrary result when it changes the central message.

## Readable

- Each paragraph has one job, and the reader can tell what it is early in the paragraph.
- Paragraphs follow the dependencies of this argument: supply the knowledge the next step needs, then add a new understanding. Connections can run from an observation to competing explanations, a measurement to its interpretation, or a method to its test. Remove repeated contrasts, including those hidden in a contributions list.
- Known before new: start each sentence from something the reader already holds (the end of the previous sentence, a term already defined) and end on the new information. Introduce a concept in words before its notation.
- One main idea per sentence, but connect ideas that belong together: a run of short declaratives that each restate a fact reads like a list, so join a cause and its consequence with "because", "so" or "which".
- Every "so", "therefore" and "thus" must follow from what precedes it alone. If the conclusion needs a premise the paragraph has not stated, state the premise or drop the connective.
- Keep subject and main verb close together and early; at most one parenthetical per sentence.
- Spell out every acronym at first use as "full name (ACRONYM)", including agencies and standard method variants, unless it is universal for the target reader (DNA, GPU); then use the short form consistently. Do not drop a useful acronym to avoid expanding it. If the inputs do not give the expansion, keep the supplied name and flag it in Notes to author. Define every symbol at first use, and keep one name per concept (do not alternate "surrogate", "emulator" and "proxy").
- Verbs over nominalizations: "we estimate the noise" rather than "estimation of the noise is performed".
- Use the level of abstraction the argument needs. Add examples, numbers and named regimes when they clarify it, not as a default preference over a general scientific statement.
- Citations support statements about what prior work does; they never replace that description.
- Vary sentence length. Reread a dense sentence for competing ideas, distant subjects and verbs, or unnecessary qualifications; do not split a coherent explanation merely to meet a word-count target.

## Example of a methods contribution (synthetic; the system and numbers are invented)

Obvious version:

> Quantum computing has attracted increasing attention in recent years due to its potential applications. Quantum error correction plays a crucial role, and many decoders have been proposed [1–12]. However, existing decoders still suffer from limitations such as high latency and limited accuracy. In this work, we propose a novel decoder that achieves state-of-the-art performance on several benchmarks.

Specific version (compressed into one paragraph for illustration):

> A surface-code quantum processor must decode each round of syndrome measurements before the next round arrives, roughly every microsecond. A slower decoder lets errors accumulate faster than they are corrected. Decoders that meet this deadline, from union-find to recent neural networks, assume that physical errors are independent across qubits and rounds [1–12]. On current hardware the assumption fails where it matters most: leakage and high-energy radiation events produce bursts of correlated errors, and these bursts cause most logical failures. Rather than correcting correlations after an independent-error decoder has run, we build the correlation structure into the decoder and estimate it from the syndrome stream while the device operates. On a distance-7 code, this lowers the logical error rate per round by a factor of 3.1 relative to the fastest independent-error decoder, within the same 1-µs budget.

What changed: the opening gives a reason the problem matters; the closest work is described by what it does and the assumption its members share; the shortfall has a mechanism and a consequence; the turn reuses "independent" and "correlated"; the selected result explains the advance. This is one suitable argument for a latency-focused study, not a requirement to open every paper with a specific system, deadline or experimental contrast. In a real paper each statement about hardware and prior decoders needs its source in the inputs.

A component description versus the scientific contribution in a computational methods paper:

- Component: "We replace the reward model with a larger network trained on more preference data."
- Idea: "Existing test-time adaptation methods assume the label distribution is the same at training and deployment; we estimate the deployment label distribution online and adapt the classifier to it."


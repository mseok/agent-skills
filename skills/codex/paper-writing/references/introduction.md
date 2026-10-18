# Introduction

The reader leaves the Introduction knowing four things: the problem, why current approaches fall short, what this paper changes, and the evidence that the change works. The difference must be unmistakable, and the path to it easy to follow.

## The first sentence and the first paragraph

Readers and editors decide in the first paragraph whether to keep reading, so it gets the most care.

- **The first sentence** states a concrete fact or tension that could only begin a paper on this topic, as a plain declarative. No frequency hedge ("sometimes", "often", "in many cases") and no softening modal ("can differ"): if the fact holds only under a condition, state the condition. No notation, no citation-list opener.
- **The first paragraph** is written for a scientist outside the subfield: the phenomenon, why it matters, and the open problem, in words. Symbols, variable names, component labels, dataset names and equation-level detail enter later, where the formulation does; a term of art is explained in words when it first appears.
- **It ends on the open problem** the paper addresses, stated in the paper's own terms rather than announced as "the open problem", so the next paragraph can start from it.
- **Make the problem concrete.** One illustration often does more than three abstract sentences: a worked number, a limiting case or a familiar consequence. Introduce it as an example in the prose ("For a clock that drifts by 0.1 s per day, …"), keep its premises explicit and its arithmetic exact, never present a hypothetical quantity as a measurement, and list any computed number in Notes to author. Prefer a number from the inputs; a hypothetical premise needs an explicit hypothetical frame ("Suppose …", "For a …") and no attribution to a real system. Keep it light: one comparison a reader can picture, such as a ratio, a fraction or a count of halvings. An illustration that needs its own explanation or a chain of calculations is too heavy for the opening paragraphs.

Synthetic contrast:

- Weak: "Quantum processors sometimes exhibit correlated errors $e_{ij}$ between syndrome bits."
- Strong: "A surface-code quantum processor must decode each round of syndrome measurements before the next round arrives, roughly every microsecond."

## The obvious flow and what replaces it

The obvious flow runs "X is important → many methods exist → they have limitations → we propose Y → experiments show it works". Readers have seen it thousands of times, and because its sentences fit any paper, the actual difference drowns in them. The progression itself can stay when it suits the argument; what changes is that every step becomes specific to this paper.

| Obvious step | Specific replacement |
|---|---|
| "X is important in many applications." | The concrete problem and what failing to solve it costs, with a number or a concrete case. |
| "Many methods have been proposed [1–20]." | The closest prior work, what it already achieves, and the specific thing it does not provide. Broader work is grouped only where the grouping is accurate and useful. |
| "However, they have limitations." | The specific reason the closest work falls short here, and when. |
| "We propose a novel framework Y." | What Y does differently, in the same terms used to describe the shortfall. |
| "Extensive experiments demonstrate …" | The headline result, with comparator and number. |

## Moves

Use the moves the argument needs, in the order it needs them.

- **Anchor.** Open on the specific phenomenon, task or tension, not on the field (first paragraph, above).
- **Closest work.** Say what the nearest approaches do and what they already achieve, as the inputs and citations describe them. Credit them precisely; the difference is only as sharp as the description of what it differs from.
- **Shortfall.** Explain why that work falls short in this setting, as concretely as the inputs allow. When the approaches share an assumption that causes the shortfall, name it: the difference then becomes one contrast instead of a list of small improvements. When they do not, do not invent one.
- **Turn.** State the difference in a sentence that names both sides, often with parallel structure ("Rather than …, we …"; "Existing decoders treat X as fixed; we estimate X from …"). Reuse the nouns of the shortfall so the reader sees the match.
- **Insight** (when the inputs have one). Why the change is possible or why it works: a property, an observation, an identity.
- **Objection** (when the inputs or their formulas answer it). The first objection a specialist would raise against the shortfall, and why it does not remove it, in one sentence.
- **Approach** (when the contribution is a multistage procedure). Its functional steps in a short prose sequence: what enters each step, what leaves it, and who makes any judgment ("The approach has three steps. First, …"). This is how the idea works, not a list of implementation components.
- **Evidence preview.** The headline results with numbers and comparators: the "Here we …" paragraph for nature-family, the closing paragraph or contributions list for ml-conference.
- **Consequence.** What the result makes possible within the tested domain, in one grounded sentence.

## Making the difference unmistakable

- State it crisply and as early as the argument allows: right after the shortfall when the change needs no new background, or where the obstacle is resolved when the change rests on a tool, representation or result the reader must first meet (background, then obstacle, then resolution and Turn). Never state the Turn before the background it depends on. State it once in the Turn and once more in the closing paragraph in the terms of the result, with the same scope words. A Turn that picks up the nouns of the paragraph before it ("Rather than …, we …") is a handoff and stays; a sentence that re-explains that paragraph's content is a restatement and goes.
- **Scope it correctly the first time.** Describe what the method delivers, not the end state it serves. If a result still depends on a reference measurement, extra data, a human decision or a condition, the Turn says so, and no later sentence has to walk the claim back.
  - Overclaim, then retraction: "The probe measures soil moisture without calibration. … Each soil type still needs one reference sample."
  - Scoped once: "The probe measures soil moisture from one reference sample per soil type, instead of the laboratory calibration curve that current probes require."
- One central difference. Distinct supported contributions stay, in the closing paragraph, without competing with it as a second turn.
- Name the contrast at the level of an idea (an assumption, a representation, an objective, a regime, a measurement), not a component swap. "We replace the MLP with a transformer" is a component; "we stop assuming errors are independent across rounds" is an idea.
- Do not undersell with hedges ("we attempt to", "a first step toward") or oversell with adjectives ("novel", "groundbreaking", "unprecedented"). The contrast and the number carry the emphasis.
- "First" claims appear only when the inputs establish them; otherwise describe the specific capability.
- A contributions list (ml-conference) holds concise, parallel statements, each naming a distinct intellectual contribution and its evidence; not routine implementation steps, not scale alone, and not a second copy of the results paragraph.

## The evidence preview

The closing paragraph makes the reader want the Results; it is not a summary of them.

- Usually the one or two headline results, each with its comparator and number; this is a default, not a quota. Keep a second number when it supplies an essential denominator, cost or trade-off.
- State each result as a concrete observation a reader outside the subtopic can picture, not as an abstract verdict about the evidence ("the picture is nuanced", "the two criteria diverge").
- Conditional or best-case variants ("reaching 63% at the largest model size"), secondary metrics and per-task scores stay in Results.
- Introduce an unfamiliar dataset, benchmark or prior experiment by its role ("one of the calibration runs", "the strongest physics-based forecast"); give its name only when the reader needs it to identify the comparison. Names of people and individual datasets that readers of the venue do not know stay in Results.
- A boundary on the headline enters as scope words inside the claim ("on noisy recordings", "for graphs with more than 10,000 nodes"), not as a list of weaker numbers. When several results bound the headline, the scope words must cover all of them; if scope words alone cannot make the claim accurate, add the shortest clause that does.

## Readable

- Each paragraph has one job, and the reader can tell what it is early in the paragraph.
- Paragraphs follow the dependencies of the argument: what the reader needs to understand the obstacle comes before the obstacle, and the obstacle before its resolution. Each paragraph connects to what the reader already holds, usually where the previous one ended; the connection lies in the argument (from a limitation to its cause, from a proposal to its obstacle, from a method to its test), not in repeated words. Remove repeated contrasts, including those hidden in a contributions list.
- Known before new: start each sentence from something the reader already holds (the end of the previous sentence, a term already defined) and end on the new information. Introduce a concept in words before its notation.
- One main idea per sentence, but connect ideas that belong together: a run of short declaratives that each restate a fact reads like a list, so join a cause and its consequence with "because", "so" or "which".
- Every "so", "therefore" and "thus" must follow from what precedes it alone. If the conclusion needs a premise the paragraph has not stated, state the premise or drop the connective.
- Keep subject and main verb close together and early; at most one parenthetical per sentence.
- Spell out every acronym at first use as "full name (ACRONYM)", including agencies and standard method variants, unless it is universal for the target reader (DNA, GPU); then use the short form consistently. Do not drop a useful acronym to avoid expanding it. If the inputs do not give the expansion, keep the supplied name and flag it in Notes to author. Define every symbol at first use, and keep one name per concept (do not alternate "surrogate", "emulator" and "proxy").
- Verbs over nominalizations: "we estimate the noise" rather than "estimation of the noise is performed".
- Concrete over abstract: a number, an example, a named regime.
- Citations support statements about what prior work does; they never replace that description.
- Vary sentence length. An average near 20–25 words reads easily; a sentence over 40 words usually carries two ideas. These are diagnostics, not a reason to break a coherent explanation into fragments.

## Example (synthetic; the system and numbers are invented)

Obvious version:

> Quantum computing has attracted increasing attention in recent years due to its potential applications. Quantum error correction plays a crucial role, and many decoders have been proposed [1–12]. However, existing decoders still suffer from limitations such as high latency and limited accuracy. In this work, we propose a novel decoder that achieves state-of-the-art performance on several benchmarks.

Specific version (compressed into one paragraph for illustration):

> A surface-code quantum processor must decode each round of syndrome measurements before the next round arrives, roughly every microsecond. A slower decoder lets errors accumulate faster than they are corrected. Decoders that meet this deadline, from union-find to recent neural networks, assume that physical errors are independent across qubits and rounds [1–12]. On current hardware the assumption fails where it matters most: leakage and high-energy radiation events produce bursts of correlated errors, and these bursts cause most logical failures. Rather than correcting correlations after an independent-error decoder has run, we build the correlation structure into the decoder and estimate it from the syndrome stream while the device operates. On a distance-7 code, this lowers the logical error rate per round by a factor of 3.1 relative to the fastest independent-error decoder, within the same 1-µs budget.

What changed: the opening could only begin this paper and needs no notation; the closest work is described by what it does and the assumption its members share; the shortfall has a mechanism and a consequence; the turn reuses "independent" and "correlated"; the evidence is one number against a named comparator, with its condition inside the claim. In a real paper each of these statements about hardware and prior decoders needs its source in the inputs.

A component-level turn versus an idea-level turn (ml-conference):

- Component: "We replace the reward model with a larger network trained on more preference data."
- Idea: "Existing test-time adaptation methods assume the label distribution is the same at training and deployment; we estimate the deployment label distribution online and adapt the classifier to it."

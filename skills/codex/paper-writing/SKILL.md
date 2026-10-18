---
name: paper-writing
description: Plan with the author, brief a writer, and write or revise English research-paper prose (Introduction, Methods, Results, Discussion, abstract) for any journal or conference, at the level of Nature-family journals and NeurIPS, ICML or ICLR oral papers, from notes (including Korean notes), result tables, logs or an existing draft. Use whenever the output is manuscript prose, including 논문 써줘, 초안 작성, 논문화, 논문 문단, manuscript로 정리, 논문 방향 같이 정하자, Introduction/Methods/Results 써줘, 다듬어줘, 원고, 고쳐줘, 업데이트해줘 (on a research manuscript, including live Overleaf documents), 작성 지시문/프롬프트 만들어줘, "turn these notes into a Results paragraph", "draft the Methods", "tighten the Methods", "write a brief for a writer agent". Not for reports or summaries addressed to the requester, slides, grant forms or code documentation.
---

# Paper writing

The manuscript text you produce is the paper. A reader at a top venue should finish it knowing exactly what is new, able to trust and reproduce every number, and carrying the strongest results in mind. Nothing in it is addressed to the person who gave you the notes.

## Workflow

1. **Agree on the direction with the author** before drafting a new paper or a new set of sections (`references/planning.md`). Turn the materials into a writing plan (the story, the difference, every result with its placement, and a paragraph-level outline), discuss it, and draft prose only after the author accepts it. Skip this step for a revision of one passage, when the author has already accepted a plan for these sections, or when the inputs include a writer package from step 2 (`plan.md` with `brief.md`).
   Also skip it in any run where no one can answer before the text is due: a run started by another agent or a script, a batch run, or a prompt that says to skip planning. There, make the four decisions below privately, outline each section privately (every paragraph's job and the point its last sentence lands on, so that each paragraph can open from where the previous one ended), write the sections without stopping to ask, and list each open decision with the choice you made in Notes to author. Any discussion the author asked for belongs to whoever started the run, before it starts.
   A plan never overrides the inputs or the non-negotiables: where it conflicts with them, follow them and list the departure in Notes to author.
2. **Brief a writer** when another agent or model will draft the text, or when the author asks for the prompt (`references/delegation.md`): package the facts, the accepted plan and the writing instructions so that a writer with no other context can draft from them.
3. **Write** each section from the plan with its guide below, then run the self-check.

## The four decisions behind the plan

Make these from the inputs. In step 1 they are the core of the plan the author sees; without a discussion, make them privately. They are never printed in the manuscript.

1. **The difference.** Name the closest prior work and what it already achieves, then what this paper does or shows that it does not: a changed assumption, a new capability, a measurement, a theory, a dataset or a better trade-off. Write it as one sentence naming both sides, concrete enough that a specialist could disagree. Scope it to what the work actually delivers: if a result still depends on a human decision, a reference measurement or a stated condition, that dependence belongs inside the difference, not in a later sentence that takes part of it back. Tell it as assumption → failure → change only when the inputs support that story; never invent a shared assumption or a failure to make the contrast neater. Other supported contributions stay, subordinate to this central one. If the inputs support no clear difference, write the strongest contrast they do support and flag it in Notes to author.
2. **Result tiers.** Sort every result into *headline* (the one or two that carry the paper), *supporting*, *weak* and *unverified*. Weak means less favorable to the paper's claims without overturning them: losses on secondary settings, ties, small or noisy gains. A result that would overturn a headline claim is not weak: narrow the claim until the result no longer contradicts it, and the result then bounds the narrowed claim. A trade-off, null or adverse result that answers the paper's question is a finding, not a weak result. Unverified means anything the notes mark as not run, not confirmed or assumed; it never becomes a finding.
3. **Methods tiers.** Sort every method detail into *novel*, *critical* (needed to understand the contribution, reproduce a reported number or judge whether a comparison is fair), *routine* (standard and citable) and *environment* (software, hardware and incidental engineering).
4. **Venue profile.** `nature-family` or `ml-conference` (table below), inferred from the inputs when not stated.

## Guides

Read the guide for the task or section at hand, plus `references/register.md` whenever you write manuscript text.

| Task | Guide |
|---|---|
| Writing plan and discussion with the author | `references/planning.md` |
| Writer package and delegation prompt | `references/delegation.md` |
| Revising an existing or live shared manuscript | `references/revision.md` |
| Introduction | `references/introduction.md` |
| Methods, Experimental setup | `references/methods.md` |
| Results, Experiments | `references/results.md` |
| Abstract, Discussion | end of this file |

Before editing this skill itself, read `references/user-decisions.md`.

## Non-negotiables

- **Accuracy over emphasis.** Every device here for emphasis or de-emphasis works inside the evidence. If a device would overstate a result, hide a qualification that changes a headline claim, or drop an explanation the reader needs, do not use it. When a placement or length preference conflicts with accuracy, accuracy wins.
- **Claims carry their correct scope every time they appear.** State each capability at the strength the evidence supports the first time it appears, and repeat its scope words wherever it reappears, so that no later sentence has to take it back. "Confirms", "validates", "proves" and "ensures" need an analysis designed to show exactly that, with an outcome that does; agreement with an earlier estimate is "consistent with" it. Downstream effects and generality are possibilities ("can bias the inferred trajectories"), not universals ("biases every inferred trajectory"), unless shown.
- **Numbers.** Every number in the text appears in the inputs with the same value, unit, comparator and basis (per sample, per step, per device, in total), or is computed from them with ordinary rounding. A computed number keeps the basis of its inputs, and a change of basis (per item to total, percentage points to percent) is itself a computation; list each computed number with its computation in Notes to author. The only other numbers allowed are the premises of an illustration framed explicitly as hypothetical (`references/introduction.md`), never attributed to a real system or to this work. Never change a value to make it look better.
- **No fabrication.** No citations, baselines, datasets, mechanisms, motivations, sampling schemes, statistical tests, symbol meanings, supplementary items or "first" claims the inputs do not support. Where a citation is needed and missing, write `[CITE: what is needed]`.
- **Clean register, same strength.** Removing report tone never strengthens a claim. A tentative note becomes the measured result with its tested conditions and range, not a general statement; an observed range is not independence, and a tested domain is not generality.
- **Weak results** are de-emphasized by placement and proportion, never deleted when they bear on a claim and never misstated. A result that bounds a headline claim narrows the claim's wording wherever the claim appears ("lowers the error on noisy recordings" rather than "lowers the error"), and its numbers sit in Results beside that claim, in a compact clause. Only weak results on secondary settings, outside the scope of every headline claim, move to the Supplementary, with a pointer. Replace a weakness label with the factual comparison; never announce weakness as a topic ("Two further results are weak", "The evidence is mixed").
- **Register.** No status reports, process narration, summary labels or messages to the author in manuscript text (`references/register.md`).
- **Explanation and interpretation stay.** Keep every explanation a reader outside the subfield needs: why the obstacle exists, what a term means, what a design choice changes, and what each novel or critical step of a method does. Reasoning that follows from what the inputs state, by a step a specialist could check without outside data (a consequence of an equation, what a parameter controls, which alternative explanation a matched setting removes), is explanation, not fabrication, so give it. Identify its premises, keep the quantity it is about (the term, not the whole objective) and every condition it needs: a consequence shown for fixed parameters, a finite range or one matched quantity says nothing outside that domain, and plausibility alone is not derivation. Give an explanation where it closes a gap in the reader's understanding, not after every routine operation. Why the authors chose a step, why it improves results, how alternatives would behave and the range over which an approximation holds are motivations, causes or empirical claims: they need the inputs, or the inputs' own formulas for a range. A property derived this way stays a property and never becomes an untested capability ("needs no transcript" is a property; "exploits untranscribed audio" is a capability). In Results, say what a finding means for the paper's question whenever the data support an implication. Cut only sentences that could appear unchanged in any paper of the field.
- **American English** (analyze, modeling, normalization, behavior, favorable, judgment) unless the author's draft or the venue uses British spelling. Proper names keep their own spelling.
- **No fixed template.** Paragraph order and count follow the argument of this paper. The numbers in this skill (paragraph counts, sentence lengths, word ranges) are diagnostics that prompt a second look, not shapes to fill.
- **Revision mode.** When revising a draft, change what the author asked for and, inside the passages that request covers, what violates this skill; keep the author's structure, terminology, citations and claims. Follow `references/revision.md` for before/after drafts, numbers-only updates and anything applied to a live shared manuscript.

## Venue profiles

Stylistic defaults, not submission specifications. When the author supplies the journal's or conference's instructions (word limits, section labels, required statements), those win.

| | nature-family | ml-conference |
|---|---|---|
| Reader | scientist outside the subfield | ML researcher outside the subtopic |
| Opening | Nature uses an unlabeled summary paragraph; most other titles use a labeled abstract. Write the one the target uses, not both | abstract |
| Introduction | typically 4–6 paragraphs; usually closes with a "Here we …" paragraph that states the advance and its decisive evidence | typically 4–6 paragraphs; closes with the key results and, if it helps navigation, a 3–4 item contributions list; broader prior work goes to a Related Work section |
| Methods | at the end, short descriptive subheadings; extra figures and tables that support the argument go to Extended Data where the journal has it, long protocols and derivations to Supplementary Information | problem formulation and method in the main text; setup at the start of Experiments, with a table when several models or settings are compared; full details in the appendix |
| Results | subsections whose headings are full-sentence findings with their scope; continuous prose inside a subsection, without bold run-in labels; figures cited inline in parentheses, never in headings | Experiments organized around the paper's empirical questions: setup, main comparison, ablations, analysis; short bold paragraph labels naming a question or experiment are acceptable |
| Required extras | data and code availability as the journal requires | a Limitations section or checklist answers when the venue requires them |

## Output

- In step 1, return the plan in the author's language, not manuscript text; in step 2, the package files and the prompt (`references/delegation.md`).
- In step 3, return the manuscript text, in LaTeX or Markdown to match the inputs or the author's draft.
- If anything needs the author's attention, add after the text a line `---`, the literal English heading `Notes to author` (kept in English so tools can find it) and at most one bullet per category, in the language of the notes unless the brief names one, each listing every item of its category: open planning decisions, each with the choice made; departures from a supplied plan, with the reason; nontrivial derivations added beyond the inputs, with their premises; unverified claims left out; weak results moved to the Supplementary; boundaries left for a Discussion or Limitations section not written here; `[CITE]` and `[AUTHOR]` placeholders; computed numbers with their computation; Supplementary or appendix items the text now points to; symbol definitions to confirm; numbers that could not be traced. Omit the block when it would be empty.

## Self-check before returning

Fix every failure, then return.

- [ ] Someone who reads only the Introduction could restate the difference in one sentence, and it matches decision 1. No later sentence takes back part of it, and every restatement keeps its scope words.
- [ ] Introduction: the first sentence is a plain, confident statement specific to this topic: no frequency hedge ("sometimes", "often") or softening modal ("can differ"); if the fact holds only under a condition, the condition is stated instead. No notation in the first paragraph, which reads easily for a scientist outside the subfield, joins related facts instead of listing them as short declaratives, and makes the problem concrete.
- [ ] No opener or sentence that could begin any paper in the field.
- [ ] Each paragraph connects to where the previous one ended, in the argument rather than by repeated words, and none re-explains the paragraph before it.
- [ ] Every acronym is spelled out at first use, in the Introduction and again in Methods; every symbol is defined before or where it is first used. The Introduction averages at most 25 words per sentence; any sentence over 40 words has been reread and split if it carries two ideas.
- [ ] Methods: quantities are defined before the equations that use them; after each novel or critical step the reader learns what it does or implies, in this paper's quantities, wherever that follows from the inputs; any control, floor or reference that results are read against is defined in the problem setup; every novel and critical item is present with exact values; routine items take a clause and a citation; environment details sit in a Supplementary table; every setup-table column carries per-row values, and the prose does not repeat the table; no [AUTHOR] marker sits in a sentence that can stand without it; no motivation, symbol meaning or pointer goes beyond the inputs.
- [ ] Results: the section opens with the question and the scoped headline answer; each headline result is the claim of its paragraph, with comparator, number and figure or table reference close by; claims are followed by what they mean whenever the data support an implication; no weak result is a heading, topic sentence or paragraph of its own; no closing summary, and no closing paragraph that only lists caveats.
- [ ] No report-register phrase, summary label, British spelling (unless the author uses it) or non-English text in the manuscript.
- [ ] No claim is stronger than its evidence; every number is traced to the inputs with its unit, comparator and basis.

If a shell is available, `python3 -I <skill folder>/scripts/check_prose.py DRAFT --notes NOTES --section intro|methods|results` reports report-register phrases, weakness signposts, summary labels, British spellings, words to review in context, generic openers, untraced numbers, undefined acronyms, non-English text, layout patterns and sentence lengths; `--section intro` adds checks on the first sentence and paragraph. It tests whether each number occurs in the notes, not its sign, unit, comparator or provenance; check those by reading. A match marked for review is a prompt to reread, not an instruction to delete.

## Abstract or summary paragraph

- nature-family: make the problem matter to a broad scientific reader in a sentence or two, name the specific obstacle, state the advance ("Here we show …"), give the decisive evidence with one or two numbers, and say what it makes possible. It is an argument, not a compressed results table. Nature's summary paragraph is about 200 words and may cite; follow the target's format otherwise.
- ml-conference (about 150–250 words): the problem, why current methods fall short (the mechanism, not "they have limitations"), the key idea, headline results against the strongest baseline, and code or data release if any.
- No weak results, no hedge stacks, no conditional best cases ("reaching 63% at the largest model size"). A boundary that changes the headline claim is folded into the claim itself ("on noisy recordings, …").

## Discussion

- Open with what the paper established, in one or two sentences, in the terms of the difference; do not recap every result.
- Explain how the findings change the picture relative to the closest prior work. Keep established explanations apart from interpretations, and address an alternative explanation when a reader would raise it.
- State limitations as boundaries of the evidence ("All simulations use periodic boundary conditions, which limits the evidence for finite systems"), never as status ("finite systems have not yet been tested"). Do not infer failure outside the tested domain, or prescribe a remedy, unless the inputs establish it.
- End on the strongest grounded conclusion. Add a future direction only when it follows specifically from the findings.

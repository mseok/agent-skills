---
name: paper-writing
description: Write or revise English research-paper prose (Introduction, Methods, Results, Discussion, abstract) from research notes, tables, logs or a draft, adapting the scientific framing, argument, explanation and disciplinary language to the target journal or conference and article type. Plan with the author when requested, or proceed from a supplied direction; brief a separate writer when needed. Use for 논문 써줘, 초안 작성, 논문화, 논문 문단, manuscript로 정리, 논문 방향 같이 정하자, Introduction/Methods/Results 써줘, 다듬어줘, 원고, 고쳐줘, 업데이트해줘 (on a research manuscript, including live Overleaf documents), 작성 지시문/프롬프트 만들어줘, "turn these notes into a Results paragraph", "draft the Methods", "tighten the Methods", or "write a brief for a writer agent". Not for reports to the requester, slides, grant forms or code documentation.
---

# Paper writing

The manuscript text you produce is the paper. Make its scientific question, contribution and meaning clear to the intended readers, with the information needed to assess and reproduce the work in the appropriate places. Write the strongest supported message in natural disciplinary language. Keep the writing process and evidence audit out of the manuscript.

Use editorial guidance selectively to serve the whole argument. Natural progression, reader motivation and the author's direction take priority over stylistic heuristics. A broad scientific statement can establish essential context; a concrete example can distract. Do not make prose unusual, more technical or more detailed merely to satisfy a writing rule. Accuracy and faithful reporting remain required.

## Workflow

1. **Choose the writing direction** from the research record and the author's goal (`references/planning.md`). For a new paper or a changed target, read `references/venue-adaptation.md`: establish the exact journal, article type and readers, inspect suitable published examples, and choose the most consequential question the available results answer. Audit the full research history, including corrections and unfavorable results; privately outline the argument and the role of each figure and paragraph.
   When the author supplies a direction and asks for prose, proceed through drafting without a planning-approval round. Infer routine editorial choices, obtain public journal guidance yourself, and reuse an accepted plan or a supplied writer package. Ask only when a missing fact or unresolved choice would materially change the requested paper and cannot be handled locally. When the author explicitly asks to discuss the direction first, return the concise plan before drafting. In unattended or delegated runs, make reasonable choices and continue; report only unresolved decisions requiring the author's attention.
   A plan never overrides the inputs or the non-negotiables. Follow the evidence and explain any material departure outside the manuscript.
2. **Brief a writer** when another agent or model will draft the text, or when the author asks for the prompt (`references/delegation.md`): package the facts, the accepted plan and the writing instructions so that a writer with no other context can draft from them.
3. **Write** each section from the plan with its guide below and the contrasting examples in `references/register.md`. First develop the scientific argument for the intended reader; then verify and refine it. Do not continually interrupt composition to satisfy local style checks.
4. **Integrate the paper** before final wording: read `references/integration.md` and check the assembled draft against the agreed one-sentence central message. Reconcile the question, evidence and conclusion across sections, then polish the prose and run the self-check. For a scoped revision, use the available surrounding text and preserve the authorized edit boundaries.
5. **Verify references last, before finalization.** After the last substantive edit, invoke the `reference-verification` skill in **full** mode on the actual deliverable and supplied SI. Resolve or report its metadata and citation-support findings before declaring the manuscript reference-cleared. A metadata-only check is permitted when explicitly requested, but does not clear the whole manuscript. For an isolated writer, the coordinating agent owns source retrieval and this final check after integration (`references/delegation.md`). Keep audit findings outside manuscript prose. This mandatory check grants no additional editing permission.

## Keep preparation separate from the prose

Before drafting, understand the research history, the author's direction, the target readers and the strongest supported contribution. Keep a complete factual record, including corrections and material contrary results. Select the headline findings and decide where supporting evidence and reproducibility details belong. These editorial decisions remain working material.

Draft from that understanding as a connected scientific argument. Do not translate the fact ledger, novelty assessment or methods inventory into successive manuscript paragraphs. Explain what the science means to the reader. After the argument works, check every claim against the record and repair its wording locally when possible; do not add an audit narrative to a sound paragraph.

For the journal context, read the relevant entry in `references/journal-profiles.md` and matched public-paper analyses. Use their decisions about readership, contribution and explanation. A paper's publication does not make every rhetorical claim sound, and a journal's prestige does not determine a paper's ambition.

## Guides

Read the guide for the task or section at hand, plus `references/register.md`, including its contrasting examples, whenever you write manuscript text. Apply the examples' editorial decisions, not their sentence patterns.

| Task | Guide |
|---|---|
| Writing plan and discussion with the author | `references/planning.md` |
| Target journal, readers, framing and disciplinary language | `references/venue-adaptation.md` |
| Dated journal examples and contribution-specific writing choices | `references/journal-profiles.md`; read only the relevant journal |
| Article-level examples for the chosen journal | `references/corpus-nature-biotech.md`, `references/corpus-computational-ai.md`, or `references/corpus-chemistry.md`; select relevant articles |
| Writer package and delegation prompt | `references/delegation.md` |
| Revising an existing or live shared manuscript | `references/revision.md` |
| Introduction | `references/introduction.md` |
| Methods, Experimental setup | `references/methods.md` |
| Results, Experiments | `references/results.md` |
| Figures and panels | the `nature-figure` skill for quantitative data charts and multi-panel plots, and the `concept-figure` skill for schematic, architecture, mechanism or pipeline diagrams; read the matching skill before planning or producing any figure |
| Final integration across sections | `references/integration.md` |
| Final reference verification, after all substantive edits | the `reference-verification` skill, full mode ([source](../reference-verification/SKILL.md)) |
| Abstract, Discussion | end of this file |

Before editing this skill itself, read `references/user-decisions.md`.

## Non-negotiables

- **Accuracy over emphasis.** Every device here for emphasis or de-emphasis works inside the evidence. If a device would overstate a result, hide a qualification that changes a headline claim, or drop an explanation the reader needs, do not use it. When a placement or length preference conflicts with accuracy, accuracy wins.
- **Keep the scientific message in front.** State findings and their scientific meaning directly. Never turn the manuscript into an evidence-status report, a catalogue of unperformed experiments or repeated explanations of what a result does not prove. Before adding a qualification, ask what interpretation it changes for the intended reader. If none, omit it. When one is needed, make the scientific statement precise rather than appending a defensive disclaimer. Do not manufacture an overclaim simply to rebut it.
- **Preserve meaning through context.** Use the right scientific object, verb and conditions for the result. Conditions established in a connected passage carry forward; do not mechanically repeat scope words or add "in this study", "under the tested conditions" or "does not establish" to each restatement. Repeat a condition when its omission would change the meaning, when the context changes, or in a passage read independently such as the abstract. Choose "confirms", "validates", "proves" and "ensures" only for the scientific operation and result actually supplied; do not narrate that choice in the paper. Express an important implication at its justified strength, without surrounding it with generic uncertainty.
- **Numbers.** Every number in the text appears in the inputs with the same value, unit, comparator and basis (per sample, per step, per device, in total), or is computed from them with ordinary rounding. A computed number keeps the basis of its inputs, and a change of basis (per item to total, percentage points to percent) is itself a computation; record each computed number and its computation in the working notes, and flag it to the author when it requires attention. The only other numbers allowed are the premises of an illustration framed explicitly as hypothetical (`references/introduction.md`), never attributed to a real system or to this work. Never change a value to make it look better.
- **No fabrication.** No citations, baselines, datasets, mechanisms, motivations, sampling schemes, statistical tests, symbol meanings, supplementary items or "first" claims the inputs do not support. Where a citation is needed and missing, write `[CITE: what is needed]`.
- **Clean register, same strength.** Removing report tone never strengthens a claim. A tentative note becomes the measured result with its tested conditions and range, not a general statement; an observed range is not independence, and a tested domain is not generality.
- **Less favorable results** get space in proportion to their bearing on the claims, are never deleted when they bear on a claim and are never misstated. A result that bounds a headline claim narrows the claim's wording wherever the claim appears ("lowers the error on noisy recordings" rather than "lowers the error"), and its numbers sit in Results beside that claim, in a compact clause. Only weak results on secondary settings, outside the scope of every headline claim, move to the Supplementary, with a pointer. Replace a weakness label with the factual comparison; never announce weakness as a topic ("Two further results are weak", "The evidence is mixed").
- **Register.** No status reports, process narration, summary labels or messages to the author in manuscript text (`references/register.md`).
- **Explanation and interpretation stay.** Keep the explanations the intended readers need: why the question matters, what an unfamiliar term means, what a design choice changes and how a non-obvious step works. Reasoning that follows from the inputs by a step a specialist could check without outside data (a consequence of an equation, what a parameter controls, which alternative explanation a matched setting removes) is explanation, so give it. Check its premises, object and conditions privately and express the consequence naturally where it helps the argument. Give explanations where they close a gap, not after every routine operation. Author motivation, causes of empirical effects and untested alternatives still need evidence; plausible reasoning alone is not an experimental finding. In Results, explain what the finding means for the paper's question. Place reproducibility details where the target format allows them to be found, preserving information that changes interpretation; keep the source notes complete.
- **American English** (analyze, modeling, normalization, behavior, favorable, judgment) unless the author's draft or the venue uses British spelling. Proper names keep their own spelling.
- **No fixed template.** Paragraph order and count follow the argument of this paper. The numbers in this skill (paragraph counts, sentence lengths, word ranges) are diagnostics that prompt a second look, not shapes to fill.
- **Revision mode.** When revising a draft, change what the author asked for and, inside the passages that request covers, what violates this skill; keep the author's structure, terminology, citations and claims. Follow `references/revision.md` for before/after drafts, numbers-only updates and anything applied to a live shared manuscript.

## Apply the journal choices

Use the target's actual requirements for abstract form, word limits, section labels, Methods placement, supplementary material and required statements. Use matching articles to inform explanatory depth, paragraph functions, headings and disciplinary usage. A short technical Introduction or a detailed specialist argument may be appropriate in either a broad or a specialist journal. Never infer a fixed paragraph count, a compulsory contributions list or a lower scientific ambition from a journal family. Reuse verified choices for the same paper instead of rediscovering them on every passage revision.

## Output

- When a planning discussion is requested, return the concise plan in the author's language; otherwise complete the requested prose. For a writer-package request, return the package and prompt (`references/delegation.md`).
- After steps 3–5, return the manuscript text, in LaTeX or Markdown to match the inputs or the author's draft; if reference verification is not clear, label the delivery as a draft and state the unresolved items.
- If anything needs the author's attention, add a line `---` and the heading `Notes to author` after the manuscript. Keep it concise, in the author's language unless the brief says otherwise: unresolved factual conflicts, placeholders, material departures or choices, nontrivial derivations, computations requiring confirmation, and figures, supplementary items or definitions the author must supply. Report moved results when their placement needs attention. Keep the complete evidence audit in working notes; do not print a routine inventory of unsupported extensions, missing experiments unrelated to the selected message, or every editorial choice. Omit an empty block.

## Self-check before returning

Resolve factual errors and material omissions, then judge the draft as a connected scientific argument. Treat stylistic checks as prompts for judgment, not quotas or automatic reasons to rewrite sound prose.

- [ ] Complete the integration pass in `references/integration.md`: the sections address the same central message at the same evidential scope. Compare the draft's editorial choices with the examples in `references/register.md`; facts are organized into findings, and each limitation earns its place by changing interpretation or satisfying a venue requirement.
- [ ] Someone who reads only the Introduction can state the central contribution and why it matters to the target readers. It matches the evidence and the rest of the paper; its meaning stays consistent without repeated scope labels or defensive recaps.
- [ ] Introduction: establish a scientific problem and a reason for the intended reader to care, then develop the question and contribution. Use the level of abstraction that supports this progression; the opening need not be unique to this paper or describe its experimental contrast. Keep genuine frequency or conditionality, and introduce technical detail when it helps the reader understand the argument.
- [ ] Each paragraph connects to where the previous one ended, in the argument rather than by repeated words, and none re-explains the paragraph before it.
- [ ] Unfamiliar acronyms and symbols are defined where the intended readers need them, including independently read sections. Review long or dense sentences for readability; preserve necessary scientific terms and logical connections rather than targeting a fixed average length.
- [ ] Methods: organize the actual study so the intended readers can follow its design and non-obvious steps. Define quantities before use; make controls and comparisons intelligible. Preserve required values across the appropriate main and supplementary materials, avoid repeating setup tables, and invent no motivation, symbol meaning or pointer.
- [ ] Results: make the scientific question and findings clear, with the measurements, comparisons and figures needed to understand them nearby. Explain supported implications and complete the semantic review in `references/results.md`. Organize findings, interpretation and synthesis for the target article type; remove redundant recaps and caveat inventories. Keep material contrary findings, and do not give secondary unfavorable results disproportionate emphasis.
- [ ] No report-register phrase, summary label, British spelling (unless the author uses it) or non-English text in the manuscript.
- [ ] No claim is stronger than its evidence; every number is traced to the inputs with its unit, comparator and basis.
- [ ] The main scientific message remains clear. Remove qualifications that change no relevant interpretation, repeated "shown/not shown" language and internal review vocabulary; retain the actual conditions, contrary findings and explanations that matter.
- [ ] The separate `reference-verification` skill has checked the delivered main text and supplied SI in the required mode; remaining findings and the checked saved artifact are stated accurately.

If a shell is available, `python3 -I <skill folder>/scripts/check_prose.py DRAFT --notes NOTES --section intro|methods|results` reports report-register phrases, weakness signposts, summary labels, British spellings, words to review in context, generic openers, untraced numbers, undefined acronyms, non-English text, layout patterns and sentence lengths; `--section intro` adds checks on the first sentence and paragraph. When the draft uses computed values, make a separate working-notes copy containing the original source facts plus labeled computations with operands, units and basis; pass that copy as `NOTES`. Preserve the source notes unchanged and keep this arithmetic outside the manuscript and routine author notes. The checker tests whether each number occurs in the notes, not its sign, unit, comparator or provenance; check those by reading. It does not assess the paragraph's role in the argument, a case's explanatory value or whether an inference follows from its premises; passing it does not replace semantic review. A match marked for review is a prompt to reread, not an instruction to delete.

## Abstract or summary paragraph

- Follow the exact journal and article type for structure, length and citations. State the scientific question, the contribution, its decisive evidence and its meaning at the target readers' level. Let a finding, mechanism, method or resource determine the argument; do not force every abstract into a failed-methods story. Select quantities that explain the advance rather than compressing the Results into a list.
- No weak results, no hedge stacks, no conditional best cases ("reaching 63% at the largest model size"). A boundary that changes the headline claim is folded into the claim itself ("on noisy recordings, …").

## Discussion

- Open with what the paper established, in one or two sentences, in the terms of the difference; do not recap every result.
- Explain how the findings change the picture relative to the closest prior work. Keep established explanations apart from interpretations, and address an alternative explanation when a reader would raise it.
- Discuss a limitation when it changes interpretation, explains a result, identifies a consequential open question or satisfies the target's requirements. Explain the scientific consequence once, in the relevant discussion; do not append a generic "this does not establish X" after each finding or enumerate unrelated things not tested. Preserve important contrary evidence without turning the Discussion into an audit.
- End on the strongest grounded conclusion. Add a future direction only when it follows specifically from the findings.



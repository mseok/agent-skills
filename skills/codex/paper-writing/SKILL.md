---
name: paper-writing
description: Write or revise English research-paper prose (Introduction, Methods, Results, Discussion, abstract) from research notes, tables, logs or a draft, adapting the scientific framing, argument, explanation and disciplinary language to the target journal or conference and article type. Plan with the author when requested, or proceed from a supplied direction; brief a separate writer when needed. Use for 논문 써줘, 초안 작성, 논문화, 논문 문단, manuscript로 정리, 논문 방향 같이 정하자, Introduction/Methods/Results 써줘, 다듬어줘, 원고, 고쳐줘, 업데이트해줘 (on a research manuscript, including live Overleaf documents), 작성 지시문/프롬프트 만들어줘, "turn these notes into a Results paragraph", "draft the Methods", "tighten the Methods", or "write a brief for a writer agent". Not for reports to the requester, slides, grant forms or code documentation.
---

# Paper writing

Write the scientific argument the intended reader needs: why the question matters, what the study changes and how its evidence supports that change. Use natural disciplinary language. The manuscript is the paper; planning, evidence audits and instructions to the author stay outside it.

The author's direction and the complete research record govern the work. Every factual claim, number, citation and explanation must be supported; preserve material contrary findings and the conditions that change interpretation. Select a truthful contribution before choosing how emphatically to express it. Never invent a result, mechanism, priority claim or failure of prior work to improve the story.

## Work in three stages

### 1. Understand and choose

Read the research record, including corrections and unfavorable results. Follow `references/planning.md` to select the contribution in relation to the closest prior accomplishment and the most informative observations. For a new or changed target, follow `references/venue-adaptation.md`, the relevant entry in `references/journal-profiles.md` and matched article analyses. Obtain public guidance and examples yourself; do not ask the author to assemble a style profile.

Make a compact private drafting brief: the author's question, what the closest work already makes possible, the new understanding supported here, the observations carrying that understanding, and the scientific explanation the reader needs. Keep the full factual record underneath it. Source-note categories, method components and audit categories are not a manuscript outline. Relevant contrary evidence determines the message rather than becoming an obligatory negative sentence appended later.

When the direction and a request for prose are supplied, make routine editorial choices and proceed. Discuss the plan first only when the author requests that discussion. Reuse accepted plans and supplied writer packages. Ask about a missing fact only when it materially changes the paper and cannot be handled locally; continue the useful work. An internal plan is provisional, not author-approved.

### 2. Compose and reconstruct

Read the section guide and the contrasting examples in `references/register.md` before writing. For an Introduction, also read the short synthetic whole-argument example in `references/argument-example.md`. Learn editorial decisions, not layouts or phrases. Develop the paper from the selected argument instead of reciting the source packet in order.

Write a complete draft. Explain scientific objects, decisions and consequences in the vocabulary the target readers use. A broad opening, concrete example, technical detail or result belongs when it advances the reasoning; none is mandatory. Let the actual question determine the paragraph order, count and depth. Keep the strongest supported scientific message visible without repeated scope labels, proof-status contrasts or a catalogue of unperformed work. Context established in a connected passage carries forward.

Then read `references/integration.md` and assess the argument actually written. For a newly requested draft, reconstruct the argument once when needed: change the allocation of background, select a different leading comparison, or explain the method's scientific role. Fix the reason to read and the connection between question and answer before polishing transitions. For a scoped revision, preserve its authorized boundaries and follow `references/revision.md`; mark proposed changes inline.

### 3. Verify and deliver

After substantive revision, read `references/accuracy.md` and `references/prose-audit.md`. Check all claims against the complete record, including unfavorable comparisons. Resolve factual errors and consequential omissions, and refine wording without turning the paper into an account of its verification. Scientific explanations and interpretations remain when supported; removing report tone must never strengthen a claim.

After the last substantive edit, invoke the separate `reference-verification` skill in **full** mode on the actual deliverable and supplied SI. Resolve or report metadata and citation-support findings before declaring the manuscript reference-cleared. A metadata-only check applies only when explicitly requested and does not clear the whole manuscript. For an isolated writer, the coordinating agent owns retrieval and this final check. It grants no additional editing permission.

Return the requested manuscript in the input's LaTeX or Markdown format. If references remain unresolved, label it a draft and state the specific unresolved items. Add `---` and `Notes to author` only for matters requiring attention: factual conflicts, placeholders, consequential departures or decisions, nontrivial derivations or computations, and missing figures, definitions or supplementary items. Use the author's language for these notes. Keep the complete audit in working notes; do not print routine editorial checks or unrelated untested possibilities.

## Select the relevant guides

| Task | Read |
|---|---|
| Direction, evidence selection and author discussion | `references/planning.md` |
| Journal, readers, explanatory depth and terminology | `references/venue-adaptation.md`; relevant part of `references/journal-profiles.md` |
| Matched published examples | Relevant articles in `references/corpus-nature-biotech.md`, `references/corpus-computational-ai.md` or `references/corpus-chemistry.md` |
| Brief another writer or produce a writer prompt | `references/delegation.md` |
| Revise an existing or live shared manuscript | `references/revision.md` |
| Introduction | `references/introduction.md`; `references/argument-example.md` |
| Methods or Experimental setup | `references/methods.md` |
| Results or Experiments | `references/results.md` |
| Abstract or Discussion | `references/abstract-discussion.md` |
| Every manuscript-writing task, before composition | Contrasting examples in `references/register.md` |
| Substantive revision and alignment across sections | `references/integration.md` |
| After substantive revision | `references/accuracy.md`; `references/prose-audit.md` |
| Final reference check | Separate `reference-verification` skill, full mode ([source](../reference-verification/SKILL.md)) |

For quantitative charts and multi-panel plots, read the `nature-figure` skill before planning or producing the figure. For schematic, architecture, mechanism or pipeline diagrams, read `concept-figure`. Do not invent missing data or make explanatory figures substitute for evidence.

For a writer-package request, return the self-contained package and prompt specified in `references/delegation.md`. For an explicitly requested planning discussion, return the concise plan in the author's language before drafting. A supplied direction otherwise permits completion in one invocation.

Before editing this skill itself, read `references/user-decisions.md`. Writers do not need that maintenance record.

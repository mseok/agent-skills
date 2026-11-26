---
name: paper-writing
description: Write or revise English research-paper prose (Introduction, Methods, Results, Discussion, abstract) from research notes, tables, logs or a draft, adapting the scientific framing, argument, explanation and disciplinary language to the target journal or conference and article type. Plan with the author when requested, or proceed from a supplied direction; brief a separate writer when needed. Use for 논문 써줘, 초안 작성, 논문화, 논문 문단, manuscript로 정리, 논문 방향 같이 정하자, Introduction/Methods/Results 써줘, 다듬어줘, 원고, 고쳐줘, 업데이트해줘 (on a research manuscript, including live Overleaf documents), 작성 지시문/프롬프트 만들어줘, "turn these notes into a Results paragraph", "draft the Methods", "tighten the Methods", or "write a brief for a writer agent". Not for reports to the requester, slides, grant forms or code documentation.
---

# Paper writing

Write the scientific argument the intended reader needs: why the question matters, what the study changes and how its evidence supports that change. Use natural disciplinary language. The manuscript is the paper; planning, evidence audits and instructions to the author stay outside it.

The author's direction and the complete research record govern the work. Every factual claim, number, citation and explanation must be supported; preserve material contrary findings and the conditions that change interpretation. Select a truthful contribution within the supplied scientific purpose before choosing how emphatically to express it. Never invent a result, mechanism, priority claim or failure of prior work to improve the story.

## Separate editorial preparation, composition and correction

The coordinating agent owns the complete research record, all applicable skill instructions and the final deliverable. For a new Introduction, a complete section draft or a substantial rewrite, use the fresh-context protocol in `references/delegation.md`: prepare the editorial brief, commission composition in a context without the preparation history, and check the resulting text in a separate correction context. A new heading or a request to forget instructions does not create a fresh context. Use the documented fallback when separate contexts are unavailable. Keep narrow edits proportionate to their authorized scope.

These are internal roles within one invocation, not additional approval rounds. A supplied direction and request for prose authorize ordinary editorial decisions and completion. Preserve explicit requests to discuss direction first, accepted plans, revision boundaries and inline change marking.

### 1. Understand and choose

Read the research record, including corrections and unfavorable results. Follow `references/planning.md` to select the contribution in relation to the closest prior accomplishment and the most informative observations. Read the applicable section guides, `references/integration.md`, `references/accuracy.md` and `references/prose-audit.md` in the coordinator's context. Read all five contrasts in `references/register.md` before preparing any manuscript draft. For an Introduction, also read `references/argument-example.md`.

For a new or changed target, follow `references/venue-adaptation.md`, the relevant entry in `references/journal-profiles.md` and matched article analyses. Obtain public guidance and examples yourself; do not ask the author to assemble a style profile. Examine complete Introduction or opening prose from matched primary articles before a new draft, and make that prose available to the composer through permitted private inputs or verified source access.

Prepare the compact editorial brief specified in `references/delegation.md`. Explain the positive scientific purpose, the live issue after the closest prior accomplishment, the organizing idea that responds to that issue, and the supported contribution's value to the intended readers. Give literature a role in that reasoning. Keep the complete facts separately available; a short brief never replaces them. Comparative controls establish what can credibly be said about the scientific purpose; they do not automatically become that purpose. Preserve material contrary findings and change the purpose only when the evidence requires it or the author directs it.

When the direction and a request for prose are supplied, make routine editorial choices and proceed. Discuss the plan first only when the author requests that discussion. Reuse accepted plans and supplied writer packages. Ask about a missing fact only when it materially changes the paper and cannot be handled locally; continue the useful work. An internal plan is provisional, not author-approved.

### 2. Compose and reconstruct

Start the composer without inherited conversation history. Supply `references/composition.md`, the editorial brief, the complete research facts, the named published openings and any authorized revision text. Do not send this coordinating guide, detailed planning or audit instructions, or preparation transcripts to the composer. Translate the five register contrasts into the positive writing intent in the composition card and the task's scientific brief; do not turn them into a checklist to narrate.

Have the composer read the complete facts and source openings, then write a complete draft in the field's language. The brief supplies scientific reasoning and author decisions, not paragraph slots. Let the actual question determine paragraph order, count and depth. No opening type, technical detail or numerical result quota is mandatory.

Read the draft as a manuscript, then apply `references/integration.md` in the coordinator's context. When the reason to read or the connection between question and answer is missing, return a short scientific instruction to the composer and reconstruct the affected argument. Do not repair an unresolved argument by adding audit prose. For a scoped revision, follow `references/revision.md`, preserve the authorized boundaries and mark proposed changes inline.

### 3. Verify and deliver

After argument revision, use a separate correction context as specified in `references/delegation.md`. Give it the actual draft, complete record, binding author decisions, source material and detailed accuracy and prose guides. Check every claim against the record, including unfavorable comparisons. Require identifiable errors, consequential omissions and precise repairs; distinguish these from editorial preferences. Preserve a coherent argument unless the evidence requires rebuilding it. Recheck any substantive correction against its source and surrounding meaning. Removing report tone must never strengthen a claim.

After the last substantive edit, invoke the separate `reference-verification` skill in **full** mode on the actual deliverable and supplied SI. Resolve or report metadata and citation-support findings before declaring the manuscript reference-cleared. A metadata-only check applies only when explicitly requested and does not clear the whole manuscript. For an isolated writer, the coordinating agent owns retrieval and this final check. It grants no additional editing permission.

Return the requested manuscript in the input's LaTeX or Markdown format. If references remain unresolved, label it a draft and state the specific unresolved items. Add `---` and `Notes to author` only for matters requiring attention: factual conflicts, placeholders, consequential departures or decisions, nontrivial derivations or computations, and missing figures, definitions or supplementary items. Use the author's language for these notes. Keep the complete audit in working notes; do not print routine editorial checks or unrelated untested possibilities.

## Select the relevant guides

| Task | Read |
|---|---|
| Direction, evidence selection and author discussion | `references/planning.md` |
| Journal, readers, explanatory depth and terminology | `references/venue-adaptation.md`; relevant part of `references/journal-profiles.md` |
| Matched published examples | Relevant articles in `references/corpus-nature-biotech.md`, `references/corpus-computational-ai.md` or `references/corpus-chemistry.md` |
| Orchestrate fresh composition and correction, or produce a writer package | `references/delegation.md` |
| Instructions given to the fresh composer | `references/composition.md` |
| Revise an existing or live shared manuscript | `references/revision.md` |
| Introduction | `references/introduction.md`; `references/argument-example.md` |
| Methods or Experimental setup | `references/methods.md` |
| Results or Experiments | `references/results.md` |
| Abstract or Discussion | `references/abstract-discussion.md` |
| Coordinator preparation for every manuscript-writing task | All five contrasting examples in `references/register.md` |
| Substantive revision and alignment across sections | `references/integration.md` |
| Coordinator preparation and separate correction after substantive revision | `references/accuracy.md`; `references/prose-audit.md` |
| Final reference check | Separate `reference-verification` skill, full mode ([source](../reference-verification/SKILL.md)) |

For quantitative charts and multi-panel plots, read the `nature-figure` skill before planning or producing the figure. For schematic, architecture, mechanism or pipeline diagrams, read `concept-figure`. Do not invent missing data or make explanatory figures substitute for evidence.

For a writer-package request, return the self-contained package and prompt specified in `references/delegation.md`. For an explicitly requested planning discussion, return the concise plan in the author's language before drafting. A supplied direction otherwise permits completion in one invocation.

Before editing this skill itself, read `references/user-decisions.md`. Writers do not need that maintenance record.

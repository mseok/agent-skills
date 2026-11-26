# Coordinate preparation, composition and correction

Use this protocol for new Introductions, complete section drafts and substantial rewrites, and when the author asks for a writer package. Complete the roles within the authorized task; do not ask the author to approve routine handoffs. An explicit request to discuss the direction first still requires that discussion before drafting. Preserve accepted plans and the scope and inline-marking rules in `revision.md`.

## Prepare the inputs

The coordinator reads the complete research record and all applicable skill guides, including all five contrasts in `register.md`, before briefing the composer. Obtain the target's current requirements and matched primary prose through `venue-adaptation.md`. Keep detailed planning and verification instructions in the coordinator's context.

Put the following inputs in a self-contained package. A short editorial brief may select an argument; it may not replace or selectively sanitize the factual record.

| Input | Contents and readers |
|---|---|
| `brief.md` | A compact editorial brief, specified below. Read by coordinator, composer and corrector. |
| `notes.md` and necessary source records | The complete research facts: each number with its source locator, unit, comparator, condition, basis, aggregation and uncertainty; figure or table identity; corrected or superseded values; conflicting facts; missing definitions; author interpretations; and planned or unrun work explicitly identified. Preserve every result that tests, bounds or contradicts a claim or belongs to a reported aggregate. Copy values exactly. Attach original tables or records when a transcription would lose information. Read by all roles. |
| Matched source material | The complete published Introductions or opening prose, with source identity and access details, plus the source passages needed to understand their contributions. Use permitted private files or source access verified for the composer. Abstracts and editorial summaries do not substitute for complete openings. Keep full text out of public skill files and final deliverables. |
| `plan.md`, when present | The original plan and its status. An accepted plan records the author's acceptance; an internal plan is provisional. Read by coordinator and corrector. Carry every binding decision, exact wording and placement constraint into the brief without carrying detailed planning or audit categories into composition. Do not invent acceptance or require a new plan. |
| Authorized revision text, when applicable | The exact source passages, sufficient surrounding context, permitted edit scope and required inline-change format. Give the composer readable context without authorizing edits outside it. |
| Calculation record, if produced | A separate composer output recording each derived value with its operands, units, basis and source locators. Name its output path in the prompt and pass the returned record to the corrector with the unchanged source facts. |
| Run record | The exact prompts, role-specific allowed inputs, source access, skill version or file hashes, input hashes, output paths, model and reasoning effort actually used, and whether history inheritance was disabled. Include the provenance of central framing premises and substantive transformations from source notes to the brief, distinguishing recorded history from editorial inference. Retain the draft checked by each review. Keep this record outside the manuscript. |

### Write the editorial brief

Write a compact, connected scientific argument that the composer can develop: the consequential problem motivating the work, the difficulty within it, the relevant accomplishment of prior research, and the specific question or opportunity that leads to this study's organizing idea and contribution. Make the transitions explicit in ordinary scientific language and show why the supported addition matters to the intended readers. Establish the motivation before naming the systems or comparisons that demonstrate the answer. Preserve the author's purpose, material contrary findings and conditions that change the message. Controls may establish useful scope without becoming the paper's purpose. Keep the source-to-argument trace in the preparation record; give the composer the resulting reasoning and access to the complete facts.

Add the exact venue and article type, intended readers and assumed knowledge, necessary disciplinary usage, binding author decisions, sections requested, format, spelling, target length when known, citation conventions and the language of author notes. Specify `[CITE: what is needed]` for unverified citation support, and `[AUTHOR: what is needed]` only where an essential missing fact prevents a required sentence. Translate the applicable section guides into the concrete scientific and output requirements this task needs, preserving reproducibility details and their agreed placement. Identify the matched openings to read and briefly explain why their editorial choices are informative. Distinguish official requirements from observed examples. A writing example is not automatically a scientific citation.

Keep this brief compact enough to guide a whole argument. Use connected reasoning rather than a method inventory, result tiers, permission labels, forbidden-claim catalogue or paragraph template. If an approved outline or wording binds the task, preserve it explicitly. The detailed record remains available to prevent selection from hiding contrary evidence. When no plan exists, make the editorial choices privately and proceed; do not transfer planning back to the author or require the composer to reconstruct the coordinator's audit.

## Compose in a fresh context

Create a new agent or model session with conversation inheritance disabled; use the harness's explicit fresh-context option when available. A full-history fork is not a fresh composer. Pass only the completed task prompt, `composition.md`, the brief, complete facts, named sources and authorized revision context. Do not attach `SKILL.md`, other skill guides, private planning notes, audit transcripts, prior evaluations or earlier candidate drafts. Include an earlier draft only when it is the actual text the author asked to revise.

Verify that the composer can read every allowed input and complete source opening and can write the requested output. If using online source access, permit only the named reading access needed for the task; otherwise supply permitted readable files. Do not depend on implicit skill discovery or the coordinator's conversation history.

Fill in this prompt, removing inapplicable revision fields:

```text
You are composing the requested research-paper prose from a prepared editorial brief.

Read only {COMPOSITION_CARD}, {BRIEF}, {COMPLETE_FACTS_AND_SOURCE_RECORDS}, {NAMED_PUBLISHED_OPENINGS_AND_SOURCE_MATERIAL}, and {AUTHORIZED_REVISION_TEXT_IF_ANY}. Read the complete facts and each complete named opening. The coordinator has handled editorial preparation and source discovery. Do not read other skill files, planning or audit records, or other drafts, and do not run review scripts. Use only the named source access supplied here.

Write {REQUESTED_SECTIONS} for the readers and scientific purpose in the brief. Develop its connected scientific reasoning in your own organization and language, respecting every binding author decision. Keep the complete factual record and material contrary findings in view; the brief selects an argument without overriding the facts. Make routine editorial decisions and finish the requested prose. Use the specified placeholder and a concise author issue if an essential fact is missing.

{REVISION_SCOPE_AND_INLINE_CHANGE_CONTRACT_IF_ANY}

Write {OUTPUT_FILES} in {FORMAT}. Put only the requested manuscript text in the manuscript files; put actionable author issues in {AUTHOR_ISSUES_FILE}. If you derive any values, write {CALCULATIONS_FILE} with each calculation's operands, units, basis and source locators; leave the source records unchanged. Read the complete passage for scientific meaning and progression before returning. Final reply: output paths and word counts. The coordinator owns the subsequent factual and full reference checks; do not claim that this draft has passed them.
```

## Read and integrate the argument

The coordinator reads the returned draft continuously before consulting its reverse outline. Apply `integration.md` to the argument actually written. Assess whether the scientific purpose, organizing idea, literature and contribution make one intelligible progression. Do not equate more technical detail, a particular opening or skill compliance with better writing.

If a substantive problem remains, return a short instruction in the paper's scientific terms to the composer, with any needed facts and the precise authorized scope. Explain the missing connection or changed scientific premise; do not send the audit transcript or demand checklist vocabulary in the paper. Reconstruct only where necessary, then retain the coherent version for correction. An accepted purpose remains unless the evidence requires a change or the author directs one.

## Check in a separate correction context

Start another session without inherited conversation history. Give it the actual draft, complete facts and relevant source material, any returned calculation record, brief, original plan or author decisions, revision scope, and `accuracy.md`, `prose-audit.md`, `register.md` and the applicable section guides. Include `revision.md` for revisions and surrounding manuscript sections when supplied. The corrector must inspect the complete record independently, not only statements chosen for the brief.

Use this prompt with all inputs named explicitly:

```text
Check {DRAFT} against {COMPLETE_FACTS_AND_SOURCE_RECORDS}, {RELEVANT_PRIMARY_SOURCE_MATERIAL}, {CALCULATIONS_FILE_IF_PRODUCED}, {BRIEF}, and {AUTHOR_DECISIONS_AND_SCOPE}. Read {ACCURACY_GUIDE}, {PROSE_AUDIT_GUIDE}, {REGISTER_GUIDE}, and {APPLICABLE_SECTION_AND_REVISION_GUIDES}. Review all claims, numbers, citations, explanations and consequential omissions, including contrary evidence. Preserve the author's approved direction and edit scope.

Return {CORRECTIONS_FILE}. For each factual problem, identify the manuscript location, exact affected text, supporting or conflicting source, scientific consequence, and smallest sufficient correction. Check meaning in the surrounding argument; a word replacement is insufficient if the claim's premise is wrong. Distinguish mandatory factual repairs from optional editorial preferences. Give any necessary report-register or clarity repair separately, preserving the existing scientific strength and argument. Do not rewrite sound prose to display the review criteria.

If the evidence requires reconstructing the argument, explain exactly which premise fails and what the record supports instead. Do not silently substitute another scientific purpose or expand the authorized revision. If no issue is found, say so for the scope actually read. Do not claim full reference clearance; the coordinator invokes the separate reference-verification skill on the final deliverable.
```

When a shell is available, the corrector or coordinator runs `python3 -I {SKILL}/scripts/check_prose.py {DRAFT} --notes {NOTES} --section {SECTION}`, with `SECTION` set to `intro`, `methods`, `results` or `other`. Preserve source notes; put labeled computations with operands, units and basis in a separate working-notes copy when needed. Review flags in context. The checker neither establishes provenance nor judges the scientific argument, and its matches are not automatic edits.

## Resolve and deliver

Apply necessary corrections within the original authorization. Preserve paragraph roles, explanatory relationships and the supported message unless evidence changes them. If a correction affects the argument, send the composer the corrected scientific premise and relevant facts, not the audit transcript, and recheck the revised passage. For a numbers-only update or other scoped revision, follow `revision.md`: propose changes to approved framing separately instead of silently applying them. Mark proposed copy edits inline.

Read corrected statements with their surrounding prose and verify that every material issue is resolved or specifically reported. Repeat affected factual checks after substantive changes; do not add review rounds without a remaining issue. After the last substantive edit, the coordinator invokes the separate `reference-verification` skill in full mode on the actual deliverable and supplied SI. Resolve or report its findings and accurately identify the checked artifact and scope. Reference checking grants no extra editing permission.

Deliver the requested manuscript format, with `Notes to author` only as specified in `SKILL.md`. Keep role prompts, reverse outlines, routine checks and the complete audit in working files. For a writer-package request, deliver the self-contained inputs and filled prompts, and state which roles remain for the receiving coordinator to run; packaging alone is not manuscript clearance.

## When comparing workflows

Freeze the skill version, workflow and input package before generation. Give compared generated conditions the same underlying research and source inputs and use the same model and reasoning effort; retain every attempt separately. Keep generation isolated from baselines, other conditions' drafts, reviews and evaluation outcomes. A no-skill condition must not inherit a skill-derived editorial brief or composition card. Comparing this multi-role workflow with a single-pass baseline evaluates the complete workflows; it is not a compute-matched causal test of the skill instructions. Record role count, revision rounds and available usage or runtime information so the comparison's limits remain visible.

## If separate contexts are unavailable

Use a fresh model session through another available harness only when it is already authorized and can access the same complete inputs. Otherwise complete the task in the current context: save the brief and complete facts, compose using the short composition card, integrate the argument, then run the full factual, prose and final reference checks. Keep detailed audit output outside the prose. Record that composition and correction were not context-isolated; do not claim that a new section heading, rereading or a request to forget created independence. Do not stop an otherwise authorized writing request merely because agents are unavailable.

For a chat interface without file access, supply the same role-specific inputs inline or as readable attachments in separate conversations when possible. Preserve complete facts and usable source openings. If only one conversation is available, use the stated fallback and keep all author approval and revision boundaries unchanged.

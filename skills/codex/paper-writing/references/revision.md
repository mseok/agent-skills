# Revising an existing manuscript

Most revision requests arrive as "고쳐줘", "업데이트해줘" or a co-author checklist against a live document. Treat them as draft requests until the user names the file to change. The writing rules of this skill still apply to every sentence you write; this guide adds how to change a manuscript without losing what the authors already decided.

## Before drafting

- Load the agreed framing from the task state or the project facts file, and from an accepted `plan.md` when there is one (the adopted key message, each figure's role, the reason for each analysis), and the manuscript's own aliases; where plan.md differs from a later decision in the task state or facts file, the later decision wins. Never draft from memory of an earlier thread.
- Read the live manuscript from the project's download or export (or the git-bridge checkout), never from the editor's selection.
- When the user fixes how a method, dataset or result must be described, add the wording to the project facts file in the same turn and grep the live source for conflicting phrases before drafting.

## Drafting the change

1. Draft first, in the working folder, never in the live source: for each requested change show the original paragraph and the revised paragraph side by side (paragraph-aligned before/after, inline in the reply when the user asks to see it here), with one line on why. Change only the paragraphs the request covers; a whole-section rewrite needs an explicit request. A class the user asked you to fix (item 4) covers every paragraph with an instance of it. Inside the covered paragraphs, also fix what violates this skill; list violations you notice elsewhere in the report without changing them.
2. Keep the user's claims, emphasis, order, structure, terminology and citations, and state supported results as direct claims scoped to their benchmark and metric. Internal run names, checkpoint tiers, job IDs, file names and work-log wording never enter the prose; define a term on first use or use the field's term; move procedure to Methods or the Supplementary (the appendix in an ml-conference paper) with one pointer sentence.
3. When only a result changes ("numbers updated"), edit only the sentences that state the changed quantity; the heading, framing, paragraph order and the strength of the conclusion stay as the user last approved, and any wording improvement goes in a separate proposal file. If a new number no longer supports a claim as approved, do not change the claim unasked: give each sentence that would need narrowing, wherever the claim appears (heading, abstract, Introduction and Discussion included), as its own before/after pair apart from the number edits, list it first in the report with the old and new value, and apply it only when the user approves.
4. Treat a user's example of a writing problem as one instance of a class: search the whole document for the class, fix every instance and report the count. Run a fresh-context reader pass that lists every term used before it is explained; compile and layout success never prove the quality goal.
5. Do not delete, hide or renumber sections, tables, figures or equations unless asked; before such a change, search the other manuscript files for references and ask if any would break. In a run where no one can answer, make no such change and list it in the report.
6. Describe a method's settings (ranges, stages, schedules) only from the retained config of the reported run; an analysis's aggregation window is not the method's scope.
7. Citations: never invent one; use `[CITE: what is needed]` for anything unverified, and run a citation check when asked ("hallucination 확인").
8. When only LaTeX is requested, return the LaTeX with no code fence, no notes and no commentary; put the before/after pairs, the report, questions for the authors and the Notes to author content in one separate file.
9. For insertions into a compiled document, live or local, also deliver a preview PDF with the added text in color.

## Live shared manuscripts

Live shared manuscripts (Overleaf, shared drives) are read-only by default.

- Apply there only when the user approves the exact change set in the current turn. Then, immediately before applying, re-download or re-export the live files; if they changed since the draft was made, stop and rebase the change on the new text. Otherwise edit the local copy, produce the diff, compile, check the PDF page, and upload or paste the verified text; never select-all, retype or reformat inside the live editor, and never while another session is editing. If the browser or upload tool fails, hand over the diff and the compiled PDF for the user to apply.
- Apply only the files the request names and only the target region; never replace other source files alongside, and show the diff of every file you upload.

## Report

Give the report in the reply after the before/after pairs (in the separate file of item 8 when only LaTeX is requested). It is not manuscript text and not part of the Notes to author block, which keeps the categories listed in SKILL.md.

- What changed (paragraphs, files, compile result, PDF page checked) and what was not applied.
- The structural changes you introduced, apart from pre-existing problems.
- Every claim, limitation, framing or motivation you removed, weakened or strengthened, with a one-line reason.
- When a revision replaces a pre-specified endpoint with one chosen after an exploratory search, or removes exclusion or missingness statements, say so once in the report and in the cover note to co-authors.
- Before delivery, grep the draft for the project's internal identifier patterns (run names, checkpoint tiers, job IDs, file names) and report the check.

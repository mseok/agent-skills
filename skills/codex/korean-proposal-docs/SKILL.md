---
name: korean-proposal-docs
description: Co-write Korean government or institutional proposals, progress reports, R&D admin forms and budget sheets in HWP, HWPX, DOCX or Google Docs, including multi-institution templates with assigned sections. Use when the user mentions 제안서, 과제, 사업계획서, 보고서, 양식, 연차, 예산, 한글 문서, or asks to fill, revise or check such a document. Not for journal manuscripts (paper-writing) or slide decks (research-talk).
---

# Korean proposals, reports and forms

These documents are shared with institutions and co-authors, follow fixed templates, and are judged by non-expert reviewers. The recurring failures were unrequested edits, template drift, wrong budget arithmetic and false "done" claims on rendering.

## Scope ledger first

Before editing, write a scope ledger in the task state and show it: the file and version that is the governing source, the sections or fields assigned to the user (others are read-only), forbidden changes (template layout, fonts, numbering, other institutions' text, official tables), format rules from the call (page budget, font, spacing), recipients and the deadline, and owner decisions still open (title, personnel, budget lines, KPIs, schedule). Keep review markers for open decisions; never fill them from memory.

## Edit on a copy

- Work on a distinctly named copy; the user's original and any `작성중` file stay untouched. Keep `source/`, `draft/` and `qa/` folders with a source index (file, status, SHA-256).
- Change only the assigned sections. Keep existing nonempty text, comments and memos; put variants or alternatives in a separate file or a colour-marked review copy, never in the main draft.
- Structure follows the prior phase or the template's numbering; a new section is proposed, not inserted.
- Fill or flag every table: no blank cells left silently; a cell without a source gets a visible marker and a line in the open-decision list.
- Write for a non-expert reviewer: define terms on first use, one claim per sentence, no internal project jargon, no English where the template uses Korean. Respect the page budget before polishing.
- Budget sheets: use the calculator's own formulas and the call's rules (indirect cost base, allowance caps, unpaid-labour fields); show the arithmetic in the reply and mark any rule you could not confirm as unconfirmed. Never state a portal procedure as fact without the FAQ or screen that says so.
- References go under the subsection that uses them, in the template's style.

## Mechanics and QA

- HWP/HWPX: use `hwp-agent-edit` for file mechanics and the native Hancom render rule (never automate Hancom while the user's documents are open; PDF export from a copy; structural ZIP/XML checks are not layout checks). DOCX and Google Docs: edit on a copy with tracked changes or a colour-marked diff.
- Before delivery, render every page (native PDF) and inspect it; if native rendering is unavailable, say "not visually verified" in the first line and name the layer that was checked.
- Report: output path, what was filled, what is still open, what was not verified. Name the file 작업본 (draft) until the user approves it; never 제출본 or 최종본. Never call a review copy submission-ready while any marker remains.
- Compile from sources: copy source tables, pictures and heading paragraphs as native objects with their styles, never re-typed as pipe text; keep untouched package members byte-identical; render every page in HWP Local Editor or native Hancom before reporting; every filled cell or sentence has a source entry (file and page or cell) in the ledger, and a cell without a source stays blank and is listed by section. Fetch the exact document the user names (the attachment, not the email body) and record which file each value came from; document scripts run with the interpreter named in host-context (system python3 lacks openpyxl).

## Messages around the document

Notes to co-institutions, administrators or professors go through `message-as-user`: plain text, in the user's register, sent only with per-message approval. Attach the exact file version you checked.

## Verified additions (2026-10-17 audit)

- Scope check: classify every changed region by the source request that assigns it (memo, role table, call field); a user request to polish text you added in a read-only section does not make that section assigned, so list such regions separately and ask once whether to keep them. Connective, background or bridging sentences inside an assigned field also need an assigning source; without one, leave them out and offer them in the reply. Reviewer panels check every changed region against this ledger and the template before judging quality.
- Filled text uses the form's body style (black, upright), never the guide or example style; a repair or conversion that changes any layout property (font, row height, columns, page break, orientation) is reverted, or reported with before and after and kept only on approval. Keep each sentence's modality from its source: planned work stays in plan form (추진/예정) and only evidenced results take completed form.
- Read every changed paragraph back in full from the rendered output, not thumbnails; a sentence split across bullets, a clipped table edge or overlapping glyphs is a defect. When native export is blocked (Hancom busy with the user's documents, a missing Accessibility grant), deliver a viewable render now (HWP Local Editor pages in a visible tab, or the Quick Look first page plus the text extract) and ask once whether they will close Hancom or export it themselves; never launch a helper that raises a permission prompt.
- Use verbs, not noun stacks: at most one middle-dot list per sentence; change-request memos follow the recipient's format (page / figure / current text → new text) in full sentences. A performance-indicator row states one plain metric, its target and a one-line rationale; pass criteria and measurement details go in the measurement-method cell.
- Budget sheets: never replace a value someone entered with a formula without listing it; after any budget change, update or flag every surface that carries the number (sheet, exported workbook, portal values, draft emails) in the same turn. Submission packages and cover emails contain only items on the recipient's checklist, each named with the call page, FAQ or message that requires it; explanations stay in the chat reply.

## Applicant voice and estimates (2026-10-17 audit)

- The proposal speaks as the applicant institution: planned work is never described as already verified by a tool or as done ("WandB로 확인하였다" belongs in a lab note, never in a proposal), and the lab's own planned work is written in the applicant's voice, not an agent's report voice.
- Request and plan cells (budget requests, personnel months, targets) take labelled estimates capped by the call's limits rather than staying blank; the label and the cap source go in the ledger and the reply.
- Portal submission: enter values from the final sheet only, read back every field before submit, and never zero a field by guess.
- Reviewer panels receive the user's recorded corrections and the scope ledger and return findings only; "all passed" without a findings list is not a review.

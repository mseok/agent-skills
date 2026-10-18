---
name: zotero-annotation-research
description: Use a local Zotero 10 library to build self-contained paper summaries, inspect and critique PDF annotations, and safely write reviewed results back to Zotero. Applies to explicit item, attachment, annotation, page, text, rectangle, tag, or color inputs; not to remote or group-library administration.
---

# Zotero Annotation Research

Use this skill when the user wants to reason from annotations they made in a
local Zotero 10 library. The goal is to keep paper evidence, the user's own
comment, and the model's interpretation visibly distinct and traceable.

## Scope and preconditions

- v1 targets one personal local Zotero library while Zotero is running.
- Use the configured `zotero` MCP server and its actual tool schemas. The
  expected server is `zotero-mcp serve` with `ZOTERO_LOCAL=true`.
- Do not use Zotero Web API credentials, group libraries, direct
  `zotero.sqlite` access, or arbitrary JavaScript for this workflow.
- Do not expose or ask the user to paste the local write key. If the server
  reports that local write access is unavailable, stop at preview and explain
  that `zotero-mcp authorize-local` or the Zotero setting must be completed.
- The current Reader mouse selection is deliberately out of scope. Require
  explicit `item_key` or `attachment_key`, and for location-specific work
  require `page` plus exact `text` or a normalized `rect`.
- If a tool name or argument differs from the list below, inspect the live MCP
  tool schema and adapt. Never guess a write call from a similar-looking tool.

## Source acquisition and Zotero placement

- When a requested paper is not already in the local library, acquire the
  authoritative full-text PDF before doing paper-level analysis or creating
  anchored annotations. Prefer an arXiv or publisher PDF URL; use
  `zotero_add_item` with `attach_mode="required"` (or a verified local PDF
  with `source_type="file"`) and then re-read the resulting Zotero
  attachment. Do not treat an abstract, search result, or repository README as
  a substitute for the paper PDF.
- If the user specifies a Zotero collection path, resolve or validate that
  collection before the add, pass the exact path/key to the add operation,
  and verify the parent item's collection membership after the write. Do not
  invent a collection or silently file the paper elsewhere.
- The normal sequence for a saved paper review is: resolve the source, secure
  the PDF in Zotero, verify the parent and attachment keys, read the actual
  PDF, then create the independent summary note and PDF-position annotations.
  A direct user request to save/add the review is write approval for this
  scoped sequence; a preview-only or analysis-only request remains read-only.
- A GitHub repository, webpage, or other non-PDF artifact is not eligible for
  a PDF-position annotation. If it is explicitly in scope, store it as a
  webpage/source item and create a source note with URL/section anchors, while
  labeling it as an implementation artifact rather than a paper result. Use
  the stable marker
  `<!-- zotero-annotation-research:source-summary:v1;item={item_key} -->`
  and skip a duplicate source note when that marker already exists.

## Modes

Route the request to exactly one primary mode unless the user asks for a
combined review.

- `explain`: state what the annotation says, what it means in context, why it
  matters, and which assumptions are carrying the claim.
- `critique`: give the strongest fair counterargument, distinguish evidence
  from interpretation, and identify what the cited result does not establish.
- `follow-up`: propose the smallest discriminating experiment, analysis, or
  verification, including a measurable outcome and the competing hypotheses it
  separates.
- `figure`: inspect the requested page and rectangle as a figure, table, or
  equation. Describe only visible or extractable evidence and report when the
  image or OCR is inadequate.
- `paper-summary`: create an independent paper note that is self-contained
  enough to reconstruct the paper's Introduction, Method, Results,
  interpretation, and limitations without opening the annotation list. This
  is a paper-level artifact, not an annotation comment and not an annotation
  synthesis.
- `synthesize`: group selected annotations by claim, method, evidence,
  contradiction, and open question. Preserve source item keys and page labels
  for every non-obvious conclusion.

## Retrieval workflow

1. Parse the explicit scope. Accept item keys, attachment keys, annotation
   keys, page numbers, exact highlighted text, normalized rectangles, tags,
   colors, collection keys, or an explicit list of item keys. Do not infer a
   location from the current Reader cursor.
2. Confirm that the target resolves to the personal local library. Resolve a
   top-level item to its child PDF attachment with
   `zotero_get_item_children` when necessary.
3. Read only the context needed for the request. Typical calls are:
   `zotero_get_item_metadata`, `zotero_get_item_children`,
   `zotero_get_annotations(format="json")`, `zotero_read_pdf_pages`,
   `zotero_get_page_layout`, and `zotero_get_pdf_outline`.
   For `paper-summary`, read the paper itself: metadata/abstract, outline,
   Introduction, Method, Results, and the discussion/conclusion pages needed
   to separate observed results from author interpretation. Do not require or
   silently substitute annotations for this evidence. Use page images when
   figures, tables, equations, or garbled extraction carry essential results.
4. Keep four layers separate in the response: exact paper text or image
   evidence; the paper's claim; the user's existing comment; and the new
   model interpretation. Never silently rewrite the quoted annotation.
5. Produce a preview before any Zotero write. A preview must show the target
   key, the proposed mode, the proposed appended block or note body, and what
   will remain unchanged.
6. Wait for explicit approval such as “승인”, “저장해”, “apply”, or “write
   it”. A request to explain or preview is not write approval.
7. After approval, re-read the current item/annotation or note, check the
   marker, perform one narrowly scoped write, then re-read and verify the
   exact result. If the target changed between preview and approval, show a
   fresh preview instead of overwriting it.

For `paper-summary`, the preview must show:

```text
Target: parent item {item_key}; PDF {attachment_key}
Mode: paper-summary
Existing summary marker: {yes/no}
Proposed destination: one child note under the parent paper
Proposed body: complete Introduction/Method/Results summary with evidence map
Annotations: not read or changed unless separately requested
Write: one note only
Marker: <!-- zotero-annotation-research:paper-summary:v1;item={item_key};attachment={attachment_key} -->
```

After approval, re-read the current child notes, skip an existing matching
marker, create or update only that summary note, and re-read it to verify the
marker and body. A paper-summary write never changes PDF annotations,
annotation comments, colors, tags, or positions.

The principal MCP tools are:

- discovery and metadata: `zotero_search_items`,
  `zotero_get_item_metadata`, `zotero_get_item_children`,
  `zotero_get_annotations`, `zotero_get_notes`;
- PDF context: `zotero_read_pdf_pages`, `zotero_get_page_layout`,
  `zotero_get_pdf_outline`;
- synthesis: `zotero_synthesize_annotations`;
- writes, only after approval: `zotero_update_annotation` and
  `zotero_manage_note`.

For library-wide tag synthesis, prefer `zotero_synthesize_annotations` with
`tag`, `collection_key`, and `format="json"`. For an explicit item list or
color filter, fetch each item's annotations and filter the returned structured
records locally. Keep the selection rule in the preview.

For `paper-summary`, use one independent child note per parent paper. If the
live schema exposes a standalone-note destination and the user explicitly
requests a cross-paper hub, it may be used; otherwise do not attach multiple
paper summaries to the first paper. Read existing child notes before writing
and use the stable paper-summary marker described in
`references/note-format.md` to avoid duplicate summaries.

## Analysis rules

For `explain`, answer in this order: interpretation, why it matters, hidden
assumption, and relation to the user's stated hypothesis. Use surrounding PDF
context when the highlight is fragmentary.

For `critique`, lead with the strongest version of the paper's claim. Then
separate (a) what the annotation directly supports, (b) the alternative
explanation, (c) the missing control or evidence, and (d) the boundary of the
conclusion. Do not call a result false merely because it is incomplete.

For `follow-up`, propose a test that could change the conclusion. Include the
perturbation or comparison, the expected pattern under each hypothesis, and a
clear readout. Prefer the smallest useful test over a long generic list.

For `figure`, call `zotero_read_pdf_pages(format="image")` for the requested
page and use `rect` only when the user supplied it or
`zotero_get_page_layout` returned a detected region. Use text extraction and
the caption as supporting context, not as a substitute for an unavailable
image. If a scanned page, equation, table, or low-quality OCR prevents a
reliable reading, say exactly what is unavailable and stop the interpretation
at that boundary.

For `synthesize`, report:

1. the selected scope and counts;
2. claims and supporting evidence grouped by source;
3. agreements and contradictions, with the exact source keys/pages;
4. recurring methodological limitations;
5. open questions and proposed discriminating follow-ups.

Do not turn a cluster of annotations into a universal, causal, or completion
claim unless the selected evidence actually supports it.

## Independent paper summaries

`paper-summary` is deliberately separate from all annotation modes. A paper
may have zero annotations and still receive a summary. Do not write the
summary into an annotation comment, and do not treat an annotation synthesis
as a substitute for a paper summary.

The summary must be readable on its own and normally contain:

1. bibliographic identity, research question, motivation, and the paper's
   strongest bounded claim;
2. `Introduction`: the problem, why existing approaches are insufficient,
   target/estimand, and the hypotheses or design objective;
3. `Method`: system/model definitions, data or benchmark construction,
   experimental protocol, baselines/comparators, metrics, train/calibration/
   test separation, and the decision rule or algorithm in plain language;
4. `Results`: each main experiment's setup, comparison, quantitative outcome,
   and what was actually measured, with page anchors and denominators when
   available;
5. interpretation: what the results support and what they do not establish;
6. limitations, assumptions, unresolved questions, and the smallest useful
   follow-up experiments;
7. a short evidence map listing the pages used for Introduction, Method,
   Results, and Discussion/Conclusion.

Use the user's Obsidian-like order—current judgment first, then motivation,
method, results, interpretation, limits, and follow-ups—but keep claims,
observations, working assumptions, and proposals explicitly distinguishable.
Preserve equations or definitions only when they are necessary to understand
the method or result. Include enough explanation that a reader does not need
to reopen the PDF to understand what was done and what was found; this does
not mean inventing missing details or reproducing every appendix.

## Safe write-back policy

The default mode is `preview`. Never switch to automatic saving because the
user has used the skill several times. Count a supervised success only after
the post-write re-read confirms the intended marker and content. After three
verified supervised successes, offer automatic mode as an option; switch only
when the user explicitly requests it. Automatic mode still re-reads before
each write and keeps the same scope and idempotency rules.

### Per-annotation analysis

When the user approves an individual analysis:

- fetch the latest `annotationComment` and preserve it byte-for-byte;
- append one clearly separated analysis block, changing only the comment;
- use a stable marker at the end of the block:
  `<!-- zotero-annotation-research:v1;annotation={annotation_key};mode={mode} -->`;
- if that marker is already present, do not append another block;
- call `zotero_update_annotation` with `annotation_key` and the complete new
  `comment`; never send `text`, `color`, `tags`, or position changes unless the
  user separately asks for that different operation;
- a different mode has a different marker and may be appended as a separate
  explicitly requested review; rerunning the same mode is a no-op.

The original user comment must remain above the new block. Do not hide an
existing comment inside a replacement note or summarize it away.

### Creating new PDF annotations

When the user asks to annotate parts that do not already have annotations:

- Re-read the attachment's current annotations first and resolve each target
  with an exact text span and 1-indexed PDF page, or with a user-supplied or
  detected normalized rectangle for a figure/table/region.
- Before creating a highlight, skip it if the same deterministic creation
  marker or the same page/text target already exists. Do not create a second
  highlight merely because the wording of the comment changed.
- New annotation comments should contain the user's concise Korean/technical
  style plus a stable marker of the form
  `<!-- zotero-annotation-research:created:v1;item={item_key};page={page};slot={slot} -->`.
  The slot is a short, stable label chosen from the paper section or claim.
- Create with `zotero_create_annotation` using only attachment key, page,
  exact text or rect, comment, and an interpretation color. Then re-read the
  annotation list and verify the created key, page, source text, comment, and
  color. Do not alter an existing annotation's text, position, or color unless
  the user separately asks for that operation.

### Synthesis notes

Create at most one synthesis note for one approved scope. Before creating it,
search the relevant child notes with `zotero_get_notes(raw_html=true)` and
look for the stable scope marker:

`<!-- zotero-annotation-research:synthesis:v1;scope={scope_digest} -->`

If the marker exists, do not create a second note. A synthesis for one parent
item can be a child note created with `zotero_manage_note(action="create")`.
For multiple parent items, use a standalone-note capability only if the live
MCP schema exposes one. The installed v1 server exposes child-note creation;
when no standalone or user-supplied hub parent is available, keep the result
at preview and ask for a hub `item_key` rather than silently attaching the
note to the first paper. Never use a fabricated parent key.

The synthesis note must preserve source item keys, attachment keys when
relevant, page labels, annotation keys, and the selection rule. Do not mix an
individual annotation block into the synthesis note unless the user asks for
that; individual review and cross-paper synthesis are separate artifacts.

### Paper summary notes

For an approved `paper-summary` request, create at most one paper-summary
note per parent item. Before creating or updating it, read the parent's child
notes with `zotero_get_notes(raw_html=true)` and look for:

`<!-- zotero-annotation-research:paper-summary:v1;item={item_key};attachment={attachment_key} -->`

If that marker exists, do not create a duplicate. A paper-summary note may be
updated only after fetching its current HTML; preserve unrelated child-note
content and do not modify annotations. The note body and evidence map should
follow `references/note-format.md`.

## Color convention

Use these colors as interpretation hints only: yellow = important claim, red =
concern or possible rebuttal, blue = method, green = transferable idea, and
purple = open question. Do not recolor existing annotations automatically.
If the stored color is unknown, report it as unknown rather than assigning a
meaning.

## Failure boundaries

Stop without a write and give the smallest corrective action when:

- Zotero is closed, the local API is disabled, or the MCP server is not
  discoverable;
- local write authorization is missing or the library is not the personal
  local library;
- the annotation, attachment, page, text, or rectangle cannot be resolved;
- the requested figure/equation/table has no reliable image or text layer;
- the current content no longer matches the approved preview; or
- a marker collision or ambiguous existing note makes idempotency uncertain.

Do not retry by opening SQLite, deleting an annotation, replacing a whole
note without fetching its current HTML, or falling back to a Web API key.

See `references/annotation-workflow.md` for the tool-by-tool procedure and
`references/note-format.md` for the stable output templates.

## Example requests

- `explain: item_key=..., annotation_key=...` — preview an explanation and
  wait before appending it to the annotation comment.
- `critique this highlight; use page 4 around the selected sentence` — read
  the annotation and nearby page context, then show a preview only.
- `figure: attachment_key=..., page=7, rect=[0.15,0.22,0.60,0.35]` — inspect
  the image region and report OCR/image limitations.
- `paper-summary: item_key=...` — build a self-contained paper note from the
  PDF, independent of annotations, then preview the one-note write.
- `synthesize annotations tagged MSA and red across these item keys` — filter
  only the named scope, preserve provenance, and preview one synthesis note.

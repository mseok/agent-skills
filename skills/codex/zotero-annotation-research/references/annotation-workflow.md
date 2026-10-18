# Annotation workflow reference

This reference records the concrete v1 sequence for the `zotero-mcp-server`
tool surface. The live MCP schema remains authoritative if a future package
version changes an argument or exposes a new tool.

## Read path

1. Use `zotero_search_items` only to resolve a human description to a stable
   top-level item key. If the user already supplied a key, do not search again.
2. Call `zotero_get_item_metadata` and verify the item belongs to the personal
   local library. Call `zotero_get_item_children` to identify the PDF
   attachment. An annotation is a child of the attachment, not usually a
   direct child of the paper.
3. Call `zotero_get_annotations(item_key=..., format="json")`. The normalized
   records should be treated as structured evidence and may include
   `annotationText`, `annotationComment`, `annotationType`, `annotationColor`,
   `annotationPageLabel`, `annotationPosition`, `annotation_key`,
   `attachment_key`, and parent metadata. Confirm exact field names from the
   returned schema/output instead of inventing missing values.
4. For nearby context, call `zotero_read_pdf_pages` with 1-indexed
   `start_page`/`end_page` and `format="text"`. For a figure, table, or
   equation call it with `format="image"`; pass a normalized `rect` only when
   supplied or detected.
5. Use `zotero_get_page_layout` before an area interpretation when a region
   must be located, and `zotero_get_pdf_outline` when the page is not known.

## Mode-specific retrieval

- `explain`, `critique`, and `follow-up`: annotation JSON plus the annotation
  page and at most the necessary neighboring pages.
- `figure`: page image first, caption/page text second. If image output is
  absent or OCR is unreliable, return a limitation report instead of a visual
  conclusion.
- `synthesize`: `zotero_synthesize_annotations(format="json", tag=...)` for a
  tag or collection scope; otherwise fetch the explicitly named items and
  filter by item key, annotation key, color, and tags. Do not scan the whole
  library unless the user explicitly asks.

## Preview and approval

The preview contains:

```text
Target: annotation {annotation_key}
Mode: {mode}
Evidence: {item title, attachment key, page label, exact annotation text}
Existing comment: preserved verbatim
Proposed append: {new block}
Write: annotation comment only
Marker: {stable marker}
```

For synthesis:

```text
Scope: {explicit item/tag/color/collection rule}
Sources: {item keys and counts}
Existing matching marker: {yes/no}
Proposed destination: {child note key or requested hub parent}
Write: one note only
```

Proceed only after an explicit approval. Then fetch the current object again,
check the marker, write once, and re-read for verification.

## Idempotency

The marker is deliberately derived from the stable source key, skill version,
and mode—not from the model's prose. This makes a same-mode retry a no-op even
if the wording would otherwise change. A different mode has its own marker.

For annotation comments, preserve the full current comment and append the
block. For notes, retrieve raw HTML and either skip an existing marker or
create one complete note. Do not use a blind append for a synthesis note.

---
name: nature-figure
description: Turn scientific data and retained image assets into Nature-style publication figures, selecting plots, composing panels, writing evidence-grounded English labels and captions, and checking final physical size, typography and editable exports. Use for new scientific figures or finalizing existing figures; not ordinary slides, dashboards or manuscript-wide rewriting.
---

# Nature-style scientific figures

Produce a scientifically faithful figure that is readable at its intended publication size, plus the editable source needed to revise it. Treat visual polish and scientific support as separate completion criteria.

## Establish scope without making the user design every detail

Read supplied data, nearby provenance and any explicitly referenced recent figure work before asking questions. Recover prior accepted color mappings, panel roles and user corrections; do not assume a prior draft was accepted. Preserve existing originals and make alternate layouts in separate files.

Resolve the reader question, target journal and submission stage, available data, and any fixed scientific message or panel arrangement. When not specified, state provisional defaults: Nature main-journal final-artwork style; a compact single column or double column as content requires; English figure text; Figma-oriented editable SVG as the primary artifact plus reproducible local source and a 600 dpi PNG proof; PDF only when requested. These are defaults, not user-adopted decisions or universal journal requirements. Read [journal-profiles.md](references/journal-profiles.md) before choosing numeric specifications.

Autonomously choose chart types, arrangement, concise wording and ordinary design details. Ask only about ambiguity that materially changes scientific meaning, such as what rows represent, paired versus independent samples, metric direction, units, uncertain sample counts or incompatible evaluation populations. Do not manufacture error bars, observations or statistical tests to complete a design. Missing optional statistics need not block an otherwise honest descriptive figure.

For broad exploratory inputs, briefly state each proposed panel's question, evidence and visual encoding, then proceed unless the user requested a design-selection checkpoint. Honor formatting-only scope: do not redesign the message, omit panels or rewrite scientific content without authorization.

## Select evidence and visual form

Use [data-and-writing.md](references/data-and-writing.md) when making plots or composing scientific text. Keep data transformations and source-to-panel mapping recoverable. Choose panels to answer a scientific question rather than to fill a preset grid. Use consistent visual encodings across related figures.

For schematic/model diagrams, inspect supplied method evidence before drawing dependencies. For molecular images, render actual provided or retrieved coordinates with scientific software; preserve camera, selections, alignment and structure identifiers. Label illustrative states as such; an interpolation is not an observed prediction or physical trajectory. Do not use generated bitmap artwork as experimental data or as a replacement for a quantitative chart.

Use standard plotting tools for scientific charts and vector composition for layout. Use the available visualize skill only when an interactive exploration would help choose variables, subsets or layout; it is optional and does not replace the standalone publication artifact. If Figma or PowerPoint is requested, load its relevant skill and maintain native editable objects where feasible. A local export does not establish that a Figma upload succeeded.

## Compose at physical size

Maintain one figure specification containing journal/stage, source URL and access date, width/height in mm, font family, point sizes by role, line widths, palette and export formats. Distinguish official requirements from local design choices. Use final-size points for font decisions, not arbitrary canvas pixels.

For canvas width U units mapped to W mm, physical width is W*72/25.4 points. Convert target point size p to canvas units as p*U/(W*72/25.4). Apply the same conversion to strokes. Set exported page dimensions explicitly; an SVG viewBox or Figma frame alone does not establish physical size. Avoid tight-crop export settings that silently change the intended page size.

Default to white backgrounds, restrained axes, black text, consistent accessible color meanings, aligned panel letters, and enough space for units and keys. Avoid decorative cards, shadows and redundant legends. Arrange or split dense content before shrinking text below the profile. Preserve aligned comparisons and common scales where scientifically appropriate. Keep labels close to their objects and panel letters in a consistent reading order.

Prefer a compact, figure-only canvas: enlarge the data panels, reduce outer margins and inter-panel/title gaps, and keep text close to the relevant mark without collisions. Do not reserve empty strips for subtitles, status notes or production commentary. Put sample-count explanations, summary/error-bar definitions and synthetic/demo provenance in the separate caption and metadata by default; retain essential axis labels, units, method keys and panel identifiers. Do not stamp "synthetic data", "layout evaluation only", or similar workflow text on the canvas unless requested or needed to disambiguate a particular panel. Preserve these facts in the delivered caption and provenance rather than deleting them.

Use comfortably readable text: prefer 7 pt ordinary lettering under the strict Nature profile instead of defaulting ticks/keys to 5–6 pt. If the user explicitly prioritizes larger lettering, apply a documented style override (for example 8 pt titles/axis labels and 7 pt ticks); do not claim strict 5–7 pt compliance for that variant. Keep the output physical size explicit. Reducing whitespace alone does not count as increasing actual point size.

Preserve live text and editable lines, arrows and keys. For Matplotlib use pdf.fonttype=42, ps.fonttype=42 and svg.fonttype='none'; explicitly resolve the requested font rather than accepting silent fallback. SVG live text alone does not embed the font. Preserve a source with live text even when a specific downstream tool needs a separate compatibility variant.

On Linux or when Arial is unavailable, read [linux-fonts.md](references/linux-fonts.md) and use [ensure_arial.py](scripts/ensure_arial.py) for persistent per-user discovery/installation from a licensed local source.

Before rendering, check that Arial is installed and that the actual rendering or editing tool can resolve it, including needed bold/italic faces. If Arial is absent, or installed but unavailable in that tool, explicitly tell the user as soon as discovered and repeat the unresolved limitation in the final delivery. Distinguish missing installation from application access or font-helper failure. Never silently substitute another font or claim Arial compliance from the requested font name alone. Continue independent layout/data work; any fallback preview must identify the actual substitute and remain provisional until the font choice is resolved. Verify the font used in the exported artifact.

## Finalize and deliver

Read [finalization.md](references/finalization.md) and inspect the exported artifact, not only the source canvas. Fix issues revealed by the checks and rerender affected outputs. A figure is finalized only for the chosen profile and checks actually performed; journal acceptance is outside this claim.

Default delivery: figure.svg (primary, Figma-oriented editable vector with live text and named panel/object groups), figure.png (600 dpi proof; always strictly above 300 dpi at final size), generation code or native source, caption.md, and a concise figure-spec.json/figure-spec.md with source locators, transforms, specifications and QA outcome. Reuse existing project conventions instead of duplicating records. PDF is an optional export, generated only when requested; an internal PDF used for QA need not be delivered. Preserve real SVG text rather than outlining it. Figma SVG import can convert or alter text: do not equate SVG text nodes with verified native Text nodes. When native editability is requested, verify import in the destination; if its importer outlines text, use a native-text import route or companion importer and disclose the limitation. The caption stays separate unless the user requests it inside the figure. Mark unresolved scientific facts or unavailable QA precisely. Link the finished preview and editable artifacts and state the final physical dimensions.

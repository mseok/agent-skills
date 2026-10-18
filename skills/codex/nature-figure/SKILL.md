---
name: nature-figure
description: Produce or revise any scientific plot, panel, schematic or publication figure (matplotlib, PyMOL, SVG, Figma), from a quick comparison bar chart to Nature-style final artwork. Use for 그림, 플롯, 패널, figure, chart, rebuild, redraw, Figma handoff requests, and whenever numbers from a benchmark are plotted; not ordinary slides (research-talk) or manuscript prose (paper-writing).
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

## House defaults for this user

Apply unless the user says otherwise; record any override in the project's `STYLE.md` and read that file first in later threads.

- Chart type: bar plots by default for method comparisons; scatter only when a relationship is the message. Percentages rather than fractions; metric direction stated in the axis label.
- Nothing decorative inside the figure: no in-figure titles, notes, explanations or status text; captions carry explanations. Little whitespace; data panels enlarged to the canvas.
- Arrows and connectors: single native editable objects, straight or one bend, consistent heads; no diagonal or multi-bend arrows. Text sits inside its box, optically centred; one legend style and position across the figure.
- Model naming follows the manuscript's aliases (for example the agreed short name for the comparison method); abbreviations defined in the caption.
- Versioned folders (`v01`, `v02`, …) with one inline preview image per version in the reply so the user can judge without opening files; the latest user-edited version is the source for the next edit.
- Final-size typography check whenever panels are combined (text found at 3–5 pt in past combos); report the measured point sizes.

## Figma handoff

Pre-flight before editing in Figma: login state in the automation browser, required fonts available in that browser, write access to the file, frame policy (edit in place; no hidden version frames; one live text object per box; native arrows). If a font cannot load, say so in the same turn with the unblock options (desktop app, user applies the exported SVG, font helper) and never change the figure's required font to suit the tool. Do not convert text to outlines. After editing, verify the Figma source itself changed, not only a local export.

## Provenance, rebuilds and redraws

- Every number in a figure is recomputed from raw outputs listed in a per-panel source manifest, following the benchmark's own evaluation docs or scripts; numbers copied from chat, Slack, slides or older figures appear only in panels labelled provisional, and no off-range point is hidden.
- Rebuild with new data: keep the established panels, comparisons and overlays; put any new comparison in a separate candidate file and ask before swapping it in. Immutable inputs (reference or input structures) may be reused once their hash matches the run's provenance record; derived numbers and renders are regenerated.
- Redraw of an existing figure: keep each panel's chart type, layout and zoom structure unless asked; list every panel whose representation changed, with a one-line reason.
- Binned continuous variables: label groups by definition and cut rule in the legend, and show the continuous relationship or a two- versus three-group sensitivity before interpreting group differences.
- Architecture schematics keep `CODE_PATHS.md` beside the figure (each arrow as source → consuming module, file:line at the cited commit); derive every arrow from it and re-check borrowed connections when imitating another paper's figure.
- Toolchain: the interpreter that has cairosvg, reportlab, pymupdf, lxml and fontTools is named in host-context; render structures with the canonical open-source PyMOL environment named there, never a new per-task environment and never the App Store build (evaluation watermark).
- Figma: arrows are single native vectors with stroke end caps; never outline text; edit the node the user points at in place; check every child's bounds against its clipping frame and inspect panel edges at 100% zoom before reporting a composition done; typography recomputed at final size (pt = units × target width mm ÷ frame width units × 72 ÷ 25.4), no text under 5 pt, panel letters 8 pt bold lowercase.

## Verified additions (2026-10-17 audit)

- Bar plots by default for comparisons of a few named quantities (methods, conditions, components); no point-and-interval panels unless asked. Captions say what each panel shows and how to read it; setup, definitions and controls go in the main or SI text. Under each inline preview, give one line per panel: axes, marks, and which rule assigned any category labels.
- Figma: edit through computer use in an in-app browser tab where the user is signed in; the Figma connector is read-only and its plan caps calls, so a cap error means switching to computer use in the same turn, not stopping. Never route a figure file through a browser's native save or file-chooser dialog: export to a new filename, move it with shell tools, upload through the destination's own file-add control; if that needs the native chooser, hand the user the exact local path and destination in one line. The final message lists every repair made to an imported copy (fills, fonts, clipping).
- When a figure is placed into a manuscript, recompute the text size at the width it actually occupies there (the scaling applied by the document), and place a vector PDF rather than a raster image.
- Before recommending or publishing a grouped or binned panel, report the grouping variable's rank correlation with the obvious size covariate and say whether the intended claim survives it.

## Figure index (2026-10-17 audit)

Keep a project figure index (`figures/INDEX.md`: figure, current version path, date, source data version, which thread produced it) and read it before editing any figure, so a sibling thread's newer version is not overwritten by an older one.

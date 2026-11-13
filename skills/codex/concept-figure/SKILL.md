---
name: concept-figure
description: "Draw the Fig. 1 kind of scientific figure (concept or teaser figure, method overview, pipeline, model architecture, paradigm comparison, agent or system diagram) as an editable HTML source rendered to vector PDF and 600 dpi PNG, following patterns taken from ML conference papers. Use for 개념도, concept figure, 모델 그림, 아키텍처 그림, overview, pipeline, schematic, teaser, Fig. 1 그려줘. Not for plots of data or results (nature-figure) or slides (html-research-deck)."
---

# Concept figures

Produce one figure that carries one idea at a glance at its printed size, with an HTML source that a person or an agent can edit and render again. The source is `figure.html`; `figure.pdf` (vector, live text) and `figure.png` are outputs of `scripts/render.py` and are never edited by hand.

## Workflow

1. **Settle the message and the facts.** Write the one sentence a reader should be able to say after five seconds with the figure. When that sentence or the picture for it is not obvious, find the concept first with [concept-development.md](references/concept-development.md): three thumbnail candidates of different patterns, shown to the user, before anything is polished. Read the method evidence (code, config, the manuscript's Methods) before drawing any dependency; for a model architecture keep `CODE_PATHS.md` beside the figure (each arrow as source → consuming module, file:line at the cited commit), derive every arrow from it and re-check borrowed connections when imitating another paper's figure. Ask only when an ambiguity changes the scientific meaning. Take the width from the target venue ([design-rules.md](references/design-rules.md), Size) and say which you used.
2. **Choose the archetype** in [archetypes.md](references/archetypes.md): architecture, pipeline, paradigm comparison, concept, or agent system. Each lists the reference figures it comes from, a layout recipe and a worked example. Read that file and [design-rules.md](references/design-rules.md) once per thread.
3. **Start from the worked example**, in the project's figure folder, never inside this skill:
   `python3 scripts/new_figure.py <figures>/<name> --example <archetype> --width <venue>` creates `v01/figure.html` and a self-contained `kit/`.
4. **Edit `figure.html`** with the kit's vocabulary ([kit.md](references/kit.md)): boxes and glyphs are laid out by CSS flex rows and columns, and arrows are `<fig-wire from="id" to="id">` tags that the kit routes between elements, so moving a box moves its arrows. Do not write absolute coordinates.
5. **Render, then pass the inspection gate**: `python3 scripts/render.py v01/figure.html` writes the outputs, zoomed `figure.tiles/` and an unticked `figure.inspection.md`. Fix every error and warning. Then look at the preview at full size and at every tile against the checklist in [inspection.md](references/inspection.md), and tick the receipt only after looking; any defect means a fix, a new render and a new look at the whole figure. "0 errors, 0 warnings" is not a finished figure: the checks have passed figures with a label lying across a rule and an arrow showing only its head. Before a figure goes out as final, a reader who did not draw it repeats the gate (a fresh agent with the tiles, or the user).
6. **Score and revise.** `python3 scripts/score.py v01/figure.report.json` gives the measured 40 points; the judged 60 come from a reader applying [rubric.md](references/rubric.md), ideally one who did not draw the figure (a fresh agent or the user). Fix the two or three largest losses in the next version and score again; the ledger `scores.jsonl` in the figure folder keeps every round. The score ranks versions and points at weaknesses; the user's verdict decides, and a verdict that contradicts the score changes the rubric.
7. **Deliver** the source and outputs with a separate `caption.md`: show the preview inline, and report the physical size, the smallest text size, the fonts embedded in the PDF, the check result, who inspected it (the receipt, and whether a second reader looked) and the score with its three largest losses. A revision goes to the next version (`new_figure.py <figures>/<name> --next`), starting from the latest version the user edited; keep the project's `figures/INDEX.md` current.

## What decides quality

- One idea per figure. The teaser makes the reader want the paper; it does not have to show the whole method.
- Colour is an encoding, never decoration: module type, modality, trained versus frozen, ours versus prior. At most four roles besides gray, the same thing in the same colour in every panel, and a key or direct labels when the meaning is not obvious.
- Show the system's input and output as concrete examples, and carry one example through the figure.
- Labels, not sentences: under about 60 words, 7 pt by default, never under 6 pt at the printed size. Explanations, definitions and provenance go in the caption; nothing in the figure is a title, note or status line.
- One arrow style for information flow; a second style (gradient, optional path) only with a key. Straight or one bend; a skip or feedback connection may go around a box with the `u` route. No diagonals outside trees and graphs.
- Emphasis comes from structure: same skeleton across compared panels with only the difference coloured, the proposed variant last and named in bold, rejected alternatives faded.
- No shadows, gradients, decorative icons or coloured accent bars. Text sits inside its box.
- Prettiness is the first aim. It comes from restraint plus something worth looking at: two or three colour roles, most of the page white, one strong part, and real pictures or computed glyphs carrying the richness. A reference figure, the user's own included, lends principles and never its palette, components or layout; do not clone one.

## Schematic versus evidence

The glyph tags (`fig-noise`, `fig-dist`, `fig-points`, `fig-bars`, `fig-matrix` values) draw illustrative stand-ins. A panel that reports data is a plot and belongs to `nature-figure`; a molecular or structural image is rendered from the actual coordinates and placed with `<img>`; real example images are placed with `<img>` as files in the version folder. Never present a stand-in or a generated bitmap as a result, and say in the caption that a schematic curve or tile is schematic when a reader could take it for data.

## Output and limits

- `render.py` needs Google Chrome or Chromium (`$CHROME` overrides the path) and drives it headless; `pdfinfo` and `pdffonts` add the page size and font list to the report when present. The PDF page equals the figure's physical size; place it in LaTeX at its natural width instead of rescaling it.
- The default font is Arial with KaTeX for `$...$` math; `data-font="serif"` switches labels to a Times-like face for papers set in Times. Confirm the font in the report's PDF font list; a substitute means the font is missing on the host (Linux: `nature-figure/references/linux-fonts.md`).
- `data-profile="nature"` puts bold lowercase panel letters top-left; the default puts "(a) name" under each panel, as ML papers do.
- A project that has its own palette or line weights keeps them in a `theme.css` beside `figure.html` (loaded after the kit's stylesheet) and notes it in the project's `STYLE.md`; the kit files in a version folder are not edited per figure.
- A figure whose content this agent may not read (see the host's reading rules for biology and chemistry) can still be consulted for style: extract numbers with a script that prints no text of the figure, and have an allowed reader write a style-only report. Never open such a figure to "just look at the layout", and take from the report what makes it work, not its values.
- SVG and Figma files are not produced. When asked for one, import `figure.html` through the Figma skill's HTML import or open the PDF in a vector editor, and verify in the destination that text stayed editable; this route has not been exercised from this skill.
- After changing the kit, run `python3 scripts/check_examples.py`: it renders every example and names the ones whose picture changed. Look at each changed one (preview and tiles, the inspection gate) before `--accept` refreshes `assets/examples/renders/`; a kit change alters examples nobody was working on. `scripts/ink_check.py` on the kit sheet's 600 dpi PNG (needs Pillow) must report symbols within 0.2 pt of their circles' centres. A visual defect the user reports becomes a kit fix plus a line in `references/user-decisions.md`, and a check when one can be measured.

## User decisions

The dated decisions behind this skill, in the user's own words, are in [references/user-decisions.md](references/user-decisions.md). Read it before editing this skill; record a new decision there and state the resulting rule in plain words in this file.

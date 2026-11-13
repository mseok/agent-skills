# Design rules

Numbers marked "measured" come from the reference figures in [archetypes.md](archetypes.md), cropped from the arXiv PDFs at print size on 2026-11-13 (word boxes from `pdftotext -bbox`, colours from the rendered crops). They describe what well-known figures do; they are starting points, and a venue's or the user's instruction wins.

## Size

Design at the width the figure will occupy and never rescale it in the manuscript. `data-width` on `<main class="fig">` takes a name or a CSS length.

| Name | Width | Source |
|---|---|---|
| `neurips`, `iclr` | 5.5 in (139.7 mm) text block | NeurIPS formatting instructions; `iclr2026_conference.sty` (`\textwidth 5.5 true in`) |
| `icml` / `icml-col` | 6.75 in (171.5 mm) / 3.25 in (82.6 mm) | ICML 2025 example paper: 6.75 in overall, 0.25 in between two columns |
| `nature` / `nature-col` | 183 mm / 89 mm | Nature final-artwork guide (see `nature-figure/references/journal-profiles.md`) |

For any other venue, print `\the\textwidth` and `\the\columnwidth` from its template and pass the length (`data-width="174.6mm"`). Height follows the content; the full-width reference figures are roughly a quarter to a half as tall as they are wide.

## Type

- Labels 7 pt, secondary labels and tensor shapes 6 pt, panel names 7 to 8 pt; nothing under 6 pt. Measured: median word-box height 5 to 10 pt across the references (ViT 6.3, CLIP 6.0, Swin 7.6, SAM 7.3, MoCo 8.8, Flamingo 9.7), which bounds the font size from above. V. Deschaintre's SIGGRAPH guide gives the same ladder: 8 pt default, 7 pt sub-labels, nothing below 6 pt.
- Arial by default. Use `data-font="serif"` when the paper is set in Times and the figure should match it (ViT, SAM and ControlNet do this); never mix both in one figure. Variables and equations are KaTeX math (`$z_\ell$`), so they match the manuscript.
- Count words. Measured: the cleanest references carry roughly 5 to 60 words (MAE 4, MoCo about 45, ViT and Swin about 50); 110 words (SD3) needed "best viewed zoomed in". `render.py` warns above 70.
- Write labels as nouns the reader already knows from the text; avoid abbreviations that send them to the caption. Units, shapes and symbols beat adjectives.

## Colour

- Fills are light tints with HSL lightness about 86 to 94 % (measured in ViT, Transformer, MoCo, SAM, CLIP, DiT, Flamingo, BLIP-2, ControlNet, Tree of Thoughts, Voyager); edges are either the same hue darker (SAM, Perceiver IO) or one dark neutral (Transformer, ViT), or absent (MoCo, DiT, I-JEPA). The kit's `data-style` picks one treatment for the whole figure: default tint + same-hue edge, `ink`, `flat`, or `quiet` (below).
- The kit's palette is built in OKLCH: every hue has the same five lightness steps (container background, box tint, box outline, accent for wires and chips, text), so any two roles sit together and no colour shouts. Text and wires are a cool near-black and slate from one gray family. Box outlines are the soft step, not the accent: the outline should close the shape without drawing attention to itself.
- Saturated fills with white text (`.solid`) are for one or two anchor modules (Genie), never for everything.
- Every colour answers "what does this colour mean?" with one of: module type, modality or data stream, trained versus frozen, ours versus prior, kept versus rejected, a quantity (with a colour bar). If the answer is "it looked nice", use gray. At most four roles besides gray; `render.py` warns above four.
- Carry a colour through: a module's outputs take the module's colour (Genie, Perceiver IO), an identity keeps its colour from input to output (DETR's object queries, I-JEPA's target blocks).
- Gray is the default for what is given, frozen or not the point. Red is for the one thing that is wrong, blocked or newly trained, not for a module type.
- Check the figure in grayscale when two roles must be told apart without a label.

## Treatments

`data-style` picks one treatment for the whole figure; do not mix them.

- default: soft tint with a soft outline of the same hue. Colour sits on the boxes, so use it when colour on the boxes is the message (layer type, trained versus frozen) and the figure has few roles.
- `flat`: the same tints without outlines, for small comparison and concept figures.
- `ink`: tints with one dark outline, the classic textbook look; use with `data-font="serif"` in a paper set in Times.
- `quiet`: boxes stay neutral and a role shows only as a pale fill; colour then lives on wires, glyphs and containers. Use it when a figure has many modules and tinted boxes would turn into a patchwork.

Whatever the treatment, the look comes from the same few habits: two or three roles, most of the area white, one strong part (`.strong`), and concrete glyphs or pictures carrying the richness.

## Shapes

Use the conventional object, and one object per meaning within a figure:

| Meaning | Draw |
|---|---|
| module, layer, operation | rounded box (`.node`) |
| encoder or decoder that changes resolution | trapezoid (`.trap-r`, `.trap-l`, `.trap-u`, `.trap-d`) |
| sequence of tokens or an embedding | row or column of cells (`fig-tokens`) |
| attention pattern, similarity or pair representation, mask | grid (`fig-matrix`) |
| a batch, several samples, per-task copies | stack (`.stack`) |
| random variable in a graphical model | circle (`.var`) |
| add, multiply, concatenate | small circle with the symbol (`.op`) |
| store, index, memory, dataset | cylinder (`.cyl`) |
| repeated unit, stage, space, component | container (`.group`) with its name inside the top edge and "×N" in a corner |
| trained / frozen | flame / snowflake or lock icon, with a key |
| prompt, transcript, code | monospace card (`.card`) |

Box size can carry meaning (a heavy encoder larger than a light head, widths following resolution); otherwise boxes of one kind share one size.

## Arrows

- One style for information flow. A second style needs a meaning and a key: dashed for gradients or a loss, faint for an auxiliary or preprocessing step, a colour for one named path.
- Straight or one bend (`hv`, `vh`). Two bends only for a skip or feedback connection that must go around a box (`u`) or to step between offset rows (`hvh`, `vhv`). Diagonals only in trees and graphs (`line`), curves only for a mapping that jumps over intermediate states or a loop.
- Keep at least 8 pt of visible shaft; if an arrow has no room, the boxes are too close.
- What flows goes on the arrow (a symbol or a tensor shape), what transforms goes in the box.
- Two opposite arrows between the same boxes are a pair of straight wires with `shift`, each labelled.
- An arrow leaves the middle of its source and meets the middle of its target, or a named position on a larger box. Line up the centres rather than letting an arrow leave a small box off-centre; `render.py` warns when a straight wire starts beside its element (`wire-detached`).
- A line that enters a box and leaves it at the same height reads as the same signal continuing. Put each output on the lane of the input it depends on, or step the lanes so that no false pairing appears.
- When the claim is one step, keep every wire slate and give that step the figure's single coloured stroke.

## Layout

- One reading direction for the main path. Align box centres on that axis and keep one gap size between siblings (the `g1` to `g6` classes), a larger one between groups. An object with a caption under it is centred as the object (`.hang`), with the caption hanging below, so that it does not ride above the axis.
- Detail belongs in a second panel: zoom lines from the block to its detail (`fig-zoom`), or a dashed rule (`.vr`) between overview and detail.
- Boxes at one level have one text size, one height and one style. Show that a part is minor with gray or with its position, never with a smaller box among its siblings (`text-level` warns).
- Compared variants share a skeleton exactly; copy the panel and change only what differs. In stacked rows the columns line up (same widths in the same order) and the same lanes run through every row, each input centred on the box it feeds (`contrast.html`: boxes of 14 pt with a 7 pt gap above, one 35 pt box below, inputs at ±10.5 pt in both).
- Use the width: `render.py` warns when content spans under 90 % of it. Empty bands at the sides mean the figure should be narrower or the objects larger.
- White space separates parts and does nothing else; what is left over loses points. Size each object to the space it has, keep arrows as long as their label needs and no longer, and give every corner of an L-shaped layout a job (the key, a note on a symbol) or close it. Pack small parts into one block around the main box rather than hanging one below it. `render.py` reports `slack` and the largest empty rectangle and warns above 24 % and 12 %; dense published figures have 11 to 15 % slack.
- A baseline that is faded (`.context`) still needs outlines: pale borderless tints at reduced opacity read as empty.
- Panel names sit under the panels as "(a) name" in ML papers and as a bold lowercase letter at the top left in Nature-family journals (`data-profile="nature"`).

## Content

- Include the input and the output of the whole system, as examples a reader recognises (an image, a sentence, a sequence), and keep the same example in every stage.
- Be specific where a reader will look for it: "LayerNorm", "cross-attention", "frozen ViT-L" instead of "normalisation", "fusion", "encoder", when the paper commits to them.
- Precision reads as a claim. Draw four tokens with an ellipsis rather than exactly nine unless nine matters; do not draw layer counts, shapes or orderings the method does not have.
- The figure with its caption should stand without the text.
- Draw the step the paper is about as what it does, not as one more named box: a small geometric picture (`.plane`), a before and after of the example, a matrix that changes. Put its rule under it as a hanging caption. One such picture per figure; the other steps stay plain boxes so that it stands out.

## Evidence behind these rules

- G. Marshall, A. Freitas, C. Jay, "An evidence-based guidance framework for neural network system diagrams", PLoS ONE 20(3): e0318800 (2025), doi:10.1371/journal.pone.0318800. Twelve guidelines derived from interviews and tested on researchers: conventional objects; one arrow type for information flow; precision with care; include the system's input and output; one consistent example; meaningful visual encodings; easy navigation; no colour for aesthetics; available conventions; what readers expect to see; be specific; usable without the text. In their ACL 2017 corpus, being specific and being self-contained correlated with citation count (p < 0.05), and no top-quartile paper's diagram depended on the text. Among the diagrams that met eleven of the twelve guidelines, six used more than one arrow type, usually to separate a kind of data flow, which is why a keyed second style is allowed here.
- V. Deschaintre, "What are figures for and how do I compose them?", SIGGRAPH Research Career Development Committee guides (research.siggraph.org/blog/guides/what-are-figures-for-and-how-do-i-compose-them/): one idea per figure; the point should land at a glance or with the caption; the teaser makes the reader curious and need not overview the method; design at the template's exact width; export vector PDF; match the figure font to the paper.

## This user's standing preferences for figures

From `nature-figure` (house defaults) and recorded feedback: prettiness comes first and no single figure's style is to be copied, the user's own figures included (see `user-decisions.md`); nothing decorative inside a figure, and white space only where it separates parts ("쓸데 없이 많은 여백은 감점요소야"); symbols centred in their circles and curves drawn as round bows; arrows straight or one bend with consistent heads; text inside its box and optically centred; one key style and position per figure; distributions and densities computed by code, not sketched; model names as the manuscript writes them; versioned folders with one inline preview per version.

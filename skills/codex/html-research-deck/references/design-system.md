# Research theme: grid, type, colour, scene grammar

Everything below was fixed on 2026-10-30 against the accepted three-slide sample (SKILL.md, User decisions). Numbers are stage pixels on the 1920×1080 stage; the engine scales the stage to the window.

## Grid

| element | position | note |
|---|---|---|
| kicker | left 110, top 50, 21 px, weight 600, no tracking | section · subtopic |
| h2 | left 110, top 92, 51 px navy | topic/method noun phrase; findings go to the closing line |
| panels | top 176, bottom 898, x 110–1810 | gutters 24 px; padding 20 px inside |
| closing line | white panel, x 110–1810, y 922–1000 | 30 px navy, weight 600, centred, one line (≤ ~70 characters) |
| cite | left 110, bottom 30, 17 px muted | `[1] Author Year · [2] …` |
| slide number | bottom right (engine) | |

Rows of panels: equal heights inside a row; widths sum to 1700 with 24 px between. Standard splits: 1700 · 838+838 · 1012+664 (scene + render) · 1236+440 (scene + small render) · two rows 388 + 310. Templates in `assets/deck/templates/` carry these coordinates; `scripts/check_deck.py` rejects any other gutter.

Inside a panel the drawing is centred: pick the `viewBox` so the content has equal top/bottom margins (slide 1 of the sample uses `viewBox="20 21 1660 682"` for a 540 px tall drawing). Keep inner margins between 20 and ~80 px; if the drawing cannot fill a 722 px panel, split the slide or add the consequence panel rather than leaving a half-empty card. Measured rule (`scripts/check_layout.py`): with the lane header baseline at scene y 28 the top gap is ≈27 px, so the lowest glyph or shape must reach scene y ≈ 650–665 in a 682 px scene (bottom gap within 24 px of the top gap, never above 80 px); text inside a box sits centred (gap above the first glyph within 10 px of the gap below the last). Fill by enlarging the figure (taller bars, wider node spacing, a DAG spread across the panel's width, bigger boxes) and the type, not by adding lines. Type scale (user decision 2026-10-31): the 24 px bold claim is the base — lane headers 24, body lines and figure labels 22–24, emphasis 26–28, chart value labels 24–26; anything under 22 only for reference-style notes (muted citations, "값은 Fig. 10") or a dense 30-row chart (19 px). Two or three lines of commentary per panel at most; a detail that does not fit at that size goes to the speaker notes. No translucent band over bars or labels: a range marker sits beside the data on the axis, and values go in one column when a reference line would otherwise cross them.

## Typography

Pretendard Variable everywhere (Korean and Latin), KaTeX for formulas. Scene classes: `.n` 26/700 names, `.s` 21 body labels (ink-soft), `.m` 19 muted, `.in` 24/700 centred in-shape label, `.lane` 21/650 lane header. In-shape names may go to 30 px (KRAS); badge digits 16 px and capsule labels 15 px are the only runs below 19 px. Panel captions 19 px muted; render labels 20 px semibold with a white halo (`paint-order: stroke`).

Korean slide copy is noun phrases (`research-talk/references/korean-slide-copy.md`); `check_deck.py` flags `~한다/된다/있다/이다/습니다` endings in visible text. Latin author names stay Latin (`Krönke 2014`).

## Colour (one meaning per hue, whole deck)

| role | value |
|---|---|
| headings, closing line | navy `#1D3A5F` |
| machinery (ligase, proteasome, cell, DNA) | grays: fills `url(#gGray)`/`url(#gSteel)`, strokes `#8E9AA6` / `#5F718A` |
| drug or path of interest | blue `#4C72B0` (`url(#gBlue)`, stroke `#2F4C7D`); the L2 segment, transfer arrows |
| substrate / transcription factor | amber `url(#gAmber)`, stroke `#B7793A`, strand `#C8692E` |
| mutation, blocked step, key phrase | red `#D1495B` (dot, ×, one bold phrase); return arrow coral `#E76F51` |
| absent / ghost state | dashed outline `#AEB7C0`, muted text `#66727F` |

At most two hue families besides gray on a slide. Nucleotides are dark capsules (`GDP` `#52606D`, `GTP` `#1F2933`), ubiquitin beads `#52606D` with white `Ub`.

## Scene grammar (sprite ids in `assets/deck/sprite-research.svg`)

| meaning | drawing | id |
|---|---|---|
| generic protein | lumpy blob, radial shading, 2.5 px stroke | `shBlob` (150×106) |
| receptor with a binding pocket | blob with a concave notch on the right | `shCrbn` |
| substrate with a recognition knob | blob with a protrusion (tip at −96,4) that touches the drug | `shIkzf` |
| adaptor, three-lobed | `shDdb1` | |
| GTPase with nucleotide pocket | `shKras`; nucleotide capsule `shNuc` at (−56,40), mutation dot at (−72,−20) | |
| small molecule | capsule `shDrug` 44×26; when covalent, a short bond line to the site dot | |
| scaffold rod | thick stroked path, outline 33 px gray over 28 px light | CUL4 in the sample |
| ubiquitin | `ub` (13 px with text) / `ubS` (9 px); poly-Ub = beads on a polyline from the substrate's top right | |
| 26S proteasome | `prot` horizontal barrel 202×124; substrate strand (amber 5 px wave) threads in, 3 short dashes exit right as peptides | |
| cell | `cellBody` (cell 348×224 + nucleus; nucleus centre at x−34, y−4), `dna` 120 px double wave, transcription arrow `M x y L x y−26 L x+36 y−26` with `marker-end="url(#ahd)"` | |
| step numbers | navy badge r 13 with a white 16 px digit, plus a 21 px label | |
| arrows | `class="ar"` gray / `arb` blue, `marker-end="url(#ah|ahd|ahb|ahc|ahl)"`; one smooth curve (quadratic) when returning, never a cubic that hooks at the end | |
| blocked | white halo circle r 19 then red × (`class="x"`) on the arrow | |
| absent state | same shape, `fill="none"` dashed stroke, muted label | |

Rules that made the sample work: the same actor keeps shape and colour across every state and panel; label the change at each arrow (binding, recognition, Ub transfer, degradation, exchange); shapes are explanatory, not geometry; what is measured (PDB render) sits in its own panel with leader labels and a caption `method · resolution · PDB id [n]`; a mechanism slide ends in the consequence the message claims (a cell panel: factor on DNA → genes → growth/arrest; the rescue experiment as the third cell). Shapes not in the sprite are drawn inline in the deck with the same conventions; promote them to the sprite when a second deck needs them.

## Anti-patterns (each was rejected by the user)

Coloured quote bars and callout boxes; blurred colour washes and gradient text; uppercase letter-spaced labels; progress bars in colour; auto-generated flow charts of boxes and gray arrows; animated canvases; dense bullet text; one closing sentence floating without a panel; mismatched gutters or a half-empty panel; figure text under 19 px; a mechanism that stops at "degradation" without showing the biological effect; the same label crossing a shape's rim.

## Per-slide procedure

1. Message (one sentence, becomes the closing line in noun form) and the evidence that supports it.
2. The picture: which actors, which states, what changes, in how many cells (2–3); which panel split; whether a render anchor is needed.
3. Draw: coordinates by hand in the panel's `viewBox` space; labels placed after the shapes; citations `[n]` at the exact claim.
4. Look: full-size PNG; fix overlaps, clipped text, rim crossings, uneven margins; repeat once.
5. Notes: original sentences, provenance of every figure, what is schematic versus measured, and what was intentionally left off the slide (e.g. gene names not in the source).

## Formulas and math labels (KaTeX; user decision 2026-11-01 "첨자 같은 것도 다 … TeX 기반으로")

Every formula and every label that carries a subscript, superscript or Greek letter is KaTeX in an HTML block — never a Unicode subscript in SVG `<text>`. Builder helpers (see the Latent SI deck's `work/build.py`): `fx(x, y, w, h, lines, size, cls)` writes a `.fx.box` strip (each line a `<p>`; a line without `$` is a Korean caption `.k`; `cls='box left'` left-aligns, `'box blue'` is the pale-blue key-equation strip); `tex(x, y, s, size, weight, color, anchor)` writes a bare `.fx` label placed like `T()` (y is the baseline, anchor start/middle/end). Panel coordinates are scene coordinates + 20; `panel(x, y, w, h, svg, html_blocks)` appends the blocks after the scene. Korean inside math goes in `\text{…}` (the theme maps it to Pretendard); write `&lt;`/`&gt;` for `<`/`>`; `\textcolor{#hex}{…}` colours a term. The engine also renders KaTeX in `h2` and the closing line, so `$z_t$` works there (TeX markers count toward the measured title length). `check_layout.py` measures `.fx` blocks as text (overlap, rim and path crossing, rasters) and flags a strip whose line is wider than its box (`html-overflow`). The 20 KaTeX woff2 fonts live in `assets/deck/vendor/katex/fonts/` and are copied by `new_deck.py`.

## Distributions (`scripts/density.py`; user decision 2026-11-01 "양키 두 … 분포 표현했던 … 코드 기반으로")

A distribution is drawn from numbers the way the reference deck does it: `density_png()` renders a density raster whose alpha follows (p/p_max)^0.5 in one tint (prior amber `#D9A552`, data or latent steel `#7FA7C9`, an unknown target gray `#9AA5B1` at alpha 0.4) as an `<image>` in `assets/figs/dens-<name>.png`, with real samples of the same distribution as 3 px dots on top (`samples()`); a 1-D density is a filled profile along an axis (`profile()` + `profile_path()`, the reference's vDensity); interpolant and bridge paths are `bridge()` samples with the σ the slide states; `Frame` maps a data window onto scene pixels. Hand-drawn blobs, dashed ellipses around dots and icon-like bell shapes are out ("둘러싸고 있는 원이나 이런 게 너무 이상"). The cite line says the drawing is a toy distribution ("예시 분포에서 계산한 밀도와 표본"); no reported number comes from it; labels never sit on a raster (`text-crosses-image`).

## Structure renders (PDB, molecules)

Produce the image with research-talk's pipeline — `research-talk/references/molecular-visualization.md` (coordinate-based PyMOL render, white background, ≥ 2400 px on the long side, trimmed margin, residue labels taken from the coordinate records, provenance JSON beside the asset) and `research-talk/scripts/draw_chem.py` for 2-D structures — then place it with the `figure-render` template: `<img>` inside `.figwrap` in its own panel, leader labels beside the image (HTML `.fx` or SVG), never on it, a `.cap` with method · resolution · PDB id, full provenance in the notes. `check_layout.py` treats `<img>`/`<image>` as rasters (clipping, labels on top). No generated-image stand-ins for structures; a slide without a structure says so instead.

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

Inside a panel the drawing is centred: pick the `viewBox` so the content has equal top/bottom margins (slide 1 of the sample uses `viewBox="20 21 1660 682"` for a 540 px tall drawing). Keep inner margins between 20 and ~80 px; if the drawing cannot fill a 722 px panel, split the slide or add the consequence panel rather than leaving a half-empty card.

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
| absent / ghost state | dashed outline `#AEB7C0`, muted text `#9AA5B1` |

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

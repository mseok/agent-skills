# Folio: the second layout (rail, spine, plate)

User decision 2026-11-12: "folio 는 font 만 기존과 동일하게 해서 다른 양식으로 만들어두자". Folio is a second layout of this skill, beside the research theme. The fonts are the research theme's (Pretendard everywhere, KaTeX for formulas); the page is different. Use it when the user asks for it by name ("Folio", "Folio 양식", "난과 판 양식"); otherwise the research theme stays the default. Everything in SKILL.md still applies (storyline, approval, gates, copy rules, taste benchmark, QA and delivery); this file replaces only `design-system.md`'s grid and the kit.

## Page

One slide is one opening of a monograph on the 1920×1080 stage: what is said on the left, what is shown on the right.

| part | position | holds |
|---|---|---|
| rail | x 96–552 | the section number (two digits, vermilion) and `section · subtopic` at y 62; the title at y 124, 44 px bold, wrapping, four lines at most; the symbols or metrics this slide uses (`recall`, four rows at most, 22 px) above the card; the closing line in a white card, y 832–1000, 27 px, three lines at most |
| spine | x 592, y 72–1000 | a hairline in segments: one segment per section, its length by the section's slide count; the current section in ink with a dot at this slide. It replaces the progress bar |
| plate | x 624–1840, y 72–1000 | one figure on the paper; `.panel` with 20 px padding, so a drawing has 1176 × 888 px |
| cite | x 644, bottom 28, 17 px | provenance under the figure |

Slide kinds (`scripts/folio_kit.py`, fragments `assets/deck/templates/folio-*.html`):

- `cover()`: the title on the left (`<em>` = the indigo words), one figure on a plate at x 932–1840 (868 × 888).
- `opener()`: a section opener on ink: the section number, the section's name and the one question the section answers. Use it where the talk turns; a deck does not need one for every section.
- `slide()`: rail + plate.
- `spread()`: a full-width plate (x 76–1860, y 196–886; 1744 × 650) under a one-line title, with the closing card across the bottom. For a table or a figure that must be wide; a backup spread is numbered B1 and has no spine.

`write_deck()` numbers the sections from `init(deck, sections=[…])` and draws every spine from the order of the slides.

## Why this page

- The plate is close to 4:3. The research theme's panel band is 1660 × 682; a drawing that stacks rows (generation above training above the loss), a plot, a 3 × 3 photo grid or a square figure of a paper gets more room here, and a long left-to-right chain gets less: stack its rows, or use a spread.
- Title and closing line sit in one column, so the argument of a slide reads down the rail while the figure stays whole.
- The rail has room for definitions at first use (SKILL.md, Gates): `recall=[('$z_t$', 'bridge 위의 latent'), ('FID', '실제 이미지 분포와의 거리')]`. A symbol goes in as KaTeX, a metric as its name. List what this slide uses, not the deck's whole notation.

## Type and colour

Pretendard Variable for everything, KaTeX for formulas; values in tabular numerals (`T(..., cls='num')`). Sizes: title 44, opener question 76, cover title 100, lane headers 24/650, figure labels 22–26, values 28–42, closing line 27, recall 22, cite 17, slide number 18. Nothing on the plate is under 22 px except what KaTeX sets as a script.

One meaning per hue: ink `#17191C` on paper `#F6F3EB`; indigo `#27477D` (fill `#DDE5F1`) for the model or the value the slide is about; ochre `#B8791F` (fill `#F1E0BC`) for the prior; machinery (encoder, decoder, frames) in warm gray `#E9E4D8` / `#77736A`; other bars `#BDB8AB`; vermilion `#CF3F2A` only for the section number and the one key phrase of a closing line (`<b>…</b>`, kept on one line). White is a card that holds one thing: the closing line, the key formula, one question of the presenter's slot. No bars, washes, gradient text, letter-spaced labels, icons or animation, as in the research theme.

Section numbers are two digits (`01`, `02`): `§` belongs to the paper's sections in the cite line, and Roman numerals read as bars in a sans-serif face.

## Drawing on the plate

- Distributions are stepped level sets, drawn from numbers: `bands2d()` for a 2-D density, `field_bands()` for the (t, x) picture of a transport, both vector and without an outline, with `dots()` and `strands()` for real samples and paths. Each step is an opaque colour (the stack's colour over the paper): a translucent fill, and above all a gradient with alpha, is drawn differently by PDF engines (Poppler dropped the alpha in the first export). On a white card pass `base='#FFFFFF'`.
- A label never sits on a band, a path or a raster; `check_layout.py` reports it (`text-crosses-path`, `text-crosses-image`). Put end labels above the frame and axis labels below it.
- Formulas: the key formula is `fx(..., 'box')`, a white card. A derivation is a stack of full-width `fx(..., 'box plain', eq='13', note='…')` rows with a hairline between them, each one relation on one line with the paper's own equation number flush right and what the row gives flush left; its result is the one `'box'` row. Check every `eq` against the paper.
- Results: one row per condition; values that are alike stay numbers, the values that differ become bars from zero (gallery 6 and 7). The row the slide is about is indigo.
- Photos and paper figures: `<image>` at or below the source's own pixels, labels beside them.
- A mechanism reads from top to bottom; the same actor keeps its shape in every row (`trap`, `grid`, `photo`, `model`); arrows are straight or one smooth curve with the head on the tangent (`arrow`, `qarrow`).
- The closing slide: what the paper answered as a ledger (question, answer, the one number behind it), and under it the presenter's slot as white cards with a content header and two or three questions (gallery 8). `owner: user` in the storyline applies to that slot.

`scripts/folio_gallery.py` is the worked example with toy content (renders in `assets/folio-gallery/`): 1 cover, 2 opener, 3 concept with a field and a formula card, 4 mechanism in stacked rows, 5 derivation, 6 results as rows, 7 small multiples, 8 closing ledger, 9 backup spread with a table. Copy the nearest slide's code and change the content.

## Scaffold, build, check

```sh
python3 scripts/new_deck.py /abs/<talk>-deck/deck --title "…" --theme folio          # default fragments: cover, opener, plate
python3 /abs/<talk>-deck/work/build.py                                               # from folio_kit import *; init(deck, sections=[…]); …; write_deck(slides)
python3 scripts/check_deck.py /abs/<talk>-deck/deck/index.html                       # Folio grid when the deck links css/theme-folio.css
python3 scripts/check_layout.py /abs/<talk>-deck/deck/index.html --json …/qa/layout.json
```

Both checkers know the layout. `check_deck.py` expects one plate per content slide at the fixed box (624, 72, 1216, 928; a spread: 76, 196, 1784, 690) and no plate or closing line on an opener. `check_layout.py` does not apply `h2-wraps` and `closing-wraps` to Folio slides (the title wraps by design; a closing line that does not fit its card is an `html-overflow`) and reports `title-too-long` when a rail title takes more than four lines. Everything else in `qa.md` is unchanged: shots, contact sheet, PDF, `pdf_compare.py`, `banned_copy_lint.py`, publishing.

## Not calibrated for Folio

The judged loops, `score_*.py`, `style_gap.py`, the rubrics and `builder-notes-gpt.md` were measured on the research theme (panel band, white-area limits, the cover template). Do not report their scores for a Folio deck, and do not run a goal loop on one, until they have been run and read on this layout. The presenter aids (`js/aids.js`: L, Z) work; T does nothing, since the spine is the tracker.

# Kit vocabulary

A figure is one HTML file: `<main class="fig" data-width="neurips">` holding flex rows and columns of components, followed by the wire tags. `figure.css` styles the classes; `figure.js` expands the `fig-*` tags, routes the wires after layout and reports the checks. All sizes are physical (pt, mm). `assets/examples/kit-sheet.html` shows every component drawn; copy from it and from the six worked examples.

## Figure attributes

| Attribute on `.fig` | Values |
|---|---|
| `data-width` | `neurips`, `iclr`, `icml`, `icml-col`, `nature`, `nature-col`, or a CSS length (`120mm`) |
| `data-style` | omitted = tint fill with same-hue edge; `ink` = tint fill with dark neutral edge; `flat` = borderless tints; `quiet` = neutral boxes, a role shows only as a pale fill, colour lives on wires, glyphs and containers |
| `data-font` | omitted = Arial; `serif` = Times-like |
| `data-profile` | omitted = "(a) name" under panels; `nature` = bold lowercase letter top-left |
| `data-min-pt` | text-size warning threshold, default 6 |

## Colour roles

`data-c="blue|teal|green|yellow|orange|red|purple|gray|none"` on any component sets five variables that it and its contents use, one hue at five lightness steps: `--pale` (container background), `--fill` (box tint), `--soft` (box outline), `--edge` (wires, chips, solid fills), `--deep` (text). Set colours only through roles; an inline colour bypasses the palette and the role count. A project with its own palette keeps a `theme.css` beside `figure.html`, loaded after `kit/figure.css`, that redefines these variables per role (and `--wire-w`, `--wire-r`, `--head-l`, `--head-w`, `--head-notch` on `.fig` for the wires).

## Layout

`.row` and `.col` are flex containers (centred, gap 6 pt). Gap classes `g0` 0, `g1` 2, `g2` 4, `g3` 8, `g4` 12, `g5` 18, `g6` 26 pt. Alignment: `.start`, `.end`, `.stretch`, `.between`, `.around`, `.evenly`, `.middle`; `.grow` takes the free space; `.fill` is full width. Use inline `style` for a specific width, height, margin or padding in pt. Leave room where a wire needs it: wires and their labels do not take space, so a curve below a row needs bottom padding on that row.

Panels: `.panels` > `.panel` > `.body` + `.cap` (`<div class="cap"><span class="tag">a</span>Name</div>`; add `.b` to bold the proposal's name). `.vr` and `.hr` are dashed rules between panels.

## Components

| Markup | Draws |
|---|---|
| `<div class="node" id="enc" data-c="blue">Encoder</div>` | module box; modifiers `.solid`, `.plain` (white fill), `.ghost` (dashed, empty), `.pill`, `.sm`, `.lg`, `.faded`, `.stack` (two copies behind; `.stack.two` exactly one, for a pair or a model called twice), `.wrap` (allow line breaks) |
| `.node.trap-r`, `.trap-l`, `.trap-u`, `.trap-d` | trapezoid narrowing right, left, up or down; give it a width and height; `data-slant="0.2"` |
| `.node.cyl` | cylinder; give it a height and `padding-top` about 6 pt |
| `<span class="sub">` inside a node | second line in the small size |
| `<fig-icon class="badge" name="snowflake">` inside a node | corner badge; without `.badge` the icon is inline |
| `<div class="obj" data-c="blue"><img …>Caption</div>` | object card: a picture or glyph on top and its caption inside the card; without `data-c` it is a neutral tile, `.bare` drops the frame |
| `<span class="hang" id="x"><fig-matrix …></fig-matrix><span class="hc">caption</span></span>` | an object whose small caption hangs below it, so the object itself stays on the flow axis; leave bottom padding on the row. `.hc.r` and `.hc.l` put the caption beside the object, for an object on a vertical axis |
| `<div class="meter" data-c="orange" style="width: 70pt; --v: 0.05"></div>` | a share made visible: a track with 5 % filled in the role colour (trained parameters, kept tokens). A schematic share unless the caption gives the number |
| `<i class="chip" data-c="orange">1</i>` | numbered disc for steps and keys |
| `<span class="op">+</span>`, `<span class="var">$x$</span>` | operator circle, variable circle (`data-c` fills it) |
| `<div class="group" data-c="…">` | container, dashed by default; `.frame` solid edge, `.tint` pale fill with a faint edge (`.tint.frame` pale fill with the soft outline), `.strong` accent edge for the one part the figure is about (also on `.node`), `.bare` invisible. Name: `<span class="gl">Name</span>` (top-left inside); `.tr`, `.bl`, `.br`, `.tc` move it, `.on` sits it on the top edge, `.b` bolds it |
| `.context` on a group, panel or row | readable context at 62 % opacity: the earlier method or the surrounding system beside the `.strong` contribution (`.faded`, 38 %, is for ghost copies) |
| `<div class="node plain plane" id="pl" style="width: 112pt; height: 35pt">` holding `<i class="pt" id="p0" style="left: 17pt; top: 16pt">` and `<span class="at" style="left: 17pt; top: 20pt">` | free placement for a small geometric picture (points on a line, vectors, a region). `.pt` is a dot centred on its left/top (`data-c`; `.strong` for the one that matters). `.at` is text placed by its top-left corner; add `transform: translateX(-50%)` to centre it on a point. Wires between `.pt` ids with `route="line"` draw the strokes. `.plane` alone is an unframed canvas. The plane counts as one object for alignment; wires inside it need no key and their labels may lie on it |
| `<span class="label">`, `.dim`, `.title`, `.mono`, `.b` | free text: normal, small gray, bold 8 pt, monospace; `.b` bolds anything; `<span class="tc" data-c="red">` prints a term in a role colour |
| `<div class="card">` with `<span class="tab">Title</span>` | monospace transcript or code card (whitespace kept); `<span class="kw" data-c>` bold keyword, `<span class="hl" data-c>` highlight |
| `<div class="legend">` > `<span class="key">` | key; start each key with `<i class="sw" data-c="…"></i>` (swatch) or `<i class="wk" data-kind="dash" data-c="…"></i>` (wire sample); `.v` vertical, `.boxed` |
| `<img class="img" src="photo.png" style="width: 30pt">` | real image, file kept in the version folder; `.img.ph` is an empty placeholder |

Math: write `$...$` anywhere in text; it is typeset by KaTeX. A symbol inside `.op`, `.var`, `.chip` or a token cell is centred on its ink by the kit, so do not nudge it by hand.

The kit lays the figure out eight times larger than print size when rendering (twice on screen) and scales the output back. Chrome snaps box edges and text baselines to whole layout pixels, which at print size is 0.75 pt and visibly lifts small text; the zoom cuts that to under 0.1 pt. Sizes in the HTML stay in real pt and mm.

## Glyph tags

All take `data-c`; sizes are in pt.

| Tag | Attributes |
|---|---|
| `fig-tokens` | `n`, `size`, `v` (vertical), `solid`, `mask="2,3"` (gray cells), `gap="4"` (ellipsis cell), `colors="purple,-,red"` (per cell, `-` keeps the default), `labels` |
| `fig-matrix` | `rows`, `cols`, `size`, `on="all|diag|lower|upper|r:c,r:c"` (tinted cells), `dim` (gray the rest), `values="0.1,0.9,…"` (row-major tint strength), `labels` |
| `fig-dist` | 1-D density: `w`, `h`, `mix="mean:sd:weight,…"` in unit coordinates, `fill`, `noaxis` |
| `fig-noise` | a small illustrated scene standing in for a photo, with gray noise laid over it: `w`, `h`, `t` (0 clean to 1 all noise), `res` (noise cells per side), `seed`, `scene="day|dusk|sunset"` (sunset is dusk pushed further), `view="x0,y0,x1,y1"` (a crop, for patches); `.stack` for several samples, `.strong` for the one picture that matters (an accent frame) |
| `fig-blob` | organic stand-in for a rendered object: `w`, `h`, `seed`, `lobes`; `.faded` for a ghost copy |
| `fig-net` | small layered network: `layers="3,4,2"`, `w`, `h` |
| `fig-points` | scatter: `clusters="x:y:spread:colour,…"`, `n` per cluster, `ring="x:y:r"`, `seed` |
| `fig-bars` | `values`, `on="1"` (highlighted bars, others gray), `w`, `h` |
| `fig-icon` | `name` = snowflake, flame, lock, database, file-text, image, search, user, bot, wrench, check, x, settings, sparkles, message-square, code, globe, brain, cpu, eye, layers, refresh-cw, zap, clock; `size` |

These are illustrative stand-ins; data and real images follow SKILL.md, "Schematic versus evidence".

## Wires

`<fig-wire from="a" to="b">` after the layout, inside `.fig`. An end is an element id, optionally with a side and a position along it: `enc.r`, `enc.l@0.3` (0 = top or left, 1 = bottom or right). An end can also be a point on an earlier wire that has an id: `from="w1@0.4"` branches off 40 % along wire `w1`.

| Attribute | Values |
|---|---|
| `route` | omitted = straight when the boxes overlap on one axis, else one bend; `h`, `v` straight; `hv`, `vh` one bend; `hvh`, `vhv` two bends (`at="0.5"` places the middle leg); `u` leaves and enters on one side (`via="l|r|t|b"`, `off` pt beyond the boxes in between); `curve` for arcs and self-loops: with both ends on one `side` it is a round bow whose height is `bend` pt (default 0.3 of the span, between 10 and 28 pt), leaving and arriving at an angle; `line` centre to centre for trees |
| `kind` | omitted = flow; `dash`, `dot`, `faint` |
| `data-c` | role colour of the wire and its label |
| `head` | `end` (default), `start`, `both`, `none` |
| `label` | text or `$math$`; `ls="t|b|l|r|on"` side of the line (`on` masks the line), `lp="0.5"` position along the segment, `lseg` segment index |
| `shift` | pt offset of a straight wire, for a pair of opposite arrows |
| `@` on a straight wire | a position on one end sets the line for the whole wire, so the other element must span it; otherwise the wire starts in mid-air (`wire-detached`). Align the two centres instead, as in `contrast.html` |
| `weight`, `gap`, `dot` | stroke multiplier; pt gap at both ends (by default the tail sits flush on its source and the head stops 1 pt before its target); dot at a branch point |
| from a `.stack` | a wire on the right or top of a stacked box leaves from the outermost copy |

`<fig-zoom from="blk" to="detail">` draws the two dashed zoom lines between a box and its detail panel. `<fig-brace of="a,b" side="b" label="T frames">` draws a brace along one side of the listed elements.

## Checks reported by `render.py`

Errors: text under 5 pt, an element, container or wire outside the figure, content overflowing its box, a wire end that does not exist, an unknown icon. Warnings: text under 6 pt, overlapping items, a label lying across a container's edge, a wire through an unrelated item, a zoom line through a piece of text, a bent wire with a leg too short for its head (`wire-leg`), text or an object across a panel rule or outside its panel (`on-rule`, `panel-overflow`), side-by-side boxes with different text sizes (`text-level`), a diagonal segment, an arrow shorter than 8 pt (mostly head), a straight wire whose end lies off its element (`wire-detached`), a label lying on its own line (`label-on-wire`), white space beyond separation (`empty-space`: over 24 % slack, or an empty rectangle over 12 % of the drawn area, with its position in mm), more than one unlabelled wire style without a key, more than four colour roles, content under 90 % of the width, more than 70 words. `data-overlap="ok"` on an element accepts an intended overlap. `render.py` also writes zoomed crops (`<stem>.tiles/`) and an unticked `<stem>.inspection.md` for the inspection gate ([inspection.md](inspection.md)): the checks cover classes of defect, the look covers the rest. The report also gives the physical size, the smallest and median text size, the fonts in the PDF, and a `metrics` block (alignment, gap variation, white space as `slack` and largest hole, balance, wire crossings and bends) that `scripts/score.py` turns into the measured 40 points of [rubric.md](rubric.md).

# Scoring rubric

A figure gets a number so that each revision can go after the largest loss. 100 points: 40 measured by `scripts/score.py` from the render report, 60 judged by a reader who looks at the figure. The number ranks versions of one figure and shows where points go; the user's verdict decides what is good, and when the two disagree the rubric is what changes (record it in `user-decisions.md`).

## Scoring a version

1. Render with `render.py` and fix the errors.
2. Judge. The best judge has not drawn the figure and has not read the brief: a fresh agent or the user. The judge
   - opens `figure.preview.png` at 100 % for about five seconds, then writes down the one sentence the figure seems to say and where the eye landed first;
   - only then reads the intended message and the caption;
   - gives each of the sixteen criteria 0, 1, 2 or 3 from the anchors below, zooming in for the craft criteria, with a one-line note for every score under 3 that names the object that caused it;
   - saves `judgement.json` beside the figure: `{"judge": "...", "first_sentence": "...", "scores": {"M1": 2, ...}, "notes": {"M1": "..."}}`.
3. `python3 scripts/score.py v02/figure.report.json --judgement v02/judgement.json` prints both parts with the losses largest first and appends a line to `scores.jsonl` in the figure folder.
4. Fix the two or three largest losses in the next version and score again. When a round gains under two points and moves no criterion, stop revising and show the user: further gains need their eye.

A judge who also drew the figure scores high; such scores are for ranking versions only, and the ledger records the judge's name.

## Judged criteria (0 to 3 each; points = 3 × weight at best)

**Message, 15 points**

| | Criterion (weight) | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|
| M1 | Message in five seconds (2.0) | the blind sentence matches the intended message, including its contrast or mechanism | right topic and direction, key contrast missed | topic only | wrong or nothing |
| M2 | Focal point and hierarchy (1.5) | the first glance lands on the contribution; second and third levels are clear | lands near it, with a competing emphasis | everything has equal weight | lands on something secondary |
| M3 | Concrete example carried through (1.0) | input and output are recognisable examples and one example runs through every stage | concrete ends, abstract middle | one end only | named boxes only |
| M4 | Stands with its caption (0.5) | every colour, symbol and abbreviation is explained by a label, the key or the caption | one unexplained item | several | needs the main text |

**Encoding, 9 points**

| | Criterion (weight) | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|
| E1 | Colour means something (1.25) | each colour has one meaning held in every panel, at most four roles, and a reader can name them | meaningful, but one colour does two jobs or one role is unexplained | mostly decorative | misleading |
| E2 | Conventional shapes, one per meaning (0.75) | each shape stands for one kind of thing and is the conventional one | one inconsistency | arbitrary variety | shapes contradict meaning |
| E3 | Arrows unambiguous (1.0) | every arrow has a clear source, target and meaning; one style per meaning; extra styles keyed or labelled | one ambiguous junction or unkeyed style | several | the flow cannot be followed |

**Composition, 12 points**

| | Criterion (weight) | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|
| C1 | One reading path (1.25) | one direction; the eye never jumps back except along a drawn loop; panel order follows it | one detour | zigzag | no order |
| C2 | Grouping and spacing (1.5) | related things sit closer than unrelated ones; equal gaps within a level, larger between groups; objects sit on the flow axis | one inconsistency visible at print size | cramped or loose areas | collisions or random spacing |
| C3 | Proportion and white space (1.25) | sizes follow importance, the width is used, white space only separates parts (no empty band, corner or over-long arrow), weight is balanced | one over- or undersized element, one loose region or a mild hole | lopsided, an obvious hole, or objects small in a large empty frame | mostly empty or crammed |

**Craft, 12 points**

| | Criterion (weight) | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|
| K1 | Line and arrow craft (1.5) | one weight per role, consistent heads, clean joints, arrows meet their boxes, shafts of 8 pt or more | one flaw | several | sloppy |
| K2 | Type craft (1.5) | two or three sizes with clear roles, a regular and a bold tier used consistently, labels beside their objects, no awkward wraps, math typeset | one flaw | several | clashing or unreadable |
| K3 | Finish (1.0) | at 400 % nothing embarrassing: consistent radii, text optically centred, crisp glyphs, shared edges aligned | one flaw | several | many |

**Aesthetics, 12 points**

| | Criterion (weight) | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|
| A1 | Palette harmony and restraint (1.5) | hues of one family in saturation and lightness; large areas quiet; saturated colour small and purposeful | harmonious, but one colour sticks out or the tints are heavy | tool-default colours or too many hues | garish |
| A2 | Richness without clutter (1.5) | something worth looking at beyond boxes (real examples, rendered objects in cards, small computed glyphs, a repeated motif) and still airy | some concrete visuals but mostly boxes, or rich but busy | boxes and arrows only | cluttered or empty |
| A3 | Identity (1.0) | one visual language of its own, carried through every part, that would not look out of place beside the best figures of the venue | clean but generic | looks like a tool's default output | looks unfinished |

## Measured part (40 points)

| Part (points) | Full marks | Zero |
|---|---|---|
| checks (6) | no errors or warnings | any error; each warning costs a quarter |
| alignment (6) | every object shares an edge or centre line with another | 75 % or fewer do |
| rhythm (6) | gaps inside each row or column vary by under 5 %, five gap sizes or fewer in the figure | variation of 60 %, eleven sizes |
| white space (5) | 12 % or less of the drawn area is farther than 6 pt from anything drawn (`slack`) | 35 % |
| largest hole (3) | largest empty rectangle is 6 % of the drawn area or less | 18 % |
| balance (3) | centre of mass within 3 % of the centre | 12 % off |
| text (6) | nothing under 6 pt, four sizes or fewer, 60 words or fewer | 5 pt, six sizes, 110 words |
| colour roles (1) | four or fewer | six |
| wires (4) | no wire crosses another, half a bend per wire or less | two crossings, 1.5 bends |

White space is measured inside the bounding box of what is drawn, so the page margin does not count and a tight crop of a published figure compares fairly. Unused white space is a loss by the user's decision (`user-decisions.md`): by the same measure taken from the papers (`tools/whitespace.py` in the skill's work folder, on crops), CLIP Fig. 1 has 15 % slack, DiT Fig. 3 and I-JEPA Fig. 2 11 %, BYOL Fig. 2 16 %, SAM Fig. 1 21 %, and the sparse MoCo Fig. 2 and ViT Fig. 1 about 29 %. Measured scores recorded before round 8 used other weights (checks 8, empty space 5 on the largest rectangle alone, colour roles 2) and are not comparable with later ones.

The measured part cannot see meaning or beauty; a figure can score 40 here and still say nothing. It exists so that the judge's attention goes to what only an eye can check.

## Calibration

Before scoring a figure, the judge scores two or more of the reference figures in [archetypes.md](archetypes.md) from their papers and keeps those numbers in view: they are what the scale means. Do not hand the judge a single "target" figure to compare with (rounds.md tells why).

Scores given on 2026-11-13 by a reader who had drawn none of them (Claude Sonnet 5.5), from crops of the papers:

| Figure | Clarity / 36 | Beauty / 24 | Judged / 60 | Scores under 3 |
|---|---|---|---|---|
| MoCo, Fig. 2 (published) | 29.5 | 18.5 | 48.0 | M2 2, M3 1, E2 2, E3 2, C3 2, K1 2, A2 1, A3 2 |
| CLIP, Fig. 1 (published) | 34.2 | 22.5 | 56.8 | M4 2, C1 2, K1 2 |
| DiT, Fig. 3 (published) | 34.0 | 22.5 | 56.5 | M3 1, A2 2 |
| I-JEPA, Fig. 2 (published) | 30.2 | 21.0 | 51.2 | M3 0, M4 2, E3 2, C3 2, A2 1 |

So a published, much-cited figure scores about 48 to 57 here, and loses its points mostly on having no concrete example (M3) and on richness (A2). A kit figure above the high fifties deserves a second look at its scores.

Totals are not comparable across figures of different size: a small figure earns its clarity points more easily than a dense multi-panel one. Compare versions of one figure.

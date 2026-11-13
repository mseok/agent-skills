# Improvement rounds of the kit and its examples

One entry per round: what changed, how the scores moved, what the user said. Add a round whenever the kit or the examples are revised against the rubric. The user's words are quoted in `user-decisions.md`.

## Rounds 1 and 2 (2026-11-13): first scores, and a wrong turn

An independent reader scored the examples with `rubric.md`. Its recurring notes on round 1 were sound and the fixes stay: arrows too thin with small heads, elements touching the page edge, colours assigned per module instead of per role, loud noise tiles, the contribution not the most salient thing, uneven gaps, captioned objects riding above the flow axis, no key for colour roles. Judged scores rose from 41 to 49 out of 60 to 45 to 51.

The wrong turn: the user had named one of their own figures as a reference, and the kit took over that figure's palette, stroke constants, card styling and a whole example in its manner. The user's verdict: "이건 너무 [내 논문] 스러운 게 되어 버린거같은데, 걍 예쁘게 하는게 제일 중요하고 굳이 그 양식을 복사 붙여넣기 하듯이 하라는 뜻은아니었어." The judge had also been shown that figure as the target, so part of the rise in its beauty scores measured resemblance. Those scores are not carried forward.

## Round 3 (2026-11-13): the user's two notes on the kit sheet

"기호들이 중앙 배열이 안 되어 있음" and "화살표가 너무 어색해 … curvature 가 커야지": symbols are centred on their ink, the layout is zoomed eight times against Chrome's pixel snapping, and curves are round bows. Measured with `ink_check.py`: symbol centres within 0.12 pt.

## Round 4 (2026-11-13): the kit's own look

Removed everything taken from the reference figure. The palette is now built in OKLCH with the same five lightness steps for every hue; boxes carry a soft outline one step darker than their tint; wires are 0.7 pt slate with rounded bends and notched heads; `quiet` is a plain neutral-box treatment with the kit's own tokens. Architecture, pipeline and agent-loop were redrawn in the default treatment with two or three roles each. Not yet scored by a judge; the user has not yet judged this look.

## Round 5 (2026-11-13): close inspection of round 4

Looked at every example at 420 dpi in tiles. Fixed: a wire label lying across a container's edge (now also a check, `label-on-edge`); adapter pills off the centre lines of their blocks in `comparison` (now one grid, key under the pills); the pixel-art scene, which read as a placeholder, replaced by a small illustrated scene with noise laid over it, so that `fig-noise` reads as a picture at every noise level. Scored by a judge calibrated on four published figures (rubric.md, Calibration: they score 48 to 57) and shown no style target:

| Example | Clarity / 36 | Beauty / 24 | Judged / 60 | Scores under 3 |
|---|---|---|---|---|
| `architecture` | 29.2 | 19.0 | 48.2 | M2 2, M3 2, M4 2, E3 2, C2 2, C3 2, K1 2, K3 2, A2 2, A3 2 |
| `pipeline` | 31.0 | 22.0 | 53.0 | M3 2, M4 2, E2 2, C2 2, C3 2, K3 2, A3 2 |
| `comparison` | 30.5 | 21.5 | 52.0 | M2 2, M3 2, M4 2, E3 2, C2 2, A2 2, A3 2 |
| `concept` | 32.2 | 19.0 | 51.2 | E3 2, C2 2, C3 2, K1 2, K3 2, A1 2, A3 2 |
| `agent-loop` | 32.2 | 16.0 | 48.2 | E3 2, C2 2, C3 2, K1 2, K2 2, K3 2, A1 2, A2 2, A3 2 |

All five blind sentences matched the intended message. The judge's reading of the set: colour roles keyed and held, one concrete example through each figure and crisp arrows are as good as or better than the published four; behind them are uneven page margins and shared axes, a second arrow family in each figure, uneven gaps, the contribution not set apart strongly enough, and thin imagery. The shared look is "pleasant and calm, and it reads as a polished UI kit: generic".

## Round 6 (2026-11-13): the judge's set-level points

Changed in the kit: 7 pt page margin; wire labels stay slate whatever the wire's colour; arrowheads grow with the square root of the stroke, so a heavier wire is not a second arrow family; `.context` (62 % opacity) for readable context beside a `.strong` contribution. Changed in the examples: architecture has one arrow family, even gaps and the patch row centred on the column axis; pipeline has one gap value and a lower encoder so that the sampler is the heaviest mass; concept is centred with one gap value and a lighter arc; comparison has a rule between every pair of panels; agent-loop has task, policy and tools on one centre line with parallel arrows landing mid-edge. Not yet scored.

## Round 7 (2026-11-13): the whole workflow on a public claim, and a second judged score

The workflow was run end to end on classifier-free guidance (claim, contrast, inventory, three thumbnails, choice, figure in five versions). It became the sixth worked example, `contrast.html`, and added to the kit: `.plane` with `.pt` and `.at` for a small geometric picture, `.stack.two`, wires leaving a stack from its outer copy, and the check `wire-detached`. Rules it taught are in design-rules.md: shared lanes through stacked rows, a straight-through line reads as the same signal, label each arrow into a combination step with what flows, draw the step the paper is about as what it does, one coloured stroke.

Judged by a fresh reader calibrated on the same four published figures (48.0 to 56.8), no style target:

| Example | Clarity / 36 | Beauty / 24 | Judged / 60 | Scores under 3 |
|---|---|---|---|---|
| `concept` | 33.5 | 22.5 | 56.0 | E3 2, C2 2, A1 2 |
| `contrast` (v04) | 33.5 | 20.0 | 53.5 | M3 2, M4 2, E3 2, K1 2, A2 2, A3 2 |
| `pipeline` | 30.8 | 21.5 | 52.3 | M3 2, M4 2, E3 2, C2 2, C3 2, K1 2, A3 2 |
| `comparison` | 30.5 | 19.0 | 49.5 | M2 2, M3 2, M4 2, E3 2, C2 2, K1 2, K3 2, A2 2, A3 2 |
| `agent-loop` | 30.5 | 19.0 | 49.5 | M2 2, C1 2, C2 2, C3 2, K2 2, K3 2, A1 2, A3 2 |
| `architecture` | 29.0 | 20.0 | 49.0 | M2 2, M3 2, M4 2, E1 2, C2 2, C3 2, K1 2, A2 2, A3 2 |

The judge also checked content and found real errors: `pipeline` drew the denoiser upstream of the starting noise; `contrast` showed no input for the second, empty-condition call; `agent-loop` had no answer leaving the policy and a memory the episode never used. One of its claims was wrong when checked against the source (that panel (c) of `comparison` had wider blocks) and was not acted on.

## Round 8 (2026-11-13): the judge's points, and white space

The user, while this round was in progress: "쓸데 없이 많은 여백은 감점요소야." White space is now measured inside the drawn area (`slack`, largest hole), warned about, and worth 8 of the 40 measured points; C3 names it.

| Example | What changed | Slack |
|---|---|---|
| `contrast` (v05) | predictions drawn as three small pictures on the line; "or ∅" on the condition lane; arrows into both combination boxes labelled with what flows | 6 % |
| `pipeline` | one example from prompt to prediction; the denoiser is the container of the states it produces, so the condition enters it and the chain starts at the noise; captions on one baseline | 12 % |
| `agent-loop` | packed into one block (task, tall policy, tools over memory); answer arrow; the episode writes to memory; one title style; no stock icon | 22 % to 12 % |
| `comparison` | baselines as context with outlines, the proposal on a framed card; adapters point into their blocks; a share bar under each panel; key, adapters and a note fill the proposal's right column | 26 % to 21 % |
| `concept` | every usual-route stroke slate, the one-call arc the single colour; both routes named; larger tiles, shallower bow | 28 % to 20 % |
| `architecture` | key for the four layer colours; output bars gray and on the axis; class token named; an attention-map glyph; tighter columns | 27 % to 21 % |

New checks: `empty-space`, `label-on-wire`, a container outside the figure, a zoom line through text, an arrow under 8 pt. Not yet judged; the three figures at about 20 % slack are the next to tighten.

## Round 9 (2026-11-13): the user on preview v5, and the inspection gate

The user: white space is no longer a problem; in `thumbnails`, text and pictures overlapped and the arrows of sketch C were wrong; could an inspection step make sure this never happens; and was the smaller LayerNorm text in `architecture` deliberate. All three figures had rendered with no errors or warnings, and `thumbnails` had not been looked at since round 6 while the kit changed under it.

Changed: `thumbnails` (labels inside their panels, sketch C redrawn as a branch and a join on one axis), `architecture` (one text size for the four boxes of the block), and further tightening of `concept` (14 % slack), `comparison` (18 %) and `architecture` (19 %). New checks: `wire-leg`, `on-rule`, `panel-overflow`, `text-level`. New process: the inspection gate (`inspection.md`), tiles and a receipt from `render.py`, the NOT INSPECTED mark in `score.py`, and `check_examples.py` for kit changes. An independent inspector then went through every example on tiles; its findings and what was done about them are in the work folder (`findings/inspection-r9.md`).

Judged after these changes by a fresh reader (same four anchors, 48.0 to 56.8, no style target), who also listed defects and found none visible at print size:

| Example | Clarity / 36 | Beauty / 24 | Judged / 60 | Round 7 | Scores under 3 |
|---|---|---|---|---|---|
| `pipeline` | 34.8 | 21.5 | 56.2 | 52.2 | C3 2, K1 2, A3 2 |
| `contrast` | 33.8 | 21.5 | 55.2 | 53.5 | E3 2, C3 2, K1 2, A3 2 |
| `concept` | 33.8 | 21.5 | 55.2 | 56.0 | E3 2, C3 2, K1 2, A3 2 |
| `comparison` | 33.8 | 20.0 | 53.8 | 49.5 | E3 2, C3 2, K1 2, A2 2, A3 2 |
| `agent-loop` | 29.8 | 21.5 | 51.2 | 49.5 | M3 2, E1 2, C1 2, C2 2, C3 2, A1 2, A3 2 |
| `architecture` | 29.2 | 21.5 | 50.8 | 49.0 | M2 2, M3 2, M4 2, E1 2, C1 2, C3 2, K1 2, A3 2 |

The mean rose from 51.6 to 53.7. What is left is the same in most figures: arrows that did not start flush on their source (K1), white space the judge still counts (C3), and identity (A3). One content error remained: the classifier in the upper row of `contrast` had no arrow from the sample.

## Round 10 (2026-11-13): the judge's common points and a second inspection

Changed in the kit: a wire's tail sits flush on its source and only the head keeps a gap; a bow's head gets a little more air; hanging captions keep one baseline with or without inline math. Changed in the examples: `contrast` (the sample also feeds the classifier), `architecture` (the block box is white, so gray means normalisation only), `agent-loop` (episode card as tall as the block), `thumbnails` (stack and chips aligned to their boxes). A second independent inspection of every example on tiles found nothing visible at print size; of its zoom-level points four were fixed and one was wrong when measured (a title said to be off-centre). Not judged again.

Judged by a third fresh reader, same anchors (48.0 to 56.8):

| Example | Clarity / 36 | Beauty / 24 | Judged / 60 | Round 9 | Scores under 3 |
|---|---|---|---|---|---|
| `agent-loop` | 33.2 | 23.0 | 56.2 | 51.2 | C2 2, C3 2, A3 2 |
| `contrast` | 33.8 | 21.5 | 55.2 | 55.2 | E3 2, C3 2, K2 2, A3 2 |
| `pipeline` | 33.2 | 22.0 | 55.2 | 56.2 | M4 2, E3 2, C3 2, K3 2, A3 2 |
| `comparison` | 32.2 | 21.5 | 53.8 | 53.8 | M3 2, M4 2, E1 2, E3 2, A2 2, A3 2 |
| `concept` | 32.0 | 21.5 | 53.5 | 55.2 | M2 2, E3 2, C2 2, K1 2, A3 2 |
| `architecture` | 28.0 | 21.5 | 49.5 | 50.8 | M2 2, M3 2, M4 2, E1 2, E3 2, C2 2, C3 2, K1 2, A3 2 |

The mean is 53.9 against 53.7 in round 9: under the two points that the rubric sets for going on. Single figures moved by up to five points between two readers with no change that explains it, so one reader's total is good to about two or three points. The reader called two things visible at print size, both fixed in round 11: the headless bracket over the strip in `concept` (now a brace) and the episode card standing closer to the tools than the loop's own columns in `agent-loop` (now behind a rule, with even gaps). No content errors.

## Round 11 (2026-11-13): stop point

`kit-sheet.html` shows the parts added since round 7. The two print-size points of round 10 are fixed and looked at. A third independent inspection covered the three figures changed in this round (every tile): nothing visible at print size, and its three zoom-level points were fixed and looked at (the answer label's clearance in `agent-loop`; a caption position and a missing head on the kit sheet). By the rubric's own rule the automatic rounds stop here: what is left (identity, A3, at 2 in every example; `architecture` at about 50) needs the user's eye and a real figure, not another pass over toy examples.

## Round 12 (2026-11-13): the user's verdict

On preview v9 the user said: "이제 좋은거같은데?" The look and the eight examples are accepted as they stand.

## Open points

- Identity (A3 is 2 for every example except `concept`): the judge's advice is one device used in every figure (faded baseline, framed contribution, one coloured stroke) and an image motif taken from each figure's own content. A real figure drawn with the kit should be scored and added here.
- `kit-sheet.html` carries two `empty-space` warnings besides its two intended ones (`check_examples.py` exempts them); its layout has not been revisited.

# Inspection gate

The checks in `render.py` catch what can be measured. They pass figures in which a label lies across a line, an arrow shows only its head, or a box is one size smaller than its neighbours for no reason, unless a check for exactly that exists. The user found each of these in figures that had "0 errors, 0 warnings" (`user-decisions.md`). So no figure, and no change to the kit, is finished on the checks alone: a person or agent looks at every part of it, enlarged, against a fixed list, and leaves a receipt.

## When

- Every version of a figure before it is scored, shown or delivered.
- Every worked example after any change to `assets/kit/`: run `python3 scripts/check_examples.py`, which renders all of them and lists the ones whose picture changed. A kit change alters examples that nobody was working on.
- Again by a reader who did not draw the figure, before a figure goes into a paper or to the user as final. The author sees what they meant to draw. Where the host allows sub-agents, give one fresh reader the tiles and this file and ask only for defects; otherwise ask the user to look, and say that no second reader has.

## How

1. `render.py` writes `<stem>.preview.png`, zoomed crops in `<stem>.tiles/` that together cover the figure, and an unticked `<stem>.inspection.md`. A new render resets the receipt, because the last look no longer describes the file.
2. Fix every error and every warning. A warning stands only with a written reason in the receipt.
3. Open the preview at 100 %, then every tile, one by one. Do not skip a tile because that region did not change.
4. For each tile go through the checklist below and name what you see, not what you intended. Tick a line in the receipt only after looking, and write each defect under "Defects found".
5. Any defect means a fix, a new render and a new inspection of the whole figure. The receipt of the version that is delivered has every line ticked and lists the defects found on the way.
6. `score.py` prints NOT INSPECTED and records `inspected: false` while a line is unticked; such a score is not reported as a result.

## Checklist

| | Look for |
|---|---|
| text | text touching or crossing a line, a box edge, a picture, a panel rule or other text; text cut by a frame; a caption nearer to a neighbour than to its own object; raw `$` or unrendered math |
| arrows | an arrow that starts beside its source or stops short of its target; a bend with only the head after it; a leg shorter than the head; an arrow through an unrelated box or label; two arrows that merge or cross without meaning to; a direction the method does not have |
| levels | boxes at one level with different text size, height, corner or outline; arrows of one kind with different weight or head; one caption style in one place and another elsewhere |
| alignment | centres that should share an axis and miss it by a little; captions on different baselines; unequal gaps in one row; a symbol off-centre in its circle; a glyph glued to the text beside it |
| colour | a colour whose meaning the figure does not state; the baseline louder than the contribution; a faded part that reads as empty |
| white space | an empty band or corner; an object small in a large frame; an arrow longer than its label needs |
| content | an input that is missing; an arrow that implies the wrong dependency or order; a label on the wrong object; a component the example never uses |
| whole figure | at print size: is the reading order obvious, is the smallest text readable, does the eye land on the contribution |

When a look finds a class of defect that a check could have caught, add the check to `figure.js` in the same change and name it in [kit.md](kit.md). The gate stays: a check covers one class, the look covers the rest.

## Receipt

`<stem>.inspection.md`, beside the render: who inspected, a ticked line for the preview and for each tile, a ticked line for each checklist row with a few words on what was seen, and the defects found in this version (or "none"). It is the evidence that the look happened; keep it with the version.

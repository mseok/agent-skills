# QA and delivery

All commands run from the skill directory with absolute paths; `CHROME` may point at another Chromium build. Outputs go under the deck folder's `qa/`, never into the skill.

```sh
python3 scripts/check_deck.py /abs/deck/index.html --json /abs/deck/qa/check.json   # exit 1 on grid/citation/copy errors
scripts/shots.sh /abs/deck/index.html /abs/deck/qa/shots 0.5                        # one PNG per slide, final build state
scripts/shots.sh /abs/deck/index.html /abs/deck/qa/shots-full 1                     # full size for the inspection pass
sh scripts/contact_sheet.sh /abs/deck/qa/shots /abs/deck/qa/contact.png 5           # whole deck on one image
scripts/export_pdf.sh /abs/deck/index.html /abs/deck/qa/deck.pdf                    # one 1440×810 pt page per slide (?print mode)
```

Inspection pass (the part no script does): open every full-size PNG; look for text crossing a shape rim, labels touching each other, arrowheads detached from their line, uneven inner margins, a panel row with different heights, anything that reads as decoration. Fix in `index.html`, re-shoot the touched slides, look again. Then open two PDF pages at low resolution (`pdftoppm -r 48`) to confirm gradients, shadows and fonts survive printing (`pdffonts` lists Pretendard as embedded).

Publish (Mac mini): copy the deck into a clean bundle with `deck.pdf` beside `index.html`, run the host's `publish.py` with `--entry index.html --slug <talk>-<date>[-vN]`, then verify the served state — `curl` the local URL and `cmp` the bytes with the source `index.html`; request every asset the page needs (css, js, fonts, each figure, `deck.pdf`) and expect 200 with the right sizes; request the HTTPS URL with `--resolve` to the Tailscale address and expect 200 with `ssl_verify=0`. Give the user the HTTPS link first and the local link second. Previous slugs stay online; name the current one.

Report format: done/blocked per requested slide; what was verified (check_deck result, PNGs inspected, PDF pages and fonts, served bytes identical, assets 200, HTTPS verified); what was not (keyboard interactions such as the presenter window, other browsers); visible word count per slide from `check_deck.py` when the user is watching text density; and any scientific content you added beyond the approved storyline, as a question, never silently.

Research-talk gates still apply before delivery: the fact-check list (every number, comparison, citation and claim mapped to its source) and the Korean copy rule; `check_deck.py` covers the markers and endings mechanically, not the truth of the claims.

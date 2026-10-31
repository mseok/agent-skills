---
name: html-research-deck
description: Build or revise a research talk as a static HTML deck in the user's approved research theme (white figure panels on a warm stage, Pretendard, textbook-style SVG mechanism scenes, one closing line per slide), with PNG/PDF export and preview publishing. Use when the user asks for slides in HTML ("HTML 덱", "HTML로", "그 방식으로 만들어", "웹 슬라이드") or to re-render an existing deck in this style; the storyline, its approval and the fact-check gate still come from research-talk. Not for PPTX production (research-talk) or standalone publication figures (nature-figure).
---

# HTML research deck

This skill owns the production step only: the engine, the visual system and the QA of an HTML deck. The argument comes first and is governed by `research-talk`: storyline table with one message per slide, slide language asked explicitly, user approval recorded, `storyline.json`, citation mapping and the fact-check gate before delivery. Read `research-talk/references/workflow.md` and `storyline-format.md` when a talk starts; when the user hands over an already approved flow, build from it without re-asking.

## Workflow

1. **Scaffold** in the project's artifact location (`inbox/<talk>-deck/` or the project's slide folder), never inside this skill:
   `python3 scripts/new_deck.py /abs/<talk>-deck --title "…" --lang ko --slides title,figure,figure-render,closing`
   This copies the engine (`css/`, `js/`, `vendor/` with Pretendard and KaTeX) and writes `index.html` with the shape sprite inlined and the chosen fragments from `assets/deck/templates/` in order. Keep one slide per `<section class="slide">`; keep every sentence of the source in `<aside class="notes">`.
2. **Taste benchmark before the rest.** Build two or three representative slides first, including one mechanism scene, run the QA below, publish, and stop for the user's verdict. Only after the verdict build the remaining slides to that standard. This is how the reference deck was accepted (user decisions below).
3. **Per slide**, read `references/design-system.md` once per thread and then: write the one message; decide what the single picture must show (actors, states, the change, in 2–3 cells); choose a layout fragment; draw the scene with the sprite shapes (`<use href="#shBlob">` etc.) and the scene grammar; put the source sentences and figure provenance in the notes. Structural evidence (PDB renders) follows `research-talk/references/molecular-visualization.md`; a render sits in its own panel with leader labels, never as a decorative background.
4. **Render loop is yours, not the user's.** After each slide: `scripts/check_layout.py` (measured boxes: text outside its panel, label collisions, rim crossings, empty bands) and `scripts/shots.sh`, open the full-resolution PNG, fix overlaps and clipped labels, render again. A slide is "drawn" only after both pass: zero layout errors, no underfilled or unbalanced panel, and one full-size inspection with no finding. The first draft already follows the rules; the loop catches geometry, not taste.
5. **QA and delivery** per `references/qa.md`: `scripts/check_deck.py` (grid, closing line, citation markers, Korean endings, text sizes), `scripts/check_layout.py` (rendered measurement), all-slide PNGs plus the contact sheet, `scripts/export_pdf.sh`, publish through the host's HTML preview workflow (host-context), verify served bytes, assets and the PDF, then report what was verified and what was not. Deliver the HTTPS link first, the local link, the PDF path and the folder on the host where it exists.
6. **Revisions** edit the slide in place; re-run `check_deck.py` and the shots for the touched slides; never regenerate the deck from an older spec over user edits. The publisher never overwrites a slug: publish `-v2`, `-v3`, … and say which is current.

## Design system (summary; details in `references/design-system.md`)

- Stage 1920×1080, margins 110; title block ends at y 152; panels from y 176 to 898; every gutter 24 px; panel padding 20 px; the closing line is a white panel at y 922–1000; cite at the bottom, 17 px.
- Every key figure sits on a white panel; panels in one row share a height; the warm stage shows only in the gutters. No coloured bars, blurred washes, gradient text, letter-spaced labels, icons or animation.
- Text budget: title (noun phrase), labels on the drawing, one closing line; sentences go to the notes. Figure text ≥ 19 px, names 24–30 px.
- Scene grammar: organic protein blobs with soft shading, capsule = small molecule, beads = ubiquitin, barrel = proteasome, cell with nucleus and DNA; the same actor keeps its shape across states; dashed outline = absent, red × = blocked, red dot = mutation; grays for machinery, one blue for the drug or path of interest, amber for the substrate, red only for a key phrase. Mechanism slides show the biological consequence (e.g. transcription → growth) as a cell-level panel, not only the molecular steps.
- Korean copy on slides is noun phrases (`research-talk/references/korean-slide-copy.md`); citations `[n]` at the point of use and resolved in the cite line; every number and claim traces to a source in the notes.

## Hosts

- Rendering needs Chrome (`CHROME` env; default `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`). No npm, no Python packages.
- Publishing: the Mac mini `html-preview` publisher (path and URL form in `~/.codex/host-context.md`) prints the MacBook HTTPS link first, then the Mac mini local link; verify both routes as in `references/qa.md`. On a host without a publisher, deliver the deck folder and the PDF and say so.
- The engine copy in `assets/deck/` is canonical; the inbox starter `html-deck-starter-20261030` on the Mac mini holds the development history and the example decks.

## User decisions (verbatim, 2026-10-30)

- Reference artifact accepted as the taste standard: the three-slide sample `taste-sample-20261030-v4` (Mac mini `inbox/html-deck-conversion-20261030/out/taste-sample/`), "와 디자인은 이제 너무 좋은데?". Compare new work against it.
- "motion graphics 자체는 중요한게 아님." → no canvas animation in research decks; scenes are static SVG.
- "디자인에 내생각에 글이 너무 많은게 1차적으로 별로고, 매커니즘 같은걸 그릴 때 너무 그림이 별로임" → text budget and hand-drawn scenes, not auto-generated node boxes.
- "이거 옆에 quote 처럼 진한색 있는거 되게 ai design 같은데 이런거 좀 줄일 수 있으면 좋을듯?" → no coloured quote bars or decorative accents.
- "이거 화살표가 끝부분이 너무 부자연스러운데?" → arrows are single smooth curves with the head on the tangent (sprite markers).
- "좀 더 교과서에 나올법한 스타일로 예쁘게 그릴 수는 없나?" and "골수종 세포 성장 억제라는 얘기를 잘 설명하는 것 같지 않아." → textbook scene grammar, and the figure explains the consequence the message claims.
- "글씨가 이런것도 전반적으로 좀 더 크면 좋을듯?" → figure text ≥ 19 px.
- "핵심 그림들은 다 흰 배경 위에 놓여 있으면 좋겠고, 그리고 한 문장 설명 같은것도 박스가 없으니까 뭔가 허전한 느낌은 드는거같네. 슬라이드마다 여백의 정도가 다를 수는 있는데, 한 슬라이드 내에서는 일관되어야 하고, 각 부분들 사이의 여백이 너무 넓어서도, 너무 얇아서도 안돼." → white panels, white closing-line panel, one fixed gutter per slide (`check_deck.py` enforces the grid).
- 2026-10-31, on the first real deck (CausalGame, 20 slides): "숫자 글자 튀어나간것들 QA 한 번 거쳐서 최종화하는게 좋을듯?" / "15페이지 같은데서도 너무 작은 글씨로 디테일하게 적는게 의미가 없는거같음" / "패널들 밑 부분의 여백이 너무 크게 남아있네 지금은?" → `check_layout.py` is mandatory (it found four overflows and 100–170 px empty bands the grid check passed); scene text is at least 20 px (one dense 30-row chart may use 19 px) and a detail line that only fits at 17–18 px is cut or merged, not shrunk; a panel's content fills it to within the measured gap rule (top ≈ 27 px with the lane header, bottom within 24 px of that, never over 80 px).
- 2026-10-31, second round on the same deck: "여기도 선이 겹쳐있네" (a dashed reference line through value labels) / "이런 부분도 아래 여백이 생기는지 QA 단계에서 확인하고 고쳐야할거같은데?" (text sitting high inside a box) / "여기도 뭔가 겹친게 일부러 그렇게 되었나?" (a translucent range band over bars and labels — intended, still rejected) / "전반적으로도 글이좀많은듯" / "이런것도 너무 여백이 쓸데없이 많은데 좀 더 나은 배열이있을거같고, 전반적으로 글씨 크기 이 파트들 조금만 더키우면좋을듯" / "최적구간 적은거 볼드체가 기본 폰트사이즈가 되면 좋을듯. 그것보다 작은건 레퍼런스정도만 넣는게 좋을듯?" → `check_layout.py` also reports a line segment through a glyph box and text that is off-centre inside a rect; no range bands over data (put the range beside the bars on the axis, or as value columns); the 24 px bold claim is the base size — body and figure labels 22–24 px, emphasis 26–28, lane headers 24, and anything smaller only for reference-style notes (muted citations, "값은 Fig. 10") or a 30-row chart; at most two or three lines of commentary per panel, the rest goes to speaker notes; a DAG spreads across its panel's width.
- "이건 지금 이번에 한거처럼 규칙을 정해두면 요청하는거 그대로 만들 수 있는거아닌가?" and "좋은거같애. 1 2b 가 좋을듯?" → the rules live here so a request yields the deck directly; the taste benchmark of 2–3 slides stays as the one user checkpoint before the full build.

## Maintenance

A new shape that will recur goes into `assets/deck/sprite-research.svg`; an accepted style correction becomes a `check_deck.py` rule or a line in `references/qa.md` in the same turn; an entry in User decisions is never dropped or narrowed without asking. Validate with the system skill-creator's `quick_validate.py` (`uv run --with pyyaml`).

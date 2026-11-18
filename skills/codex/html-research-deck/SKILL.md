---
name: html-research-deck
description: Develop a research presentation storyline with the user and, after they approve the flow, build it as a static HTML deck in the approved research theme (figures directly on a warm stage, white only for cards that hold one thing, context-dependent academic terms in English, Pretendard, textbook-style SVG mechanism scenes, one closing line per slide) or, when asked for it, in the Folio layout (rail, spine, plate), with PNG/PDF export, preview publishing and a claim-by-claim fact-check gate before delivery. Use whenever the user asks for 발표자료, 슬라이드, a deck or a presentation from existing results or records, including "HTML 덱", "HTML로", "그 방식으로 만들어", "웹 슬라이드", informal decks and edits or re-renders of an existing deck, on any host or harness. Editable PPTX and PDF in the dissertation style are built only when the user asks for PPTX, PowerPoint or Keynote. Not for manuscript rewriting, automatic experiment reporting or standalone publication figures (nature-figure).
---

# Research deck: storyline first, then an HTML deck

Work with the researcher on the argument before making slides. Read the relevant experiment context yourself; the user should not have to reformat notes into slide-ready material. This skill holds both halves of a talk: the storyline with its approval and gates, and the production of the deck (the former `research-talk` skill was merged into this one on 2026-11-12). The product is a static HTML deck; an editable PPTX is a second route, taken only on request. The HTML deck has two layouts with the same fonts: the research theme (default) and Folio, used when the user asks for it by name (`references/folio.md`).

## Routes

| the user asks for | do |
|---|---|
| a new talk (발표자료, 슬라이드, a deck, "HTML 덱") | Storyline → approval → Build the HTML deck |
| a deck from an already approved flow or brief | build from it without re-asking (Brief-driven runs) |
| "same as before" (이전과 같이) | the earlier approved flow from the presentation note; read it and proceed unless the user changes it |
| the Folio layout ("Folio", "Folio 양식", "난과 판 양식") | the same storyline, gates and QA; grid, kit and checks from `references/folio.md` |
| a change to an existing deck | Revisions |
| PPTX, PowerPoint or Keynote output, or an edit of an existing PPTX | the storyline and gates here, production by `references/pptx-production.md` |

The storyline, the approval step and the gates apply in every harness and on every host (Codex desktop, Claude Code, Antigravity, the lab server); only the production step differs. If a tool the route needs is unreachable in the current harness, say so once and build with what is reachable; never skip the approval step because a tool is missing.

## Storyline (develop or resume)

1. Read `references/workflow.md`. Use only `obsidian_main` (in Antigravity: `migrated-settings_obsidian_main`) for Vault access. Search for an existing presentation preparation note before creating one. Read its current SHA, approved flow, unresolved issues, evidence links and latest edited deck location.
2. Take the user's topic and overall context as the starting point. Recover question reports with `investigation_context`, then read relevant experiments and linked evidence. Narrow retrieval to the presentation question. Do not infer that the newest experiment replaces all earlier evidence.
3. Establish audience, purpose, time and slide language. The product is an HTML deck unless the user asks for PPTX, PowerPoint or Keynote; do not ask about the format. For each new talk, explicitly ask whether slides should be Korean or English unless the user has already specified the language for that talk; never infer it from the chat language or a previous talk. On resume, honor the user's recorded choice without asking again. Record that choice and its user reference in the brief/preparation note before approval. Ask concise questions for other consequential gaps. Discuss motivation, main claim, comparisons, explanatory background and transitions. Keep observation, hypothesis, interpretation and proposal distinct.
4. Show a concrete slide-by-slide storyline: stable ID, role, title, message, evidence, visual plan, closing line (the one takeaway sentence that ends the slide and hands off to the next) and transition; the first slide names the target and objective. Title and closing-line register follow `references/message-style.md` (title = the slide's point as a noun phrase, closing line = one lesson or one number, jargon glossed at first use, no section-label prefixes such as "결과 1:"; user feedback 2026-10-31). Discuss and revise with the user. Run a content-budget check on that table before asking for approval: a slide that must carry more than one claim, more than three numbers beside its figure, or two unrelated topics is flagged with a proposed split or a supplementary slide, and the user decides. Do not author the deck until the user accepts that flow. A topic exploration request or timeout is not approval. If this exact flow was already approved, continue without asking again. A request "same as before" (이전과 같이) carries the earlier approved flow from the presentation note; read it and proceed unless the user changes it.
5. Retain the approved flow, date and actual user task/turn reference in the presentation note. Read before `knowledge_revise`, use the current SHA and preserve prior context. Create a dedicated presentation note with `record_create` when none exists. Ordinary preparation-note writes are authorized; unrelated human research notes are not edit targets.

Example: “Project-A의 최근 실험 기록을 바탕으로 20분 연구 발표 흐름부터 같이 정하자. 핵심은 prior가 언제 도움이 되는지야.” After discussion: “이 흐름으로 확정하자. 슬라이드를 만들어 줘.”

## Brief-driven runs

When no Obsidian access or interactive approval is available (an automated build, a failed `obsidian_main`), an approved content brief stands in for the approval: record that in `storyline.json` (`approval.user_reference` = the brief) and skip Vault steps; never invent an approval timestamp beyond the brief's own date. Use `approval.basis = "brief"` when the brief has no date, write each slide's `visual` plan and `closing` line yourself (a brief supplies neither), and leave Obsidian paths out of the notes (use the brief's host-qualified source paths). PPTX-only details of such a run are in `references/pptx-production.md`.

## Build the HTML deck (after approval)

Materialize the approved flow as `storyline.json` (`references/storyline-format.md`; an HTML deck's storyline also carries `closing`, `glossary` and `owner`) and run `scripts/check_storyline.py` on that approved snapshot before the first build; separately verify that its approval reference is a real user decision. A goal loop later re-snapshots titles and closing lines into `work/storyline.json` while `work/storyline-v1.json` keeps the approved ids, roles and evidence, so the checker is not rerun on a loop's snapshot. Then:

1. **Scaffold** in the project's artifact location (`inbox/<talk>-deck/` or the project's slide folder), never inside this skill:
   `python3 scripts/new_deck.py /abs/<talk>-deck --title "…" --lang ko --slides title,figure,figure-render,closing`
   This copies the engine (`css/`, `js/`, `vendor/` with Pretendard and KaTeX) and writes `index.html` with the shape sprite inlined and the chosen fragments from `assets/deck/templates/` in order. For the Folio layout add `--theme folio` (`cover,opener,plate,spread`) and draw with `scripts/folio_kit.py` (`references/folio.md`). Keep one slide per `<section class="slide">`; keep every sentence of the source in `<aside class="notes">`.
2. **Taste benchmark before the rest.** Build two or three representative slides first, including one mechanism scene, run the QA below, publish, and stop for the user's verdict. Only after the verdict build the remaining slides to that standard. A handed-over deck that already passed this checkpoint, a headless builder run and a revision skip it.
3. **Model-specific kit guidance.** GPT models (Astra, Sol, Terra and so on) must read `references/builder-notes-gpt.md` before drawing: copy worked slides from `scripts/kit_gallery.py`, draw with `scripts/scene_kit.py`, and measure distance to accepted decks with `scripts/style_gap.py`. Gemini builders in Antigravity may also use `scripts/scene_kit.py` and `scripts/style_gap.py`. Claude models skip `builder-notes-gpt.md`.
4. **Per slide**, read `references/design-system.md` once per thread (mandatory: holds exact pixel coordinates, type scale, colour roles, KaTeX formula helpers, `density.py` clouds/bridges, and 2026-11-12 additions), then write the one message, choose a layout fragment, draw the scene with sprite shapes (`<use href="#shBlob">` etc.) and scene grammar, and place source sentences and figure provenance in `<aside class="notes">`. Structural evidence (PDB/molecule renders) follows `references/molecular-visualization.md` in its own panel with leader labels, never as a decorative background.
5. **Render loop is yours, not the user's.** After each slide: run `scripts/check_layout.py` and `scripts/shots.sh`, inspect the full-resolution PNG, fix overlaps and clipped labels, and re-render until zero layout errors, balanced/filled panels, and zero visual findings hold.
6. **QA and delivery** per `references/qa.md`: run `scripts/check_deck.py`, `scripts/check_layout.py`, `scripts/banned_copy_lint.py` (zero errors), `scripts/regression_run.py` (zero FAIL; inspect MANUAL items), all-slide PNGs plus `scripts/contact_sheet.sh`, and `scripts/export_pdf.sh` + `scripts/pdf_compare.py` (no flagged page). Complete the fact-check and completion gates below before publishing through the host's HTML preview workflow (`~/.codex/host-context.md`), verifying served bytes, assets and PDF. Deliver the HTTPS link first, the local link, the PDF path and the host folder.
7. **Revisions** edit the slide in place and re-run `check_deck.py` and shots for touched slides; never regenerate over user edits. Publish a new slug (`-v2`, `-v3`, …) rather than overwriting one, and state which is current.
8. **Obsidian archive** follows `references/workflow.md`: save the PDF and Markdown script in `Slides/` with date/title names (no version/hash suffix), preserve existing script length and `<aside class="notes">` order without expansion, and link them through the presentation note.

## Design system (rules summary; full coordinates and APIs in `references/design-system.md`)

- **Stage first (2026-11-02):** 1920×1080 warm stage with transparent figure panels, fixed 24 px gutters, equal heights within a row, and a white closing-line card aligned with title/panels/cite at `x = 130` (exact coordinates and type scale in `references/design-system.md`: 24 px base, 22–24 px labels, ≥ 19 px muted/30-row chart floor). White is reserved for single-item cards (`.fx.box`, `.panel.card`, closing line). No canvas animation, coloured quote bars, blurred washes, gradient text, letter-spaced labels, decorative icons or range bands over bars.
- **Language, formulas and scenes:** Context-dependent academic terms stay in English in Latin script on titles and labels (`references/message-style.md` rule 4); Korean slide copy uses noun phrases (`references/korean-slide-copy.md`). Formulas and math labels use KaTeX `.fx` blocks (`references/design-system.md`, Formulas — one relation per line, avoid double-escaping `<`/`>` into `tex-unrendered`). Textbook SVG scenes keep each actor's shape/colour across states and end mechanism slides in the cell-level biological consequence; 2-D distributions/paths use `scripts/density.py` (`cloud()`, `bridge()`), never hand-drawn blobs or dashed rings. Citations `[n]` appear at point of use and resolve in the cite line.
- **Taste standard & slots:** Compare new work against `taste-sample-20261030-v4` (`inbox/html-deck-conversion-20261030/out/taste-sample/`). On the closing slide's user-owned question panel (`owner: user` in `storyline.json`), generate only a content header and 2–3 questions (never `"발표자 생각"`), untouched by loop builders. Cover figures use `kit.hero_bridge` on a transparent panel, with no cover QR code unless requested.
- **2026-11-12 v18a additions** (`references/design-system.md`, Additions): text-only kicker section tracker (`init(deck, sections=…)`), verified paper equation numbers (`fx(..., eq=)`), closing-slide `tile()` summary cards, `B1+` backup slides (`slide(..., backup=True)`) with three-rule `table()`, 2–3 step builds (`step()`, `at()`), and presenter keys `L` / `Z` / `T`.

## Gates before delivery (both routes)

- **Fact-check gate:** Extract every number, named comparison, citation and claim from the slides into a checklist mapped to its source (paper section, figure, record, data file), marking unresolved items. Any unresolved item blocks readiness and must be stated on the first line of the delivery; format checks never count as content verification.
- **Completion list:** Report each requested slide or change as done or blocked (never as a "follow-up suggestion"). A rebuild request ("skill 업데이트해서 다시 만들어") requires a fresh build from the storyline, not a patch of the old deck; report any figure that could not be fetched.
- **Evidence & native objects:** Use existing evidence only (no new experiments unless asked; never manufacture results or reuse example-deck numbers). No pasted images of text/charts, no generated-image biology/molecules/data, no AI-template headers or callout boxes; PPTX uses editable native objects only.
- **Definitions & citations:** Define every metric, comparison set and ambiguous abbreviation on first appearance (`scripts/pptx/check_slide_conventions.py` on PPTX; `references/message-style.md` + storyline `glossary` on HTML). Map external claims, named compounds and reused panels to `[1]`-numbered citations at point of use (`references/citations.md`); this study's own analyses carry no citation label.
- **Feedback ledger & visual proof:** Record slide-level user corrections in the presentation note and `storyline.json`, carrying the full ledger into fresh-context briefs, and turn recurring prose rules into script checks. Prove visual claims on rendered PDF/PNG (not DOM/XML); follow application slide numbers rather than PDF page numbers; for existing PPTX edits, pull in the deck's source template and style reference first, keeping one meaning per non-gray colour.
- **Fan-out:** Give each subagent/worker one output path and a required artifact list. In Codex, poll with the agent wait tool (never `sleep`), ask for the blocker after two empty waits, and create Browser tasks from the GUI; in Claude (`Agent`) and Antigravity (`invoke_subagent`, `swarm`, `run_workflow`), workers wake reactively without polling.

## Verification mode

Use full visual review by default (`references/qa.md`; PPTX: `references/pptx-qa.md`). Only when the user requests a rushed draft or an agreed deadline requires it, skip full rendering/visual QA, preserve source fidelity, label the output a draft with visual verification skipped, and list the checks that actually ran.

## Revisions (never lose user edits)

Always start from the latest user-edited deck (verifying its hash), never regenerating the whole deck from an older storyline or builder. Preserve untouched slides, notes and user layout changes; discuss substantive agent-proposed message/order changes while applying fit repairs directly. Update the same presentation note with output paths, version, slide mapping and open needs (if Vault recording fails, keep local work and bridge outbox, report pending status, and never write Vault files directly). Archive under `Slides/` per Build step 8 and `references/workflow.md`, and publish HTML revisions under a new slug.

## Copy and scores

- User checkpoint rule: rules live in this skill so a request yields the deck directly, with the 2–3 slide taste benchmark as the single checkpoint before full build.
- Read `references/message-style.md` before writing visible copy (`rubric-message.md` M1–M10): width-weighted limits count Latin letters/digits as `0.6` Hangul glyph (title ≤ 34, kicker section ≤ 14 / subtopic ≤ 24, closing line 12–48); visible copy must contain none of `저자`, `발표자`, `모식`, `번역` (put attribution/caveats in the cite line, M10); enforce one `use` form and zero `avoid` forms per `glossary` entry (M4b).
- Goal pass requires **both** message ≥ 90 and design ≥ 90 from fresh independent judges; a design pass near 90 on one draw requires two replicate draws before reporting. On `owner: user` slides flagged by the message judge, the caller fixes factual wording, logs before/after, and re-runs `score_message.py` and `check_layout.py`.
- Read `references/loops-and-builders.md` before running any judged loop (`goal_loop.py`, `goal_chain.py`, `iterate_deck.py`, `iterate_message.py`), cross-CLI runner (`agent_cli.py`), or equivalence test (`equiv_run.py`, ±3 on design and message; calibrated on the research theme, not Folio): keep the judge fixed (Opus 5.5 max), start loops with `--judges 3`, change rules/checks instead of stacking prescriptions, budget loop iterations for GPT builders, and use Sonnet 5.5 as the Claude baseline when the safety classifier stops Opus 5.5.

## Hosts

- Rendering needs Chrome or Chromium (`CHROME` env, macOS `/Applications/Google Chrome.app/...`, or `google-chrome` / `chromium` on `PATH` on Linux). No npm or external Python packages are needed on the HTML route.
- Publishing uses Mac mini `html-preview` (`~/.codex/host-context.md`), printing the HTTPS link first and local link second (`references/qa.md`); on hosts without a publisher, deliver the deck folder and PDF and say so.
- `assets/deck/` is the canonical engine (`html-deck-starter-20261030` holds earlier history); PPTX host details live in `references/pptx-production.md`.

## Fresh-context rebuild and skill evaluation

When explicitly asked to rebuild from a fresh context, start from the approved content brief, raw evidence and clean template rather than a prior deck or builder, preserving old outputs. For fresh-context skill evaluations, follow `references/fresh-context-evaluation.md` and assess the artifact before editing the skill.

## User decisions

The dated decisions behind these rules, in the user's own words, are in [references/user-decisions.md](references/user-decisions.md). Read it before editing this skill or when a rule's origin or scope is in doubt; record a new decision there and state the resulting rule in plain words in this file.

## Maintenance

Recurring shapes go into `assets/deck/sprite-research.svg`; accepted style corrections become a `check_deck.py` / `scripts/pptx/` rule or `references/qa.md` / `pptx-qa.md` line in the same turn; every user-reported visual defect becomes a case in `regression/manifest.json` (`regression/README.md`); never drop or narrow a `user-decisions.md` entry without asking. Fresh-context briefs carry the approved storyline and full feedback ledger, never a summary. Validate with `quick_validate.py` (`uv run --with pyyaml`); after PPTX kit edits run `scripts/pptx/test_*.py` and `scripts/test_storyline_brief.py`; after checker/theme edits run `scripts/regression_run.py`; after `scene_kit.py`, `folio_kit.py`, stylesheet or checker edits rebuild `kit_gallery.py` / `folio_gallery.py` in scratch, pass `check_deck.py` and `check_layout.py`, and refresh changed renders in `assets/kit-gallery/` or `assets/folio-gallery/`.

# Regression set

Every visual defect the user reports joins this set as one case, in the turn the defect is fixed. `scripts/regression_run.py` replays all cases: `python3 scripts/regression_run.py` (exit 1 on FAIL; `--list`, `--only ID,ID`, `--no-render` for a run without Chrome).

## Manifest (`manifest.json`)

`{"version": 1, "cases": [ … ]}`, one object per case:

| key | meaning |
| --- | --- |
| `id` | short kebab-case name, unique |
| `date` | the day the user reported it (YYYY-MM-DD) |
| `source` | file inside this skill that records the defect, usually `references/user-decisions.md` |
| `quote` | text copied verbatim from `source`; the runner fails the case when it is not found there, so a case exists only for a recorded defect |
| `defect` | one line, plain words |
| `tool` | `check_layout`, `check_deck`, `banned_copy_lint` or `manual` |
| `expect` | what the tool must report on `bad`: a `check_layout` finding kind, a `banned_copy_lint` rule, or a substring of a `check_deck` message |
| `bad`, `fixed` | fixture paths relative to this folder; `fixed` is optional and must not report `expect` |
| `check` | `manual` only: one sentence for the inspection pass |

## Fixtures

A fixture is a file of `<section class="slide">` fragments with neutral placeholder text, never copy from a real deck or paper. The runner puts it into a throw-away deck built from `assets/deck/templates/index.template.html` that links this skill's `css/`, `js/` and `vendor/`. Keep it to the smallest slide that shows the defect; the `bad` and `fixed` files should differ only in what the user complained about. A copy-lint fixture needs a cover slide first, because the cover is not checked.

## Adding a case

1. Record the defect and the user's words in `references/user-decisions.md` (existing rule).
2. If a checker can see it, write `bad` and `fixed`, add the case, run `--only <id>`: `bad` must give PASS only because the checker fires.
3. If no checker sees it, add the case with `tool: manual` and a `check` sentence; the runner prints it as MANUAL on every run. Teaching a checker the pattern later turns it into a measured case.
4. If the checker does not fire on a defect it should catch, fix the checker first; never weaken `expect` to make a case pass.

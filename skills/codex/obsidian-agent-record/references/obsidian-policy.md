# Obsidian vault policy

This file is the single source of the rules for the user's Obsidian vault. Skills
(`research-workflow`, `experiment-ledger`, `obsidian-agent-record`,
`obsidian-user-note`, `research-talk`, `html-research-deck`,
`single-paper-review`) carry only their procedures and point here. The vault's
own `AGENTS.md` is a short map that points here. The gateway enforces the
permissions in section 2. Change a rule here, not in a copy; read this file
once per task and reuse it.

## 1. The vault and the only way in

- The canonical vault is `/Volumes/ExternalSSD/Obsidian/kepano-obsidian-main`
  on the Mac mini. Devices use Obsidian Sync. The old iCloud copy is not a
  vault; never read or edit it.
- Every agent read and write goes through the host-local `obsidian_main` MCP
  bridge to the Mac mini gateway, the single writer. Never read, write, move or
  delete vault files directly, and never run Git in the vault: Git is a Mac mini
  backup job that only commits and pushes. `un note`, `un push`,
  `codex_note_commit`, `obsidian_branch_publish.py` and remote vault checkouts
  are retired.
- The authenticated token fixes the host (`local` is the Mac mini; `messi` and
  `grok-bot` are remote; gpu22 was retired on 2026-11-06). Never pass or infer a host.

## 2. Permissions (enforced by the gateway)

| Host | Read | Write |
|---|---|---|
| Mac mini (`local`) | the whole vault except hidden folders (`.obsidian`, `.git`, `.trash`) | `knowledge_revise`: revise, create, move, delete and undelete any `.md`, `.base` or `.canvas` note outside hidden folders; plus every remote right |
| Remote hosts | `People/`, `People.md`, `Slides/`, `Concepts/`, `Writing/`, `Notes/`, `Inbox/Agents/`, `AGENTS.md`, `HOME.md` | `record_create` and `record_append` in `Inbox/Agents/<host>/`, `research_capture` on shared question reports, `note_draft_create`, `knowledge_revise` of their own records and of question reports, `attachment_upload` |

- Every revision checks the expected SHA and keeps the exact prior content;
  `history`, `read_revision` and `restore` recover it. A `revision_conflict`
  means someone changed the note: read it again and redo only that note, never
  force.
- Revision history is kept for 30 days after a note's last revision: a note
  untouched longer loses its prior versions (no `restore`) and is tracked again
  from its next revision. The gateway prunes at start and daily; completed write
  plans keep only their routing fields.
- `delete` keeps the content, the gateway record rows and a copy outside the
  vault; `undelete` with the `deletion_id` brings the note back. Pass
  `replacement` when another note takes over its content, so question-report
  history links follow it. Question reports are never deleted.
- `move` keeps identity, history and question-report registration; it does
  not rewrite inbound links, so fix them in the same change.
- `created` is never changed once set; a note without one may gain it.
  `record_id`, `operation_id`, `host`, `agent` and `writer` are set by the
  gateway and never edited by hand.
- A change to more than about twenty notes is shown first with its count,
  exceptions and examples and applied only after the user approves, as one
  script that writes a restore list. Each live edit of a note the user is
  writing in still needs the user's request.
- Attachments travel as raw bytes through `attachment_upload` from a small
  approved file, never as base64 or MCP arguments; embed a figure once.

## 3. Folders

| Place | Holds | Written by |
|---|---|---|
| root | `HOME.md`, `AGENTS.md`, `People.md` and one project overview note per project, named after the project (`kind/project-hub`; restored on 2026-11-10 at the user's request after the older hubs were deleted on 2026-11-06). An overview note holds only Bases views that list the project's notes by `project` and `project/*` | the user; agents on request, and the overview-note rule below |
| `Writing/` | the user's own essays, reflections, meeting records and personal synthesis | `note_draft_create` on explicit request |
| `Concepts/` | reusable definitions, mechanisms and background explanations | `knowledge_revise(create)` on explicit request |
| `People/` | one note per person (`kind/person`), indexed by `People.md` | on explicit request |
| `Study/` | study notes for a book or course: one subfolder per source holding a hub note named after the source and one note per chapter or section (`kind/study`) | on explicit request, from the Study template; no `writer` or `reviewed` |
| `Slides/` | `YYYY-MM-DD Title.pdf` and its spoken script `YYYY-MM-DD Title.md` | `research-talk` on request |
| `Inbox/Agents/<host>/` | agent records and question reports; later agents search and fetch them, the user does not read every one | the gateway chooses the path |
| `Notes/` | the user's older research notes | the user; agents revise only on request |
| `Sources/` | papers, clippings and other external material | the user |
| `Archive/` | frozen history and imported old records | nobody unless the user asks |
| `Attachments/` | figures and files registered by the gateway | `attachment_upload` |
| `Templates/` | one template per note type and `Bases/Research.base` (section 5) | agents on request |
| `Excalidraw/` | drawings | the user |

Folders separate purpose and lifecycle, never topic; topics live in tags and
links. A new top-level folder is created only when the user asks for it. Large data, checkpoints, logs, environments and caches never go
into the vault. Do not create an empty note just to resolve a link.

When a note is written with a `project` value that has no overview note in the
root, create `<project>.md` from `Templates/Project Template.md` in the same
task (replace `{{title}}` with the project name and `{{date}}` with today) and
add its link to the project overview line in `HOME.md` (user decision
2026-11-10). Remote hosts cannot create root notes: they say in the reply that
the overview note is missing instead.

## 4. Which note, if any

| Situation | What to do |
|---|---|
| meaningful hypothesis, implementation, result interpretation, adopted decision or change of direction in research | `research-workflow`: update the question report |
| separately comparable terminal result | `experiment-ledger`: one evidence record per run, batch, sweep or screening round |
| other reusable agent outcome or an explicitly requested revision of an agent record | `obsidian-agent-record`: `record_create` or an authorized `knowledge_revise` of the existing record |
| the user explicitly asks for a concept reference, meeting note or personal prose to read and edit | `obsidian-user-note`: `Concepts/` for reusable explanation, `Writing/` for the user's own prose, both linked for a mixed request; an explicit destination wins |
| the user asks for study material on a book or course | `Study/<source>/`: a hub note plus one note per chapter or section, written from the Study template |
| a talk | `research-talk`: its preparation note and `Slides/` |
| ordinary chat explanation, routine checks, polling, tooling, layout-only edits, prose draft versions, administrative and personal tasks | no note |

Ordinary research milestones need no new permission. When the turn-end check
asks about a turn without a milestone, answer with `research_disposition`
(`no-material-change`, short reason) and say nothing about it in the reply.

## 5. Metadata

- One template per note type lives in `Templates/`, kepano style: `Person`,
  `Writing`, `Meeting`, `Concept`, `Experiment`, `Paper`, `Slides`, `Study`, `Project` and
  `Weekly Note` (Periodic Notes is off; weekly notes are not created); `Single
  Paper Review Template` belongs to its skill and uses the Paper fields with
  `kind/paper-review`. The
  unique-note command creates `Writing/YYYY-MM-DD HHmm` from the Writing
  template. `Templates/Bases/` keeps only `Research.base`. A new note copies its template's fields in that order and fills
  what it knows; an unknown field is left out rather than left empty. The
  gateway writes agent records and Writing notes in the same order.
- Field order everywhere: `title`, `created`, `updated`, `date`,
  `presentation_date`, `writer`, `reviewed`, `tags`, `project`, `branch`, `aliases`, then
  the type's own fields (person: `name` ... `education`; meeting: `people`,
  `org`, `loc`; paper: `author` ... `keywords`; study: `book`, `chapter`, `part`,
  `pages`, `prev`, `next` (a hub: `author`, `publisher`, `doi`); research: `investigation_id`,
  `investigation_report`, `record_role`, `evidence_key`, the four experiment
  fields, `superseded_by`), `related`, any other field, and last the gateway's
  `record_id`, `operation_id`, `host`, `agent`.
- New notes have `title`, `created` (`YYYY-MM-DD`) and `tags`; an older note
  without `title` uses its file name. `created` never changes once set.
- Empty fields are removed, not kept as placeholders. `topics` (kepano-style
  list) is kept where it has values; `related` lists wikilinks.
- `tags`: one or more `kind/*`, one `project/*` when the note belongs to a
  project, and only useful `topic/*`. Reuse an existing tag before making one;
  never make a tag from an uncertain or transcribed term. `kind/*` in use:
  `experiment`, `report`, `project-note`, `concept`, `reference`, `meeting`,
  `implementation`, `person`, `audit`, `session`, `lecture`, `decision`,
  `project-hub`, `log`, `presentation-preparation`, `presentation-script`,
  `idea`, `source-audit`, `paper-review`, `manuscript`, `overview`,
  `style-guide`, `weekly`, `stub`, `study`. A source series is grouped by its
  folder and the `book` link to its hub, not by a `book/*` tag.
- `project` is the canonical project name and matches its tag exactly
  (`project: K-Fold` with `project/K-Fold`). Reuse the spelling already in the
  vault: `K-Fold` (not `KFold`, `kfold`), `rdbdock` (not `RDBDock` in metadata);
  for any other project read the existing `project` values and tags before
  writing one. The gateway maps renamed project names to their current name.
  A task label that is not a project or branch is not folded into a project. Code paths and run names keep their own spelling.
- `Writing/` notes carry `writer: 문석현` and the checkbox `reviewed`.
  `note_draft_create` writes `reviewed: false`; only the user ticks it after
  reading, and HOME shows it as 검수. No `review_status` anywhere.
- `Concepts/` notes carry `kind/concept` and aliases for verified
  abbreviations, without `writer` or `reviewed`.
- Terminal experiment records carry four flat fields: `experiment_status`
  (`completed`, `failed`, `inconclusive`, `cancelled`), `provenance_state`
  (`retained`, `partial`, `unverified`, `not-applicable`), `evidence_access`
  (`durable`, `local-only`, `mixed`, `unknown`) and `claim_state` (`current`,
  `bounded`, `superseded`, `inconclusive`); `superseded_by` only names the exact
  later note that changes the claim. Reports and concepts do not get these
  fields, and legacy notes do not get them in bulk.
- Question reports carry `investigation_id` and `record_role: investigation`;
  their evidence records may carry the same ID and `record_role: evidence`.
- `categories`, `projects` (list), `review_status`, `knowledge_state`,
  `meeting_date` (use `date`), `related_notes` (use `related`), `source_host`
  and `type: daily-note` are retired; do not add them. In an experiment record
  `status` is not used; the state is `experiment_status`, and a record never
  stays `running` or `planned`: one that stopped without a recorded result is
  closed as `inconclusive`. A note that spans several projects keeps the primary
  in `project` and links the others in `related`. A branch name goes in `branch`
  next to its project (`kfold-claude` is a `K-Fold` branch; the gateway maps the
  old project value). `source_host` stays only on archived imports, because the
  gateway never lets a note gain `host`.

## 6. Writing

- Korean prose with English scientific and technical terms (titles and
  headings too), or English. Korean and English only, in complete sentences
  with normal spacing; never Chinese characters or Japanese kana (the gateway
  rejects them in judgments and Writing drafts).
- Titles are specific phrases that read well inside a sentence. Writing,
  Concepts and People use the title as the filename without a date; records
  get `YYYY-MM-DD title--<id>.md` from the gateway; slides use
  `YYYY-MM-DD Title` without version or hash suffixes.
- Short paragraphs, tables when they make a comparison easier, headings only
  when a reader needs them; no empty "요약/검증/결론" sections. `$...$` for
  short math, block equations for objectives and derivations with unfamiliar
  symbols defined.
- Link each distinct scientific or technical concept at its first substantive
  mention as `[[concept]]`, even when no note exists; reuse an existing exact
  title, use `[[target|abbreviation]]` for verified abbreviations, keep
  distinct concepts separate, and never nest or self-link.
- Cite a factual claim only from a passage actually read, with its section,
  page, figure or paragraph locator.
- Notes the user reads (`Writing/`, `Concepts/`, `People/`) contain verified
  facts and attributed discussion, in full detail; no agent bookkeeping (hosts,
  chat IDs, hashes, local paths, follow-up question lists, authorization
  notes). Requested follow-up research gets its own linked note.

## 7. Research records

- Keep one cumulative report per research question across all hosts. Find it
  by its `investigation_id` before searching by project or words; shared words
  do not make two questions the same.
- Lead with the current judgment and next action, then why the question
  matters, the hypothesis, the core method, what was observed and how it is
  interpreted. Keep observations, working assumptions, proposals and adopted
  decisions apart. Never invent the original hypothesis or record an agent
  proposal as the user's decision; keep user corrections and the dates on
  which interpretations changed.
- Converging circumstantial evidence may support a bounded working assumption.
  State only the limitations that change the next decision. Missing provenance
  is a recovery issue, separate from the strength of an observed result; a run
  that never reached a measurement cannot supply it. Keep a primary null result
  next to exploratory signals.
- Retain what reproduction needs: code revision, execution-affecting config,
  data and checkpoint identity, launch method, compared population and result
  location, with the execution host named for host-local paths. Raw prompts,
  transcripts, logs, code, configs, datasets and credentials stay in their own
  systems.
- Never write a hash, path, job ID or count that was not read from output in
  the current turn.
- One record per batch, sweep or screening round, with a table or an attached
  file, never one record per item; reuse the `evidence_key` of the same run or
  analysis. When a record is a key experiment or decision behind a note the
  user writes, link that note from the record.
- A capture belongs to the invoking session and turn; never borrow IDs from
  another task. A failed delivery stays in the host-local outbox: inspect it
  with `obsidian-research status`, preview `replay --session-id SESSION
  --dry-run`, then replay that session; never claim pending content was saved.
  A recording failure never blocks a scientific job.

## 8. Retired

Do not use or recreate: the LLM Wiki contract (`LLM-WIKI.md`) and `Derived/`,
the vault `STYLE.md` and `CLAUDE.md` (merged here), `maintenance-scope.json`
(the Mac mini host no longer needs a scope), `review_status`, `knowledge_state`
and `categories`, Daily notes, the iCloud vault copies, the read-only pilot vault
(`namespace: pilot`; `both` now means the main vault) and the `SPIRAL.md` hub.

---
name: obsidian-user-note
description: Write or revise Obsidian notes the user explicitly requests to read and edit, including concept explanations in Concepts and their own prose or meeting notes in Writing. Preserve detailed context, research necessary gaps and add academic wikilinks. Agent work records belong to obsidian-agent-record; research question reports and comparable experiments use their dedicated skills. Ordinary chat explanations do not trigger a save.
---

# Obsidian user notes: Concepts and Writing

Use this skill for the user's readable notes. For example, “turn this meeting into a note I can review” or “write a concept note explaining this mechanism” belongs here. The distinction is the requested artifact's purpose, not whether the request comes from Chat, Codex or Claude; this is not a Chat-plugin-only skill.

Read the [Obsidian vault policy](../obsidian-agent-record/references/obsidian-policy.md) once per task; it holds the vault rules (permissions, folders, metadata, writing). This skill adds the note-writing procedure and its detailed guidance.

## Trigger boundary

- Use this skill **only** when the user explicitly asks to create, draft, revise, organize, or add concept links to a user-facing concept note or personal note. An explicit request for an agent record still uses `obsidian-agent-record`; an ordinary explanation in chat does not authorize saving a note.
- Keep all ongoing research continuity unchanged: automatic milestone updates still use `research-workflow` (question reports under `Inbox/Agents/<host>/`), comparable terminal runs still use `experiment-ledger`, and autonomous agent outcome records still use `obsidian-agent-record` (`Inbox/Agents/`).
- Do not quiz or interrogate the user before writing. Unless the requested topic itself is genuinely ambiguous, gather context and write a complete, readable draft so the user can review and edit it in Obsidian.

## Choose the destination by the purpose of the text

- **Concepts/<title>.md:** reusable definitions, principles, mechanisms, equations, background explanations and reference notes. For example, an explanation of entorhinal cortex or Free Energy belongs here even when researched to support the user's writing. Save it directly as a concept reference, without personal `writer` attribution on a newly created note.
- **Writing/<title>.md:** the user's own essays, arguments, reflections, meeting records and personal synthesis. A scientific topic does not by itself make the user's prose a concept reference. Writing notes carry an Obsidian checkbox property `reviewed`: `note_draft_create` writes `reviewed: false`, and only the user ticks it after reading. Never set it to `true` yourself, and never add `review_status`.
- An explicit destination from the user takes precedence. For a mixed request, keep the user's narrative in Writing and put substantial reusable background in Concepts, linking the notes in both directions. Infer the purpose from the request and supplied material; do not ask the user to reconfirm this standing folder rule.
- This rule does not move or reclassify other existing notes automatically. When relocation is requested, move the original through `knowledge_revise(action: "move")`, verify unchanged content at the destination, then revise it in a separate operation. Preserve its identity, creation date and existing authorship metadata; repair affected path-qualified links. The creation-time metadata rule above does not authorize stripping metadata from migrated originals.

## Content standards

- Keep verified facts and the actual discussion, goals or decisions the user supplied. Attribute a meeting participant's idea as something discussed; never turn it into an established scientific finding. Omit unverified anecdotes and assistant-invented speculation rather than adding provisional appendices.
- Preserve the user's detailed context, explanations, reasoning, alternatives and motivations. “Facts only” is a reliability requirement, not an instruction to shorten the note. Meeting notes should be detailed enough for the user to reread and organize independently; do not drop supplied substance merely to meet a length target.
- Write scientific and technical terms in English throughout both kinds of Korean notes, including titles and headings: for example, protein structure, binding affinity, sequence alignment, cell culture and hypothesis generation. Keep Korean explanatory prose and use natural Korean particles after English terms. Preserve verbatim quotations and official source titles; when a note title changes, update its internal links and retain former names as aliases.
- Keep agent bookkeeping out of the note: no unsolicited follow-up questions, next-check lists, authorization disclaimers, host names, chat IDs, hashes, local artifact paths or internal provenance footers. Do not automatically append links to agent reports or presentation-preparation logs. Readable paper/source links may support factual statements where useful.
- Proactively investigate gaps needed to understand the requested note, such as undefined terms, missing mechanisms or unsupported factual premises. Use appropriate primary sources, explain supported findings, and preserve material uncertainty. Put substantial researched explanations in separate Concepts notes linked in both directions; include enough explanation in the original note to make it self-contained. Do not leave an unsolicited question checklist in place of this work or expand into unrelated research. The existing research-continuity workflow remains separate.
- Before citing a factual claim, read the supporting passage and map the claim to its actual section, page, figure/table or uniquely identifiable paragraph. Put that locator and a concise description of what it supports near the citation; use stable anchors only when verified. A title, topical relevance or search snippet does not establish support for a detailed claim. If only an abstract was read, stay within its claims and label the locator as Abstract. Separate the paper's observation from author hypotheses and the assistant's synthesis; preserve the experimental system and endpoint. Narrow or remove a claim whose source does not support it. Keep the detailed claim-to-passage audit outside the personal note so internal provenance does not return as a footer.

## Academic concept links

- In both Concepts and Writing notes, link every distinct scientific or technical concept at its first substantive mention, even when no target note exists. Cover anatomy, molecules, diseases, mechanisms, methods, models and metrics; do not limit links to a few main topics or to existing notes. Ordinary connective words need no links. In a long note, repeat a link when a later section should be readable independently.
- Reuse the exact title or path of an existing concept note when its meaning matches. Reuse established spellings from relevant existing wikilinks, including unresolved links. If no match is found, use the standard English concept name as an unresolved `[[concept]]` link. Missing targets are intentional future connections, not errors or a reason to omit links. Do not create empty notes just to resolve them; create substantive explanations only under the existing note-writing scope.
- Use one target for a concept and its verified synonyms or abbreviations: `[[entorhinal cortex|EC]]`, `[[entorhinal cortex]]`. Keep the displayed wording with `[[target|original wording]]` in a link-only revision. Expand an abbreviation only when its meaning is established by the note or a checked source; otherwise retain the literal term without inventing an expansion.
- Keep scientifically distinct concepts separate. `[[tau protein]]` and `[[tau pathology]]` are different targets, as are transentorhinal and entorhinal regions. A note that merely mentions a term is not automatically its concept note. Do not funnel every related term into a broad meeting or project note.
- Link a meaningful compound as one concept, such as `[[binding affinity]]`. Do not nest links, add self-links, or change existing links, quotations, source titles, citation labels/URLs, code, equations or metadata just to increase link coverage. Keep ordinary headings stable so their anchors survive.
- For a link-only request, preserve the text, claims, attribution and references. Apply the link pass only to the requested note or passage; do not use this as a trigger for new research or vault-wide rewrites.

Example using the user's supplied meeting wording, with only link markup added:

```markdown
발표자는 [[tau pathology]]가 [[entorhinal cortex|EC]]에서 [[hippocampus]]와 연결된 회로를 거쳐 더 넓은 뇌 영역으로 확산되는 맥락을 설명했다. EC는 **[[entorhinal cortex]]**이다.
```

This adopts the first-mention and unresolved-link practice from [Kepano's Links section](https://stephango.com/vault#links). It does not adopt his folder layout. [Obsidian's link guide](https://obsidian.md/help/link-notes) documents links to notes that do not exist yet.

## Workflow

1. **Check vault context first (`obsidian_main`):**
   - Run bounded `knowledge_search` queries (and `knowledge_read` when relevant) across `Concepts/`, `Writing/`, `Notes/`, and `Inbox/Agents/` so terminology, equations, and `[[wikilinks]]` align with existing concept titles, unresolved links and project hubs (such as `[[K-Fold]]` or `[[RDBDock]]`). A missing concept note still receives an unresolved link.
2. **Draft detailed, high-signal prose at the depth the user needs:**
   - Do not impose a character, line or paragraph limit on the finished note. Keep one coherent requested narrative in one note; split only when the topics serve genuinely separate reading purposes or the user asks. A tool request-size limit is not a reason to shorten or split the note.
   - Open immediately with a 2–3 sentence core definition or takeaway in clear Korean with standard English technical terms. Skip empty template banners or decorative emoji headings.
   - Include an equation, mechanism block or comparison only when it helps explain the requested facts; do not force a template onto a meeting record.
   - End when the requested content is covered. Apply the academic concept-link pass above and retain links to relevant topical notes. Check concept coverage and target consistency before saving; a link is navigation, not supporting evidence for a claim.
   - Write in Korean and English only with normal spacing. Never include Chinese characters (Hanja) or Japanese kana (`note_draft_create` rejects them), em dashes, or contrastive `"X가 아니라 Y다"` filler.
3. **Save using the selected branch:**
   - **Concepts:** use `knowledge_revise(action: "create", path: "Concepts/<title>.md")` with complete Markdown in `content`, including YAML `title`, `created`, `tags: [kind/concept, ...]` and useful aliases. Use the canonical English concept title so existing wikilinks resolve. Include the required `reason`, journal `source_refs` and a stable `operation_id`; do not copy the journal into the note body. Read the saved note back to verify it.
   - Creating or revising a Concepts note, and revising a Writing note this host did not create, runs on the Mac mini, whose gateway permits it without any scope file (policy section 2). A remote session hands the change to a Mac mini session; it never substitutes Writing, impersonates a host or edits vault files directly. Never overwrite a collision or create a duplicate to avoid the revision path.
   - **Writing:** create the personal draft via `note_draft_create`; it generates the personal `writer` metadata automatically. If the complete body exceeds that tool's current input limit, create the same titled note with its opening passage, read its SHA, then immediately use `knowledge_revise(action: "revise")` to save the complete prepared note at the same path while preserving gateway-generated metadata. Do not report completion at the intermediate step. Verify the final saved body against the full prepared text; if a request ceiling prevents completion, report the transport blocker instead of silently splitting or truncating the writing.
   - **For Writing only**, call `obsidian_main` tool `note_draft_create` with:
     - `title`: exact user-chosen title when the user provides one, or a concise natural concept/topic title when omitted. Do not prepend dates or append `--hash` suffixes (`note_draft_create` saves directly to `Writing/<title>.md` and records `created: YYYY-MM-DD` in YAML frontmatter).
     - `body`: Markdown body prose without frontmatter.
     - `tags`: 1–16 canonical tags describing the actual personal writing, such as `kind/meeting` or a project tag. A concept tag is not a substitute for routing a standalone reference to Concepts.
     - `project`: optional canonical project name (`"K-Fold"`, `"RDBDock"`, etc.) when tied to a project.
     - Omit `source_refs` for `note_draft_create`: that argument renders an internal provenance footer in the personal note. Keep operational provenance in task state or the research record. `knowledge_revise` still requires source references for its revision journal; pass them there without copying them into the note body.
     - `attachment_ids`: optional IDs returned by `attachment_upload` when an approved figure is embedded.
     - `operation_id`: fresh unique ID (`>= 8` chars, `[A-Za-z0-9._-]+`), reused only when retrying the exact same payload.
   - `note_draft_create` never overwrites an existing file (`409 note_already_exists`). To revise an existing `Writing/` note, read its current `sha256` with `knowledge_read` and update it in place with `knowledge_revise` (`action: "revise"`).
4. **Report concisely:**
   - Name the actual saved collection and title after readback. Writing appears in HOME's Writing table; Concepts is the population for HOME's random concept view. Do not imply that every new concept is necessarily one of the five randomly displayed notes.

## User decisions

- 2026-11-09: `"그리고 내가 12000자 제한? 이런거 둬가지고 writign 을 분리해서 했다고 이전에 얘기하던데, 이거 제한 skill 에서 없애주고, 이전에 작성해야했던것도 writing  을 합칠 수 있는건 합쳐주라."` Finished Writing notes have no skill-imposed length cap. Preserve coherent narratives with the same-note create-then-revise route when a creation tool has a smaller input limit; consolidate the existing split writing under the user's requested scope.
- 2026-11-06: `"호출 이름도 obsidian-user-note랑 obsidian-agent-record로 바꾸자. 참조하는 곳도 같이 맞추고 다른 호스트에도 동기화해줘."`
- 2026-11-06: `"음 이거 확실히 구분할 수 잇으면 좋겠는데"` The user wants the user-note and agent-record skills to be clearly distinguishable.
- 2026-11-04: `"굳이 질문을 하기보다는, 내가 어떤 내용을 적어달라고 요청하면 그걸 잘 writing 해주고, 내가 그걸 검수하는게 나을거같은데? 구조만 잘 설계하면 좋을거같음."` (Do not gate note creation on Socratic questioning; write a clean, structured draft when requested so the user can review it.)
- 2026-11-04: `"그리고 기본적인 연구 진행 상황들은 여전히 기존 workflow 그대로하고, 내가 note 만들어달라고 직접 요청할 때만 새로 만드는 스킬로 새로운 장소에 잘 보관하고, 그 노트들이 그냥 언제나 obsidian 바로들어가자마자 쉽게 볼 수 있게 해줘"` (Preserve `research-workflow`, `experiment-ledger`, and `obsidian-agent-record` unchanged; trigger this skill only on explicit note requests, store in the dedicated personal folder, and surface immediately on `HOME.md` startup Base.)
- 2026-11-04: `"날짜는 메타데이터로 넣고, 제목도 내가 설정보통할테니까 그냥 그렇게해야할듯? 그리고 Wiki 말고 다른 폴더명 추천좀."` / `"Writing 으로 해줘."` (Store personal notes in `Writing/<title>.md` using the user's title without a filename date prefix, keeping `created: YYYY-MM-DD` in YAML frontmatter metadata.)
- 2026-11-05: After quoting the assistant-added follow-up questions, execution-authorization disclaimer and internal source footer, the user said: `"이런거 내가 쓰는 노트에서는 없으면 좋겠어."` / `"내가 쓰는 노트에는 확실한 사실만 있으면 좋겠고, 앞으로 추가 자료 조사 요청이 있으면 새로운 노트 페이지와 함께 링크를 달아서 만들어주면 좋겠어."` Keep personal notes factual and free of those additions; requested follow-up research gets its own linked note.
- 2026-11-05: `"그리고 미팅 노트는 왜이렇게 간략해진거지? 내가 다 읽고 정리할 수 있게 최대한 자세하게 하고, 중간중간 빈 부분들은 조사를 하도록 언제나 설정해줘."` This supersedes the short-draft target and the restriction on researching necessary gaps without a separate request. Preserve detailed meeting substance, investigate gaps proactively, and connect substantial researched explanations through separate notes.
- 2026-11-05: `"레퍼런스를 달 때는 실제로 어느 부분의 어떤 내용이 그걸 뒷받침하는지 hallucination 없게 달아야해."` Cite only a claim supported by a passage actually read, with its specific location and support made clear; do not substitute a plausible paper for verified evidence.
- 2026-11-05: `"야 노트들 좀 업데이트해야할듯. … 이런 전문용어들은 모두 영어로 쓰자."` Use English scientific and technical terminology in the existing personal notes and future notes while retaining the Korean narrative.
- 2026-11-05: `"entorhinal cortex 이런것들은 그냥 노트가 없더라도 [[]] 이거로 link 만들 수 있게 뭔가 skill 을 만들 수 없나? 학술 용어들을 모두 그렇게 다 노트로 연결해두고 싶은거야. Kepano 가 쓰는것처럼."` Link academic concepts even when their notes do not exist, with consistent English targets and verified abbreviation aliases. This changes future note-writing guidance; existing-note edits still follow the requested scope.
- 2026-11-05: `"ㅇㅇ 앞으로 개념 설명은 Concepts에, 내가 쓰는 글은 Writing에 넣도록 스킬에도 반영하고 다른 호스트에도 동기화해줘."` Route reusable explanations to Concepts and the user's own prose to Writing. Apply this distinction by purpose, including researched background notes created alongside personal writing; preserve the separate research-recording workflow.
- 2026-11-06 (voice transcript): `"리뷰 스테이터스 말고 그 추가 위드들들은 리뷰 스테이터스가 사실 필요 없을 것 같아. 그냥 그거 위드는 제가 체크하는 거 된다는 거야. 그래서 그것도 좀 업데이트를 해주면 좋을 것 같아."` Writing notes carry no `review_status`; the user checks them by reading. HOME shows one Writing table without review tabs, and its 바로가기 section was removed (`"꿈의 바로가기 테이블들 ... 그건 좀 잘 없애는 게 낫지 않을까"`).
- 2026-11-06 (voice transcript): `"개념 노트 이것도 새로 하는 그 컨셉이라는 폴더에 그냥 다 넣으면 좋겠어. ... 옛날 노트에 있던 건 그냥 다 옮기면 좋겠다"` Concept notes from the older `Notes/` collection move to `Concepts/` in the reviewed vault cleanup; this is the relocation request the destination rule above refers to.
- 2026-11-06 (annotation on the removed review marker): `"writing 을 내가 검수한건 있어야지."` and, on the proposed `reviewed` checkbox written as false for new notes, `"좋아."` Writing notes keep the user's own review mark as the `reviewed` checkbox; HOME's Writing table shows it as 검수. This refines the review_status entry above: still no `review_status`, but the user's review is recorded.

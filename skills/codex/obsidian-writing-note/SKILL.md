---
name: obsidian-writing-note
description: Write or revise detailed personal Markdown notes in Obsidian through obsidian_main when the user explicitly asks for a note. Preserve their context and reasoning, research gaps needed for understanding, and link substantial explanations as separate topical notes. Do not trigger automatically for ordinary research progress, milestones, or experiments (keep using research-workflow, experiment-ledger, and obsidian-main-note).
---

# Write a personal note in Writing/ for review

## Trigger boundary

- Use this skill **only** when the user explicitly asks to create, draft, or organize a personal note for their own reading and review.
- Keep all ongoing research continuity unchanged: automatic milestone updates still use `research-workflow` (`Notes/` question reports), comparable terminal runs still use `experiment-ledger`, and autonomous agent outcome records still use `obsidian-main-note` (`Inbox/Agents/`).
- Do not quiz or interrogate the user before writing. Unless the requested topic itself is genuinely ambiguous, gather context and write a complete, readable draft so the user can review and edit it in Obsidian.

## Personal-note content

- Keep verified facts and the actual discussion, goals or decisions the user supplied. Attribute a meeting participant's idea as something discussed; never turn it into an established scientific finding. Omit unverified anecdotes and assistant-invented speculation rather than adding provisional appendices.
- Preserve the user's detailed context, explanations, reasoning, alternatives and motivations. “Facts only” is a reliability requirement, not an instruction to shorten the note. Meeting notes should be detailed enough for the user to reread and organize independently; do not drop supplied substance merely to meet a length target.
- Write scientific and technical terms in English throughout Korean personal notes, including titles and headings: for example, protein structure, binding affinity, sequence alignment, cell culture and hypothesis generation. Keep Korean explanatory prose and use natural Korean particles after English terms. Preserve verbatim quotations and official source titles; when a note title changes, update its internal links and retain former names as aliases.
- Keep agent bookkeeping out of the note: no unsolicited follow-up questions, next-check lists, authorization disclaimers, host names, chat IDs, hashes, local artifact paths or internal provenance footers. Do not automatically append links to agent reports or presentation-preparation logs. Readable paper/source links may support factual statements where useful.
- Proactively investigate gaps needed to understand the requested note, such as undefined terms, missing mechanisms or unsupported factual premises. Use appropriate primary sources, explain supported findings, and preserve material uncertainty. Put substantial researched explanations in separate topical notes linked in both directions; include enough explanation in the original note to make it self-contained. Do not leave an unsolicited question checklist in place of this work or expand into unrelated research. The existing research-continuity workflow remains separate.
- Before citing a factual claim, read the supporting passage and map the claim to its actual section, page, figure/table or uniquely identifiable paragraph. Put that locator and a concise description of what it supports near the citation; use stable anchors only when verified. A title, topical relevance or search snippet does not establish support for a detailed claim. If only an abstract was read, stay within its claims and label the locator as Abstract. Separate the paper's observation from author hypotheses and the assistant's synthesis; preserve the experimental system and endpoint. Narrow or remove a claim whose source does not support it. Keep the detailed claim-to-passage audit outside the personal note so internal provenance does not return as a footer.

## Workflow

1. **Check vault context first (`obsidian_main`):**
   - Run `knowledge_search` (and `knowledge_read` when relevant) across `Writing/`, `Notes/`, and `Inbox/Agents/` so terminology, equations, and `[[wikilinks]]` align with existing project hubs (such as `[[K-Fold]]` or `[[RDBDock]]`) and duplicate notes are avoided.
2. **Draft detailed, high-signal prose at the depth the user needs:**
   - Do not impose a short line or paragraph target. The gateway's 12,000-character body limit is a per-note transport limit; use meaningfully linked topical notes if needed, without discarding the user's content.
   - Pass **only** Markdown body prose in `body`; `note_draft_create` generates YAML frontmatter (`title`, `created`, `writer: "문석현"`, `review_status: pending`, `tags`, `project`, `record_id`, `operation_id`, `agent`) automatically.
   - Open immediately with a 2–3 sentence core definition or takeaway in clear Korean with standard English technical terms. Skip empty template banners or decorative emoji headings.
   - Include an equation, mechanism block or comparison only when it helps explain the requested facts; do not force a template onto a meeting record.
   - End when the requested content is covered. Add `[[wikilinks]]` when they serve the content or connect an explicitly requested follow-up note.
   - Write in Korean and English only with normal spacing. Never include Chinese characters (Hanja) or Japanese kana (`note_draft_create` rejects them), em dashes, or contrastive `"X가 아니라 Y다"` filler.
3. **Create the draft in `Writing/` via `note_draft_create`:**
   - Call `obsidian_main` tool `note_draft_create` with:
     - `title`: exact user-chosen title when the user provides one, or a concise natural concept/topic title when omitted. Do not prepend dates or append `--hash` suffixes (`note_draft_create` saves directly to `Writing/<title>.md` and records `created: YYYY-MM-DD` in YAML frontmatter).
     - `body`: Markdown body prose without frontmatter.
     - `tags`: 1–16 canonical tags (for example `["kind/concept", "topic/diffusion"]` or `["kind/reference", "project/K-Fold"]`).
     - `project`: optional canonical project name (`"K-Fold"`, `"RDBDock"`, etc.) when tied to a project.
     - Omit `source_refs` for `note_draft_create`: that argument renders an internal provenance footer in the personal note. Keep operational provenance in task state or the research record. `knowledge_revise` still requires source references for its revision journal; pass them there without copying them into the note body.
     - `attachment_ids`: optional IDs returned by `attachment_upload` when an approved figure is embedded.
     - `operation_id`: fresh unique ID (`>= 8` chars, `[A-Za-z0-9._-]+`), reused only when retrying the exact same payload.
   - `note_draft_create` never overwrites an existing file (`409 note_already_exists`). If the user asks to revise or mark an existing `Writing/` note as `human-reviewed`, read its current `sha256` with `knowledge_read` and update it in place with `knowledge_revise` (`action: "revise"`).
4. **Report concisely:**
   - Tell the user the saved `Writing/<title>.md` path and note that it appears immediately in `HOME.md` (`전체 내 노트` / `검수 대기 (Pending)` views) on Obsidian startup.

## User decisions

- 2026-11-04: `"굳이 질문을 하기보다는, 내가 어떤 내용을 적어달라고 요청하면 그걸 잘 writing 해주고, 내가 그걸 검수하는게 나을거같은데? 구조만 잘 설계하면 좋을거같음."` (Do not gate note creation on Socratic questioning; write a clean, structured draft when requested so the user can review it.)
- 2026-11-04: `"그리고 기본적인 연구 진행 상황들은 여전히 기존 workflow 그대로하고, 내가 note 만들어달라고 직접 요청할 때만 새로 만드는 스킬로 새로운 장소에 잘 보관하고, 그 노트들이 그냥 언제나 obsidian 바로들어가자마자 쉽게 볼 수 있게 해줘"` (Preserve `research-workflow`, `experiment-ledger`, and `obsidian-main-note` unchanged; trigger this skill only on explicit note requests, store in the dedicated personal folder, and surface immediately on `HOME.md` startup Base.)
- 2026-11-04: `"날짜는 메타데이터로 넣고, 제목도 내가 설정보통할테니까 그냥 그렇게해야할듯? 그리고 Wiki 말고 다른 폴더명 추천좀."` / `"Writing 으로 해줘."` (Store personal notes in `Writing/<title>.md` using the user's title without a filename date prefix, keeping `created: YYYY-MM-DD` in YAML frontmatter metadata.)
- 2026-11-05: After quoting the assistant-added follow-up questions, execution-authorization disclaimer and internal source footer, the user said: `"이런거 내가 쓰는 노트에서는 없으면 좋겠어."` / `"내가 쓰는 노트에는 확실한 사실만 있으면 좋겠고, 앞으로 추가 자료 조사 요청이 있으면 새로운 노트 페이지와 함께 링크를 달아서 만들어주면 좋겠어."` Keep personal notes factual and free of those additions; requested follow-up research gets its own linked note.
- 2026-11-05: `"그리고 미팅 노트는 왜이렇게 간략해진거지? 내가 다 읽고 정리할 수 있게 최대한 자세하게 하고, 중간중간 빈 부분들은 조사를 하도록 언제나 설정해줘."` This supersedes the short-draft target and the restriction on researching necessary gaps without a separate request. Preserve detailed meeting substance, investigate gaps proactively, and connect substantial researched explanations through separate notes.
- 2026-11-05: `"레퍼런스를 달 때는 실제로 어느 부분의 어떤 내용이 그걸 뒷받침하는지 hallucination 없게 달아야해."` Cite only a claim supported by a passage actually read, with its specific location and support made clear; do not substitute a plausible paper for verified evidence.
- 2026-11-05: `"야 노트들 좀 업데이트해야할듯. … 이런 전문용어들은 모두 영어로 쓰자."` Use English scientific and technical terminology in the existing personal notes and future notes while retaining the Korean narrative.

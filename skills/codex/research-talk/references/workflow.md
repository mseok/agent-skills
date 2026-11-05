# Presentation preparation note

Use one note per actual presentation, separate from cumulative scientific question reports. Reuse an existing note when the event/topic and intent match. Do not create a second experiment record for already recorded evidence.

Retain purpose, audience, duration, slide language, intended outcome; current storyline and open decisions; approved version/date and actual user reference; per-slide ID, role, message, evidence, visual and transition; original question/experiment links with conditions; latest user-edited deck path; missing figures/data and material QA limitations.

For a new talk whose language is unspecified, ask “슬라이드는 한국어와 영어 중 어떤 언어로 만들까요?” and keep language pending until answered. The user may request both. Retain the actual language decision/reference; conversation language and previous talks do not establish it. Existing user choices for this same talk remain valid on resume.

Use `knowledge_search` for presentation notes, `investigation_context` for research questions, and bounded `knowledge_read`/section/batch reads for evidence. All Vault reads use the bridge, including `attachment_preview` for images. Obtain full assets through supported bridge mechanisms or explicit host-qualified original locations, not the Vault filesystem.

Create notes using `record_create`, stable operation IDs and presentation-preparation tags (not `kind/experiment`). Revise using current-SHA `knowledge_revise`. On conflict reread and merge; never force. Do not alter original experiment records for a cleaner story. Use research-workflow separately when discussion reaches a material scientific interpretation or adopted research decision.

Approval must come from the user. An agent recommendation, unchecked checkbox or status field is not approval. Record the actual user reference when it happens and do not request it twice. Failed recording remains outside the Vault in the bridge outbox; do not claim it was saved.

## Archive slides and scripts in Obsidian

When asked to save presentation material, store the slide PDF as `Slides/YYYY-MM-DD Title.pdf`. Use the actual presentation date when known; for a self-study deck without an event date, use its verified creation date. Do not append version labels or hashes to the visible filename. Keep identity, checksums and retained revisions in the gateway record.

Use `obsidian_main.attachment_upload` with `slide: {date: "YYYY-MM-DD", title: "Title"}`. The upload is still raw HTTPS; do not pass file bytes or base64 as tool arguments. The slide option stores a verified PDF under the date/title and promotes identical content already in Attachments while retaining its attachment identity. Update every active note link that used the previous path. If the running client has an older schema, use the documented host-local obsidian_main bridge bootstrap; do not write the vault directly or silently fall back to Attachments.

Keep the spoken script as `Slides/YYYY-MM-DD Title.md` and preserve its existing content and length unless the user asks for a substantive revision. Do not generate a script PDF by default or delete an existing script PDF without authorization. When extracting existing HTML speaker notes, retain all notes in slide order without adding explanatory prose. Create or revise the Markdown through scoped `knowledge_revise`; ordinary `Writing/` review metadata does not belong on an archived script.

In the existing presentation note, link to both the PDF and its Markdown script. In the script, link to its matching PDF and presentation note. These are note links; do not alter the PDF binary to add a return link or create a second preparation record for the same talk.

The same date/title may reuse identical bytes. A different PDF at that name is a collision requiring an authorized replacement, never silent overwrite or an invented version suffix. Verify the returned Slides path, PDF SHA, preserved script body and working note links after writing.

## User decisions (2026-11-05)

- "PDF 이렇게 발표자료 올리는 거는 스킬을 좀 수정하는 게 낫지 않을까 싶기는 한데 어태치먼트 말고 Slides라는 폴더에 따로 이제 넣는 게 좋지 않을까 싶고. 슬라이드 그렇게 넣을 때는 언제나 이제 저거 날짜랑 제목 이렇게 해서 넣는 게 좋고 버전 얘기는 그냥 빼는 게 좋지 않을까 싶거든."
- "그 슬라이드랑 함께 이제 그 대본 뭐 대본 길이를 늘릴 필요는 없을 것 같고 그 대본도 PDF로 하기보단 대본은 그냥 마크다운 파일로 계속 그냥 해주고 그 연결을 시키는 게 좋을 것 같아."

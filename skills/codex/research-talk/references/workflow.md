# Presentation preparation note

Use one note per actual presentation, separate from cumulative scientific question reports. Reuse an existing note when the event/topic and intent match. Do not create a second experiment record for already recorded evidence.

Retain purpose, audience, duration, slide language, intended outcome; current storyline and open decisions; approved version/date and actual user reference; per-slide ID, role, message, evidence, visual and transition; original question/experiment links with conditions; latest user-edited deck path; missing figures/data and material QA limitations.

For a new talk whose language is unspecified, ask “슬라이드는 한국어와 영어 중 어떤 언어로 만들까요?” and keep language pending until answered. The user may request both. Retain the actual language decision/reference; conversation language and previous talks do not establish it. Existing user choices for this same talk remain valid on resume.

Use `knowledge_search` for presentation notes, `investigation_context` for research questions, and bounded `knowledge_read`/section/batch reads for evidence. All Vault reads use the bridge, including `attachment_preview` for images. Obtain full assets through supported bridge mechanisms or explicit host-qualified original locations, not the Vault filesystem.

Create notes using `record_create`, stable operation IDs and presentation-preparation tags (not `kind/experiment`). Revise using current-SHA `knowledge_revise`. On conflict reread and merge; never force. Do not alter original experiment records for a cleaner story. Use research-workflow separately when discussion reaches a material scientific interpretation or adopted research decision.

Approval must come from the user. An agent recommendation, unchecked checkbox or status field is not approval. Record the actual user reference when it happens and do not request it twice. Failed recording remains outside the Vault in the bridge outbox; do not claim it was saved.

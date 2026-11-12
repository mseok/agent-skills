# Local storyline snapshot

The Obsidian note is the durable human-readable record. Local JSON binds a build to the accepted flow and input deck. The agent writes it; do not ask the user to write JSON.

`brief.language` must reflect the user's explicit choice for this talk, not a guessed default. The example's English value is illustrative, not a default. The checker rejects a missing or pending language; the agent separately verifies the actual user decision in the preparation note.

```json
{
  "presentation_id": "talk-event-topic",
  "status": "drafting",
  "brief": {"purpose": "Explain a prior ablation", "audience": "Research group", "duration_minutes": 20, "language": "English"},
  "slides": [{"id": "s01", "role": "question", "title": "When does the prior help?", "message": "State the question", "evidence": [], "visual": "editable explanation", "transition": "Introduce comparison"}],
  "approval": null,
  "input_deck": null
}
```

After actual approval set status `approved` and `approval = {"user_reference": "actual task/turn or retained note anchor", "approved_at": "ISO timestamp", "flow_sha256": "digest"}`. Brief-driven runs with no interactive approval and no brief date: `approval = {"user_reference": "<the brief path>", "basis": "brief", "flow_sha256": "digest"}` (no invented timestamp). Each slide may also carry `closing` (the one takeaway sentence) and `transition`. Obtain the digest of presentation_id, brief and slides with `python3 scripts/check_storyline.py storyline.json --digest`.

Run `python3 scripts/check_storyline.py storyline.json` before creation. It rejects drafting status, absent approval metadata and post-approval flow changes. The script cannot authenticate a human decision; verify the actual cited user message.

For revisions set `input_deck = {"path": "/absolute/path/latest-user-edited.pptx", "sha256": "current digest"}`. If it changes, reread the latest deck. Never regenerate an older deck over user changes.

Evidence entries identify source note/run/artifact and relevant conditions. Each slide needs nonempty id, role, title, message and visual fields plus an evidence list. Empty evidence is allowed for setup/questions. Result, finding, benchmark and conclusion roles need evidence or an explicit nonempty `missing_inputs` list; missing-data slides must withhold unsupported findings and show the needed input instead. A visual plan must be explicit, including when it calls for a placeholder.

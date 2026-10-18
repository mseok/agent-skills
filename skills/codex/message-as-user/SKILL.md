---
name: message-as-user
description: Draft or send text that goes out under the user's name (Gmail, Slack posts or DMs, collaborator handoff notes, marketplace replies, cover notes). Use when the user says 메일 써줘, 슬랙에 올려줘, 초안 만들어줘, 답장, 전달해줘, or asks for a message to a colleague, professor, collaborator or buyer. Not for chat replies to the user themselves.
---

# Messages sent as the user

The user is judged by these texts, so they must read like the user, not like an agent.

## Draft

1. Plain text. No markdown markers, no arrows, no bold, no headers, no bullet symbols unless the destination renders them and the user uses them there.
2. The user's register: Korean to Korean colleagues in the user's usual politeness level, English to English speakers; short sentences; no agent phrasing ("I have verified", "as requested").
3. Content order for a handoff or status note: what was done and where it is, what is still in progress or unverified, what the recipient must do. Keep finished and in-progress work visibly separate.
4. Attachments and links: name each one and check it exists and opens before mentioning it.
5. Show the final text in full in the reply, in a fenced block, before anything is saved or sent.

## Save and send

1. Save as a draft only on request; after saving or editing a Gmail draft, close the compose view and reopen the saved draft to confirm the stored text matches.
2. Send only with the user's explicit approval of that exact text in the current turn. Sending is irreversible; a retraction is not a fix.
3. Never type the user's email address or other identifiers into an external service or a subagent prompt unless the user asked. Never send from an automated or evaluation run; send-capable connectors stay disabled there.
4. After sending, report the recipient, time and whether delivery or receipt was confirmed; "delivery started" is not receipt.

## Slack specifics

- Post into the channel or DM the user named; confirm the destination name before posting.
- Threads and mentions follow the user's habit; do not add emoji or reactions on the user's behalf.
- Korean text is character-based: never truncate by bytes.

## Verified additions (2026-10-17 audit)

- If the draft may be open in the user's compose window, ask them to close it before editing through the API, then reopen the saved draft and read it back.
- A public profile, seller introduction, service description or FAQ on an external platform is text sent as the user: draft every field locally, show them all in one block, and save only the fields the user approves in that turn.

## Handoff packages (2026-10-17 audit)

A package sent to a colleague lets the recipient recompute every number cited in the note from the package alone: include the upstream tables, the scripts and their input paths, and name the version of each; check the list before sending, not after the colleague asks.

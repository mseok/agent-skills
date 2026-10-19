---
name: gmail-attachments
description: Download Gmail attachments (PDF etc.) to local disk over IMAP so they can be read, because the Gmail connector tools only return attachment metadata. Use when the user asks to read, open or summarize a file attached to an email (메일 첨부파일, Gmail 첨부, 첨부 PDF). Needs the user's Gmail app password stored once with --store-app-password.
---

# Gmail attachments to disk

The Gmail connector tools (`search_threads`, `get_thread`, `get_message`) return only attachment
filenames and IDs. They cannot fetch or extract attachment content. This skill saves attachments
to disk with `scripts/gmail_attachments.py` (standard library only, IMAP to `imap.gmail.com`).
Read the saved files afterwards with the Read tool (PDFs, use `pages` for more than 10 pages) or
`pdftotext -layout`.

## Steps

1. Find the message. Use the Gmail connector (the message `id` it returns is the Gmail message
   ID and works with `--message`), or pass a Gmail search query, which uses the same syntax as
   the Gmail search box.
2. Dry run, then fetch. Run from the project root; the default destination is
   `./references/gmail` (check that it is gitignored first: `git check-ignore references`).

```bash
S=~/.claude/skills/gmail-attachments/scripts/gmail_attachments.py
python3 $S --message <ID> --dry-run
python3 $S --message <ID>
python3 $S "subject:<keyword> has:attachment" --max 5 --ext pdf
```

   Options: `--ext pdf` (default), `--ext pdf,docx`, or `--ext all`; `--dest DIR`; `--max N`
   (newest N messages for a query). Files are saved as `YYYYMMDD_<msgid8>_<name>` with mode 600,
   existing files of the same size are skipped, and `manifest.jsonl` in the destination records
   message ID, thread ID, sender, subject, size, sha256 and path. `--dry-run` still downloads the
   message data to list attachments but writes no files.
3. Read the files and report their absolute paths.

## One-time setup (done by the user)

The user stores the Gmail address and a Google app password (needs 2-step verification) in
`~/.config/gmail-attachments/` with mode 600 by running this in their own terminal on the host,
because the password prompt is hidden and needs a TTY:

```bash
python3 ~/.claude/skills/gmail-attachments/scripts/gmail_attachments.py --store-app-password
```

Then `--check` (login test; prints only the mailbox size) can be run from here.

If the script reports a missing credential file or a login failure, tell the user exactly what is
missing. Do not ask the user to paste the password, the file contents or a manual download into
the chat. If the user pastes an app password anyway, say that it must be revoked and recreated
at myaccount.google.com/apppasswords.

## Rules

- An app password gives full mailbox access, so this skill only ever reads: the mailbox is opened
  read-only and messages are fetched with `BODY.PEEK`. Never send, delete, label or move mail.
- Never print or log the password or the credential files.
- Attachments can be confidential (for example partner documents); do not commit them.
- A few IMAP calls and small files are fine on a shared login node.

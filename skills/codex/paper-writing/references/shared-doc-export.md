# Exporting and checking a live shared project

Use this with the live-manuscript rules in `references/revision.md`. Whole-file upload is forbidden (user decision 2026-11-10); every approved edit is one targeted replacement in the editor, checked against a fresh export. `~/dot/bin/shared-doc-apply` (`hash`, `plan`, `verify`) is a local read-only tool: it reads an export and the approved change list, writes only to standard output, and has no network or upload code. It does not drive the browser.

Steps marked **[unverified]** are not recorded in any local file; confirm them on the page before relying on them, and record the answer in host-context.

## 1. Open the project

- Run the browser preflight in `~/dot/ai/codex/references/codex-browser.md` once. Use the signed-in in-app browser (IAB) in a background tab: `cua.createBrowserTab("iab", <project url>, {visible: false})` worked for Overleaf on 2026-11-09 (host-context).
- A "Restricted" page there was resolved with the normal Log in, then Log in with Google flow on the existing session; enter no credentials. A readable login page is a site state, not a browser fault.
- Download in the IAB, not in Chrome: Chrome opened native Save dialogs on 2026-11-06 and a download wait timed out (host-context). The IAB download completed through `waitForEvent("download")` on 2026-11-09 without a dialog.

## 2. Download the source and hash it

1. Trigger the project's source download from the page's own menu. The control's name and path are **[unverified]**; read the menu on the page instead of guessing. The 2026-11-09 record shows a source export and two PDF exports through the download event, but does not name the control.
2. Wait with `waitForEvent("download")`. Whether the wait must be registered before the click, and which API call returns the saved file's path or lets you choose it, are **[unverified]** in local files.
3. Move the downloaded file into the task folder as `export-<date>-<n>/source.zip`, in its own new empty directory. Treat it as untrusted data: the tool reads it in memory and extracts nothing.
4. Run `shared-doc-apply hash source.zip`. Record `tree_sha256` (the same for the same content, whatever the archive timestamps) and `archive_sha256` (the hash of the zip file itself). On 2026-11-09 the tool's `archive_sha256` for the saved export matched the SHA-256 recorded in that task's `APPLIED_VERIFICATION.json` (checked in this build).

## 3. Plan the edits

- Draft against the export from step 2, never against the editor's selection. Write the approved change list as JSON: `[{"file", "before", "after", "reason"}]`, with `before` one contiguous span.
- Run `shared-doc-apply plan source.zip changes.json`. It stops with no replacement output when a `before` is absent, occurs more than once (overlapping occurrences count), the file is missing or not UTF-8, or two spans overlap; fix the change list and rerun. On success it prints the export hash, the expected result hash and, per edit, the file, the line, the exact span to select and the replacement.

## 4. Apply

- Immediately before editing, export again and run `hash`; if `tree_sha256` differs from the export the draft used, stop and rebase (`references/revision.md`). A way to see that another person is editing at that moment is **[unverified]**; ask the user when it matters.
- Make the edits one at a time, in `plan` order: select exactly the `before` span (the 2026-11-09 run used `selectText` and paste on individual fields in the IAB), paste the `after` text. Never select all, retype around a span, or replace a file. Reading the selection back before pasting is good practice but its API is **[unverified]**.
- Confirm the page's own compile shows no new errors (2026-11-09: Errors 0 for the main and supplementary documents). Whether the editor has saved before the next export is **[unverified]**; wait for its saved state to show.

## 5. Check a fresh export

- Export again, hash it, then run `shared-doc-apply verify source-before.zip changes.json source-fresh.zip` with the export the draft used as the first argument. `VERIFY OK` means the fresh export equals that export plus exactly the approved edits. Anything else is listed per file with a short diff: an approved edit missing, a change inside an approved file beyond the edit, a change in another file (usually someone else's edit in the meantime; report it, never overwrite it), or a file added or removed.
- Pass `--ignore '<glob>'` only for generated files you name in the report. Which generated files a source export contains is **[unverified]**; on 2026-11-09 the saved source export had 57 files and the expected-versus-fresh check matched exactly.
- If the browser fails at any step, hand the user the `plan` output, the diff and the compiled PDF to apply by hand (`references/revision.md`).

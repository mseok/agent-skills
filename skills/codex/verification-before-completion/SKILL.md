---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always
---

# Verification Before Completion

## Overview

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

## Red Flags - STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!", etc.)
- About to commit/push/PR without verification
- Trusting agent success reports
- Relying on partial verification
- Thinking "just this once"
- Tired and wanting work over
- **ANY wording implying success without having run verification**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Regression tests (TDD Red-Green):**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**Build:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**Agent delegation:**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

## When To Apply

**ALWAYS before:**
- ANY variation of success/completion claims
- ANY expression of satisfaction
- ANY positive statement about work state
- Committing, PR creation, task completion
- Moving to next task
- Delegating to agents

**Rule applies to:**
- Exact phrases
- Paraphrases and synonyms
- Implications of success
- ANY communication suggesting completion/correctness

## Verify the end state the user cares about

| Claim | Proof that counts | Not sufficient |
|---|---|---|
| Edited a shared or live document (Overleaf, Docs, Gmail draft, CMS) | Reopen the saved document and read the changed passage back | Local file changed; editor iframe shows it; "upload started" |
| Published or deployed | The public URL reached through the site's own navigation, logged out; the branch that serves it | Preview, draft page, admin view, a different URL |
| Sent a message | Receipt or the sent item with timestamp | "delivery started"; the draft exists |
| Slides, figures, documents look right | Rendered PDF or PNG of the final artifact inspected (native app render when layout matters) | XML inspection, unit tests, format checker |
| Service, VPN or gateway is up | A real request through the path the user uses (SSH login, gateway read, HTTPS from another host) | Health endpoint, process present, local port open |
| Job or campaign progressing | At least one completed task's output artifact opened | Queue shows "running" |
| Cutover or migration done | Every consumer of the old path listed and switched (instruction files, skills, services, cron, deploy scripts) | The new path works |
| State, cause or denial ("I did not rename it", "a run is in progress") | Checked on the surface in question before saying it | Memory of earlier turns |

If the checking tool is broken, say "not visually verified" (or "not verified on the target") in the first line and name what was checked instead. Report each requested item as done or blocked; never present unfinished work as a follow-up suggestion.

Cutover or migration checklist: list every consumer of the old path (loaded instruction files, skills, deploy scripts, services, cron, automations) and switch each; `rg -l '<old path or command>'` over every skill root and automation returns nothing, or each hit is listed in the final answer. A smoke test uses a real-sized input for the stage under test. Never explain away a user-visible defect as an editor or preview artifact without confirming it on the logged-out page first.

## More rows (2026-10-17 audit)

| Claim | Proof that counts | Not sufficient |
|---|---|---|
| Background monitor or recovery automation changed | Its own scheduler run (launchd or cron, not a manual script) recovers from the real failed state it exists for; each transient-error path has a test; the previous mechanism stayed active until this passed | A manual run of the same code; a scheduled run while healthy; one successful login |
| Login or boot automation | Waits for each dependency (network, volume, daemon) with retry and backoff and was run once with each dependency withheld | One timed attempt that worked |
| Review findings addressed | Every unresolved review thread on the PR listed (not a time window), each fixed or answered, with the count | Comments newer than the last push; the bot's summary |
| Evaluation is correct | At least two selected rows traced to the evaluator's native per-item output with entity match | The aggregated table reproduces |
| Quality goal for writing or figures | The user's stated goal checked explicitly (for example a fresh-context reader pass listing terms used before definition) or declared unchecked | Compile, render or layout success |

## More rows (2026-10-27 review)

| Claim | Proof that counts | Not sufficient |
|---|---|---|
| A change is safe or touches nothing else | Effects outside the diff listed and each checked by running or opening it: documents or files that cite what you removed, OS permissions tied to a build signature, live sessions and their history, caches and indexes | The diff looks contained; tests in the touched module pass |

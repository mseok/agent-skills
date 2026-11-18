---
name: llm-quota
description: Check live subscription quotas for Codex, Claude, and Gemini, plus recorded Claude API bridge cost estimates, without model inference. Use for remaining allowance, usage percentages, reset times, 내 사용량, 남은 한도, or recorded bridge API spend. Not for context-window usage, general API billing, or price estimates.
---

# LLM quota

Read subscription limits through the provider's official runtime without model inference. Codex and Claude use the calling CLI account; inside an Antigravity session, `swarm{action: "models", all: true}` returns live Gemini and Google-provided Claude/GPT remaining percentages and reset times directly, while the bridge's dedicated Gemini ACP profile (`acp/`) was retired across hosts on 2026-11-17. No package installation, MCP registration, listener, or background polling is required. The bundled helper uses Node.js built-ins.

## User decisions

The dated decisions behind these rules, in the user's own words, are in [references/user-decisions.md](references/user-decisions.md). Read it before editing this skill or when a rule's origin or scope is in doubt; record a new decision there and state the resulting rule in plain words in this file.

## Query

Run the helper relative to this skill's directory:

```sh
node scripts/quota.mjs codex
node scripts/quota.mjs claude
node scripts/quota.mjs claude-api
node scripts/quota.mjs all
```

- **Inside an Antigravity session**: call `swarm{action: "models", all: true}` to read live remaining percentages and reset timestamps for Gemini (`gemini-4-*`, `gemini-3.8-*`) and Google-provided Claude/GPT models with zero model inference, alongside `node scripts/quota.mjs codex`, `claude`, and `claude-api` (or `all`) for OpenAI Codex, Anthropic Claude subscription, and recorded bridge API spend.
- For an unqualified quota request, report all available providers (`all`, plus `swarm{action: "models", all: true}` when running inside Antigravity), regardless of the model running this chat. Select a single provider only when the user explicitly asks for that provider alone.
- In a ChatGPT bridge with the local quota handler installed, a standalone skill selection, `!quota`, `$llm-quota`, or `llm quota` is answered locally with all providers. The visible quota exchange is excluded from later model requests. A request that also asks for analysis or planning still goes to the model. Installing this skill alone does not add that bridge handler or remove model context; that integration is verified on the Mac mini, not on the other hosts.
- A CLI must already be installed and logged in. Preserve the calling environment, including `CODEX_HOME` and `CLAUDE_CONFIG_DIR`. The result is for that local CLI account.
- Codex and Claude use initialization and quota control requests only. When an explicit Gemini ACP runtime is configured, `quota.mjs gemini` opens a fresh ACP session with no MCP servers and invokes exactly `/usage` only after the official runtime advertises it. This is a native local command, not a natural-language model prompt. Never fall back to asking a model about its quota. Authentication stays inside the official runtime; do not read credential files or Keychain, extract tokens, or replace this helper with `npx ai-quota`.
- The bridge's dedicated Gemini `acp/` directory was retired across hosts on 2026-11-17: when `GEMINI_ACP_BIN` is unset and `acp/runtime/agy_acp_server.par` is absent, `quota.mjs gemini` returns `status: "unavailable", reason: "bridge_acp_retired"` so `node scripts/quota.mjs all` exits `0`. `GEMINI_ACP_BIN` and `GEMINI_ACP_PROFILE` select an explicitly configured ACP runtime/profile (`BRIDGE_STATE_DIR` selects the bridge directory). Do not copy credentials or sign in merely to repair a quota query.
- Codex uses `account/rateLimits/read` over app-server stdio. Claude uses its experimental `get_usage` control request over stream-json. Protocol details and sources are in [references/native-protocols.md](references/native-protocols.md); read that reference when diagnosing a protocol failure.
- When the native Claude reading fails or has no values (for example an expired `/login` sign-in; the bridge's one-year `setup-token` token cannot answer `get_usage`), the helper uses the selected bridge's `claude-rate-limits.json` if it exists. The bridge writes it from the `rate_limit_event` that each subscription chat turn reports (numbers and times only). Such a result has `status: "ok"`, a `source` naming the bridge observation, `nativeStatus`, and `observedAt` on the result and each window. `BRIDGE_STATE_DIR` selects the bridge; a host without that file keeps the native result.
- When the selected bridge has its one-year token file `claude-oauth-token`, the Claude result carries `bridgeToken` (`savedAt`, `estimatedExpiresAt`, `daysLeft`, `renewDue`). Only the file's modification time is read, never its contents; the expiry is estimated as one year after it was saved, because the CLI does not report it.
- A Gemini `error` with reason `auth_required` (when `GEMINI_ACP_BIN` is explicitly configured) means that ACP profile's sign-in was refused, not a quota value.
- `claude-api` reads only local cost snapshots under the selected bridge's `claude-api/usage` directory. It never reads the API key or calls an inference or billing endpoint. `BRIDGE_STATE_DIR` selects the bridge. A host without that API route returns `api_not_configured`.

## Interpret

- Report provider, used/remaining percentage, reset time in the user's timezone, and `checkedAt`. Keep different quota buckets and model-scoped limits separate. These are shared subscription windows, not this conversation's token usage.
- For Gemini (from Antigravity `swarm{action: "models", all: true}` or an explicit ACP runtime), retain the separate Gemini model buckets and Google-provided Claude/GPT groups when returned. The latter group is not the user's separate Anthropic or OpenAI subscription. ACP `usage_update.used` and context size are token/context counters, not subscription utilization.
- Show Claude API separately as **this host bridge's recorded cost estimate**, with its recording period and any `unknownRuns`. It is not subscription utilization, final billing, account-wide spend, or remaining credit. Snapshots are cumulative per CLI process, so the helper replaces each process's total instead of adding successive turns. Active calls after the latest result, crashed calls without a result, and API use outside this bridge are not fully covered. No records means unknown, not zero spend. Remaining credit and account spend limits remain unavailable; ordinary API keys do not authorize the Admin Usage/Cost APIs.
- Identify windows by their reported duration. A Codex `primary` window can be weekly; never assume that `primary` means five hours.
- Missing windows, percentages, or reset times stay unavailable. Do not replace them with zero, infer a reset from the window duration, or infer quota from token logs or estimated cost. A reported zero is a measured zero.
- A Claude window with `observedAt` is the value a bridge chat turn last reported, not a fresh reading: report its observation time and that later use is not included.
- When `bridgeToken.renewDue` is true, report the D-day (`daysLeft`, or that the estimated date has passed) and that running `renew-claude-token` (or `renew-llm-logins`, which is Claude-only since the bridge's Gemini ACP retirement; `--check` only shows) in a terminal on that host renews it with one browser approval. For an explicitly configured ACP profile returning `auth_required`, report that the profile needs interactive re-authentication on that host. Never run a renewal for the user, sign in, or treat the reminder as a quota value.
- The Claude renewal reminder (`bridgeToken.renewDue`) starts 30 days before the estimated one-year expiry. Gemini has no one-year subscription token, and a Gemini API key is not a substitute because it is billed through the API.
- If a reset time is already in the past, identify that window as stale. Do not infer that its remaining allowance has reset to 100%.
- For subscription providers, `ok` means at least one reported utilization is available, and `unavailable` means no usable percentage was supplied. For `claude-api`, `ok` means the configured route's snapshot directory was readable; inspect the estimate and coverage fields, which may still be unknown. `error` means the query failed; use its sanitized reason. The process exits nonzero on an error while retaining successful providers.

## Use during work

Query when the user asks, or before sustained work whose scope depends on the remaining allowance. Reuse a recent result in the same conversation; do not poll on every tool call. A skill alone does not provide continuous updates or guaranteed invocation on every turn.

Report a constrained window before starting work likely to exhaust it. Do not silently change the chosen model, reasoning effort, task scope, or spending mode. A query failure does not authorize a login retry, token refresh script, dependency installation, or configuration change.

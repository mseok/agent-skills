---
name: llm-quota
description: Check live subscription quotas for Codex, Claude, and Gemini, plus recorded Claude API bridge cost estimates, without model inference. Use for remaining allowance, usage percentages, reset times, 내 사용량, 남은 한도, or recorded bridge API spend. Not for context-window usage, general API billing, or price estimates.
---

# LLM quota

Read subscription limits through the provider's official runtime. Codex and Claude use the calling CLI account; Gemini uses the selected dedicated ACP profile. No package installation, MCP registration, listener, or background polling is required. The bundled helper uses Node.js built-ins.

## User decisions

- 2026-10-18: "Ai quota mcp 그냥 그러면 기능 이해힌다음에 스킬로만들면안되나?"
- 2026-11-02: "quota skill 도 맞춰서 업데이트해주고." This accompanies the approved Mac mini Gemini ACP bridge deployment.
- 2026-11-03: "chatgpt 만 llm quota 를 하면 thinking 을 많이 하고 뭔가 chatgpt 내용만 반환하는거같은데, 이것도 다른 모델과 동일하게 모든 모델 결과 보여주고, context 오염도 안 시키게 해줄 수 있나?"
- 2026-11-03: "그럼 실행환경 분리해서 실제로 새로운 claude (api) 경로를 만들어줄래? 그리고 quota 도 업데이트해야할듯"
- 2026-11-09: "이런거 내가 설정안해도되게 renew 했으면 좋겟는데 자동으로." The proposal to show the usage that the bridge's subscription chat turns report when the four-week `/login` sign-in can no longer be read was approved: "좋은듯."
- 2026-11-09: "3번도 넣어주라." Approved proposal: a reminder in the quota result from 30 days before the bridge's one-year Claude token expires, and a sign-in failure that names the renewal command (Claude `renew-claude-token`, Gemini `renew-gemini-login`).
- 2026-11-09: "gemini 도 1년 간의 토큰을 오늘 만들어서 한 번에 관리되게 하자." Gemini offers no one-year subscription token (a Gemini API key never expires but is billed through the API, so it was not adopted); `renew-llm-logins` manages both sign-ins in one command.

## Query

Run the helper relative to this skill's directory:

```sh
node scripts/quota.mjs codex
node scripts/quota.mjs claude
node scripts/quota.mjs gemini
node scripts/quota.mjs claude-api
node scripts/quota.mjs all
```

- For an unqualified quota request, use `all`, regardless of the model running this chat. Select `codex`, `claude`, `gemini`, or `claude-api` only when the user explicitly asks for that provider alone.
- In a ChatGPT bridge with the local quota handler installed, a standalone skill selection, `!quota`, `$llm-quota`, or `llm quota` is answered locally with all providers. The visible quota exchange is excluded from later model requests. A request that also asks for analysis or planning still goes to the model. Installing this skill alone does not add that bridge handler or remove model context; that integration is verified on the Mac mini, not on the other hosts.
- A CLI must already be installed and logged in. Preserve the calling environment, including `CODEX_HOME` and `CLAUDE_CONFIG_DIR`. The result is for that local CLI account.
- Codex and Claude use initialization and quota control requests only. Gemini opens a fresh ACP session with no MCP servers and invokes exactly `/usage` only after the official runtime advertises it. This is a native local command, not a natural-language model prompt. Never fall back to asking a model about its quota. Authentication stays inside the official runtime; do not read credential files or Keychain, extract tokens, or replace this helper with `npx ai-quota`.
- Gemini uses the bridge's dedicated ACP profile, not the ordinary `agy` CLI login. Defaults are its `acp/runtime/agy_acp_server.par` and `acp/profile`. `GEMINI_ACP_BIN` and `GEMINI_ACP_PROFILE` select another already configured runtime/profile; `BRIDGE_STATE_DIR` selects the bridge directory. Do not copy credentials or sign in merely to repair a quota query. The official ACP runtime may retain native quota-session history.
- Codex uses `account/rateLimits/read` over app-server stdio. Claude uses its experimental `get_usage` control request over stream-json. Protocol details and sources are in [references/native-protocols.md](references/native-protocols.md); read that reference when diagnosing a protocol failure.
- When the native Claude reading fails or has no values (for example an expired `/login` sign-in; the bridge's one-year `setup-token` token cannot answer `get_usage`), the helper uses the selected bridge's `claude-rate-limits.json` if it exists. The bridge writes it from the `rate_limit_event` that each subscription chat turn reports (numbers and times only). Such a result has `status: "ok"`, a `source` naming the bridge observation, `nativeStatus`, and `observedAt` on the result and each window. `BRIDGE_STATE_DIR` selects the bridge; a host without that file keeps the native result.
- When the selected bridge has its one-year token file `claude-oauth-token`, the Claude result carries `bridgeToken` (`savedAt`, `estimatedExpiresAt`, `daysLeft`, `renewDue`). Only the file's modification time is read, never its contents; the expiry is estimated as one year after it was saved, because the CLI does not report it.
- A Gemini `error` with reason `auth_required` means the dedicated ACP profile's sign-in was refused (ACP auth_required or an authentication message), not a quota value.
- `claude-api` reads only local cost snapshots under the selected bridge's `claude-api/usage` directory. It never reads the API key or calls an inference or billing endpoint. `BRIDGE_STATE_DIR` selects the bridge. A host without that API route returns `api_not_configured`.

## Interpret

- Report provider, used/remaining percentage, reset time in the user's timezone, and `checkedAt`. Keep different quota buckets and model-scoped limits separate. These are shared subscription windows, not this conversation's token usage.
- For Gemini, retain the separate Gemini Models, Gemini 4 Argon, and Google-provided Claude/GPT groups when returned. The last group is not the user's separate Anthropic or OpenAI subscription. ACP `usage_update.used` and context size are token/context counters, not subscription utilization.
- Show Claude API separately as **this host bridge's recorded cost estimate**, with its recording period and any `unknownRuns`. It is not subscription utilization, final billing, account-wide spend, or remaining credit. Snapshots are cumulative per CLI process, so the helper replaces each process's total instead of adding successive turns. Active calls after the latest result, crashed calls without a result, and API use outside this bridge are not fully covered. No records means unknown, not zero spend. Remaining credit and account spend limits remain unavailable; ordinary API keys do not authorize the Admin Usage/Cost APIs.
- Identify windows by their reported duration. A Codex `primary` window can be weekly; never assume that `primary` means five hours.
- Missing windows, percentages, or reset times stay unavailable. Do not replace them with zero, infer a reset from the window duration, or infer quota from token logs or estimated cost. A reported zero is a measured zero.
- A Claude window with `observedAt` is the value a bridge chat turn last reported, not a fresh reading: report its observation time and that later use is not included.
- When `bridgeToken.renewDue` is true, report the D-day (`daysLeft`, or that the estimated date has passed) and that running `renew-claude-token` in a terminal on that host renews it with one browser approval. For Gemini `auth_required`, report that `renew-gemini-login` on that host signs the profile in again with a Google approval in that host's browser. `renew-llm-logins` on that host shows both sign-ins and runs only the renewal that is due (`--check` only shows). Never run a renewal for the user, sign in, or treat the reminder as a quota value.
- If a reset time is already in the past, identify that window as stale. Do not infer that its remaining allowance has reset to 100%.
- For subscription providers, `ok` means at least one reported utilization is available, and `unavailable` means no usable percentage was supplied. For `claude-api`, `ok` means the configured route's snapshot directory was readable; inspect the estimate and coverage fields, which may still be unknown. `error` means the query failed; use its sanitized reason. The process exits nonzero on an error while retaining successful providers.

## Use during work

Query when the user asks, or before sustained work whose scope depends on the remaining allowance. Reuse a recent result in the same conversation; do not poll on every tool call. A skill alone does not provide continuous updates or guaranteed invocation on every turn.

Report a constrained window before starting work likely to exhaust it. Do not silently change the chosen model, reasoning effort, task scope, or spending mode. A query failure does not authorize a login retry, token refresh script, dependency installation, or configuration change.

# Native quota protocols

Implementation and live queries were checked on 2026-10-18 with Codex CLI `0.162.1` and Claude Code `2.1.300` on the Mac mini. Recheck the protocol if a newer CLI rejects a request; do not fall back to credentials or a model prompt.

## What was retained from ai-quota

The [ai-quota project](https://github.com/metyatech/ai-quota) provides provider-specific quota fetchers, a CLI, and an MCP `get_quota` tool. Its current Claude implementation reads a credential file, refreshes rejected or expiring OAuth tokens, and writes updates back. Its Codex implementation reads `auth.json` and calls a ChatGPT backend endpoint. This skill retains the quota-reading purpose and missing-data distinctions, and delegates authentication to native CLIs and host runtimes instead. It implements Codex, Claude, Antigravity native model-roster quotas (`swarm{action: "models", all: true}` inside Antigravity sessions), and optional explicit Gemini ACP overrides; Copilot is outside its scope.

## Codex

Launch `codex app-server --listen stdio://`, send JSON-RPC `initialize`, then the `initialized` notification, then `account/rateLimits/read`. No thread or turn is created. See the [official app-server protocol](https://learn.chatgpt.com/docs/app-server#6-rate-limits-chatgpt).

Prefer the complete `rateLimitsByLimitId` map when present; otherwise read `rateLimits`. For each bucket, preserve `primary` and `secondary`, `usedPercent`, `windowDurationMins`, and `resetsAt`. Use the reported duration to identify 300-minute and 10080-minute windows. The live query returned a weekly `primary` with no five-hour window.

## Claude

Launch the CLI in print/stream-json mode with an open stdin. Send a `control_request` with `request.subtype: "initialize"`; after its successful `control_response`, send another with `request.subtype: "get_usage"`. Read `response.response.rate_limits_available` and `rate_limits`. Never write a `type: "user"` message.

The request is experimental. Percentage-valued `get_usage` responses differ from the fractional streamed rate-limit events. The helper consumes only `get_usage`, so it never multiplies utilization by 100.

Read account-wide `five_hour` and `seven_day`, any populated legacy `seven_day_*` buckets, and `model_scoped` entries. Keep model names as scope labels. Disable hooks, MCP discovery, tools, session persistence, IDE auto-connect, and auto-update for this short-lived helper; these flags apply to its subprocess only and do not alter user settings. The live query returned both account windows and a model-scoped weekly window.

Do not set `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`. On 2026-10-27 with Claude Code `2.1.311`, `get_usage` still answered `rate_limits_available: true` with that variable set, but `rate_limits` was `null`, so the helper reported `unavailable`; the same request without it returned `five_hour`, `seven_day` and a `model_scoped` window. If a later CLI again returns `rate_limits: null` while reporting availability, check the subprocess environment before suspecting the protocol.

## Failure and privacy boundaries

Each subprocess has one 25-second deadline and is terminated after its response. No automatic retry is performed. Missing CLIs, rejected initialization or quota requests, unexpected interactive requests, invalid stream JSON, and early exit produce a sanitized error. Raw initialization data, stderr, account identifiers, and token-bearing data are never printed or persisted. Native CLIs retain ownership of their ordinary authentication behavior.

## Gemini in Antigravity sessions and via official ACP

Inside an Antigravity session, `swarm{action: "models", all: true}` reads the local Language Server's live model table directly with zero model inference, returning `quota_remaining` percentages and `quota_resets` timestamps for Gemini models (`gemini-4-*`, `gemini-3.8-*`) and Google-provided Claude/GPT models.

On 2026-11-17 the third-party bridge's dedicated `acp/` directory and its Gemini login wrapper were retired across hosts (`renew-llm-logins` is now Claude-only). When `GEMINI_ACP_BIN` is unset and the retired `acp/runtime/agy_acp_server.par` binary is absent, `gemini-acp.mjs` returns `status: "unavailable", reason: "bridge_acp_retired"` so `node scripts/quota.mjs all` exits `0`.

When `GEMINI_ACP_BIN` and `GEMINI_ACP_PROFILE` are explicitly set to an active ACP runtime and profile (verified on 2026-11-02 with ACP 1.4.5), `gemini-acp.mjs` sends `initialize`, then `session/new` with no MCP servers, waits for the asynchronous `available_commands_update`, and invokes `/usage` via `session/prompt` only when advertised (documented in the [official release notes](https://antigravity.google/docs/changelog)). It parses explicit remaining percentages and reset timestamps across Gemini and Google-provided Claude/GPT groups, preserves native credential ownership, and aborts on any tool call or positive `usage_update.used` token activity. An explicit `GEMINI_ACP_BIN` or `GEMINI_ACP_PROFILE` path that does not exist remains an explicit `error` (`acp_runtime_missing` / `acp_profile_missing`), never a reason to install, log in, or read tokens.

## Claude API bridge estimates

The separate API route uses official Claude Code `--bare`, an explicit API key, and its own HOME/config directory. Installed CLI help confirms that bare mode never reads OAuth or the keychain. Subscription execution receives neither that key nor the API profile. There is no automatic switch to API billing.

The bridge stores one atomically replaced cost snapshot per CLI process from `total_cost_usd`. This is a cumulative client-side estimate, not authoritative billing; see [official cost tracking](https://code.claude.com/docs/en/agent-sdk/cost-tracking). The quota helper sums the latest snapshots and reports unknown records separately. It does not read credentials or make model requests. Actual account-wide usage/cost and spend-limit endpoints require an [Admin API key](https://platform.claude.com/docs/en/manage-claude/admin-api-keys); an ordinary inference key does not provide that access.

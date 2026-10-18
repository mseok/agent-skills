# Native quota protocols

Implementation and live queries were checked on 2026-10-18 with Codex CLI `0.162.1` and Claude Code `2.1.300` on the Mac mini. Recheck the protocol if a newer CLI rejects a request; do not fall back to credentials or a model prompt.

## What was retained from ai-quota

The [ai-quota project](https://github.com/metyatech/ai-quota) provides provider-specific quota fetchers, a CLI, and an MCP `get_quota` tool. Its current Claude implementation reads a credential file, refreshes rejected or expiring OAuth tokens, and writes updates back. Its Codex implementation reads `auth.json` and calls a ChatGPT backend endpoint. This skill retains the quota-reading purpose and missing-data distinctions, and delegates authentication to native CLIs instead. It implements the user's active Codex and Claude services; Gemini and Copilot are outside this skill's current scope.

## Codex

Launch `codex app-server --listen stdio://`, send JSON-RPC `initialize`, then the `initialized` notification, then `account/rateLimits/read`. No thread or turn is created. See the [official app-server protocol](https://learn.chatgpt.com/docs/app-server#6-rate-limits-chatgpt).

Prefer the complete `rateLimitsByLimitId` map when present; otherwise read `rateLimits`. For each bucket, preserve `primary` and `secondary`, `usedPercent`, `windowDurationMins`, and `resetsAt`. Use the reported duration to identify 300-minute and 10080-minute windows. The live query returned a weekly `primary` with no five-hour window.

## Claude

Launch the CLI in print/stream-json mode with an open stdin. Send a `control_request` with `request.subtype: "initialize"`; after its successful `control_response`, send another with `request.subtype: "get_usage"`. Read `response.response.rate_limits_available` and `rate_limits`. Never write a `type: "user"` message.

The request is experimental. T3's own [Claude provider](https://github.com/pingdotgg/t3code/blob/main/apps/server/src/provider/ClaudeProvider.ts) uses the SDK's experimental usage request without yielding a user prompt. Its [quota mapper](https://github.com/pingdotgg/t3code/blob/main/apps/server/src/provider/claudeUsageLimits.ts) distinguishes percentage-valued `get_usage` responses from fractional streamed rate-limit events. The helper consumes only `get_usage`, so it never multiplies utilization by 100.

Read account-wide `five_hour` and `seven_day`, any populated legacy `seven_day_*` buckets, and `model_scoped` entries. Keep model names as scope labels. Disable hooks, MCP discovery, tools, session persistence, IDE auto-connect, and auto-update for this short-lived helper; these flags apply to its subprocess only and do not alter user settings. The live query returned both account windows and a model-scoped weekly window.

## Failure and privacy boundaries

Each subprocess has one 25-second deadline and is terminated after its response. No automatic retry is performed. Missing CLIs, rejected initialization or quota requests, unexpected interactive requests, invalid stream JSON, and early exit produce a sanitized error. Raw initialization data, stderr, account identifiers, and token-bearing data are never printed or persisted. Native CLIs retain ownership of their ordinary authentication behavior.

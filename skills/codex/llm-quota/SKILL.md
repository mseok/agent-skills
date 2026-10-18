---
name: llm-quota
description: Check live 5-hour and weekly subscription quotas for Codex and Claude without an MCP server or model inference. Use for remaining allowance, usage percentages, reset times, 내 사용량, 남은 한도, or when planning sustained work depends on subscription capacity. Not for context-window usage, token accounting, or API cost estimates.
---

# LLM quota

Read the active local CLI account's subscription limits through the provider's own CLI. No package installation, MCP registration, listener, or background polling is required. The bundled helper uses Node.js built-ins.

## User decisions

- 2026-10-18: "Ai quota mcp 그냥 그러면 기능 이해힌다음에 스킬로만들면안되나?"

## Query

Run the helper relative to this skill's directory:

```sh
node scripts/quota.mjs codex
node scripts/quota.mjs claude
node scripts/quota.mjs all
```

- For "my quota", select the current agent's provider: Codex → `codex`; Claude → `claude`. Use `all` when both services are requested or the provider is unclear.
- A CLI must already be installed and logged in. Preserve the calling environment, including `CODEX_HOME` and `CLAUDE_CONFIG_DIR`. The result is for that local CLI account; do not claim it belongs to a custom T3 provider instance unless its binary and account binding have been established.
- The helper sends initialization and quota control requests only. It never sends a user prompt or starts a model turn. Authentication stays inside the native CLI; do not read credential files or Keychain, extract tokens, or replace this helper with `npx ai-quota`.
- Codex uses `account/rateLimits/read` over app-server stdio. Claude uses its experimental `get_usage` control request over stream-json. Protocol details and sources are in [references/native-protocols.md](references/native-protocols.md); read that reference when diagnosing a protocol failure.

## Interpret

- Report provider, used/remaining percentage, reset time in the user's timezone, and `checkedAt`. Keep different quota buckets and model-scoped limits separate. These are shared subscription windows, not this conversation's token usage.
- Identify windows by their reported duration. A Codex `primary` window can be weekly; never assume that `primary` means five hours.
- Missing windows, percentages, or reset times stay unavailable. Do not replace them with zero, infer a reset from the window duration, or infer quota from token logs or estimated cost. A reported zero is a measured zero.
- If a reset time is already in the past, identify that window as stale. Do not infer that its remaining allowance has reset to 100%.
- `ok` means at least one reported utilization is available. `unavailable` means the CLI supplied no usable subscription percentage. `error` means the query failed; use its sanitized reason. The process exits nonzero on an error, while retaining successful results from the other provider.

## Use during work

Query when the user asks, or before sustained work whose scope depends on the remaining allowance. Reuse a recent result in the same conversation; do not poll on every tool call. A skill alone does not provide continuous updates or guaranteed invocation on every turn.

Report a constrained window before starting work likely to exhaust it. Do not silently change the chosen model, reasoning effort, task scope, or spending mode. A query failure does not authorize a login retry, token refresh script, dependency installation, or configuration change.

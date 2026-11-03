---
name: llm-quota
description: Check live subscription quotas for Codex, Claude, and Gemini through the official Antigravity ACP profile, without model inference. Use for remaining allowance, usage percentages, reset times, 내 사용량, 남은 한도, or when planning sustained work depends on subscription capacity. Not for context-window usage, token accounting, or API cost estimates.
---

# LLM quota

Read subscription limits through the provider's official runtime. Codex and Claude use the calling CLI account; Gemini uses the selected dedicated ACP profile. No package installation, MCP registration, listener, or background polling is required. The bundled helper uses Node.js built-ins.

## User decisions

- 2026-10-18: "Ai quota mcp 그냥 그러면 기능 이해힌다음에 스킬로만들면안되나?"
- 2026-11-02: "quota skill 도 맞춰서 업데이트해주고." This accompanies the approved Mac mini Gemini ACP bridge deployment.
- 2026-11-03: "chatgpt 만 llm quota 를 하면 thinking 을 많이 하고 뭔가 chatgpt 내용만 반환하는거같은데, 이것도 다른 모델과 동일하게 모든 모델 결과 보여주고, context 오염도 안 시키게 해줄 수 있나?"

## Query

Run the helper relative to this skill's directory:

```sh
node scripts/quota.mjs codex
node scripts/quota.mjs claude
node scripts/quota.mjs gemini
node scripts/quota.mjs all
```

- For an unqualified quota request, use `all`, regardless of the model running this chat. Select `codex`, `claude`, or `gemini` only when the user explicitly asks for that provider alone.
- In a ChatGPT bridge with the local quota handler installed, a standalone skill selection, `!quota`, `$llm-quota`, or `llm quota` is answered locally with all providers. The visible quota exchange is excluded from later model requests. A request that also asks for analysis or planning still goes to the model. Installing this skill alone does not add that bridge handler or remove model context; that integration is verified on the Mac mini, not on the other hosts.
- A CLI must already be installed and logged in. Preserve the calling environment, including `CODEX_HOME` and `CLAUDE_CONFIG_DIR`. The result is for that local CLI account.
- Codex and Claude use initialization and quota control requests only. Gemini opens a fresh ACP session with no MCP servers and invokes exactly `/usage` only after the official runtime advertises it. This is a native local command, not a natural-language model prompt. Never fall back to asking a model about its quota. Authentication stays inside the official runtime; do not read credential files or Keychain, extract tokens, or replace this helper with `npx ai-quota`.
- Gemini uses the bridge's dedicated ACP profile, not the ordinary `agy` CLI login. Defaults are its `acp/runtime/agy_acp_server.par` and `acp/profile`. `GEMINI_ACP_BIN` and `GEMINI_ACP_PROFILE` select another already configured runtime/profile; `BRIDGE_STATE_DIR` selects the bridge directory. Do not copy credentials or sign in merely to repair a quota query. The official ACP runtime may retain native quota-session history.
- Codex uses `account/rateLimits/read` over app-server stdio. Claude uses its experimental `get_usage` control request over stream-json. Protocol details and sources are in [references/native-protocols.md](references/native-protocols.md); read that reference when diagnosing a protocol failure.

## Interpret

- Report provider, used/remaining percentage, reset time in the user's timezone, and `checkedAt`. Keep different quota buckets and model-scoped limits separate. These are shared subscription windows, not this conversation's token usage.
- For Gemini, retain the separate Gemini Models, Gemini 4 Argon, and Google-provided Claude/GPT groups when returned. The last group is not the user's separate Anthropic or OpenAI subscription. ACP `usage_update.used` and context size are token/context counters, not subscription utilization.
- Identify windows by their reported duration. A Codex `primary` window can be weekly; never assume that `primary` means five hours.
- Missing windows, percentages, or reset times stay unavailable. Do not replace them with zero, infer a reset from the window duration, or infer quota from token logs or estimated cost. A reported zero is a measured zero.
- If a reset time is already in the past, identify that window as stale. Do not infer that its remaining allowance has reset to 100%.
- `ok` means at least one reported utilization is available. `unavailable` means the CLI supplied no usable subscription percentage. `error` means the query failed; use its sanitized reason. The process exits nonzero on an error, while retaining successful results from the other provider.

## Use during work

Query when the user asks, or before sustained work whose scope depends on the remaining allowance. Reuse a recent result in the same conversation; do not poll on every tool call. A skill alone does not provide continuous updates or guaranteed invocation on every turn.

Report a constrained window before starting work likely to exhaust it. Do not silently change the chosen model, reasoning effort, task scope, or spending mode. A query failure does not authorize a login retry, token refresh script, dependency installation, or configuration change.

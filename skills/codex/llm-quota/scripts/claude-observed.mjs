// Claude subscription usage as the bridge's own subscription turns report it. Each Claude Code
// turn made with the bridge's one-year token streams a `rate_limit_event` whose unifiedWindows
// carry utilization (0..1) and reset times (epoch seconds), observed 2026-11-09. The token itself
// cannot answer the `get_usage` quota request (rate_limits_available=false), so when the stored
// /login sign-in has expired the quota falls back to the latest values seen here, labelled with
// the time they were seen. Only numbers and times are stored; no ids, text or credentials.
// User decision 2026-11-09: "이런거 내가 설정안해도되게 renew 했으면 좋겟는데 자동으로." / "좋은듯."
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

export const OBSERVED_FILE = 'claude-rate-limits.json';
// The one-year subscription token that claude-engine.mjs passes to subscription Claude children.
export const TOKEN_FILE = 'claude-oauth-token';
// `claude setup-token` tokens are valid for one year (Claude Code docs, Authentication). The CLI
// does not report the date, so the expiry is estimated from when the file was saved; the warning
// starts this many days before it. User decision 2026-11-09: "3번도 넣어주라." (D-30 line)
export const TOKEN_VALID_DAYS = 365;
export const TOKEN_WARN_DAYS = 30;
export const DEFAULT_STATE_DIR = process.env.BRIDGE_STATE_DIR ?? path.join(os.homedir(), process.platform === 'darwin' ? 'Library/Application Support/chatgpt-claude-bridge' : '.codex/claude-bridge/bridge');

const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const fraction = value => typeof value === 'number' && Number.isFinite(value) && value >= 0 ? value : null;
const epoch = value => typeof value === 'number' && Number.isFinite(value) && value > 0 ? value : null;
const WINDOW_KEY = /^(five_hour|seven_day(_[a-z0-9_]+)?)$/;

function read(file) {
  try {
    const data = JSON.parse(fs.readFileSync(file, 'utf8'));
    return object(data) && object(data.windows) ? data : null;
  } catch {
    return null;
  }
}

// Merges one rate_limit_event into the snapshot; each window keeps the time it was last seen.
export function recordClaudeRateLimit(stateDir, info, now = new Date()) {
  if (!stateDir || !object(info)) return false;
  const seen = {};
  if (object(info.unifiedWindows)) {
    for (const [key, raw] of Object.entries(info.unifiedWindows)) {
      if (WINDOW_KEY.test(key) && object(raw) && fraction(raw.utilization) !== null) seen[key] = { utilization: raw.utilization, resetsAt: epoch(raw.resetsAt) };
    }
  } else if (typeof info.rateLimitType === 'string' && WINDOW_KEY.test(info.rateLimitType) && fraction(info.utilization) !== null) {
    seen[info.rateLimitType] = { utilization: info.utilization, resetsAt: epoch(info.resetsAt) };
  }
  if (!Object.keys(seen).length) return false;
  const file = path.join(stateDir, OBSERVED_FILE);
  const observedAt = now.toISOString();
  const windows = { ...(read(file)?.windows ?? {}) };
  for (const [key, value] of Object.entries(seen)) windows[key] = { ...value, observedAt };
  const tmp = `${file}.${process.pid}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify({ schemaVersion: 1, source: 'rate_limit_event', updatedAt: observedAt, windows }) + '\n', { mode: 0o600 });
  fs.renameSync(tmp, file);
  return true;
}

// Windows in the quota helper's shape, or null when nothing has been observed. A null stateDir
// (a caller that did not name a bridge) reads nothing.
export function readClaudeObserved({ stateDir = DEFAULT_STATE_DIR } = {}) {
  if (!stateDir) return null;
  const data = read(path.join(stateDir, OBSERVED_FILE));
  if (!data) return null;
  const windows = Object.entries(data.windows).flatMap(([id, raw]) => {
    if (!WINDOW_KEY.test(id) || !object(raw) || fraction(raw.utilization) === null) return [];
    const usedPercent = Math.round(raw.utilization * 1000) / 10;
    return [{
      id, bucket: 'claude', scope: id === 'five_hour' || id === 'seven_day' ? 'account' : id.slice(10),
      windowMinutes: id === 'five_hour' ? 300 : 10080,
      usedPercent, remainingPercent: Math.max(0, Math.round((100 - usedPercent) * 10) / 10),
      resetsAt: raw.resetsAt ? new Date(raw.resetsAt * 1000).toISOString() : null,
      observedAt: typeof raw.observedAt === 'string' ? raw.observedAt : null,
    }];
  });
  if (!windows.length) return null;
  const observedAt = windows.map(w => w.observedAt).filter(Boolean).sort().at(-1) ?? null;
  return { windows, observedAt };
}

// A failed or empty native Claude reading, replaced by the observed values when there are any.
export function withObservedClaude(result, options = {}) {
  if (result?.status === 'ok') return result;
  const observed = readClaudeObserved(options);
  if (!observed) return result;
  const { reason, ...rest } = result ?? {};
  return {
    ...rest, provider: 'claude', status: 'ok', source: 'bridge-observed rate_limit_event (subscription chat turns)',
    observedAt: observed.observedAt, nativeStatus: result?.status ?? null, ...(reason ? { nativeReason: reason } : {}),
    windows: observed.windows,
  };
}

// The token's estimated expiry. Only the file's modification time is read, never its contents.
export function readTokenAge({ stateDir = DEFAULT_STATE_DIR, now = new Date() } = {}) {
  if (!stateDir) return null;
  let stat;
  try {
    stat = fs.statSync(path.join(stateDir, TOKEN_FILE));
  } catch {
    return null;
  }
  if (!stat.isFile()) return null;
  const expires = new Date(stat.mtimeMs + TOKEN_VALID_DAYS * 86_400_000);
  const daysLeft = Math.ceil((expires.getTime() - now.getTime()) / 86_400_000);
  return { savedAt: stat.mtime.toISOString(), estimatedExpiresAt: expires.toISOString(), daysLeft, renewDue: daysLeft <= TOKEN_WARN_DAYS };
}

// A Claude quota result with the bridge token's age attached when the bridge has a token.
export function withTokenAge(result, options = {}) {
  const age = readTokenAge(options);
  return age ? { ...result, bridgeToken: age } : result;
}

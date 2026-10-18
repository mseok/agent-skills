#!/usr/bin/env node
import { spawn } from 'node:child_process';
import { realpathSync } from 'node:fs';
import { createInterface } from 'node:readline';
import { pathToFileURL } from 'node:url';

const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const percentage = value => typeof value === 'number' && Number.isFinite(value) && value >= 0 ? value : null;

function resetTime(value) {
  if (typeof value !== 'number' && typeof value !== 'string') return null;
  const date = new Date(typeof value === 'number' ? value * 1000 : value);
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

function windowValue({ id, bucket, scope, minutes, used, reset }) {
  const usedPercent = percentage(used);
  return {
    id, bucket, scope,
    windowMinutes: typeof minutes === 'number' && Number.isFinite(minutes) && minutes > 0 ? minutes : null,
    usedPercent,
    remainingPercent: usedPercent === null ? null : Math.max(0, 100 - usedPercent),
    resetsAt: resetTime(reset),
  };
}

export function normalizeCodex(result) {
  if (!object(result)) return [];
  const buckets = object(result.rateLimitsByLimitId) && Object.keys(result.rateLimitsByLimitId).length
    ? Object.entries(result.rateLimitsByLimitId)
    : object(result.rateLimits) ? [[result.rateLimits.limitId ?? 'codex', result.rateLimits]] : [];
  return buckets.flatMap(([bucket, snapshot]) => {
    if (!object(snapshot)) return [];
    return ['primary', 'secondary'].flatMap(slot => {
      const raw = snapshot[slot];
      return object(raw) ? [windowValue({
        id: slot, bucket, scope: 'account', minutes: raw.windowDurationMins,
        used: raw.usedPercent, reset: raw.resetsAt,
      })] : [];
    });
  });
}

export function normalizeClaude(result) {
  if (!object(result) || result.rate_limits_available !== true || !object(result.rate_limits)) return [];
  const limits = result.rate_limits;
  const windows = Object.entries(limits).flatMap(([id, raw]) => {
    if (id !== 'five_hour' && id !== 'seven_day' && !id.startsWith('seven_day_')) return [];
    if (!object(raw) || !('utilization' in raw)) return [];
    return [windowValue({
      id, bucket: 'claude', scope: id === 'five_hour' || id === 'seven_day' ? 'account' : id.slice(10),
      minutes: id === 'five_hour' ? 300 : 10080, used: raw.utilization, reset: raw.resets_at,
    })];
  });
  if (Array.isArray(limits.model_scoped)) {
    limits.model_scoped.forEach((raw, index) => {
      if (!object(raw) || typeof raw.display_name !== 'string') return;
      windows.push(windowValue({
        id: `model_scoped_${index}`, bucket: 'claude', scope: raw.display_name,
        minutes: 10080, used: raw.utilization, reset: raw.resets_at,
      }));
    });
  }
  return windows;
}

const sources = {
  codex: 'native CLI: account/rateLimits/read',
  claude: 'native CLI: get_usage (experimental)',
};

export function readQuota(provider, { spawnChild = spawn, timeoutMs = 25_000 } = {}) {
  return new Promise(resolve => {
    const args = provider === 'codex' ? ['app-server', '--listen', 'stdio://'] : [
      '--print', '--input-format', 'stream-json', '--output-format', 'stream-json', '--verbose',
      '--no-session-persistence', '--setting-sources', '', '--settings', '{"disableAllHooks":true}',
      '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--tools', '',
    ];
    const env = provider === 'codex' ? process.env : {
      ...process.env, ENABLE_CLAUDEAI_MCP_SERVERS: 'false', CLAUDE_CODE_AUTO_CONNECT_IDE: '0',
      CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC: '1', DISABLE_AUTOUPDATER: '1',
    };
    const child = spawnChild(provider, args, { stdio: ['pipe', 'pipe', 'pipe'], env });
    const lines = createInterface({ input: child.stdout });
    let settled = false;
    let phase = 'initialize';
    const timer = setTimeout(() => finish({ status: 'error', reason: 'timeout', phase }), timeoutMs);

    function finish(result) {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      lines.close();
      child.stdin.end();
      child.kill('SIGTERM');
      const killTimer = setTimeout(() => child.kill('SIGKILL'), 1000);
      killTimer.unref();
      child.once('close', () => clearTimeout(killTimer));
      resolve({ provider, source: sources[provider], checkedAt: new Date().toISOString(), windows: [], ...result });
    }

    const send = message => child.stdin.write(`${JSON.stringify(message)}\n`);
    function requestUsage() {
      phase = 'quota';
      if (provider === 'codex') {
        send({ method: 'initialized' });
        send({ id: 2, method: 'account/rateLimits/read' });
      } else {
        send({ type: 'control_request', request_id: 'quota-read', request: { subtype: 'get_usage' } });
      }
    }

    child.stderr.resume();
    child.on('error', error => finish({ status: 'error', reason: error.code === 'ENOENT' ? 'cli_missing' : 'spawn_failed', phase }));
    child.stdin.on('error', () => finish({ status: 'error', reason: 'cli_input_closed', phase }));
    child.on('close', () => finish({ status: 'error', reason: 'cli_exited_before_response', phase }));
    lines.on('line', line => {
      if (settled || !line.trim()) return;
      let message;
      try { message = JSON.parse(line); }
      catch { finish({ status: 'error', reason: 'invalid_protocol_json', phase }); return; }
      if (!object(message)) {
        finish({ status: 'error', reason: 'invalid_protocol_message', phase });
        return;
      }
      if (message.type === 'control_request' || (provider === 'codex' && 'id' in message && 'method' in message)) {
        finish({ status: 'error', reason: 'interaction_required', phase });
        return;
      }
      const response = provider === 'codex' ? message : message.type === 'control_response' ? message.response : null;
      if (!object(response)) return;
      const id = provider === 'codex' ? response.id : response.request_id;
      const expected = phase === 'initialize' ? (provider === 'codex' ? 1 : 'quota-init') : (provider === 'codex' ? 2 : 'quota-read');
      if (id !== expected) return;
      if (response.error || (provider === 'claude' && response.subtype !== 'success')) {
        finish({ status: 'error', reason: 'native_request_rejected', phase });
        return;
      }
      if (phase === 'initialize') { requestUsage(); return; }
      const raw = provider === 'codex' ? response.result : response.response;
      if (!object(raw)) { finish({ status: 'error', reason: 'invalid_quota_response', phase }); return; }
      const windows = provider === 'codex' ? normalizeCodex(raw) : normalizeClaude(raw);
      finish({ status: windows.some(window => window.usedPercent !== null) ? 'ok' : 'unavailable', windows });
    });

    if (provider === 'codex') {
      send({ id: 1, method: 'initialize', params: { clientInfo: { name: 'llm_quota_skill', version: '1.0.0' }, capabilities: { experimentalApi: true } } });
    } else {
      send({ type: 'control_request', request_id: 'quota-init', request: { subtype: 'initialize', hooks: {} } });
    }
  });
}

async function main() {
  const [target = 'all', ...extra] = process.argv.slice(2);
  if (target === '--help' && !extra.length) {
    console.log('Usage: node quota.mjs [codex|claude|all]\nRead native CLI subscription quotas without model inference.');
    return;
  }
  if (!['codex', 'claude', 'all'].includes(target) || extra.length) {
    console.log(JSON.stringify({ status: 'error', reason: 'usage: quota.mjs [codex|claude|all]' }));
    process.exitCode = 2;
    return;
  }
  const providers = await Promise.all((target === 'all' ? ['codex', 'claude'] : [target]).map(provider => readQuota(provider)));
  console.log(JSON.stringify({ schemaVersion: 1, accountScope: 'calling environment native CLI login', providers }, null, 2));
  if (providers.some(result => result.status === 'error')) process.exitCode = 1;
}

if (process.argv[1] && pathToFileURL(realpathSync(process.argv[1])).href === import.meta.url) await main();

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

export function readClaudeApiUsage({ stateDir = process.env.BRIDGE_STATE_DIR ?? path.join(os.homedir(), process.platform === 'darwin' ? 'Library/Application Support/chatgpt-claude-bridge' : '.codex/claude-bridge/bridge') } = {}) {
  const root = path.join(stateDir, 'claude-api');
  const configured = fs.existsSync(path.join(stateDir, 'claude-api-on')) && fs.existsSync(path.join(root, 'api-key'));
  const result = { provider: 'claude-api', source: 'local Claude Code API cost snapshots', accountScope: 'this host bridge only, all recorded API runs', checkedAt: new Date().toISOString(), configured, windows: [], remainingCreditUsd: null, accountSpendLimitUsd: null };
  if (!configured) return { ...result, status: 'unavailable', reason: 'api_not_configured' };
  try {
    const dir = path.join(root, 'usage');
    const files = fs.existsSync(dir) ? fs.readdirSync(dir).filter(name => name.endsWith('.json')) : [];
    let estimatedCostUsd = 0, unknownRuns = 0, recordedSince = null, updatedAt = null;
    for (const name of files) {
      const row = JSON.parse(fs.readFileSync(path.join(dir, name), 'utf8'));
      if (typeof row.estimatedCostUsd === 'number' && Number.isFinite(row.estimatedCostUsd) && row.estimatedCostUsd >= 0) estimatedCostUsd += row.estimatedCostUsd;
      else unknownRuns++;
      for (const field of ['startedAt', 'updatedAt']) if (typeof row[field] !== 'string' || !Number.isFinite(Date.parse(row[field]))) throw new Error();
      if (recordedSince === null || row.startedAt < recordedSince) recordedSince = row.startedAt;
      if (updatedAt === null || row.updatedAt > updatedAt) updatedAt = row.updatedAt;
    }
    return { ...result, status: 'ok', estimatedCostUsd: files.length > unknownRuns ? estimatedCostUsd : null, recordedRuns: files.length, unknownRuns, recordedSince, updatedAt, billingAuthoritative: false };
  } catch {
    return { ...result, status: 'error', reason: 'local_api_usage_unreadable' };
  }
}

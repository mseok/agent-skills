import assert from 'node:assert/strict';
import { test } from 'node:test';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { readQuota } from '../scripts/quota.mjs';

test('API snapshots are separate estimates and never read the key or launch a CLI', async () => {
  const stateDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quota-api-'));
  const run = () => readQuota('claude-api', { claudeApi: { stateDir }, spawnChild: () => { throw new Error('must not spawn'); } });
  try {
    assert.equal((await run()).reason, 'api_not_configured');
    fs.mkdirSync(path.join(stateDir, 'claude-api/usage'), { recursive: true });
    fs.writeFileSync(path.join(stateDir, 'claude-api-on'), '');
    fs.writeFileSync(path.join(stateDir, 'claude-api/api-key'), 'PRIVATE_SECRET_SENTINEL', { mode: 0o000 });
    assert.equal((await run()).estimatedCostUsd, null);
    const base = { startedAt: '2026-11-03T00:00:00Z', updatedAt: '2026-11-03T01:00:00Z' };
    const file = path.join(stateDir, 'claude-api/usage/one.json');
    fs.writeFileSync(file, JSON.stringify({ ...base, estimatedCostUsd: 1.2 }));
    fs.writeFileSync(file, JSON.stringify({ ...base, estimatedCostUsd: 1.7 }));
    fs.writeFileSync(path.join(stateDir, 'claude-api/usage/two.json'), JSON.stringify({ ...base, estimatedCostUsd: null }));
    const r = await run();
    assert.equal(r.estimatedCostUsd, 1.7); assert.equal(r.unknownRuns, 1);
    assert.equal(r.billingAuthoritative, false); assert.equal(r.remainingCreditUsd, null);
    assert.doesNotMatch(JSON.stringify(r), /PRIVATE_SECRET_SENTINEL/);
    fs.writeFileSync(file, 'PRIVATE_BAD_RECORD');
    const bad = await run(); assert.equal(bad.status, 'error'); assert.doesNotMatch(JSON.stringify(bad), /PRIVATE_BAD_RECORD/);
  } finally { fs.rmSync(stateDir, { recursive: true, force: true }); }
});

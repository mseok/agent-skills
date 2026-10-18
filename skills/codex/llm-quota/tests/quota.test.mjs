import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { test } from 'node:test';
import { normalizeClaude, normalizeCodex, readQuota } from '../scripts/quota.mjs';

test('a weekly primary is preserved without inventing a five-hour quota or reset', () => {
  const windows = normalizeCodex({ rateLimits: { primary: { usedPercent: 0, windowDurationMins: 10080 } } });
  assert.equal(windows.length, 1);
  assert.equal(windows[0].windowMinutes, 10080);
  assert.equal(windows[0].usedPercent, 0);
  assert.equal(windows[0].remainingPercent, 100);
  assert.equal(windows[0].resetsAt, null);
});

test('Codex buckets remain separate and the complete map supersedes the legacy duplicate', () => {
  const result = {
    rateLimits: { primary: { usedPercent: 99, windowDurationMins: 300 } },
    rateLimitsByLimitId: {
      codex: { primary: { usedPercent: 25, windowDurationMins: 300, resetsAt: 1800000000 } },
      codex_other: { secondary: { usedPercent: 60, windowDurationMins: 10080 } },
    },
    account: 'PRIVATE_ACCOUNT_SENTINEL', credits: { balance: 'PRIVATE_CREDITS_SENTINEL' },
  };
  const windows = normalizeCodex(result);
  assert.deepEqual(windows.map(window => [window.bucket, window.remainingPercent]), [['codex', 75], ['codex_other', 40]]);
  assert.equal(windows[0].resetsAt, '2027-01-15T08:00:00.000Z');
  assert.doesNotMatch(JSON.stringify(windows), /PRIVATE_/);
});

test('Claude get_usage is percentage-valued and retains model scope and missing fields', () => {
  const windows = normalizeClaude({ rate_limits_available: true, rate_limits: {
    five_hour: { utilization: 5, resets_at: '2026-10-18T02:00:00Z' },
    seven_day: null,
    seven_day_sonnet: { utilization: 0, resets_at: null },
    seven_day_breakdown: {},
    model_scoped: [{ display_name: 'Example model', utilization: null, resets_at: 'invalid' }],
  } });
  assert.equal(windows.length, 3);
  assert.equal(windows[0].usedPercent, 5);
  assert.equal(windows[0].remainingPercent, 95);
  assert.equal(windows[1].scope, 'sonnet');
  assert.equal(windows[1].usedPercent, 0);
  assert.equal(windows[2].scope, 'Example model');
  assert.equal(windows[2].usedPercent, null);
  assert.equal(windows[2].remainingPercent, null);
  assert.equal(windows[2].resetsAt, null);
  assert.deepEqual(normalizeClaude({ rate_limits_available: false, rate_limits: { five_hour: { utilization: 0 } } }), []);
});

function fakeCli(provider, { rejected = false, malformed = false, silent = false } = {}) {
  return (command, args, options) => {
    assert.equal(command, provider);
    assert.equal(options.stdio.join(','), 'pipe,pipe,pipe');
    if (provider === 'codex') assert.deepEqual(args, ['app-server', '--listen', 'stdio://']);
    else {
      assert.ok(args.includes('--no-session-persistence'));
      assert.ok(args.includes('--strict-mcp-config'));
      assert.ok(args.includes('{"disableAllHooks":true}'));
    }
    const program = `
      const {createInterface}=require('node:readline');
      const provider=${JSON.stringify(provider)};
      const rejected=${rejected}, malformed=${malformed}, silent=${silent};
      let stage=0;
      createInterface({input:process.stdin}).on('line',line=>{
        const m=JSON.parse(line);
        if(silent)return;
        if(malformed){console.log('not-json PRIVATE_STDOUT_SENTINEL');return;}
        const type=provider==='codex'?m.method:m.request?.subtype;
        const expected=stage===0?'initialize':provider==='codex'?'account/rateLimits/read':'get_usage';
        if(type==='initialized'&&provider==='codex')return;
        if(type!==expected||m.type==='user'){process.exit(91);return;}
        stage++;
        const id=provider==='codex'?m.id:m.request_id;
        const body=stage===1?{account:'PRIVATE_ACCOUNT_SENTINEL'}:provider==='codex'
          ?{rateLimits:{primary:{usedPercent:25,windowDurationMins:10080}}}
          :{rate_limits_available:true,rate_limits:{five_hour:{utilization:5,resets_at:null}}};
        if(rejected){process.stderr.write('PRIVATE_STDERR_SENTINEL');}
        console.log(JSON.stringify(provider==='codex'
          ?rejected?{id,error:{message:'PRIVATE_ERROR_SENTINEL'}}:{id,result:body}
          :{type:'control_response',response:rejected?{request_id:id,subtype:'error',error:'PRIVATE_ERROR_SENTINEL'}:{request_id:id,subtype:'success',response:body}}));
      });
    `;
    return spawn(process.execPath, ['-e', program], options);
  };
}

for (const provider of ['codex', 'claude']) {
  test(`${provider}: initialization and quota only, with identity-free output`, async () => {
    const result = await readQuota(provider, { spawnChild: fakeCli(provider), timeoutMs: 3000 });
    assert.equal(result.status, 'ok');
    assert.equal(result.windows.length, 1);
    assert.doesNotMatch(JSON.stringify(result), /PRIVATE_/);
  });

  test(`${provider}: rejection fails closed without exposing native errors or stderr`, async () => {
    const result = await readQuota(provider, { spawnChild: fakeCli(provider, { rejected: true }), timeoutMs: 3000 });
    assert.equal(result.status, 'error');
    assert.equal(result.reason, 'native_request_rejected');
    assert.equal(result.phase, 'initialize');
    assert.doesNotMatch(JSON.stringify(result), /PRIVATE_/);
  });
}

test('invalid protocol JSON is an explicit error, not an empty successful quota', async () => {
  const result = await readQuota('codex', { spawnChild: fakeCli('codex', { malformed: true }), timeoutMs: 3000 });
  assert.equal(result.reason, 'invalid_protocol_json');
  assert.equal(result.status, 'error');
  assert.doesNotMatch(JSON.stringify(result), /PRIVATE_/);
});

test('an unresponsive native CLI stops at the deadline', async () => {
  const result = await readQuota('claude', { spawnChild: fakeCli('claude', { silent: true }), timeoutMs: 100 });
  assert.equal(result.reason, 'timeout');
  assert.equal(result.status, 'error');
});

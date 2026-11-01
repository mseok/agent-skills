#!/usr/bin/env python3
"""agent_cli.py — run a builder or a judge on whichever CLI serves the requested model.

    claude-*            → `claude -p`   (Claude Opus 5.5, Fable 5.1, …)
    anything else       → `codex exec`  (gpt-6-astra, gpt-6.1-sol, gpt-6.1-terra, …; effort via -c model_reasoning_effort="…")

run(prompt, model, effort, cwd, role, timeout, add_dirs) returns one env dict whatever the backend:
    result            final assistant message (text)
    total_cost_usd    Claude: from the CLI; Codex: None (subscription — the usage tokens are the spend record)
    usage             Claude: the CLI's usage block; Codex: the turn.completed usage (input/cached/output/reasoning tokens)
    num_turns, duration_ms, is_error, error_text, no_json (True when the CLI returned nothing parseable)
    backend, model_requested, model_reported (Claude: modelUsage keys; Codex: None — the event stream carries no model
                      field, verified 2026-11-01 with codex-cli 0.164.0, so the request is the only record), cli_version

Roles. 'judge' = read-only tools and isolation from the user's own instructions: Claude gets `--setting-sources '' --strict-mcp-config`
(2026-11-01: a judge loaded the global CLAUDE.md and ran a bio-safe-reading pre-screen on an ML deck); Codex gets a minimal CODEX_HOME
(auth.json link + the bridge base-URL line only) and `-s read-only` — with the normal home a one-line probe answered "yes" to
"do your instructions contain 'Shared working agreement'" and carried 28k input tokens, with the minimal home "no" and 14k.
Builder prompts: Codex builders get references/builder-notes-gpt.md appended (builder_prompt); Claude builders get the prompt as written.
'builder' = edit + shell in the user's normal environment (that is what the user's own sessions look like): Claude `acceptEdits`
with Read/Edit/Write/Bash…, Codex `-s danger-full-access` because headless Chrome (check_layout.py, shots.sh) aborts inside the
seatbelt sandbox of `-s workspace-write` (observed 2026-11-01: "Abort trap: 6", no DOM dump) — the same trust the Claude builder has.

probe(model) is the cheap quota check goal_loop.py runs before each iteration; LIMIT matches the usage-limit wording of both CLIs.
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

LIMIT = re.compile(r'(usage limit|rate limit|rate_limit|limit reached|too many requests|429|quota|overloaded|insufficient_quota)', re.I)
JUDGE_HOME = Path(os.environ.get('CODEX_JUDGE_HOME', str(Path.home() / '.codex-judge-home')))
GPT_NOTES = Path(__file__).resolve().parent.parent / 'references' / 'builder-notes-gpt.md'


def backend_of(model):
    return 'claude' if str(model).startswith('claude') else 'codex'


def reset_wait(text, default=18300):
    """Seconds to sleep after a usage-limit answer: the reset time in the message ('resets in 2h 15m') + 5 min when parseable, else the default (5 h 5 min)."""
    m = re.search(r'(\d+)\s*h(?:ours?)?\s*(\d+)?\s*m?', text or '', re.I)
    if m and 'reset' in (text or '').lower():
        return int(m.group(1)) * 3600 + int(m.group(2) or 0) * 60 + 300
    return default


def user_owned(work):
    """Slides a loop builder must not touch: storyline entries with owner == 'user' (the closing slide's question panel the user rewrites per talk)."""
    p = Path(work) / 'storyline.json'
    if not p.exists():
        return []
    st = json.loads(p.read_text(encoding='utf-8'))
    return [f"{i + 1}장({s.get('id')})" for i, s in enumerate(st.get('slides', [])) if s.get('owner') == 'user']


def cli_version(backend):
    try:
        r = subprocess.run([backend, '--version'], capture_output=True, text=True, timeout=20)
        return (r.stdout or r.stderr).strip().splitlines()[0][:80]
    except (OSError, subprocess.SubprocessError, IndexError):
        return None


def judge_home():
    """A CODEX_HOME that carries only the login and the bridge base URL: no AGENTS.md, no skills, no MCP servers, no hooks."""
    JUDGE_HOME.mkdir(parents=True, exist_ok=True)
    auth = JUDGE_HOME / 'auth.json'
    src = Path.home() / '.codex' / 'auth.json'
    if not auth.exists() and src.exists():
        auth.symlink_to(src)
    cfg = JUDGE_HOME / 'config.toml'
    if not cfg.exists():
        lines = []
        user_cfg = Path.home() / '.codex' / 'config.toml'
        if user_cfg.exists():
            lines = [l for l in user_cfg.read_text(encoding='utf-8').splitlines() if l.startswith('openai_base_url')]
        cfg.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return JUDGE_HOME


def _run_claude(prompt, model, effort, cwd, role, timeout, add_dirs):
    cmd = ['claude', '-p', prompt, '--model', model, '--effort', effort, '--output-format', 'json']
    if role == 'judge':
        cmd += ['--allowedTools', 'Read', '--setting-sources', '', '--strict-mcp-config']
    else:
        cmd += ['--permission-mode', 'acceptEdits', '--allowedTools', 'Read,Edit,MultiEdit,Write,Bash,Glob,Grep', '--disallowedTools', 'Task,WebFetch,WebSearch']
        for d in add_dirs:
            cmd += ['--add-dir', str(d)]
    t0 = time.time()
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    env = {'backend': 'claude', 'model_requested': model, 'effort': effort, 'role': role, 'cli_version': cli_version('claude'), 'exit_code': r.returncode}
    try:
        j = json.loads(r.stdout)
    except json.JSONDecodeError:
        env.update({'result': r.stdout[-3000:], 'error_text': (r.stdout[-1500:] + r.stderr[-1500:]), 'is_error': True, 'no_json': True,
                    'total_cost_usd': None, 'num_turns': None, 'duration_ms': int((time.time() - t0) * 1000), 'usage': None, 'model_reported': None})
        return env
    env.update({'result': j.get('result') or '', 'total_cost_usd': j.get('total_cost_usd'), 'num_turns': j.get('num_turns'), 'duration_ms': j.get('duration_ms'),
                'usage': j.get('usage'), 'is_error': bool(j.get('is_error')), 'error_text': r.stderr[-1500:] if r.returncode else '', 'no_json': False,
                'model_reported': sorted((j.get('modelUsage') or {}).keys()) or None, 'session_id': j.get('session_id')})
    return env


def _run_codex(prompt, model, effort, cwd, role, timeout, add_dirs):
    td = tempfile.mkdtemp(prefix='agent-cli-codex.')
    last = Path(td) / 'last.txt'; events = Path(td) / 'events.jsonl'
    cmd = ['codex', 'exec', '-m', model, '-c', f'model_reasoning_effort="{effort}"', '--skip-git-repo-check', '--ephemeral', '-C', str(cwd),
           '--json', '-o', str(last), '-s', 'read-only' if role == 'judge' else 'danger-full-access', '-']
    env_vars = dict(os.environ)
    if role == 'judge':
        env_vars['CODEX_HOME'] = str(judge_home())
    else:
        for d in add_dirs:  # writable alongside the workspace (no effect under danger-full-access; kept so both backends read the same call)
            cmd[-1:-1] = ['--add-dir', str(d)]
    t0 = time.time()
    try:
        with open(events, 'w', encoding='utf-8') as ef:
            r = subprocess.run(cmd, cwd=cwd, input=prompt, stdout=ef, stderr=subprocess.PIPE, text=True, timeout=timeout, env=env_vars)
        usage = None; turns = 0; messages = []; errors = []
        for line in events.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = str(e.get('type', ''))
            if t == 'turn.completed':
                usage = e.get('usage'); turns += 1
            elif t == 'item.completed' and (e.get('item') or {}).get('type') == 'agent_message':
                messages.append((e['item'].get('text') or ''))
            if 'error' in t.lower() or (e.get('item') or {}).get('type') == 'error':
                errors.append(json.dumps(e, ensure_ascii=False)[:600])
        result = last.read_text(encoding='utf-8') if last.exists() else (messages[-1] if messages else '')
        stderr_tail = '\n'.join(l for l in (r.stderr or '').splitlines() if ' WARN ' not in l and 'rmcp::' not in l and '426 Upgrade Required' not in l)[-1500:]
        env = {'backend': 'codex', 'model_requested': model, 'effort': effort, 'role': role, 'cli_version': cli_version('codex'), 'exit_code': r.returncode,
               'result': result, 'total_cost_usd': None, 'num_turns': turns or None, 'duration_ms': int((time.time() - t0) * 1000), 'usage': usage,
               'is_error': bool(r.returncode) or usage is None, 'error_text': ('\n'.join(errors) + '\n' + stderr_tail).strip(), 'no_json': usage is None and not result,
               'model_reported': None, 'events_file': str(events)}
        return env
    finally:
        # keep the event log when something went wrong (the caller may want to read it); drop it on a clean run
        if not last.exists():
            pass
        shutil.rmtree(td, ignore_errors=True) if last.exists() else None


def builder_prompt(prompt, model):
    """What a builder is told. Codex builders also get references/builder-notes-gpt.md (user 2026-11-01: GPT-specific comments, with
    little effect on Claude runs); a Claude builder's prompt comes back unchanged."""
    if backend_of(model) == 'claude':
        return prompt
    return prompt + '\n\n---\n' + GPT_NOTES.read_text(encoding='utf-8')


def run(prompt, model, effort, cwd, role='judge', timeout=1800, add_dirs=()):
    """One blocking agent run. Raises subprocess.TimeoutExpired like subprocess.run does."""
    if role not in ('judge', 'builder'):
        raise ValueError(role)
    if role == 'builder':
        prompt = builder_prompt(prompt, model)
    fn = _run_claude if backend_of(model) == 'claude' else _run_codex
    env = fn(prompt, model, effort, str(cwd), role, timeout, add_dirs)
    env['started_wall'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
    return env


def probe(model):
    """Cheap account check before a long run: (ok, message). A usage-limit answer comes back as an error or a non-JSON failure."""
    try:
        if backend_of(model) == 'claude':
            r = subprocess.run(['claude', '-p', 'Reply with exactly the word OK.', '--model', model, '--effort', 'low', '--output-format', 'json', '--permission-mode', 'plan',
                                '--setting-sources', '', '--strict-mcp-config'], capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
            try:
                d = json.loads(r.stdout)
            except json.JSONDecodeError:
                return False, (r.stdout + r.stderr)[-600:]
            if d.get('is_error'):
                return False, str(d.get('result'))[-600:]
            return True, str(d.get('result'))[:40]
        with tempfile.TemporaryDirectory(prefix='agent-cli-probe.') as td:
            env_vars = dict(os.environ); env_vars['CODEX_HOME'] = str(judge_home())
            r = subprocess.run(['codex', 'exec', '-m', model, '-c', 'model_reasoning_effort="low"', '-s', 'read-only', '--skip-git-repo-check', '--ephemeral', '-C', td,
                                '--json', '-o', f'{td}/last.txt', '-'], input='Reply with exactly the word OK.', capture_output=True, text=True, timeout=300, env=env_vars)
            last = Path(td, 'last.txt').read_text(encoding='utf-8') if Path(td, 'last.txt').exists() else ''
            if r.returncode or 'OK' not in last:
                return False, (last + r.stdout[-400:] + r.stderr[-600:])[-600:]
            return True, last.strip()[:40]
    except subprocess.TimeoutExpired:
        return False, 'probe timeout'
    except OSError as e:
        return False, f'probe failed to start: {e}'


def spend(env):
    """Short human line for logs: dollars when the CLI reports them, else tokens."""
    if env.get('total_cost_usd') is not None:
        return f"${env['total_cost_usd']:.2f}"
    u = env.get('usage') or {}
    if u:
        return f"{u.get('input_tokens', '?')} in / {u.get('output_tokens', '?')} out tokens"
    return 'no usage record'

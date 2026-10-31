#!/usr/bin/env python3
"""Unattended goal loop: run iterate_deck.py (builder -> measure -> independent judge) again and again until the merged
score reaches the target, pausing for the Claude usage window when a run hits the usage limit.

usage: goal_loop.py /abs/deck-folder [--target 90] [--model claude-opus-5-5] [--effort max] [--max-hours 72] [--quota-sleep 18300]
  status  : deck/qa/loop-status.json (phase, iteration, last totals, next wake time), log deck/qa/loop.log
  stop    : create deck/qa/STOP (checked between steps); the loop also ends when total >= target and valid, or after --max-hours
  quota   : before each iteration a cheap probe (`claude -p "OK"`) checks the account; a usage-limit error there or in a run
            puts the loop to sleep until the reset time parsed from the message, else --quota-sleep seconds (5 h + 5 min)
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIMIT = re.compile(r'(usage limit|rate limit|rate_limit|limit reached|too many requests|429|quota|overloaded)', re.I)


def now():
    return datetime.datetime.now().astimezone()


def log(qa, msg):
    line = f"{now().isoformat(timespec='seconds')} {msg}"
    with open(qa / 'loop.log', 'a', encoding='utf-8') as f:
        f.write(line + '\n')
    print(line, flush=True)


def status(qa, **kw):
    p = qa / 'loop-status.json'
    cur = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
    cur.update(kw)
    cur['updated'] = now().isoformat(timespec='seconds')
    p.write_text(json.dumps(cur, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def probe(model):
    """Return (ok, message). A usage-limit answer comes back as an error result or a non-JSON failure."""
    try:
        r = subprocess.run(['claude', '-p', 'Reply with exactly the word OK.', '--model', model, '--effort', 'low', '--output-format', 'json', '--permission-mode', 'plan'],
                           capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return False, 'probe timeout'
    try:
        d = json.loads(r.stdout)
    except json.JSONDecodeError:
        return False, (r.stdout + r.stderr)[-600:]
    if d.get('is_error'):
        return False, str(d.get('result'))[-600:]
    return True, str(d.get('result'))[:40]


def reset_wait(text, default):
    """Seconds to sleep: a reset time in the message ('resets in 2h 15m') when parseable, else the default."""
    m = re.search(r'(\d+)\s*h(?:ours?)?\s*(\d+)?\s*m?', text or '', re.I)
    if m and 'reset' in (text or '').lower():
        return int(m.group(1)) * 3600 + int(m.group(2) or 0) * 60 + 300
    return default


def alive_iteration(qa):
    for pidf in qa.glob('iter-*.pid'):
        try:
            pid = int(pidf.read_text().strip())
            os.kill(pid, 0)
            return pid
        except (ValueError, OSError):
            continue
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('deck')
    ap.add_argument('--target', type=float, default=90)
    ap.add_argument('--model', default='claude-opus-5-5')
    ap.add_argument('--effort', default='max')
    ap.add_argument('--max-hours', type=float, default=72)
    ap.add_argument('--quota-sleep', type=int, default=18300)
    ap.add_argument('--iterate', default='iterate_deck.py', help='iteration script in this folder (iterate_deck.py for design, iterate_message.py for copy)')
    ap.add_argument('--prefix', default='iter', help='record file prefix: iter (design) or iter-msg (message)')
    ap.add_argument('--note', default='심사 근거(evidence)에 적힌 장을 우선 고친다. 측정 항목 만점을 유지한다.')
    a = ap.parse_args()
    deck = Path(a.deck).resolve()
    qa = deck / 'deck' / 'qa'
    pre = a.prefix; bpre = 'builder' + pre[4:]  # iter → builder, iter-msg → builder-msg
    t_end = time.time() + a.max_hours * 3600
    log(qa, f'loop start target={a.target} model={a.model}/{a.effort} max_hours={a.max_hours} iterate={a.iterate} prefix={pre}')
    (qa / 'loop-status.json').write_text('{}\n', encoding='utf-8')  # a new loop starts from a clean status (no totals of an earlier loop)
    status(qa, phase='start', target=a.target, pid=os.getpid(), iterate=a.iterate, prefix=pre)
    while time.time() < t_end:
        if (qa / 'STOP').exists():
            log(qa, 'STOP file present; ending')
            status(qa, phase='stopped')
            return
        running = alive_iteration(qa)
        if running:
            status(qa, phase='waiting-for-running-iteration', waiting_pid=running)
            time.sleep(60)
            continue
        done = sorted(int(p.stem[len(pre) + 1:]) for p in qa.glob(f'{pre}-*.json') if p.stem[len(pre) + 1:].isdigit())
        if done:
            last = json.loads((qa / f'{pre}-{done[-1]}.json').read_text(encoding='utf-8'))
            if last.get('valid') and (last.get('total') or 0) >= a.target:
                log(qa, f"target reached at iteration {done[-1]}: {last['total']}")
                status(qa, phase='done', iteration=done[-1], total=last['total'])
                return
        n = (done[-1] + 1) if done else 1
        ok, msg = probe(a.model)
        if not ok:
            wait = reset_wait(msg, a.quota_sleep) if LIMIT.search(msg or '') else 600
            wake = now() + datetime.timedelta(seconds=wait)
            log(qa, f'probe failed ({msg[:120]!r}); sleeping {wait}s until {wake.isoformat(timespec="minutes")}')
            status(qa, phase='sleeping-quota', next_wake=wake.isoformat(timespec='seconds'), probe_message=msg[:300])
            time.sleep(wait)
            continue
        status(qa, phase=f'iteration-{n}', iteration=n, started=now().isoformat(timespec='seconds'))
        log(qa, f'iteration {n} start')
        with open(qa / f'{pre}-{n}.log', 'w', encoding='utf-8') as lf:
            r = subprocess.run([sys.executable, '-I', str(HERE / a.iterate), str(deck), '--n', str(n), '--builder', '--model', a.model, '--effort', a.effort,
                                '--note', a.note], stdout=lf, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=4 * 3600)
        rec_p = qa / f'{pre}-{n}.json'
        rec = json.loads(rec_p.read_text(encoding='utf-8')) if rec_p.exists() else {}
        b_p = qa / f'{bpre}-{n}.json'
        b = json.loads(b_p.read_text(encoding='utf-8')) if b_p.exists() else {}
        judge_text = ' '.join(str(rec.get(k, '')) for k in ('judge_parse_error', 'judge_stdout', 'message_judge_parse_error', 'message_judge_stdout', 'design_judge_parse_error', 'design_judge_stdout'))
        hit = (b.get('is_error') and LIMIT.search(str(b.get('result')))) or ((rec.get('judge_parse_error') or rec.get('message_judge_parse_error') or rec.get('design_judge_parse_error')) and LIMIT.search(judge_text))
        log(qa, f"iteration {n} end rc={r.returncode} total={rec.get('total')} valid={rec.get('valid')} costs={rec.get('costs_usd')}")
        status(qa, phase='between', iteration=n, total=rec.get('total'), valid=rec.get('valid'), costs=rec.get('costs_usd'), last_rc=r.returncode)
        if hit:
            wait = reset_wait(str(b.get('result')) + judge_text, a.quota_sleep)
            wake = now() + datetime.timedelta(seconds=wait)
            log(qa, f'usage limit during iteration {n}; sleeping {wait}s until {wake.isoformat(timespec="minutes")}')
            status(qa, phase='sleeping-quota', next_wake=wake.isoformat(timespec='seconds'))
            time.sleep(wait)
        elif not rec:
            log(qa, 'iteration produced no record; pausing 15 min')
            time.sleep(900)
    log(qa, 'max hours reached')
    status(qa, phase='max-hours')


if __name__ == '__main__':
    main()

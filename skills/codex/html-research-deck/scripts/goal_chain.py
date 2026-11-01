#!/usr/bin/env python3
"""goal_chain.py — the two goal loops in order with one spend cap: design (iterate_deck.py) until ≥ target, then message (iterate_message.py,
median of --judges draws) until ≥ target with design still ≥ target; a fresh judge-only baseline iteration first.

usage: goal_chain.py /abs/deck-folder [--design-target 90] [--message-target 90] [--judges 3] [--cost-cap-usd 160]
                     [--model claude-opus-5-5] [--effort max] [--judge-model claude-opus-5-5] [--judge-effort max]
                     [--design-note "…"] [--message-note "…"] [--skip-baseline] [--skip-design]
  stages  : baseline (iterate_deck.py --n 1 without --builder) → design loop (goal_loop.py) → message loop (goal_loop.py --iterate iterate_message.py)
  cap     : every two minutes the summed costs_usd of deck/qa/iter-*.json and iter-msg-*.json are compared with --cost-cap-usd; above it the
            running loop gets deck/qa/STOP and the chain ends with phase 'cost-cap' (the user said to keep going across quota windows, not
            across any amount of money — the cap is the agreed estimate plus margin and is reported, never silently raised)
  status  : deck/qa/chain-status.json (phase, spend, last totals), log deck/qa/chain.log; stop: deck/qa/STOP
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable


def now():
    return datetime.datetime.now().astimezone()


def log(qa, msg):
    line = f"{now().isoformat(timespec='seconds')} {msg}"
    with open(qa / 'chain.log', 'a', encoding='utf-8') as f:
        f.write(line + '\n')
    print(line, flush=True)


def status(qa, **kw):
    p = qa / 'chain-status.json'
    cur = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
    cur.update(kw); cur['updated'] = now().isoformat(timespec='seconds')
    p.write_text(json.dumps(cur, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def spend(qa):
    total = 0.0; rows = []
    for p in sorted(list(qa.glob('iter-*.json')) + list(qa.glob('iter-msg-*.json'))):
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            continue
        c = sum(v for v in (d.get('costs_usd') or {}).values() if isinstance(v, (int, float)))
        total += c; rows.append((p.name, round(c, 2), d.get('total'), d.get('valid')))
    return round(total, 2), rows


def run_loop(qa, args, cap, phase):
    p = subprocess.Popen(args, stdout=open(qa / f'{phase}-loop.stdout.log', 'a', encoding='utf-8'), stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    while p.poll() is None:
        time.sleep(120)
        total, rows = spend(qa)
        status(qa, phase=phase, spend_usd=total, iterations=rows[-6:], loop_pid=p.pid)
        if total > cap and not (qa / 'STOP').exists():
            (qa / 'STOP').write_text(f'cost cap {cap} reached at {total} ({now().isoformat(timespec="seconds")})\n', encoding='utf-8')
            log(qa, f'cost cap {cap} reached (spend {total}); STOP written, waiting for the loop to end')
    return p.returncode


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('deck'); ap.add_argument('--design-target', type=float, default=90); ap.add_argument('--message-target', type=float, default=90)
    ap.add_argument('--judges', type=int, default=3); ap.add_argument('--cost-cap-usd', type=float, default=160)
    ap.add_argument('--model', default='claude-opus-5-5'); ap.add_argument('--effort', default='max')
    ap.add_argument('--judge-model', default='claude-opus-5-5'); ap.add_argument('--judge-effort', default='max')
    ap.add_argument('--design-note', default='심사 근거(evidence)에 적힌 장을 우선 고친다. 측정 항목 만점을 유지한다.')
    ap.add_argument('--message-note', default='심사 근거(evidence)에 적힌 장을 우선 고친다. 측정 항목 만점을 유지한다.')
    ap.add_argument('--skip-baseline', action='store_true'); ap.add_argument('--skip-design', action='store_true')
    a = ap.parse_args()
    deck = Path(a.deck).resolve(); qa = deck / 'deck' / 'qa'
    if (qa / 'STOP').exists():
        (qa / 'STOP').unlink()
    log(qa, f'chain start cap=${a.cost_cap_usd} design≥{a.design_target} message≥{a.message_target} judges={a.judges} builder={a.model}/{a.effort} judge={a.judge_model}/{a.judge_effort}')
    status(qa, phase='start', pid=os.getpid(), cap_usd=a.cost_cap_usd)
    common = ['--model', a.model, '--effort', a.effort, '--judge-model', a.judge_model, '--judge-effort', a.judge_effort]
    if not a.skip_baseline and not (qa / 'iter-1.json').exists():
        status(qa, phase='baseline')
        log(qa, 'baseline: judge-only iteration 1')
        r = subprocess.run([PY, '-I', str(HERE / 'iterate_deck.py'), str(deck), '--n', '1'] + common, stdout=open(qa / 'iter-1.log', 'w', encoding='utf-8'), stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=4 * 3600)
        log(qa, f'baseline rc={r.returncode} spend={spend(qa)[0]}')
    if not a.skip_design:
        rc = run_loop(qa, [PY, '-I', str(HERE / 'goal_loop.py'), str(deck), '--target', str(a.design_target), '--note', a.design_note] + common, a.cost_cap_usd, 'design')
        st = json.loads((qa / 'loop-status.json').read_text(encoding='utf-8')) if (qa / 'loop-status.json').exists() else {}
        log(qa, f"design loop rc={rc} phase={st.get('phase')} total={st.get('total')} spend={spend(qa)[0]}")
        if st.get('phase') != 'done':
            status(qa, phase='cost-cap' if (qa / 'STOP').exists() else f"design-{st.get('phase')}", design=st)
            log(qa, 'design loop did not reach its target; message loop not started'); return
    if (qa / 'STOP').exists():
        status(qa, phase='stopped'); return
    rc = run_loop(qa, [PY, '-I', str(HERE / 'goal_loop.py'), str(deck), '--target', str(a.message_target), '--iterate', 'iterate_message.py', '--prefix', 'iter-msg',
                             '--judges', str(a.judges), '--note', a.message_note] + common, a.cost_cap_usd, 'message')
    st = json.loads((qa / 'loop-status.json').read_text(encoding='utf-8')) if (qa / 'loop-status.json').exists() else {}
    total, rows = spend(qa)
    log(qa, f"message loop rc={rc} phase={st.get('phase')} total={st.get('total')} spend={total}")
    status(qa, phase=('done' if st.get('phase') == 'done' else 'cost-cap' if (qa / 'STOP').exists() else f"message-{st.get('phase')}"), message=st, spend_usd=total, iterations=rows)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""equiv_run.py — builder-equivalence test: several models build the same deck from the same paper and storyline, one fixed judge scores all.

usage: equiv_run.py /abs/ROOT --paper /abs/<deck>/paper --storyline /abs/<deck>/work/storyline-v1.json
                    --builders gpt-6-astra:high,gpt-6.1-sol:xhigh,claude-opus-5-5:max
                    [--judge-model claude-opus-5-5] [--judge-effort max] [--judges 3] [--phase all|build|measure|judge|summary]
                    [--build-timeout 12600] [--codex-parallel] [--only gpt-6-astra-high]

ROOT/<model>-<effort>/ gets paper/ (copy), work/storyline-v1.json + work/storyline.json (copies of the approved flow), and the builder's
own deck/ and work/build.py. Phases, each resumable (a folder with its record is skipped):
  build    agent_cli.run(builder-brief-fresh.md + paths, role='builder') → deck/qa/equiv-build.json (tokens, cost, duration, turns, report)
  measure  check_deck · check_layout · shots 1 / 0.5 · contact · pdf · deck_copy · copy_lint · score_deck/score_message measured-only
           → deck/qa/equiv-measure.json
  judge    --judges design draws of judge_deck.py on a frozen copy of shots-full → judge_median.py → score_deck.py --judge;
           --judges message draws of judge_message.py → judge_median.py → score_message.py --judge (same judge model for every builder)
  summary  ROOT/summary.json + ROOT/summary.md: per builder the build spend, check counts, measured and judged halves, totals, and the
           gap to the first builder in --builders (the baseline)
Quota: agent_cli.probe before each Claude stage; a usage-limit answer sleeps until the reset time in the message (else 5 h 5 min) and retries.
Codex builders run concurrently with --codex-parallel (they draw on the Codex plan, not on Claude); Claude builders run one at a time after them.
Status: ROOT/equiv-status.json, log ROOT/equiv.log. Stop: create ROOT/STOP.
"""
import argparse
import datetime
import json
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
PY = sys.executable
sys.path.insert(0, str(HERE))
import agent_cli  # noqa: E402  (skill script, trusted)


def now():
    return datetime.datetime.now().astimezone()


def sh(cmd, cwd=None, timeout=3600):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)


class Log:
    def __init__(self, root):
        self.root = root; self.lock = threading.Lock()

    def __call__(self, msg):
        line = f"{now().isoformat(timespec='seconds')} {msg}"
        with self.lock:
            with open(self.root / 'equiv.log', 'a', encoding='utf-8') as f:
                f.write(line + '\n')
            print(line, flush=True)

    def status(self, **kw):
        p = self.root / 'equiv-status.json'
        with self.lock:
            cur = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
            cur.update(kw); cur['updated'] = now().isoformat(timespec='seconds')
            p.write_text(json.dumps(cur, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def wait_for_quota(model, log, root):
    while True:
        if (root / 'STOP').exists():
            return False
        ok, msg = agent_cli.probe(model)
        if ok:
            return True
        wait = agent_cli.reset_wait(msg) if agent_cli.LIMIT.search(msg or '') else 600
        log(f'probe {model} failed ({msg[:120]!r}); sleeping {wait}s')
        time.sleep(wait)


def prepare(dest, paper, storyline, log):
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'work').mkdir(exist_ok=True); (dest / 'deck' / 'qa').mkdir(parents=True, exist_ok=True)
    if not (dest / 'paper').exists():
        shutil.copytree(paper, dest / 'paper')
    for name in ('storyline-v1.json', 'storyline.json'):
        if not (dest / 'work' / name).exists():
            shutil.copy(storyline, dest / 'work' / name)
    log(f'prepared {dest.name}')


def build(dest, model, effort, timeout, log, root):
    rec_p = dest / 'deck' / 'qa' / 'equiv-build.json'
    if rec_p.exists():
        log(f'{dest.name}: build record exists, skipping'); return json.loads(rec_p.read_text(encoding='utf-8'))
    brief = (SKILL / 'references' / 'builder-brief-fresh.md').read_text(encoding='utf-8')
    prompt = (brief + f"\n\n---\n스킬 폴더: {SKILL}\n작업 폴더: {dest}\n스토리라인: {dest / 'work' / 'storyline-v1.json'}\n논문: {dest / 'paper'}\n"
              f"빌더: {model} ({effort}). 시작 시각 {now().isoformat(timespec='minutes')}. 끝나면 위 '보고' 항목대로 적는다.")
    attempts = 0
    while True:
        attempts += 1
        if agent_cli.backend_of(model) == 'claude' and not wait_for_quota(model, log, root):
            return {'aborted': 'STOP'}
        log(f'{dest.name}: build start ({model}/{effort}, attempt {attempts})')
        t0 = time.time()
        try:
            env = agent_cli.run(prompt, model, effort, cwd=str(dest), role='builder', timeout=timeout, add_dirs=[SKILL])
        except subprocess.TimeoutExpired:
            env = {'result': f'builder run exceeded {timeout} s', 'is_error': True, 'error_text': 'timeout', 'backend': agent_cli.backend_of(model), 'duration_ms': int((time.time() - t0) * 1000)}
        hit = env.get('is_error') and agent_cli.LIMIT.search((env.get('result') or '') + (env.get('error_text') or ''))
        if hit and attempts < 3 and not (dest / 'deck' / 'index.html').exists():
            wait = agent_cli.reset_wait((env.get('result') or '') + (env.get('error_text') or ''))
            log(f'{dest.name}: usage limit during build; sleeping {wait}s'); time.sleep(wait); continue
        break
    rec = {'model': model, 'effort': effort, 'backend': env.get('backend'), 'cli_version': env.get('cli_version'), 'started': env.get('started_wall'),
           'duration_ms': env.get('duration_ms'), 'total_cost_usd': env.get('total_cost_usd'), 'usage': env.get('usage'), 'num_turns': env.get('num_turns'),
           'is_error': env.get('is_error'), 'error_text': (env.get('error_text') or '')[-2000:], 'report': (env.get('result') or '')[-6000:],
           'index_exists': (dest / 'deck' / 'index.html').exists(), 'build_py_exists': (dest / 'work' / 'build.py').exists(), 'attempts': attempts}
    rec_p.write_text(json.dumps(rec, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    log(f"{dest.name}: build end · {agent_cli.spend(env)} · {round((env.get('duration_ms') or 0) / 60000)} min · index={rec['index_exists']}")
    return rec


def measure(dest, log):
    qa = dest / 'deck' / 'qa'; index = dest / 'deck' / 'index.html'; work = dest / 'work'
    rec = {'at': now().isoformat(timespec='seconds'), 'index_exists': index.exists()}
    if not index.exists():
        (qa / 'equiv-measure.json').write_text(json.dumps(rec, indent=1) + '\n', encoding='utf-8'); return rec
    cd = sh([PY, '-I', str(HERE / 'check_deck.py'), str(index), '--json', str(qa / 'check.json')])
    cl = sh([PY, '-I', str(HERE / 'check_layout.py'), str(index), '--json', str(qa / 'layout.json'), '--quiet'])
    rec['check_deck'] = (cd.stdout.strip().splitlines() or [''])[-1]; rec['check_layout'] = ([l for l in cl.stdout.splitlines() if 'slides ·' in l] or [cl.stderr[-300:]])[-1]
    sh(['sh', str(HERE / 'shots.sh'), str(index), str(qa / 'shots-full'), '1'], timeout=1800)
    sh(['sh', str(HERE / 'shots.sh'), str(index), str(qa / 'shots'), '0.5'], timeout=1800)
    sh(['sh', str(HERE / 'contact_sheet.sh'), str(qa / 'shots'), str(qa / 'contact.png'), '5'], timeout=600)
    sh(['sh', str(HERE / 'export_pdf.sh'), str(index), str(qa / 'deck.pdf')], timeout=1200)
    sh([PY, '-I', str(HERE / 'deck_copy.py'), str(index), '--json', str(qa / 'copy.json'), '--text', str(qa / 'copy.txt'), '--notes', '500'])
    lint = sh([PY, '-I', str(HERE / 'copy_lint.py'), '--json', str(qa / 'copy.json')], timeout=120)
    (qa / 'copy-lint.txt').write_text(lint.stdout, encoding='utf-8'); rec['copy_lint'] = ([l for l in lint.stdout.splitlines() if l.startswith('요약')] or [''])[-1]
    sd = sh([PY, '-I', str(HERE / 'score_deck.py'), str(index), '--out', str(qa / 'score.json'), '--storyline', str(work / 'storyline.json')])
    sm = sh([PY, '-I', str(HERE / 'score_message.py'), str(index), '--out', str(qa / 'score-message.json'), '--storyline-v1', str(work / 'storyline-v1.json')])
    rec['score_deck_measured'] = sd.stdout.strip().splitlines()[-3:]; rec['score_message_measured'] = sm.stdout.strip().splitlines()[-3:]
    rec['shots_full'] = len(list((qa / 'shots-full').glob('slide-*.png'))); rec['pdf'] = (qa / 'deck.pdf').exists()
    (qa / 'equiv-measure.json').write_text(json.dumps(rec, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    log(f"{dest.name}: measured · {rec['check_deck']} · {rec['check_layout']}")
    return rec


def draws(cmd_base, out_files, timeout, log, name):
    procs = [subprocess.Popen(cmd_base + ['--out', str(f)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, text=True) for f in out_files]
    outs = []
    for p in procs:
        try:
            outs.append(p.communicate(timeout=timeout)[0].strip()[-300:])
        except subprocess.TimeoutExpired:
            p.kill(); outs.append('timeout')
    good = [f for f in out_files if f.exists() and not json.loads(f.read_text(encoding='utf-8')).get('parse_error')]
    log(f'{name}: {len(good)}/{len(out_files)} usable judge draws')
    return good, outs


def judge(dest, judge_model, judge_effort, n_judges, log, root):
    qa = dest / 'deck' / 'qa'; index = dest / 'deck' / 'index.html'; work = dest / 'work'
    rec_p = qa / 'equiv-judge.json'
    if rec_p.exists():
        log(f'{dest.name}: judge record exists, skipping'); return json.loads(rec_p.read_text(encoding='utf-8'))
    if not index.exists() or not list((qa / 'shots-full').glob('slide-*.png')):
        rec = {'skipped': 'no deck or no shots'}; rec_p.write_text(json.dumps(rec) + '\n', encoding='utf-8'); return rec
    if not wait_for_quota(judge_model, log, root):
        return {'aborted': 'STOP'}
    ts = now().strftime('%Y%m%dT%H%M%S'); rec = {'at': ts, 'judge_model': judge_model, 'judge_effort': judge_effort, 'judges': n_judges, 'costs_usd': {}}
    frozen = qa / f'judge-shots-{ts}'; shutil.rmtree(frozen, ignore_errors=True); shutil.copytree(qa / 'shots-full', frozen)
    base = [PY, '-I', str(HERE / 'judge_deck.py'), str(frozen), '--model', judge_model, '--effort', judge_effort, '--timeout', '2400']
    good, outs = draws(base, [qa / f'judge-{ts}-r{k + 1}.json' for k in range(n_judges)], 2700, log, f'{dest.name} design')
    rec['design_draws'] = outs
    jd = qa / f'judge-{ts}.json'
    if len(good) >= 2:
        m = sh([PY, '-I', str(HERE / 'judge_median.py'), '--out', str(jd)] + [str(f) for f in good], timeout=120); rec['design_median'] = m.stdout.strip()[-300:]
    elif good:
        shutil.copy(good[0], jd); rec['design_median'] = 'single usable draw'
    if jd.exists():
        rec['costs_usd']['design_judge'] = json.loads(jd.read_text(encoding='utf-8')).get('cost_usd')
        s = sh([PY, '-I', str(HERE / 'score_deck.py'), str(index), '--out', str(qa / 'score.json'), '--storyline', str(work / 'storyline.json'), '--judge', str(jd)])
        rec['score_deck'] = s.stdout.strip().splitlines()[-3:]
    # message judge on the copy dump
    n = json.loads((qa / 'copy.json').read_text(encoding='utf-8'))['n']
    base = [PY, '-I', str(HERE / 'judge_message.py'), '--copy', str(qa / 'copy.txt'), '--context', str(dest / 'paper' / 'context-for-judge.txt'), '--contact', str(qa / 'contact.png'),
            '--slides', str(n), '--model', judge_model, '--effort', judge_effort, '--timeout', '2400']
    if not wait_for_quota(judge_model, log, root):
        return {'aborted': 'STOP'}
    good, outs = draws(base, [qa / f'judge-msg-{ts}-r{k + 1}.json' for k in range(n_judges)], 2700, log, f'{dest.name} message')
    rec['message_draws'] = outs
    jm = qa / f'judge-msg-{ts}.json'
    if len(good) >= 2:
        m = sh([PY, '-I', str(HERE / 'judge_median.py'), '--out', str(jm)] + [str(f) for f in good], timeout=120); rec['message_median'] = m.stdout.strip()[-300:]
    elif good:
        shutil.copy(good[0], jm); rec['message_median'] = 'single usable draw'
    if jm.exists():
        rec['costs_usd']['message_judge'] = json.loads(jm.read_text(encoding='utf-8')).get('cost_usd')
        s = sh([PY, '-I', str(HERE / 'score_message.py'), str(index), '--out', str(qa / 'score-message.json'), '--storyline-v1', str(work / 'storyline-v1.json'), '--judge', str(jm)])
        rec['score_message'] = s.stdout.strip().splitlines()[-3:]
    rec_p.write_text(json.dumps(rec, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    log(f"{dest.name}: judged · {rec.get('score_deck', ['?'])[-1]} · {rec.get('score_message', ['?'])[-1]} · costs {rec['costs_usd']}")
    return rec


def summary(root, builders, log):
    rows = []
    for model, effort in builders:
        dest = root / f'{model}-{effort}'; qa = dest / 'deck' / 'qa'
        rd = lambda p: json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
        b, me, j = rd(qa / 'equiv-build.json'), rd(qa / 'equiv-measure.json'), rd(qa / 'equiv-judge.json')
        sd, sm = rd(qa / 'score.json'), rd(qa / 'score-message.json')
        u = b.get('usage') or {}
        rows.append({'builder': f'{model}:{effort}', 'backend': b.get('backend'), 'build_min': round((b.get('duration_ms') or 0) / 60000, 1), 'build_cost_usd': b.get('total_cost_usd'),
                     'build_tokens_in': u.get('input_tokens') if u else None, 'build_tokens_out': u.get('output_tokens') if u else None, 'build_turns': b.get('num_turns'),
                     'index': b.get('index_exists'), 'check_deck': me.get('check_deck'), 'check_layout': me.get('check_layout'),
                     'design_measured': sd.get('measured_total'), 'design_judged': sd.get('judged_total'), 'design_total': sd.get('total'), 'design_items': sd.get('judged'),
                     'message_measured': sm.get('measured_total'), 'message_judged': sm.get('judged_total'), 'message_total': sm.get('total'), 'message_items': sm.get('judged'),
                     'judge_costs_usd': j.get('costs_usd'), 'copy_lint': me.get('copy_lint')})
    base = rows[0] if rows else {}
    for r in rows:
        r['design_gap_to_baseline'] = round(r['design_total'] - base['design_total'], 2) if r.get('design_total') is not None and base.get('design_total') is not None else None
        r['message_gap_to_baseline'] = round(r['message_total'] - base['message_total'], 2) if r.get('message_total') is not None and base.get('message_total') is not None else None
        r['within_3'] = (abs(r['design_gap_to_baseline'] or 99) <= 3 and abs(r['message_gap_to_baseline'] or 99) <= 3) if r is not base else None
    out = {'at': now().isoformat(timespec='seconds'), 'baseline': base.get('builder'), 'rows': rows}
    (root / 'summary.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    md = ['# Builder equivalence — ' + out['at'], '', f"baseline (first in --builders): {base.get('builder')}", '',
          '| builder | backend | build min | build spend | checks (deck / layout) | design measured+judged = total | message measured+judged = total | gap design / message | within ±3 |', '|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        spend = f"${r['build_cost_usd']:.2f}" if r.get('build_cost_usd') is not None else (f"{r.get('build_tokens_in')} in / {r.get('build_tokens_out')} out tok" if r.get('build_tokens_in') else '—')
        md.append(f"| {r['builder']} | {r['backend']} | {r['build_min']} | {spend} | {r.get('check_deck')} / {r.get('check_layout')} | {r.get('design_measured')} + {r.get('design_judged')} = **{r.get('design_total')}** | "
                  f"{r.get('message_measured')} + {r.get('message_judged')} = **{r.get('message_total')}** | {r.get('design_gap_to_baseline')} / {r.get('message_gap_to_baseline')} | {r.get('within_3')} |")
    (root / 'summary.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    log('summary written')
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('root'); ap.add_argument('--paper', required=True); ap.add_argument('--storyline', required=True)
    ap.add_argument('--builders', required=True, help='comma-separated model:effort; the first is the baseline')
    ap.add_argument('--judge-model', default='claude-opus-5-5'); ap.add_argument('--judge-effort', default='max'); ap.add_argument('--judges', type=int, default=3)
    ap.add_argument('--phase', default='all', choices=['all', 'build', 'measure', 'judge', 'summary']); ap.add_argument('--build-timeout', type=int, default=12600)
    ap.add_argument('--codex-parallel', action='store_true'); ap.add_argument('--only')
    a = ap.parse_args()
    root = Path(a.root).resolve(); root.mkdir(parents=True, exist_ok=True)
    log = Log(root)
    builders = [tuple(b.split(':', 1)) for b in a.builders.split(',') if b]
    todo = [(m, e) for m, e in builders if not a.only or f'{m}-{e}' == a.only]
    partial = bool(a.only) or a.phase != 'all'
    log(f'equiv start phase={a.phase} only={a.only} builders={builders} judge={a.judge_model}/{a.judge_effort}×{a.judges}')
    if partial:  # a side run (one builder, one phase) must not overwrite the main run's phase in the shared status file
        log.status(last_partial_run={'phase': a.phase, 'only': a.only, 'pid': __import__('os').getpid(), 'started': now().isoformat(timespec='seconds')})
    else:
        log.status(phase=a.phase, builders=[f'{m}:{e}' for m, e in builders], pid=__import__('os').getpid())
    if a.phase in ('all', 'build'):
        for m, e in todo:
            prepare(root / f'{m}-{e}', Path(a.paper), Path(a.storyline), log)
        codex = [(m, e) for m, e in todo if agent_cli.backend_of(m) == 'codex']; claude = [(m, e) for m, e in todo if agent_cli.backend_of(m) == 'claude']
        if a.codex_parallel and len(codex) > 1:
            ths = [threading.Thread(target=build, args=(root / f'{m}-{e}', m, e, a.build_timeout, log, root), daemon=True) for m, e in codex]
            for t in ths: t.start()
            for t in ths: t.join()
        else:
            for m, e in codex:
                build(root / f'{m}-{e}', m, e, a.build_timeout, log, root)
        for m, e in claude:
            if (root / 'STOP').exists(): break
            build(root / f'{m}-{e}', m, e, a.build_timeout, log, root)
    if a.phase in ('all', 'measure'):
        for m, e in todo:
            measure(root / f'{m}-{e}', log)
    if a.phase in ('all', 'judge'):
        for m, e in todo:
            if (root / 'STOP').exists(): break
            judge(root / f'{m}-{e}', a.judge_model, a.judge_effort, a.judges, log, root)
    summary(root, builders, log)
    if partial:
        log.status(last_partial_run={'phase': a.phase, 'only': a.only, 'ended': now().isoformat(timespec='seconds')})
    else:
        log.status(phase='done')
    log('equiv end')


if __name__ == '__main__':
    main()

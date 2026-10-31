#!/usr/bin/env python3
"""One goal iteration for a deck: (builder →) measure → independent judge → merged score. Honest by construction: the judge
sees a frozen copy of the PNGs the builder cannot touch, the rubric hashes are checked against the frozen file, and every
Opus run's cost is recorded.

usage: iterate_deck.py /abs/deck-folder --n 2 [--builder] [--model claude-opus-5-5] [--effort max] [--note "..."]
  deck-folder holds work/build.py, deck/index.html, deck/qa/ (score.json, rubric-frozen.json, judge-*.json), work/storyline.json
  --builder : run the builder first (claude -p, builder-brief.md + the latest score and judge evidence), blocking
  result    : deck/qa/score.json (merged), deck/qa/iter-<n>.json (what ran, costs, totals)
"""
import argparse
import datetime
import glob
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
PY = sys.executable


def sh(cmd, cwd=None, timeout=3600):
    # stdin=DEVNULL: `claude -p` otherwise re-reads the launcher's inherited stdin (a heredoc) and appends it to its prompt
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)


def latest_judge(qa):
    files = [p for p in sorted(qa.glob('judge-*.json')) if p.is_file()]
    return files[-1] if files else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('deck'); ap.add_argument('--n', type=int, required=True); ap.add_argument('--builder', action='store_true')
    ap.add_argument('--model', default='claude-opus-5-5'); ap.add_argument('--effort', default='max'); ap.add_argument('--note', default='')
    ap.add_argument('--skip-judge', action='store_true', help='measure only (no Opus cost)')
    a = ap.parse_args()
    deck = Path(a.deck).resolve(); qa = deck / 'deck' / 'qa'; index = deck / 'deck' / 'index.html'
    rec = {'n': a.n, 'started': datetime.datetime.now().astimezone().isoformat(timespec='seconds'), 'model': a.model, 'effort': a.effort, 'costs_usd': {}}
    if a.builder:
        shutil.copy(deck / 'work' / 'build.py', qa / f'build.before-iter-{a.n}.py')
        jf = latest_judge(qa)
        brief = (SKILL / 'references' / 'builder-brief.md').read_text(encoding='utf-8')
        score = json.loads((qa / 'score.json').read_text(encoding='utf-8')) if (qa / 'score.json').exists() else {}
        prompt = (brief + f"\n\n---\n이번 반복: {a.n}회차. 작업 폴더: {deck} (스킬: {SKILL}).\n현재 점수: 측정 {score.get('measured_total')}/60, 심사 {score.get('judged_total')}/40, 합계 {score.get('total')}/100. "
                  f"측정 세부는 deck/qa/score.json 의 detail, 심사 근거는 {jf.name if jf else '(없음)'} 의 judge.slides[].evidence. " + a.note +
                  "\n끝나면 바꾼 장과 내용, check_deck/check_layout 결과 줄을 보고한다. 점수는 호출자가 다시 잰다.")
        cmd = ['claude', '-p', prompt, '--model', a.model, '--effort', a.effort, '--output-format', 'json', '--permission-mode', 'acceptEdits',
               '--allowedTools', 'Read,Edit,MultiEdit,Write,Bash,Glob,Grep', '--disallowedTools', 'Task,WebFetch,WebSearch', '--add-dir', str(SKILL)]
        r = sh(cmd, cwd=str(deck), timeout=5400)
        try:
            env = json.loads(r.stdout)
        except json.JSONDecodeError:
            env = {'result': r.stdout[-3000:], 'error_text': r.stderr[-1000:]}
        (qa / f'builder-{a.n}.json').write_text(json.dumps(env, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        rec['costs_usd']['builder'] = env.get('total_cost_usd'); rec['builder_turns'] = env.get('num_turns'); rec['builder_report'] = (env.get('result') or '')[-2500:]
        # the builder must leave the checks clean and the full-size shots current; re-run both here regardless
        sh([PY, '-I', str(HERE / 'check_deck.py'), str(index)])
        sh(['sh', str(HERE / 'shots.sh'), str(index), str(qa / 'shots-full'), '1'], timeout=1200)
    m = sh([PY, '-I', str(HERE / 'score_deck.py'), str(index), '--out', str(qa / 'score.json'), '--storyline', str(deck / 'work' / 'storyline.json'), '--frozen', str(qa / 'rubric-frozen.json')])
    rec['measured_stdout'] = m.stdout.strip().splitlines()[-3:]
    jf = None
    if not a.skip_judge:
        frozen = qa / f'judge-shots-iter-{a.n}'
        shutil.rmtree(frozen, ignore_errors=True); shutil.copytree(qa / 'shots-full', frozen)
        ts = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
        jf = qa / f'judge-{ts}.json'
        j = sh([PY, '-I', str(HERE / 'judge_deck.py'), str(frozen), '--out', str(jf), '--model', a.model, '--effort', a.effort, '--timeout', '2400'], timeout=2700)
        rec['judge_stdout'] = j.stdout.strip()[-400:]
        if jf.exists():
            jd = json.loads(jf.read_text(encoding='utf-8')); rec['costs_usd']['judge'] = jd.get('cost_usd'); rec['judge_parse_error'] = jd.get('parse_error')
    else:
        jf = latest_judge(qa)
    args = [PY, '-I', str(HERE / 'score_deck.py'), str(index), '--out', str(qa / 'score.json'), '--storyline', str(deck / 'work' / 'storyline.json'), '--frozen', str(qa / 'rubric-frozen.json')]
    if jf and jf.exists():
        args += ['--judge', str(jf)]
    s = sh(args)
    rec['score_stdout'] = s.stdout.strip().splitlines()[-3:]
    sc = json.loads((qa / 'score.json').read_text(encoding='utf-8'))
    rec.update({'measured_total': sc['measured_total'], 'judged_total': sc['judged_total'], 'total': sc['total'], 'valid': sc['valid'], 'invalid_reason': sc['invalid_reason'], 'judge_file': str(jf) if jf else None,
                'finished': datetime.datetime.now().astimezone().isoformat(timespec='seconds')})
    (qa / f'iter-{a.n}.json').write_text(json.dumps(rec, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('\n'.join(rec['score_stdout']))
    print(f"iteration {a.n}: total {sc['total']}/100 valid={sc['valid']} · costs {rec['costs_usd']}")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""One message-goal iteration: (builder →) rebuild + checks + shots → design score with a fresh design judge → copy dump →
independent message judge → message score → storyline snapshot → iter-msg-<n>.json. Pass = message ≥ target AND design ≥ target.

usage: iterate_message.py /abs/deck-folder --n 1 [--builder] [--model claude-opus-5-5] [--effort max] [--note "..."]
                          [--reuse-design-judge /abs/deck/qa/judge-<ts>.json] [--skip-judges] [--design-target 90]
  deck-folder holds work/build.py, work/storyline.json, work/storyline-v1.json, paper/context-for-judge.txt,
  deck/index.html, deck/qa/ (rubric-frozen.json, rubric-message-frozen.json, score.json, score-message.json, judge*.json)
  --reuse-design-judge : accept an existing design judge file only if its frozen PNG folder is byte-identical to the current shots-full
"""
import argparse
import datetime
import filecmp
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
PY = sys.executable


def sh(cmd, cwd=None, timeout=3600):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)


def latest(qa, pattern):
    files = [p for p in sorted(qa.glob(pattern)) if p.is_file()]
    return files[-1] if files else None


def same_pngs(a, b):
    pa = sorted(p.name for p in Path(a).glob('slide-*.png')); pb = sorted(p.name for p in Path(b).glob('slide-*.png'))
    return bool(pa) and pa == pb and all(filecmp.cmp(Path(a) / x, Path(b) / x, shallow=False) for x in pa)


def snapshot_storyline(deck, n_iter):
    """Copy the deck's current titles and closing lines into work/storyline.json (ids/roles/evidence untouched)."""
    sys.path.insert(0, str(HERE))
    from deck_copy import dump  # noqa: E402
    st_p = deck / 'work' / 'storyline.json'
    st = json.loads(st_p.read_text(encoding='utf-8'))
    doc = dump(str(deck / 'deck' / 'index.html'))
    changed = 0
    for s, d in zip(st.get('slides', []), doc['slides']):
        title = d['h2'] or d['h1'] or d['title']
        if s.get('title') != title or s.get('closing') != (d['closing'] or s.get('closing')):
            changed += 1
        s['title'] = title
        if d['closing']:
            s['closing'] = d['closing']
    st['status'] = 'revised'
    st['revision'] = {'basis': "user instruction 2026-10-31: '디자인은 이제 좋네. 이제 메시지만 좀 조절하면 되겠다 … 기준을 만들고 계속 스킬을 개선해줘. goal 을 통해서' — titles/closing lines re-snapshotted from the deck by iterate_message.py; ids, roles and evidence unchanged (work/storyline-v1.json)",
                      'iteration': n_iter, 'at': datetime.datetime.now().astimezone().isoformat(timespec='seconds'), 'slides_changed': changed, 'user_review': 'pending'}
    st_p.write_text(json.dumps(st, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return changed


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('deck'); ap.add_argument('--n', type=int, required=True); ap.add_argument('--builder', action='store_true')
    ap.add_argument('--model', default='claude-opus-5-5'); ap.add_argument('--effort', default='max'); ap.add_argument('--note', default='')
    ap.add_argument('--reuse-design-judge'); ap.add_argument('--skip-judges', action='store_true'); ap.add_argument('--design-target', type=float, default=90)
    a = ap.parse_args()
    deck = Path(a.deck).resolve(); qa = deck / 'deck' / 'qa'; index = deck / 'deck' / 'index.html'; work = deck / 'work'
    rec = {'n': a.n, 'kind': 'message', 'started': datetime.datetime.now().astimezone().isoformat(timespec='seconds'), 'model': a.model, 'effort': a.effort, 'costs_usd': {}}
    if a.builder:
        shutil.copy(work / 'build.py', qa / f'build.before-msg-{a.n}.py')
        jm = latest(qa, 'judge-msg-*.json'); jd = latest(qa, 'judge-2*.json')
        brief = (SKILL / 'references' / 'builder-brief-message.md').read_text(encoding='utf-8')
        sm = json.loads((qa / 'score-message.json').read_text(encoding='utf-8')) if (qa / 'score-message.json').exists() else {}
        sd = json.loads((qa / 'score.json').read_text(encoding='utf-8')) if (qa / 'score.json').exists() else {}
        prompt = (brief + f"\n\n---\n이번 반복: 메시지 {a.n}회차. 작업 폴더: {deck} (스킬: {SKILL}).\n"
                  f"현재 메시지 점수: 측정 {sm.get('measured_total')}/50, 심사 {sm.get('judged_total')}/50, 합계 {sm.get('total')}/100 (세부: deck/qa/score-message.json 의 detail; 심사 근거: {jm.name if jm else '(없음)'}).\n"
                  f"현재 디자인 점수: {sd.get('total')}/100 (심사 근거: {jd.name if jd else '(없음)'}) — 90 아래로 떨어뜨리지 말 것.\n" + a.note +
                  "\n끝나면 바꾼 장과 문구(제목·마무리줄 전후), 측정 점수 줄, check_deck/check_layout 결과 줄을 보고한다. 심사와 최종 점수는 호출자가 잰다.")
        cmd = ['claude', '-p', prompt, '--model', a.model, '--effort', a.effort, '--output-format', 'json', '--permission-mode', 'acceptEdits',
               '--allowedTools', 'Read,Edit,MultiEdit,Write,Bash,Glob,Grep', '--disallowedTools', 'Task,WebFetch,WebSearch', '--add-dir', str(SKILL)]
        r = sh(cmd, cwd=str(deck), timeout=5400)
        try:
            env = json.loads(r.stdout)
        except json.JSONDecodeError:
            env = {'result': r.stdout[-3000:], 'error_text': r.stderr[-1000:]}
        (qa / f'builder-msg-{a.n}.json').write_text(json.dumps(env, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        rec['costs_usd']['builder'] = env.get('total_cost_usd'); rec['builder_turns'] = env.get('num_turns'); rec['builder_report'] = (env.get('result') or '')[-3000:]
    # rebuild from the builder script (idempotent when nothing changed) and refresh every QA artefact the judges read
    b = sh([PY, '-I', str(work / 'build.py')], cwd=str(deck)); rec['build_stdout'] = b.stdout.strip()[-200:] + b.stderr.strip()[-300:]
    cd = sh([PY, '-I', str(HERE / 'check_deck.py'), str(index)]); rec['check_deck'] = cd.stdout.strip().splitlines()[-1:] 
    cl = sh([PY, '-I', str(HERE / 'check_layout.py'), str(index), '--quiet']); rec['check_layout'] = [l for l in cl.stdout.splitlines() if 'slides ·' in l][-1:]
    sh(['sh', str(HERE / 'shots.sh'), str(index), str(qa / 'shots-full'), '1'], timeout=1200)
    sh(['sh', str(HERE / 'shots.sh'), str(index), str(qa / 'shots'), '0.5'], timeout=1200)
    sh(['sh', str(HERE / 'contact_sheet.sh'), str(qa / 'shots'), str(qa / 'contact.png'), '5'], timeout=600)
    if (work / 'fact_check.py').exists():
        sh([PY, '-I', str(work / 'fact_check.py')], cwd=str(deck))
    # design score with a fresh (or verified-reusable) design judge
    jd = None
    if a.reuse_design_judge:
        cand = Path(a.reuse_design_judge)
        meta = json.loads(cand.read_text(encoding='utf-8')) if cand.exists() else {}
        if meta.get('shots') and same_pngs(meta['shots'], qa / 'shots-full'):
            jd = cand; rec['design_judge_reused'] = str(cand)
        else:
            rec['design_judge_reused'] = f'refused: {cand.name} PNGs differ from current shots-full'
    if jd is None and not a.skip_judges:
        frozen = qa / f'judge-shots-msg-{a.n}'
        shutil.rmtree(frozen, ignore_errors=True); shutil.copytree(qa / 'shots-full', frozen)
        ts = datetime.datetime.now().strftime('%Y%m%dT%H%M%S'); jd = qa / f'judge-{ts}.json'
        j = sh([PY, '-I', str(HERE / 'judge_deck.py'), str(frozen), '--out', str(jd), '--model', a.model, '--effort', a.effort, '--timeout', '2400'], timeout=2700)
        rec['design_judge_stdout'] = j.stdout.strip()[-300:]
        if jd.exists():
            m = json.loads(jd.read_text(encoding='utf-8')); rec['costs_usd']['design_judge'] = m.get('cost_usd'); rec['design_judge_parse_error'] = m.get('parse_error')
    args = [PY, '-I', str(HERE / 'score_deck.py'), str(index), '--out', str(qa / 'score.json'), '--storyline', str(work / 'storyline.json'), '--frozen', str(qa / 'rubric-frozen.json')]
    if jd and Path(jd).exists():
        args += ['--judge', str(jd)]
    s = sh(args); rec['design_score_stdout'] = s.stdout.strip().splitlines()[-3:]
    sd = json.loads((qa / 'score.json').read_text(encoding='utf-8'))
    # message score with a fresh message judge
    sh([PY, '-I', str(HERE / 'deck_copy.py'), str(index), '--json', str(qa / 'copy.json'), '--text', str(qa / 'copy.txt'), '--notes', '500'])
    jm = None
    if not a.skip_judges:
        ts = datetime.datetime.now().strftime('%Y%m%dT%H%M%S'); jm = qa / f'judge-msg-{ts}.json'
        n = json.loads((qa / 'copy.json').read_text(encoding='utf-8'))['n']
        j = sh([PY, '-I', str(HERE / 'judge_message.py'), '--copy', str(qa / 'copy.txt'), '--context', str(deck / 'paper' / 'context-for-judge.txt'), '--contact', str(qa / 'contact.png'),
                '--slides', str(n), '--out', str(jm), '--model', a.model, '--effort', a.effort, '--timeout', '2400'], timeout=2700)
        rec['message_judge_stdout'] = j.stdout.strip()[-300:]
        if jm.exists():
            m = json.loads(jm.read_text(encoding='utf-8')); rec['costs_usd']['message_judge'] = m.get('cost_usd'); rec['message_judge_parse_error'] = m.get('parse_error')
    else:
        jm = latest(qa, 'judge-msg-*.json')
    args = [PY, '-I', str(HERE / 'score_message.py'), str(index), '--out', str(qa / 'score-message.json'), '--storyline-v1', str(work / 'storyline-v1.json'),
            '--design-frozen', str(qa / 'rubric-frozen.json'), '--frozen', str(qa / 'rubric-message-frozen.json')]
    if jm and Path(jm).exists():
        args += ['--judge', str(jm)]
    s = sh(args); rec['message_score_stdout'] = s.stdout.strip().splitlines()[-3:]
    sm = json.loads((qa / 'score-message.json').read_text(encoding='utf-8'))
    rec['storyline_slides_changed'] = snapshot_storyline(deck, a.n)
    rec.update({'message_total': sm['total'], 'message_valid': sm['valid'], 'message_invalid_reason': sm['invalid_reason'], 'message_measured': sm['measured_total'], 'message_judged': sm['judged_total'],
                'design_total': sd['total'], 'design_valid': sd['valid'], 'design_invalid_reason': sd['invalid_reason'], 'design_target': a.design_target,
                'total': sm['total'], 'valid': bool(sm['valid'] and sd['valid'] and sd['total'] >= a.design_target),
                'judge_file': str(jm) if jm else None, 'design_judge_file': str(jd) if jd else None,
                'finished': datetime.datetime.now().astimezone().isoformat(timespec='seconds')})
    (qa / f'iter-msg-{a.n}.json').write_text(json.dumps(rec, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('\n'.join(rec['message_score_stdout']))
    print(f"message iteration {a.n}: message {sm['total']}/100 (valid={sm['valid']}) · design {sd['total']}/100 (valid={sd['valid']}) · pass={rec['valid']} · costs {rec['costs_usd']}")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Run the independent message judge (rubric-message.md items N1–N5, 50 points) with a model that did not build the deck.

usage: judge_message.py --copy /abs/deck/qa/copy.txt --context /abs/paper/context-for-judge.txt --contact /abs/deck/qa/contact.png
                        --slides 20 --out /abs/deck/qa/judge-msg-<ts>.json [--model claude-opus-5-5] [--effort max]

The judge runs `claude -p` inside a temporary folder that holds only copy.txt, context.txt and contact.png (Read tool only), so it
cannot see the builder's code, scores or earlier judgements. The raw model output is kept next to the parsed JSON.
`--setting-sources ''` and `--strict-mcp-config` keep the user's global CLAUDE.md, settings and MCP servers out of the judge: on 2026-11-01 a judge run
loaded the shared working agreement, applied its bio-safe-reading rule to an ML deck (an Opus 5 pre-screen, $1.06) and reported itself non-independent.
Backends: `--model claude-*` runs `claude -p`; any other model (gpt-6-astra, gpt-6.1-sol, …) runs `codex exec` with a minimal CODEX_HOME — see agent_cli.py.
"""
import argparse
import datetime
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import agent_cli  # noqa: E402  (skill script, trusted)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--copy', required=True); ap.add_argument('--context', required=True); ap.add_argument('--contact', required=True)
    ap.add_argument('--slides', type=int, required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--model', default='claude-opus-5-5'); ap.add_argument('--effort', default='max'); ap.add_argument('--timeout', type=int, default=1800)
    a = ap.parse_args()
    n = a.slides
    rubric = (SKILL / 'references' / 'rubric-message.md').read_text(encoding='utf-8')
    judged = rubric[rubric.index('## 심사 항목'):rubric.index('## 정직성 규칙')]
    prompt = ((SKILL / 'references' / 'judge-message-prompt.md').read_text(encoding='utf-8') + '\n\n---\n채점표 심사 항목:\n' + judged +
              f'\n\n---\n이 폴더의 파일: copy.txt (슬라이드 {n}장의 문구), context.txt (논문 초록·범위), contact.png (전체 보기).\n'
              f'내용 슬라이드 = 2 … {n - 1} (1장 표지, {n}장 정리 제외). 세 파일을 Read 도구로 읽은 뒤 JSON만 출력하라.')
    t0 = datetime.datetime.now()
    with tempfile.TemporaryDirectory(prefix='judge-msg-') as td:
        shutil.copy(a.copy, Path(td) / 'copy.txt'); shutil.copy(a.context, Path(td) / 'context.txt'); shutil.copy(a.contact, Path(td) / 'contact.png')
        try:
            env = agent_cli.run(prompt, a.model, a.effort, cwd=td, role='judge', timeout=a.timeout)
        except subprocess.TimeoutExpired:
            sys.exit(f'judge run exceeded {a.timeout}s')
    if env.get('no_json'):
        sys.exit(f"{env['backend']} returned no result: " + (env.get('error_text') or '')[-1200:])
    text = env.get('result') or ''
    m = re.search(r'```json\s*(\{.*?\})\s*```', text, re.S) or re.search(r'(\{.*\})', text, re.S)
    parsed = None; err = ''
    if m:
        try:
            parsed = json.loads(m.group(1))
        except json.JSONDecodeError as e:
            err = f'judge JSON unparsable: {e}'
    else:
        err = 'no JSON block in judge output'
    if parsed:
        rows = {int(s.get('n', 0)): s for s in parsed.get('slides', [])}
        missing = [i for i in range(2, n) if i not in rows]
        bad = [i for i, s in rows.items() if any(s.get(k) not in (0, 1, 2) for k in ('N1', 'N2', 'N4'))]
        deck = parsed.get('deck') or {}
        deck_bad = not (isinstance(deck.get('N3'), (int, float)) and 0 <= deck['N3'] <= 10 and isinstance(deck.get('N5'), (int, float)) and 0 <= deck['N5'] <= 12)
        if missing or bad or deck_bad:
            err = f'judge file incomplete: missing {missing} bad {bad} deck_bad {deck_bad}'
    out = {'at': t0.isoformat(timespec='seconds'), 'model': a.model, 'effort': a.effort, 'copy': str(Path(a.copy).resolve()), 'slides_total': n,
           'cost_usd': env.get('total_cost_usd'), 'duration_ms': env.get('duration_ms'), 'usage': env.get('usage'),
           'is_error': env.get('is_error'), 'parse_error': err, 'judge': parsed, 'raw': text,
           'backend': env.get('backend'), 'model_reported': env.get('model_reported'), 'cli_version': env.get('cli_version'), 'error_text': env.get('error_text')}
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f"message judge {a.model}/{a.effort} ({env.get('backend')}): {agent_cli.spend(env)} · {env.get('duration_ms')} ms · {'OK' if parsed and not err else 'PROBLEM: ' + err} → {a.out}")
    sys.exit(0 if parsed and not err else 1)


if __name__ == '__main__':
    main()

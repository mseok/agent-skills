# Korean slide copy: noun phrases, checked automatically

Use compact noun phrases for Korean text visible on slides: titles, subtitles, body explanations, captions, labels and table cells. Avoid report-like declarative sentences ending in `~한다`, `~된다`, `~있다`, `~이다` or their past/polite variants. This applies to Korean presentation copy, not the assistant's conversation or the spoken speaker script.

Rewrite the whole phrase while preserving the scientific relation, scope and uncertainty. Do not simply delete the last syllable or mechanically turn every sentence into `~함`.

| Avoid | Prefer |
|---|---|
| CHEK1 구조는 GSK3B 결합 가설과 선택성 검증을 연결한다 | CHEK1 구조 기반 결합 가설과 선택성 검증 |
| GSK3가 기질을 인산화한다 | GSK3에 의한 기질 인산화 |
| 카보닐 산소는 수소결합 수용체가 될 수 있다 | 카보닐 산소의 수소결합 수용 가능성 |
| 세포 반응은 아직 검증되지 않았다 | 세포 반응: 미검증 |

After exporting a Korean PPTX, run:

```sh
python3 /Users/mseok/.codex/skills/research-talk/scripts/check_korean_slide_copy.py /absolute/path/deck.pptx --report /absolute/path/qa/korean-copy.json
```

Exit 1 means unresolved findings. The report identifies slide number, XML part, object ID/name, paragraph, text and matched ending. Correct the source copy and re-export, then rerun; do not deliver on the assumption that a visual proofread caught the issue. The checker is read-only and rejoins formatting runs, including table and chart text. It excludes speaker notes, hidden slides, master-only text and raster image labels. Its suffix rules are a useful automatic gate, not a complete Korean grammar analysis. Inspect uncovered text when present, especially text baked into a newly made image.

Preserve exact quoted paper titles and literal source text. If such text or a proper name triggers a false positive, `--exceptions /path/literal-exceptions.json` accepts a list with the exact report fields `part`, `object_id`, `paragraph`, `text`, plus a nonempty `reason` explaining the immutable source. No wildcard or slide-wide exemptions. Never exempt author-written declarative prose instead of revising it. Exempted findings remain visible in the report.

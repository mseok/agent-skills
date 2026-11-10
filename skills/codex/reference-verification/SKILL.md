---
name: reference-verification
description: Verify reference metadata against official records and, when requested, assess whether citations support manuscript claims. Use for bibliography or reference checks, BibTeX/DOI/title/author/year/version validation, citation audits, and the final reference check called by paper-writing. Metadata-only requests exclude scientific-content or entailment review. Review and correction proposals do not authorize live document edits.
---

# Reference verification

Use the actual saved document and bibliography, including supplied SI. Preserve the original and declare the population checked.

## Choose the scope

- **Metadata** is the default for bibliography, BibTeX, or bibliographic-information checks. Verify identity, title, ordered authors, date, venue, volume/issue/pages, identifiers and cited version. Do not include scientific-content findings or prior claim-support blockers in this verdict.
- **Full** adds a claim-by-claim citation-support review. Use it when explicitly requested or when `paper-writing` calls this skill before manuscript finalization. A metadata-only pass never implies that cited claims are supported.

Read [the workflow](references/workflow.md), execute the chosen scope, and keep primary-source evidence and field-level decisions outside the manuscript. For each applicable metadata field record `verified`, `format_equivalent`, `missing_optional`, `mismatch`, or `unverified`; distinguish genuine conflicts from initials, accents, accepted abbreviations and online/issue dates. Conflicts between official sources require version-specific adjudication, not blind replacement with one API response.

For LaTeX, run the bundled `scripts/check_reference_gate.py` with explicit `--mode metadata` or `--mode full` on the final saved source and the evidence-backed review. The tool checks review coverage, recorded findings and freshness; it does not fetch metadata or judge its truth. Other document formats use an explicit reference inventory and the same evidence requirements.

Report the selected scope, counts checked, concrete mismatches, unresolved metadata and optional enrichment separately. Provide minimal correction candidates. Do not change the manuscript unless the user has authorized that change set.

## User decisions

- 2026-11-09: "이거 paper-writing? 가장 최근에 manuscript writing skill 로 최신화한거에 reference 체킹하는걸 언제나 맨 마지막에 최종화전에는 해야한다는 식으로 추가해줬으면 좋겠음. 그리고 실제로 검사도 한 번 해보고." The mandatory finalization call remains in paper-writing.
- 2026-11-09: "좋아 그럼 원고에서 각 레퍼들 내용말고 레퍼 메타데이터 문제없는지 지금 만든 스킬로 검증해줘. Papet writing skill 자체에 넣기보다 그게 인용ㅇ할 수 있게 새로은 스킬로 만들어두는게 여러모로 관리하기 편하지 않을지?" This separates the reusable procedure and tools into this skill. The requested K-Fold run is metadata-only; the prior full-verification requirement for paper finalization is retained.

# Journal editor review behavioral fixtures

These are synthetic regression cases for the intended review workflow. They do not encode real journal decisions, acceptance probabilities, or a validated model of editorial practice. Every manuscript, journal, letter, numerical result and `.example` URL in the inputs is invented for these tests.

## Files and separation

- `inputs.json`: execution boundary plus 16 self-contained cases in eight pairs. Each case contains raw manuscript excerpts, mock official pages, access states and, where applicable, raw history or mock reviewer responses. It contains no expected verdict.
- `rubric.json`: evaluator-only expectations and critical failures. Never supply it to the response-producing agent.

The A/B cases within a family must be generated in separate fresh contexts. Do not show either output or the other pair member to the producer. Family titles and expectations belong to the evaluator, not the producer.

## Bounded test procedure

1. Select one case. Give the producer the skill, only the relevant references, the top-level execution contract and that case. Preserve the user request and source access/version/date metadata.
2. This is an offline read-only fixture run. Do not visit the synthetic URLs, execute scientific code, edit a manuscript, save review artifacts or contact services. The producer may return an orchestration plan or `mock_calls`; the supplied reviewer records are mock responses, not proof that real agents ran.
3. Capture the answer and any proposed/mock actions outside the source checkout. Record the skill commit, tested model, mode, supplied references and run conditions. These recording instructions are for the test runner; they do not authorize the producer to write.
4. An evaluator with `rubric.json` judges each response, then compares the paired outputs. Assess supported judgments and changes under new evidence, not exact wording, headings, fixed concern counts or a fixed accept/reject label.
5. Report all eight family scores, critical failures and access/execution limits. Keep structural validation, simulated behavioral results, live source retrieval and real journal outcomes separate. Do not infer desk-rejection prediction accuracy from fixture success.

Critical is the default and should be meaningfully skeptical. Stress may intentionally use harsher personas to generate hypotheses; final retained findings still require evidence. Neither mode must reject, and the pair is not expected to flip verdicts merely because the mode changed.

A useful missing-input question names the actual dependency, offers a recommended path and relevant alternatives, and leaves independent useful work available. Do not ask again for facts the input already supplies.

## Coverage

| Family | Contrast |
| --- | --- |
| T01 | Ambiguous journal versus confirmed publisher/article type; useful options and recommendation |
| T02 | Same scientific evidence, different journal eligibility |
| T03 | Search summary versus primary Methods/query contract |
| T04 | Missing manuscript/SI versus supplied validation |
| T05 | Missing decisive controls versus adequate controls; no forced issues |
| T06 | Rejection history and later policies/results versus an earlier evaluation date |
| T07 | Cosmetic/narrative revision versus new bounded empirical evidence |
| T08 | Critical versus Stress; verified findings, failed reviewer, shared model and inaccessible page |

The core acceptance target is 2/2 on every family and no critical failures. This checks the intended behavior of the fixtures; it does not certify that the skill predicts a journal decision.

## Implementation validation — 2026-11-09

- Structural checks: frontmatter/UI metadata, installer syntax, local Markdown links, 16 unique cases with eight A/B pairs, unique source IDs and reserved `.example` URLs passed. These checks do not evaluate scientific judgment.
- First behavioral run: 16 responses in separate fresh contexts, one case per producer, without the paired case or evaluator rubric. Two independent evaluators scored the eight pairs **15/16**, with zero rubric-critical failures. T06 received 1/2 for inferring no external review at Venue D from an editorial letter without an attached report. T03's central comparison passed, but one response incorrectly called differently scoped firstness statements contradictory.
- Narrow correction: explicitly compare subjects, qualifiers and scope before alleging contradiction; require explicit evidence for a historical review stage. Inputs and grading rubric were unchanged.
- Targeted retest: four fresh responses for T03A/B and T06A/B. An independent evaluator scored both pairs 2/2, with no material or smaller unsupported claims identified. Combining unchanged-family results and these retests gives **16/16 across the eight families**. This was a targeted regression run, not a second execution of all 16 cases on the amended instructions.
- Total synthetic production: **20 responses** (16 initial + 4 targeted retests). The inherited session model was used without a model override; the exact backend identifier was not independently verified. Instruction hashes, response artifacts and assertion-level grading were captured outside Git. The only authorized test-runner writes were those isolated capture records; they were not treated as permission from the fictional manuscript author to save or edit anything.
- Scope: evaluators compared captured answers and action plans with raw fixture evidence; they did not independently audit every producer tool trace. Mock delegation does not establish actual panel execution. Real-journal prediction accuracy, user manuscript outcomes and improvement over a no-skill baseline have not been validated.

### Live public-source workflow check

Used Konstantinos Bougiatiotis, Dimitrios Kelesis and Georgios Paliouras, [Improving Molecular Property Prediction in Small Language Models Using Graph-based Tools, arXiv:2607.13115v1](https://arxiv.org/html/2607.13115v1), as a public workflow exercise against current NMI Article and JCIM Articles criteria. This was not a reconstruction of a historical journal decision.

The coordinating Editor retrieved official criteria, dispatched two genuinely fresh-context editorial readers with contribution/reader-value and evaluation/evidence lenses, and then dispatched a separate fresh-context audit with neutral questions and raw source links. The audit was not given the first readers' reports or verdicts. The Editor reconciled the memos against audited evidence rather than vote counts. Only isolated test records were saved; no manuscript, service, analysis code or scientific experiment was changed or run.

Both readers applied different journal-specific considerations, including JCIM's editorial guidance beyond its broad scope. Full main text and Appendix A, source figures, relevant primary-method literature and official criteria were checked across roles. A material source gap was returned to the coordinator as a recommended request for evaluation records plus the alternative of proceeding on v1 with stated limits; the coordinator selected the latter. The audit and Editor retained reporting gaps as unresolved and did not infer numerical errors, biological causality, a universal wet-lab requirement or confirmed duplication.

Limits: some official Nature pages were retrieved through indexed official text after direct-access redirects. One reader could not inspect artwork that the other reader and auditor later inspected. A bounded literature search incidentally exposed the auditor to third-party AI-review snippets; those pages were not opened or used, but the audit was not perfectly blind. The public manuscript may be familiar to the models. This check establishes an observed workflow with source/access reporting, not independent human expertise, causal improvement, representative journal calibration or publication-prediction accuracy. The user's own manuscript was not evaluated.

## Design provenance

These instructions are newly written for this skill, drawing on inspected workflow ideas rather than importing a package or its journal/personality presets:

- [pedrohcgs review-paper](https://github.com/pedrohcgs/claude-code-my-workflow/blob/main/.claude/skills/review-paper/SKILL.md): editor-first workflow, contribution restatement and verification of criticisms.
- [Aperivue self-review](https://github.com/Aperivue/medsci-skills/blob/main/skills/self-review/SKILL.md): domain-specific checks and reducing over-defended narratives while preserving necessary disclosure.
- [neuromechanist paper-review](https://github.com/neuromechanist/research-skills/blob/main/plugins/manuscript/skills/paper-review/SKILL.md): independent-context readers and location-grounded concerns.
- [sohan-shingade paper-reviewer](https://github.com/sohan-shingade/paper-reviewer): issue tracking and revision lifecycle; its generic desk gate and difficulty biases are not journal profiles here.

Profile sources, case coverage and actual validation must be reported for this implementation. These predecessors do not establish this skill's real-journal prediction accuracy.

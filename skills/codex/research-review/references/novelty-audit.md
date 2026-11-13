# Novelty Audit

## Trigger and inputs

Use for novelty, prior-art overlap, differentiation, originality or claims that existing work cannot do something. Also use when an idea evaluation depends on those claims. Brainstorming may produce labelled hypotheses without completing a final novelty audit; inspect obvious overlap before presenting a proposal as new.

Required: the scientific question or decision, proposed contribution and scope of the novelty claim. An idea need not already be implemented or evaluated. Recover relevant user decisions and earlier attempts when available; do not infer adoption from an assistant's proposal or an absence of objection.

## Checks

1. **Define the contribution being tested.** Separate a new method or decision policy, scientific finding, data/measurement, evaluation procedure, new validated application and rigorous reproduction/refutation. Explain value relative to the user's current objective instead of making algorithmic novelty the only acceptable outcome.
2. **Find the closest actual competitors.** Search by question, input/output, action/decision, method and evaluation scope, including strong non-agent specialist approaches. Names and keywords may differ. Treat paper names recalled from earlier notes or conversations as leads whose relevance and facts must be checked, not a permanent required reading list.
3. **Verify consequential overlap.** For the papers that determine the judgment, read the relevant Methods/SI, implementation/configuration and actual evaluation when available. Compare claimed capability, implemented behavior, evaluated conditions, limitations and overlap with the proposal. Mark each unknown. Abstracts support triage, not a final judgment about an unreported implementation.
4. **Test both supporting and contrary explanations.** A familiar component may overlap while the scientific question or demonstrated capability differs. A feature may be implemented without resolving the claimed problem. Conversely, relabelling known operators, orchestration or personas does not by itself establish a new method or superior capability. Attribute the exact remaining difference rather than declaring the whole idea new or redundant.
5. **Separate differentiation from demonstration.** A distinct proposed computation can remain a plausible contribution before experiments. Claims of achieved transfer, discovery, reliability or superiority require corresponding evidence. Do not require an unbuilt idea to have already won an evaluation merely to remain worth investigating.
6. **Check earlier decisions in their conditions.** Distinguish implementation failure, negative scientific findings, unavailable resources and user rejection. Do not repeat the same proposal under unchanged conditions. New data, tools or objectives may justify reconsideration; state what changed, and obtain clarification before overriding a still-applicable explicit exclusion.
7. **Bound the search and verdict.** Prioritize material nearest neighbors; do not require a fixed paper count or exhaustive literature access. Stop at the authorized search/resource boundary, when decisive overlaps are resolved, or when the unresolved evidence can be stated clearly. Record the searched concepts, source/version range and decisive remaining gap. Search failure is not proof that no prior work exists.

## Sources

Use claim-relevant primary papers, Methods/SI, actual released code and settings, evaluation tables/records and authoritative benchmark definitions. Code availability alone is not proof of behavior; a missing symbol or keyword alone is not proof of absence. Preserve discrepancies across paper versions and releases. A negative statement must stay within the inspected source/version scope.

## Output

Return the judgment first, then a small overlap comparison when useful. Include:

- What overlaps, what differs and the supporting source locations.
- The proposed contribution's kind and scientific value.
- Whether the remaining difference is conceptual, implemented or empirically demonstrated.
- Search coverage, unresolved access/version conflicts and the evidence most likely to change the judgment.

Use bounded conclusions such as confirmed overlap, differentiation insufficient for this claim, plausible differentiation not yet validated, or low overlap within the reviewed scope. Do not merge novelty, scientific value, current feasibility and evidence confidence into one score or unconditional Go/No-go label.

## Failure handling and regression

If decisive sources cannot be read, limit the relevant novelty or absence claim and provide the supported comparison. Do not turn unknown implementation into a novelty gap, nor reject an idea solely because code or experiments are unavailable. Recommend a minimal discriminating check only when it informs the next decision; an audit request authorizes no implementation or experiment.

Primary regression families: T01, T03, T04, T12, T13, T15. Include counter-cases where genuine new evidence supports differentiation, the user legitimately changes the research objective, and changed failure conditions justify revisiting a proposal. Fixed negative conclusions tied to paper names fail the audit.

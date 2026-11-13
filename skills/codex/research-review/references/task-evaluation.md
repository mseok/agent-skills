# Scientific Task Evaluation

## Trigger and inputs

Use to assess whether a research idea or claimed capability can be evaluated, and whether proposed data, benchmark, oracle, baseline and resources support that evaluation. Dataset feasibility is part of this mode. A code bug or formatting-only task does not require this full procedure.

Required: the capability/claim to test, initial information, allowed actions/tools and known data/resource constraints. Missing paths or metadata should be investigated when accessible, not invented. Distinguish a proposed evaluation from an approved run.

## Checks

1. **Define the decision and evidence unit.** Describe input, allowed action, output and the observation that could support or weaken the claim. Establish whether records represent molecules, formulations, cells, donors, profiles, experiments or trajectories, and what is independent. Preserve unique entity, condition, repeat and row counts separately.
2. **Inspect actual data and conditions.** Read schema, definitions, protocol, access terms and relevant examples. Identify fixed and changing variables, grouping/pairing, missingness, assays, units and confounders. Do not assume a needed paired dataset or unreported outcome exists. Uncontrolled data may support descriptive analysis or prediction under stated assumptions without directly identifying a causal effect.
3. **Separate task inputs from evaluation evidence.** Identify the source, meaning, accessibility and reliability of labels or oracle responses. Mark proxy labels and restricted candidate sets. Inspect shared sources/correlated errors in combined verifiers, error propagation and whether relevant ablations establish additional information. Several tools repeating the same model output are not independent validation. Keep evaluation-only answers hidden from the solver. An expert protocol, prospective measurement or formal test may be suitable; a ready-made label table is not required for all valuable research.
4. **Inspect information flow and leakage.** Check tuning versus final evaluation, related samples, time/campaign/scaffold/cohort overlap where relevant, and answers exposed by prompts, examples, retrieval, tools or label construction. Distinguish known exposure, plausible exposure and unknown pretraining access. Public data do not automatically prove contamination, and anonymization or a temporal split does not certify its absence.
5. **Match the metric to the claim.** State direction, units, denominator, coverage, failures/abstentions and what the metric does and does not measure. Preserve the distinction between reproducing an analysis, optimizing a predictor, ranking candidates, explaining a mechanism and discovering validated knowledge. Choose uncertainty and repetition for the evidence unit and question; do not impose a fixed seed count or fabricate intervals/significance.
6. **Choose discriminating comparisons.** Use baselines and ablations needed to attribute the claimed contribution. For multi-agent superiority, consider strong single, iterative single and domain methods with consequential data/tool/information/compute/query access controlled or disclosed. Select random search or Bayesian optimization only when relevant. Include a cost-performance tradeoff where strict budget matching would hide the actual decision. Single-agent success may weaken a multi-agent superiority claim without making the scientific task worthless.
7. **Check feasibility and identifiability separately.** Verify access, tool outputs, runtime/query costs and actual execution constraints. Distinguish missing data/resources, a test design that is not yet specified, and a claim the supplied information cannot identify. Conditional prediction, prioritization or next-experiment selection can remain useful without confirming a specific outcome or causal mechanism.
8. **Find the smallest useful validation.** Identify existing evidence that can answer first, a representative check, failure/stopping conditions and the strongest conclusion even success would permit. Respect the user's current phase: scientific scope only does not authorize milestones, architecture, new benchmarks or experimental runs.

## Sources

Use actual dataset schema/README and access conditions, scientific protocols, raw/processed record definitions, evaluation code, tool documentation and supplied run logs. Trace sample counts and result numbers to their real source. A literature description, simulated oracle or prior assistant report is not proof that an evaluation resource is available. Use the current host's actual resources instead of assuming another machine's environment.

## Output

Lead with what can be assessed now. Provide a compact task contract when useful: question, supplied input, allowed action/output, evaluation evidence, metric, baseline and resource boundary. Separate:

- Feasible with current evidence and access.
- Feasible conditional on named data, measurement, protocol or resources.
- Not identifiable for the specified claim from the supplied information.

Explain the limits and discriminating next check. Keep current feasibility separate from scientific value and novelty. Do not produce fictional scores or convert a proposal into an executed result. Requested figures and durable records follow their existing specialists.

## Failure handling and regression

If an oracle, required pairing or access condition is unverified, withhold only the dependent feasibility claim and identify what must be checked. If current inputs cannot establish a mechanism, bound that conclusion and distinguish possible predictive or observational work. Do not discard all incomplete datasets, treat all simulations as invalid, or optimize the task definition until the preferred system wins.

Primary regression families: T05, T06, T07, T08, T09, T10, T11, T12, T15. T04 and T13 test scope, T14/T16 test interpretation, and T17 tests execution reporting. Pair weak-information cases with added-information cases, include valid synthetic/theoretical evaluations, and accept single/domain baselines when the evidence favors them. Tests must assess the supplied evidence, not an agent count, a benchmark name or a preset rejection label.

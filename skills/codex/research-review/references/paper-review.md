# Paper Review

## Trigger and inputs

Use for a paper's actual task, method, implementation, agent autonomy, evaluation or scientific claim. A short explanation needs only the checks relevant to that question; do not automatically perform a novelty audit.

Required: an identifiable paper or supplied source and the question to answer. Resolve versions and relevant Methods, Supplementary Information (SI), figures, tables and public implementation from available sources. Missing material is an access state, not evidence that a feature is absent. Apply the main skill's source ledger and action boundaries.

## Checks

1. **Recover the actual task.** State the initial inputs, required output and scientific decision. Separate information supplied to the system from predictions, selections, experiments or evidence it newly obtains. Do not redefine a task from words such as scientific, discovery or agent in the abstract.
2. **Trace the mechanism of the method.** Identify the optimized variable, state, action, score, selection, update and stopping rule where relevant. Distinguish molecule edits from workflow or predictor optimization. For a non-agent or theoretical paper, explain its actual operations or argument rather than imposing an agent loop.
3. **Check implementation and attribution.** Locate claim-critical Methods/SI passages, functions/configuration or public trajectories. Separate proposed components, implemented components and components actually used in evaluation. Identify fixed expert scaffolds, tools and supplied evidence before attributing capability to the model. A repository's existence is not implementation inspection, and code inspection is not execution.
4. **Inspect the reported evaluation.** Establish data origin, record and independent evidence units, counts, conditions, ground truth/proxy, split and access rules, metrics, consequential baseline differences and reported results. When they affect the performance judgment, inspect replication/run variability, uncertainty, aggregation and subgroup coverage at the right unit of analysis. Do not invent missing intervals or significance. Preserve failures and coverage. Trace important quantitative statements to the actual table, figure, SI item or evaluation record.
5. **Bound the claim.** Separate author claims, reported observations, your inference and proposed explanations. Link each important conclusion to the evidence that supports it. Distinguish an association or pathway inference from causal/fitness validation, and aggregate human statistics from observed individual decisions. Evaluate proof, simulation, observational and intervention evidence against the claim they address, without a universal wet-lab hierarchy.
6. **Explain one concrete path when needed.** Use an actual input, node/action or trajectory from the source. If unavailable, use a clearly labelled hypothetical example or qualitative path; do not invent a paper's scores, outputs or experiment. Explain unfamiliar terms at first use.

If paper, SI, code and logs disagree, retain their versions and the specific conflict. Do not assume the newest code produced the published results or choose the version that best supports the desired conclusion.

## Sources

Use primary paper text and claim-relevant Methods/SI, figure/table captions, released implementation and configuration, evaluation scripts and public execution records. Inspect the source supporting the claim, not only search snippets or other agents' summaries. Additional literature discovery is needed only when the question requires context or comparison.

## Output

Lead with the answer and its supported scope. Include only useful parts of:

- Actual task and supplied inputs versus produced outputs.
- How the method operates, with a concrete walkthrough where it helps.
- What is proposed, implemented and evaluated under which conditions.
- The decisive result and exact source locations.
- Material uncertainty, conflicting versions and the claim that remains unsupported.

Keep method novelty, scientific value and feasibility separate if they arise. Do not force a long paper card or competitor table into a targeted question. When a durable note or figure is requested, pass supported content to its specialist rather than copying acquisition logs into the scientific body.

## Failure handling and regression

With abstract-only access, provide a faithful abstract-level explanation and limit implementation, performance and novelty conclusions. Code that is private, unavailable or unnecessary for the question does not invalidate the whole paper. Ask for missing decisive material only when it blocks the requested judgment; continue with supported parts.

Primary regression families: T02, T03, T08, T09, T10, T14, T16, T18. Relevant cross-checks: T07 and T11; T17 applies to every statement about reading, running or saving. Test both overclaiming under weak evidence and appropriate stronger conclusions when decisive evidence is supplied. Do not fix a verdict to a paper's name or blacklist particular verbs.

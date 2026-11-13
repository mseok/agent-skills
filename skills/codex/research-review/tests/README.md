# Research-review regression fixtures

This suite preserves the handoff document's **T01–T18** as 18 behavioral regression families. Each family has a base case and a contrasting or recovery case, for **36 cases**. The examples are synthetic; anonymous paper labels, results, decisions and tool transcripts are not claims about real literature or past conversations.

## Inputs and evaluator separation

- `inputs.json` is the producer input: case ID, family, variant, user request and self-contained source materials. It contains no expected verdict or grading assertions.
- `rubric.json` is evaluator-only material: the same case IDs with evidence-based assertions and critical failures. Do not provide it to the producer or summarize its intended answer before evaluation.
- Every fixture is a review-only task. Service and execution records are explicitly mock. Do not browse, run scientific code, edit project files or contact Obsidian or any other service to resolve these cases. Supplied source access failures remain part of the input condition.

Use a fresh evaluation context with the installed skill and only the selected input case. A batch may contain several independent cases, but responses must retain their IDs and must not import facts or decisions from another case. Save evaluation responses outside the skill/repository's tracked source, following the task's authorized destination.

## What to judge

Read each response against the supplied source locations and that case's assertions. Record each assertion as satisfied, partial or unsatisfied, with the response passage and supporting fixture evidence. Record critical failures separately; a polished answer or high average score does not compensate for fabrication, unsupported certainty, decision-state corruption or unauthorized actions.

Judge semantic agreement with the evidence, not exact headings, a fixed negative verdict, keyword presence, number of citations or answer length. Concision must preserve the conditions needed to understand the judgment. Source excerpts count as supplied evidence; they do not establish independent reproduction by the reviewing agent.

The paired cases test both restraint and appropriate updating:

- T01/T03/T14 add substantive differentiation or newly accessible evidence.
- T04 changes the user's adopted goal; T12 explicitly permits a changed-condition revisit.
- T05/T07/T09 add information or controls supporting a stronger but bounded judgment.
- T06 permits a strong single-agent result to be a valid conclusion.
- T10 distinguishes aggregate counts from a documented candidate-level protocol.
- T11 distinguishes demonstrated answer exposure from bounded controls and unknown pretraining membership.
- T13 changes scope-only discussion into an authorized architecture proposal, still without execution.
- T16 pairs limited DFT evidence with a self-contained proof supporting a strong statement under explicit assumptions.
- T17 pairs incomplete and successful **mock** tool records; neither implies real service operations.
- T18 pairs an exact synthetic numerical trace with a source lacking real trajectory values.

The fixture family IDs preserve traceability to the handoff; they do not certify the historical paper descriptions in that handoff. Taxonomy IDs such as `type:F01` and case-history IDs such as `case:F01` are distinct and are not used as test-case identifiers here.

## Validation and reporting

Validate JSON shape, unique IDs, all 18 base/counter pairs, nonempty materials and rubric assertions, and one-to-one input/rubric coverage before behavioral evaluation. These checks prove fixture consistency only. They do **not** mean that the research-review skill has passed 36 behavioral tests.

After running a behavioral evaluation, report the actual cases attempted, assertion outcomes, critical failures, review method and any unresolved judgments. Do not state that a case passed solely because the response used cautious language. A response that ignores sufficient positive evidence or refuses all useful analysis can fail too. Reassess failed cases after a skill change, and use additional unseen inputs to check transfer beyond these development fixtures.

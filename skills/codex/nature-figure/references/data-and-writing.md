# From evidence to panels and text

Inspect column meanings, units, missingness, replicate identity, grouping and metric direction. Preserve exact input locators and relevant run/checkpoint/subset identity. A repository default does not establish a reported experimental setting. Data transcribed from an image remain transcribed data, not raw observations.

Choose an encoding from the question:

| Reader question | Useful starting point | Meaning to preserve |
|---|---|---|
| How do groups differ? | Individual points with a summary/interval; box or distribution plot | Independent sample unit, sample counts, what interval represents |
| How did the same cases change? | Paired points, connecting lines or paired differences | Match cases by identifier; do not pair by row order |
| How do two quantities relate? | Scatter; density/hexbin for crowding | Axis units, population, transform; association is not causation |
| How does an outcome vary over time or a control parameter? | Ordered lines with justified uncertainty | True order/spacing, observed versus interpolated values |
| How do methods compare across benchmarks? | Dot/interval plot or heatmap | Matched conditions, denominators, missing cells and metric direction |
| What is the accuracy–cost tradeoff? | Scatter or supported Pareto frontier | Hardware, cost units, conditions; no unmeasured interpolation claim |
| What differs structurally? | Coordinate render, consistent-view comparison, useful inset | Source structure, alignment/selection, predicted versus experimental status |
| How does a method work? | Directed schematic of necessary inputs and transformations | Actual dependencies, training/inference distinction, deliberate omissions |

These are starting choices, not mandatory templates. Avoid hiding distributions behind bars when individual observations are available. If only aggregates exist, show them honestly. Use zero baselines for magnitude-encoded bars; disclose justified truncation elsewhere. Label log scales. Missing values are not zero. Report filters, aggregation, normalization, pairing, uncertainty method and statistical tests used. Do not pool mismatched evaluation populations for cosmetic simplicity or run new model experiments merely to finish a figure.

Write concise natural academic English. Prefer short noun phrases for axis labels and panel subjects, with units; define specialized abbreviations locally or in the caption. A panel heading should name its subject or state a supported result. Avoid promotional claims such as unprecedented or superior without evidence. Separate observed results, working assumptions and illustrative proposals.

Draft a caption with a short supported overview followed by panel descriptions in reading order. Include encodings, sample definition/count, summary and error-bar definitions, tests and relevant structural identifiers when known and applicable. Do not invent missing details. Keep long methodological explanations and source-to-claim audit notes outside the graphic; preserve them in accompanying records. The in-figure key and manuscript caption have different roles.

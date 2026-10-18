# Zotero note and comment templates

These are content templates, not commands. Escape user text for HTML when the
destination is a Zotero note. Keep annotation comments plain unless the live
tool accepts HTML safely.

## Independent paper summary note

This note is a separate paper-level artifact. It is not copied into an
annotation comment and it must not depend on the presence of annotations.

```html
<h1>{paper title}</h1>
<p><strong>Item:</strong> {item_key} · <strong>PDF:</strong> {attachment_key}</p>
<p><strong>Current judgment:</strong> {bounded one-sentence reading of the paper}</p>

<h2>Purpose and research question</h2>
<p>{why the problem matters, target, and strongest bounded claim}</p>

<h2>Introduction</h2>
<p>{problem, prior limitation, hypothesis or design objective}</p>

<h2>Method</h2>
<h3>System/model</h3>
<p>{objects, assumptions, variables, and mechanism}</p>
<h3>Experimental or benchmark design</h3>
<p>{data/benchmarks, interventions, controls, baselines, and splits}</p>
<h3>Evaluation</h3>
<p>{metrics, decision rule, calibration, and what counts as success}</p>

<h2>Results</h2>
<h3>Result 1: {name}</h3>
<p><strong>Setup:</strong> {what was compared}</p>
<p><strong>Observation:</strong> {measured result with page/denominator}</p>
<p><strong>Interpretation:</strong> {what this supports, bounded}</p>

<h2>What the paper establishes</h2>
<p>{supported conclusion}</p>
<h2>What it does not establish</h2>
<p>{alternative explanations, missing controls, scope boundary}</p>
<h2>Limitations and follow-ups</h2>
<ul><li>{limitation or discriminating next experiment}</li></ul>
<h2>Evidence map</h2>
<ul>
  <li>Introduction: p. {pages}</li>
  <li>Method: p. {pages}</li>
  <li>Results: p. {pages}</li>
  <li>Discussion/Conclusion: p. {pages}</li>
</ul>
<!-- zotero-annotation-research:paper-summary:v1;item={item_key};attachment={attachment_key} -->
```

For multiple results, repeat the `Result` block. Include the actual comparison
population and quantitative outcome rather than only the authors' headline.
When a figure/table/equation is essential, retain its page and figure/table
label; if the image or extraction is insufficient, state that limitation in
the note instead of inferring the result.

## Per-annotation comment append

Append after the user's existing comment, separated by a blank line:

```text
AI review ({mode})
Interpretation: {what the highlighted text means in context}
Why it matters: {importance to the paper or the user's hypothesis}
Hidden assumption / limitation: {what must be true, or what is not shown}
Follow-up: {smallest useful test or question}
<!-- zotero-annotation-research:v1;annotation={annotation_key};mode={mode} -->
```

Only include sections that are meaningful for the requested mode, but keep the
marker unchanged. Do not include a fabricated page, citation, or experiment.

## Non-PDF source note

Use this for a repository or webpage that is explicitly included alongside
papers but has no reliable PDF position to annotate. Keep it separate from
paper summaries and label repository claims as implementation evidence.

```html
<h1>{source title}</h1>
<p><strong>Item:</strong> {item_key} · <strong>URL:</strong> <a href="{url}">{url}</a></p>
<p><strong>Artifact type:</strong> repository/webpage, not a paper</p>
<p><strong>Current judgment:</strong> {bounded interpretation of what the artifact demonstrates}</p>
<h2>Purpose and workflow</h2>
<p>{what the artifact is intended to do}</p>
<h2>Implementation loop</h2>
<p>{stages, inputs, candidate changes, evaluation and selection gates}</p>
<h2>Observed demonstration</h2>
<p>{reported example, clearly labeled as repository evidence}</p>
<h2>What it does not establish</h2>
<p>{lack of peer-reviewed control, provenance, holdout or independent replication}</p>
<h2>Relation to the paper evidence</h2>
<p>{how it operationalizes or differs from the cited paper}</p>
<!-- zotero-annotation-research:source-summary:v1;item={item_key} -->
```

## Cross-paper synthesis note

Use simple HTML in the note body when the tool accepts it:

```html
<h1>{topic}</h1>
<p><strong>Scope:</strong> {selection rule and counts}</p>
<h2>Evidence by source</h2>
<ul>
  <li>{item key} · {annotation key} · p. {page}: {evidence and bounded claim}</li>
</ul>
<h2>Common claims</h2>
<p>{clustered claim with provenance}</p>
<h2>Contradictions and limits</h2>
<p>{conflict, alternative explanation, or missing control}</p>
<h2>Open questions and follow-ups</h2>
<p>{discriminating next experiments}</p>
<!-- zotero-annotation-research:synthesis:v1;scope={scope_digest} -->
```

The `scope_digest` is a stable digest of the sorted source keys, annotation
keys, tag/color filters, and mode. It is used only for duplicate detection and
must not contain a secret or the full paper text.

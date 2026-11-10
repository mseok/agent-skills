# Reference verification workflow

Choose **metadata** or **full** mode from SKILL.md. In a paper-writing finalization call, run full mode after the last substantive edit. For an explicit metadata-only request, stop at bibliographic verification and do not import citation-support findings into the result. Include supplied main text and SI when establishing which references are cited. Inspect the saved/exported deliverable, not a remembered draft. This procedure grants no permission to change a live document.

## Establish coverage

Inventory all cited bibliography entries and every citation use, including repeated and grouped citations. Resolve missing keys, duplicate keys and conflicting records for the same identifier. An unused library entry or two aliases for the same paper are not automatically errors. Preserve citation keys unless changing them is necessary and authorized.

For LaTeX with literal `input`, `include`, `subfile`, `bibliography` or `addbibresource` paths, the bundled script inventories the reachable sources and bibliography:

```sh
python3 scripts/check_reference_gate.py --source-root /path/to/export \
  --roots manuscript.tex supplementary_information.tex --mode metadata --inventory inventory.json
```

It is a static scanner for `cite`/natbib and `nocite` commands, not a TeX interpreter. For other citation commands, macro-generated citations/paths, conditional includes, verbatim examples, or non-LaTeX documents, use the compiled reference list and actual document to establish coverage explicitly; do not report a scanner-only pass. Detected unsupported citation commands, unresolved includes and `nocite{*}` block its automated gate.

## Verify identity and metadata

Retrieve the official BibTeX, CSL/registry metadata, or publisher/arXiv/software-release citation for **every cited entry**. Prefer DOI content negotiation (`Accept: application/x-bibtex`), Crossref/DataCite, and the exact publisher or release page. Scholar's BibTeX is a useful import source, but still compare it with the authoritative record. Do not generate factual fields from memory or infer a full author name from initials.

Compare title, ordered author list, publication year, venue, volume/issue/pages or article number, DOI, and any version-specific URL or software/dataset version. Read the returned values, not merely the HTTP status. Use the cited version: a valid preprint need not be replaced by a journal article; a software DOI does not prove which version an experiment used. Official README examples can themselves disagree with DOI records. A registry's BibTeX conversion may omit fields such as version, which then require the release record. Distinguish actual mismatches from optional DOI/issue enrichment or journal-style abbreviations.

Retain source URL, access date, relevant locator, and the raw export or inspected passage. Blocked access and rate limits are unverified, not proof of fabrication; do not repeatedly retry a rate-limited request. Never fill a missing field with a plausible guess.

## Verify each citation's role (full mode only)

Read the exact sentence/clause and enough primary text to assess its scope, direction, conditions and version. Record whether the citation directly supports the claim, supplies background, identifies a resource, supports part of a grouped citation, or fails to support it. A paper title or abstract may suffice for broad attribution but not a detailed mechanism or exact methods claim.

Do not expect an external resource paper to report the manuscript's new results or author-chosen settings. Do not require every paper in a grouped citation to support every clause; identify their respective roles. A correct bibliography entry does not establish entailment. Separate bibliographic errors, claim-support mismatches, and access limits.

## Record and check the final state

Keep evidence outside reader-facing prose. Both modes retain the final source digest, all cited keys, metadata verdicts, field-level decisions, primary evidence and locators, and unresolved metadata. Full mode additionally retains every citation-use identifier and a support verdict with rationale. Existing metadata evidence may be reused after checking the entry and cited version are unchanged; full mode also checks the claim/context. Rerun the chosen gate after any subsequent edit. For live application, verify the saved source by export/readback and rerun on that exact artifact.

For the bundled LaTeX gate, save a JSON review with this structure. All reference keys must be present. `uses` is required only in full mode. Each reference requires decisions for the nine fields listed below; use `not_applicable` with a reason where a source has no such field.

```json
{
  "snapshot_sha256": "digest from inventory",
  "references": {
    "paperKey": {
      "entry_sha256": "digest from inventory",
      "metadata_status": "verified",
      "fields": {
        "title": {"status": "verified", "reason": "Matches the publisher title."},
        "authors": {"status": "verified", "reason": "Ordered author names checked."},
        "date": {"status": "verified", "reason": "Year and any month match the cited edition."},
        "venue": {"status": "verified", "reason": "Matches the cited venue."},
        "volume": {"status": "not_applicable", "reason": "Preprint has no volume."},
        "issue": {"status": "not_applicable", "reason": "Preprint has no issue."},
        "pages": {"status": "not_applicable", "reason": "No publication page range."},
        "identifier": {"status": "verified", "reason": "Identifier resolves to this work."},
        "version": {"status": "verified", "reason": "Metadata and URL refer to the same version."}
      },
      "evidence": [{"url": "https://doi.org/...", "locator": "registry title and authors", "accessed": "YYYY-MM-DD"}],
      "reason": "Fields agree with the cited version; optional issue number omitted."
    }
  },
  "uses": {
    "use identifier from inventory": {
      "context_sha256": "digest from inventory",
      "references": {
        "paperKey": {
          "status": "supported",
          "evidence": [{"url": "https://...", "locator": "Results section 2", "accessed": "YYYY-MM-DD"}],
          "reason": "This passage supports the stated condition and direction."
        }
      }
    }
  }
}
```

Metadata statuses: `verified`, `mismatch`, `unverified`. Field statuses: `verified`, `format_equivalent`, `missing_optional`, `not_applicable`, `mismatch`, `unverified`; the last two block metadata clearance. Retain recorded and authoritative values when available. Do not infer a missing expected value from the manuscript itself. Full-mode use statuses are `supported`, `background`, `resource`, `partial`, `mismatch`, `unverified`. A `partial` verdict needs `disposition` equal to `covered_by_group`, `authors_own_work`, `needs_revision`, or `unresolved`, with a rationale. The last two block full clearance. Optional enrichment is not an automatic failure.

```sh
python3 scripts/check_reference_gate.py --source-root /path/to/export \
  --roots manuscript.tex supplementary_information.tex \
  --mode metadata --review reference-review.json --inventory inventory.json > gate-result.json
```

Use `--mode full` for manuscript finalization. Exit 0 means every review required by the selected mode is present, bound to the current source, and records no blocking finding. Exit 1 means that scope is not clear. The script does **not** fetch papers, verify reviewers' truthfulness, or prove scientific support. Perform metadata comparisons and, only in full mode, semantic review before populating it. Never mark an item verified merely to obtain exit 0.

Finish with the selected mode, population checked, metadata issues, access limits, applied versus proposed fixes, and the saved artifact checked. Add support issues only in full mode. Compilation and visual QA remain separate checks.

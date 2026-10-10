# Synthetic case artifacts for the SRCoT brief report

These are **partial public exports of existing research artifacts**, not new experiments or a validated emergency decision-support product. The scenarios, patient records, incident events, and unit interactions are synthetic, as confirmed by the corresponding author on 10 October 2026. Addresses and place names are used as scenario locations; no real incident at those locations is claimed.

**Do not use the generated outputs as medical advice, treatment protocols, dispatch instructions, or operational guidance.** They contain unverified and potentially incorrect statements. They are preserved to allow inspection of the reported behavior, including failures.

## Files and manuscript mapping

| Illustration | Human-readable report | Matching saved result |
| --- | --- | --- |
| EMS, Figure 2 | [report_srcot_run_2.public.md](ems-report-2/report_srcot_run_2.public.md) | [result_srcot_run_3.public.json](ems-report-2/result_srcot_run_3.public.json) |
| Munich-Sim, Figure 3, incident #000053 | [report.public.md](munich-sim-000053/report.public.md) | [result.public.json](munich-sim-000053/result.public.json) |

The manuscript figures are selected, condensed, and translated illustrations, not continuous verbatim reproductions of the reports.

The EMS filenames are crossed: the contents of `report_srcot_run_2.md` match `result_srcot_run_3.json`, **not** `result_srcot_run_2.json`. Final text, draft, and stored Judge metrics were compared before export. Original filename stems are retained; no matching-looking file pair was manufactured. The selected report has 11 claims and 5 missing facts in its stored heuristic metrics. These numbers are not correctness scores.

Munich-Sim run: `srcot_1768397359157_c7f6a1`, 14 January 2026. Its [partial request](munich-sim-000053/request.public.json) retains the recorded model/retrieval/Judge configuration and embedded synthetic Environment/Memory inputs.

## What was preserved and what was omitted

The Markdown exports preserve verbatim the original report's question, final answer, first-pass draft, follow-up questions, raw first-pass model output, Judge summary/metrics, and raw Judge output. No generated medical or operational statement was corrected or removed to make the results look better.

Added quotation blocks clearly mark the export warning and omissions. The omitted sections are retrieved contexts and evidence maps containing repeated source passages. The JSON exports retain generated outputs, claims, queries, control signals, and original metrics, but omit the retrieved-context and evidence-text payloads.

Those payloads contain SOP-labeled and general reference fragments whose provenance and redistribution rights have not been established. The complete corpora are **not** included here. The Munich request also has two local filesystem paths replaced with `null`, with an explicit explanation. It is therefore not a directly runnable request.

Original source files remain unchanged in the author's local archive. [provenance.json](provenance.json) records original and public-file SHA-256 hashes, filename mapping, and consistency checks without disclosing private filesystem paths.

## Reproducibility and interpretation limits

- Both selected report/result pairs identify the model as `gpt-oss-120b`. The available local EMS request names `gpt-oss-20b`; it is not published as the original request for this report.
- The historical model artifact, quantization, inference-runtime version, complete run configuration for EMS, and exact code revision producing these reports are not established by this export. The repository's current code must not be assumed to be the exact historical execution version.
- Stored `has_evidence`, `coverage`, and confidence fields are heuristic or model-generated signals. A non-empty retrieval result or source marker does **not** verify semantic support, factual correctness, clinical safety, or operational effectiveness.
- This is a selected two-case artifact illustration, not a representative benchmark, controlled comparison, or operator study. Omitted source payloads limit independent source-entailment checking.
- Full case material and source-rights questions can be addressed to the manuscript's corresponding author. Public access does not imply that third-party source text is licensed for redistribution.

## Export and verification

The standard-library-only exporter is [scripts/export_public_case_artifacts.py](../../scripts/export_public_case_artifacts.py). It requires the original local input directories, verifies their reviewed SHA-256 hashes, preserves retained model text, checks report/result consistency, and scans the exports for common secret patterns and private absolute paths. It does not call a model or run a new simulation.

From the repository root, validate the published files with:

```sh
python3 scripts/verify_public_case_artifacts.py
```

To reproduce the export from the original local files:

```sh
python3 scripts/export_public_case_artifacts.py \
  --ems-dir /path/to/original/ems \
  --munich-dir /path/to/original/munich-run \
  --output-dir artifacts/frontiers-cases
```

# Analysis Manifest Contract

Use `analysis_manifest.json` as the machine-readable execution record for a
provenance-sensitive analysis variant. Keep scientific interpretation and the
choice of the preferred variant in the parent `NOTES.md`.

## Decision rule

Require a manifest when any of these is true:

- the run is part of a parameter sweep, sensitivity analysis, model comparison,
  or repeated tailored rerun
- thresholds, controls, cell/sample subsets, statistical models, random seeds,
  normalization, smoothing, or other choices can change the result
- the workflow is multi-step, expensive, stochastic, or used downstream
- several inputs or external inputs make reconstruction non-obvious
- one result is selected from competing variants for a maintained conclusion

Do not require a new manifest when the task is only:

- color, font, label, legend, panel layout, or file-format adjustment
- deterministic copying, renaming, or conversion with no analytical change
- a transient diagnostic that creates no maintained result

A decorative output should point to the analytical variant that supplied its
data. If a nominally decorative rerun changes a subset, threshold,
transformation, fitted curve, or statistical result, treat it as analytical.

Examples from `topic_analysis`:

- cluster parameter searches, mediation variants, shared-control matching,
  permutation analyses, and condition-specific inferential summaries require
  manifests
- a PDF export, palette change, label adjustment, or manuscript panel layout
  does not require a separate manifest when its source analytical variant is
  already identified
- trajectory smoothing, fate-axis changes, or cell-type exclusions require a
  manifest when they change the scientific curve or interpretation, even when
  the output is a figure

## Storage contract

Give every maintained analytical execution an immutable, meaningfully named
variant directory:

```text
results/<goal>/<analysis>/runs/<meaningful-variant>/
├── analysis_manifest.json
└── <generated artifacts>
```

Do not reuse a successful variant directory for an execution with different
code, inputs, environment, or resolved parameters. Add a semantic suffix or a
run-date suffix when the same parameter label is executed again.

Track `analysis_manifest.json` in Git even when generated outputs are ignored.
Use `.gitignore` rules equivalent to:

```gitignore
/results/**
!/results/**/
!/results/**/NOTES.md
!/results/**/analysis_manifest.json
```

## Required schema

Use this minimum shape. Pipelines may add fields but must not rename these.

```json
{
  "schema_version": 1,
  "analysis_id": "T8-06",
  "variant_id": "shared_control_min200",
  "created_at": "2026-07-11T20:00:00Z",
  "provenance_mode": "native",
  "execution": {
    "command": ["python", "scripts/analysis.py", "--min-cells", "200"],
    "working_directory": "/absolute/repo/path",
    "script": "scripts/analysis.py",
    "script_sha256": "<64-character sha256>",
    "git_commit": "<commit sha>",
    "git_dirty": false,
    "interpreter": "/absolute/path/to/python"
  },
  "inputs": [
    {
      "path": "/path/to/input.h5ad",
      "role": "single-cell input",
      "size_bytes": 123,
      "mtime_utc": "2026-07-11T19:00:00Z",
      "sha256": null
    }
  ],
  "parameters": {
    "min_cells": 200,
    "control_mode": "shared"
  },
  "outputs": {
    "directory": "results/goal/analysis/runs/shared_control_min200",
    "artifacts": ["summary.csv", "figure.pdf"]
  },
  "validation": {
    "status": "passed",
    "checks": ["row counts", "focused tests"]
  },
  "relationships": {
    "derived_from": null,
    "supersedes": "shared_control_min100"
  }
}
```

Record resolved parameters, including defaults, rather than only the flags
typed on the command line. Use SHA-256 for scripts and reasonably sized inputs.
For very large inputs, record path, size, modification time, and a stable
dataset identifier; add a content checksum when practical.

Write the manifest only after the run succeeds and validation is known. Write
atomically so a partial run cannot look complete. Validate it with
`scripts/validate_analysis_manifest.py`.

## Relationship to `NOTES.md`

Do not duplicate the command, complete parameter map, input inventory, or
artifact inventory in `NOTES.md` when a valid manifest exists. Keep only:

- which analytical variant is currently preferred
- why it was selected over retained alternatives
- the scientific answer and supporting evidence
- trust limitations and the next decision
- links to the relevant variant directories or manifests

## Existing repositories

Do not demand manifests for every historical folder. Prioritize active and
scientifically important branches that meet the decision rule.

- If a real rerun is planned, let the pipeline write a native manifest.
- If exact legacy facts are recoverable, a backfill may use
  `"provenance_mode": "reconstructed"` and must state unknowns explicitly.
- Do not invent resolved defaults, hashes, timestamps, or validation.
- Until a missing manifest can be recovered, do not delete the only remaining
  reproducibility facts from a legacy note.


# Analysis Index

> This file is the repo-wide map of maintained analyses or workstreams.
>
> Use it to answer: what exists, where it lives, which version is current, and
> what has been superseded.

## Agent Instructions

- Read this file at the start of any session involving analysis outputs or
  analysis scripts.
- Match the current task to an existing maintained branch before creating new
  output directories.
- Keep same-direction variants and parameter sweeps under the parent branch's
  `runs/` directory. Use `analysis_manifest.json` for execution facts and the
  parent `NOTES.md` for comparison and scientific interpretation.
- Keep `Status` current: `ACTIVE`, `FINAL`, or `ARCHIVED`.

## Index

| ID | Theme | Analysis | Primary output dir | Status | Key scripts |
|----|-------|----------|--------------------|--------|-------------|

## Adding new analyses

1. Decide whether the work continues an existing maintained branch or starts a
   new one.
2. Create the output root under `results/<theme>/<branch-root>/` when the repo
   uses theme folders, or `results/<branch-root>/` otherwise.
3. Put same-direction variants under `runs/<variant>/`.
4. Require `analysis_manifest.json` when a variant is provenance-sensitive;
   presentation-only exports may point to their source analytical variant.
5. Add one branch-level `NOTES.md` at the shared root.
6. Add one row here for each distinct maintained analysis branch.

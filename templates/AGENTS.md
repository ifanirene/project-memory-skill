# Repository Guidelines

## Instructions

These guidelines apply to the entire repository. Keep changes focused, tested,
and easy to review.

- Treat `ANALYSIS_INDEX.md`, `results/.../NOTES.md`, `docs/LESSONS.md`, and
  `docs/pipelines/*.md` as a layered documentation system with distinct roles.
- Treat `docs/LESSONS.md` as the repo's memory document unless the repo already
  uses a different equivalent.
- On every new or continuing analysis session, review the relevant `NOTES.md`,
  `ANALYSIS_INDEX.md`, and `docs/LESSONS.md` together.
- `AGENTS.md` may evolve, but require explicit user permission before removing,
  weakening, or materially rewriting environment names, paths, versions,
  activation commands, security rules, execution requirements, mandatory
  validation commands, infrastructure instructions, or user-authored approval
  requirements. General cleanup permission is not sufficient.

## Project Structure & Module Organization

- Use this expandable computational-biology structure:

  ```text
  repo/
  ├── config/                 # analysis configuration
  ├── data/
  │   ├── raw/                # immutable source data
  │   ├── external/           # imported reference data
  │   ├── interim/            # restartable intermediate data
  │   └── processed/          # analysis-ready data
  ├── scripts/
  │   ├── preprocessing/
  │   ├── analysis/
  │   ├── visualization/
  │   └── utils/
  ├── notebooks/              # exploratory work
  ├── results/
  │   └── <goal>/<analysis>/runs/<variant>/
  ├── docs/
  │   ├── LESSONS.md
  │   └── pipelines/
  └── tests/
  ```

- If the repo already uses `src/`, keep one code home rather than splitting
  reusable logic across both `scripts/` and `src/`.
- When the repo groups outputs by theme, use
  `results/<theme>/<branch-root>/runs/<variant>/` for same-direction variants.
- When the repo does not use theme buckets, collapse that to
  `results/<branch-root>/runs/<variant>/`.
- Variant names should encode the provenance-changing choice, not a generic
  label like `v2`, `test`, or `rerun`.
- For most runs, save all outputs directly inside `<variant>/`. Only add
  artifact-type subfolders when the run is unusually large or mixes logically
  separate deliverables.

## Analysis Documentation Convention

- `ANALYSIS_INDEX.md` = repo-wide map of maintained analyses or workstreams.
- `results/.../NOTES.md` = scientific narrative and branch-level decision
  record.
- `results/.../runs/<variant>/analysis_manifest.json` = machine-readable
  execution record for provenance-sensitive analytical variants.
- `docs/LESSONS.md` = distilled repo-facing defaults, checks, traps, and
  preferences.
- `docs/pipelines/*.md` = shared workflow mechanics reused across analyses.
- Do not add a new `ANALYSIS_INDEX.md` row for minor reruns, figure polish, or
  small parameter changes inside an existing maintained branch.
- If script logic changes in a way that can change output semantics, save it as
  a new script path/name rather than silently reusing the old path.
- Require `analysis_manifest.json` for parameter sweeps, repeated meaningful
  reruns, inferential or multi-step pipelines, and runs whose thresholds,
  controls, subsets, models, seeds, or transformations can change the result.
- Do not require a new manifest for presentation-only colors, fonts, labels,
  layouts, or format conversions when the source analytical variant is clear.
- Pipelines that require a manifest must write it atomically after a successful
  run. Record the exact command, resolved parameters, code/Git provenance,
  inputs, output inventory, and validation. Keep the manifest in Git even when
  generated artifacts are ignored.
- Validate new or modified manifests with
  `python "$CODEX_HOME/skills/project-memory/scripts/validate_analysis_manifest.py" --repo .`.
- Do not duplicate manifest fields in `NOTES.md`. Link the current and retained
  analytical variants and explain why one is preferred.
- Rewrite the note around its current question, answer, evidence, canonical
  reproduction, limitations, and next decision instead of appending a dated
  update. Existing chronology is not protected content.
- Start every new or rewritten lesson with `Default:`, `Check:`, `Trap:`, or
  `Preference:` and state a trigger, action, and reason.

## `NOTES.md` Template

```md
## Status
ACTIVE | FINAL | ARCHIVED — last updated: YYYY-MM-DD

## Note archetype
branch runbook | child variant | synthesis/staging | provenance appendix

## Question
[one sentence: what this analysis is trying to answer]

## Branch scope
[one sentence: what variations belong here, and what would count as a new branch]

## Current answer
[the shortest defensible claim supported by the current artifacts]

## Evidence
- [result or validation that directly supports the current answer]

## Analytical variants
- Current: `runs/<variant>/analysis_manifest.json` — [why it is preferred]
- Retained comparison: `runs/<variant>/analysis_manifest.json` — [why it remains useful]
- Manifest decision: [required | not required — presentation-only or transient reason]

## Trust status
[what is validated and what remains uncertain]

## Decisions shaping the current analysis
- [decision and why it changes interpretation or reproduction]

## Limitations
- [caveat that constrains trust or interpretation]

## Next decision
- [the next evidence or choice needed]

## Cross-document review
- `ANALYSIS_INDEX.md`: [updated | no change — why]
- `docs/LESSONS.md`: [updated | no change — why]
- `Personal memory`: [updated | no change — why]

## Provenance appendix
[include only when sequence itself is needed to understand the current state]
```

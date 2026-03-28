# Document Contract Reference

Use these templates when setting up or repairing a repo memory system.

## Repo Guide Scope Block

```md
## Documentation Contract

- `AGENTS.md` stores repo-wide rules and documentation roles.
- `ANALYSIS_INDEX.md` maps maintained analyses, their output roots, and status.
- `NOTES.md` files live with each maintained analysis and describe reruns,
  validation, and extension context.
- `docs/LESSONS.md` stores durable cross-run lessons, defaults, and recurring
  traps.
- `docs/pipelines/` stores reusable workflow mechanics when a shared pipeline
  needs a dedicated runbook.
```

## Analysis Index Column Suggestion

```md
| ID | Theme | Analysis | Primary output dir | Status | Key scripts |
| -- | ----- | -------- | ------------------ | ------ | ----------- |
```

Suggested status values:

- `ACTIVE`: still being extended
- `FINAL`: settled and reproducible
- `ARCHIVED`: kept for provenance, not the live branch of record

## NOTES Template

```md
# <Analysis Name>

## Question

What this analysis is trying to answer.

## Current Output Root

`output/...` or `results/...`

## Inputs

- canonical source files
- important configuration files

## Entrypoints

- primary scripts or notebooks

## Validation

- what to inspect after reruns
- what is expected to stay stable

## Final Run

- exact command or reproducible entrypoint for the current accepted run

## Cross-document Review

- `ANALYSIS_INDEX.md`: updated or intentionally unchanged, with reason
- `docs/LESSONS.md`: updated or intentionally unchanged, with reason
```

## LESSONS Style

Prefer durable lessons written as:

- `Default`: the normal choice unless there is a reason to deviate
- `Check`: something to verify before rerunning or extending work
- `Trap`: a recurring failure mode to avoid
- `Preference`: a durable user or repo preference

Rewrite session-specific observations until they can survive outside the current
run. If they cannot, they belong in `NOTES.md` instead.

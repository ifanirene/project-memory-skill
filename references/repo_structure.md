# Repo Structure Reference

Use or adapt this structure when a project needs predictable placement rules.

```text
repo/
├── scripts/                  # runnable code and entrypoints
│   ├── python/
│   ├── r/
│   └── bash/
├── output/                   # generated outputs
│   ├── analysis/             # tables and stats
│   ├── plots/                # figures
│   ├── reports/              # rendered summaries
│   └── tmp/                  # regenerable scratch outputs
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   └── pipelines/
├── tests/
└── notebooks/
```

## Placement Rules

- Keep runnable code in one obvious home.
- Keep generated outputs out of the repo root.
- Co-locate each maintained analysis with its `NOTES.md`.
- Use `docs/` for durable narrative or operational documentation, not generated
  artifacts.
- Avoid creating new top-level directories for one-off outputs when a durable
  home already exists.

## Branching Pattern

Use one primary output root per maintained direction of work. Keep sibling
variants inside that root unless they have truly become a new branch of record.

# Personal Memory Bridge

Use this reference when a repo needs to stay minimal while still learning from
user-specific preferences, troubleshooting strategies, and Codex dialogs.

The personal-memory bridge should stay outside the repo. The repo keeps the
shared project memory; the external workspace keeps the distilled personal
memory that may later inform multiple repos.

## Recommended external structure

Use or adapt a layout like this:

```text
long-term-memory/
├── AGENTS.md
├── REPO_REGISTRY.md
├── config/
│   └── repos.json
├── state/
│   ├── dialog_cursor.json
│   ├── monthly_cycle.json
│   ├── repo_cursors_v2.json
│   ├── maintenance_queue_v2.json
│   └── weekly_rollout.json
├── logs/
│   └── runs/
├── dialogs/
│   ├── session_manifest.jsonl
│   └── extracts/
├── observations/
│   ├── repo_events/
│   └── dialog_events/
├── reflections/
│   └── REFLECTIONS.md
├── axioms/
│   └── AXIOMS.md
└── mirrors/
    └── AXIOM_TO_REPO_LESSONS.md
```

Keep raw dialog logs and raw repo histories in their original systems. Store
only source pointers, distilled extracts, and promoted memory here.

Use unique run-ID logs such as `<run-id>_weekly-collector.md`,
`<run-id>_weekly-<repo>.md`, and `<run-id>_monthly.md`.

## Promotion model

Use two linked promotion ladders:

### Repo ladder

- branch-local detail -> `NOTES.md`
- repo map or maintained location change -> `ANALYSIS_INDEX.md`
- durable repo-facing heuristic -> `docs/LESSONS.md`

Only promote `NOTES.md -> docs/LESSONS.md` when the observation can be
rewritten as a `Default`, `Check`, `Trap`, or `Preference` without
branch-specific nouns.

### Personal ladder

- first candidate signal -> `OBSERVATIONS.md` or monthly observation files
- 2 independent recurrences -> `REFLECTIONS.md`
- 3 confirmations plus 28-day stability or explicit user endorsement ->
  `AXIOMS.md`

Possible sources include:

- `NOTES.md`
- `docs/LESSONS.md`
- direct user corrections
- Codex dialogs
- automation decision logs

Classify automation-only lessons as `automation_operations`. Keep them out of
personal axioms unless the user explicitly endorses them as personal decision
rules.

## Loop ownership

Keep loop ownership explicit so promotions do not overlap:

- weekly central collection: update repo observations, repo cursors, and
  maintenance queue entries without editing monitored repos
- weekly repo-local maintenance: update one repo's docs, apply repo-local
  `NOTES.md -> docs/LESSONS.md` promotions, and resolve its claimed queue items
- monthly review: collect new dialog signals and update `REFLECTIONS.md`,
  `AXIOMS.md`, and repo mirror candidates

The weekly collector should not update reflections, axioms, or mirrors. The
monthly loop should not edit repo docs directly.

Use `scripts/memoryctl.py` for deterministic access checks, bounded collection,
proposal validation, locking, cursor updates, and atomic state writes. Keep
semantic summarization and generalization in the LLM proposal step.

## Dialog distillation rules

Distill Codex dialogs. Do not copy raw session bodies.

Good dialog-derived candidates include:

- repeated user corrections
- stable communication preferences
- accepted and rejected solution patterns
- troubleshooting pivots that recur
- decision rules the user keeps endorsing

Keep only:

- source path or session id
- timestamps or last updated markers
- processed-through event boundary for sessions that continue across multiple
  maintenance runs
- short quoted snippets when necessary
- paraphrased candidate principles
- confidence and recurrence notes

Do not mirror:

- full raw JSONL bodies
- long verbatim chat transcripts
- one-off emotional context with no durable implication

## Mirror rules

`AXIOMS.md` may mirror back into repo `docs/LESSONS.md` only when:

- the axiom is relevant to work in that repo
- it can be rewritten in repo-facing language
- the mirror would change future work in that repo

Keep personal-only axioms in the external workspace even if they were learned
from repo work.

## Provenance fields

Track enough provenance that future distillation can trust the source:

- repo
- session id
- cwd
- git ref or worktree
- analysis id if known
- branch root
- source file
- note archetype
- signal type
- candidate text
- confidence

Signals from non-main worktrees should be marked provisional until merged or
independently repeated.

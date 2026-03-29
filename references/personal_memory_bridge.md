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
├── state/
│   ├── dialog_cursor.json
│   └── repo_cursors.json
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

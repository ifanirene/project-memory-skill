# Scheduled Loops

Use this reference when pairing project memory with automation.

## Recommended loop model

Prefer two loops, not many overlapping ones:

1. daily distillation loop
2. weekly repo-maintenance loop

The daily loop distills new signals into the external personal-memory
workspace. The weekly loop updates repo docs automatically when the evidence is
strong enough.

## Daily distillation loop

Responsibilities:

- read only new or updated repo-memory signals since the last successful run
- read only new or updated dialog signals since the last successful run
- distill signals into observations, reflections, axioms, and mirror candidates
- update run logs and cursor state

Good inputs:

- changed `AGENTS.md`
- changed `ANALYSIS_INDEX.md`
- changed `docs/LESSONS.md`
- changed `docs/pipelines/*.md`
- changed `NOTES.md`
- session manifests and stable archived dialog logs

Required guardrails:

- do not copy raw dialogs
- do not rewrite repo docs in the daily loop
- do not reprocess the full history by default
- always update cursor state and write a run log

## Weekly repo-maintenance loop

Responsibilities:

- review the latest mirrors, observations, and decision logs
- update repo-memory docs automatically when the review shows they should
  change
- restrict edits to documentation files only
- preserve valid note archetypes instead of forcing every note into one
  runbook template
- write a detailed decision log for every run

Allowed edit targets:

- `AGENTS.md`
- `ANALYSIS_INDEX.md`
- `docs/LESSONS.md`
- `docs/pipelines/*.md`
- `NOTES.md`

Do not edit:

- code
- data
- generated outputs
- raw dialog archives

## Incremental processing

Use cursor files in the external workspace.

### Dialog cursor

Track:

- last successful run
- last processed session updated-at value
- whether bootstrap is complete

Use the stable dialog archive as the source of truth. Use a lightweight session
index only to discover new or updated sessions.

### Repo cursors

Track per repo:

- last processed commit and/or mtime
- known unresolved gaps from earlier runs
- whether bootstrap is complete

Process only changed files plus unresolved gaps recorded in earlier logs.

## First-run bootstrap

The first run is the only time the loop should backfill broadly.

Even then:

- process incrementally
- favor the most relevant or recent material first
- distill instead of copying
- establish the cursors and manifest so later runs can stay small

## Logs

Every automated run should write a human-readable decision log that includes:

- what was processed
- what changed
- what did not change
- why each change or non-change decision was made
- unresolved gaps
- any provisional signals held back from promotion

Logs are the main guardrail when updates are automated instead of manual-review
gated.

## Worktrees

Treat the main repo worktree as canonical for automated repo updates.

Extra worktrees may be read for signal collection, but:

- their signals should be marked provisional
- they should not trigger direct repo doc edits until merged or independently
  repeated

# Scheduled Loops

Use this reference when pairing project memory with automation.

## Recommended loop model

Prefer three non-overlapping loops:

1. daily signal-distillation loop
2. weekly repo-maintenance loop
3. monthly axiom-review loop

Each loop should own one layer of maintenance:

- daily: harvest and distill new repo or dialog signals into the external
  workspace
- weekly: update repo docs from the maintenance queue and repo-local
  `NOTES.md -> docs/LESSONS.md` promotions
- monthly: consolidate cross-repo reflections, axioms, and repo mirror
  candidates without editing repos directly

## Daily signal-distillation loop

Responsibilities:

- read only new or updated repo-memory signals since the last successful run
- read only new or updated dialog signals since the last successful run
- distill signals into session manifests, extracts, observations, and repo
  maintenance queue entries
- update daily run logs and cursor state

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
- do not update `REFLECTIONS.md`, `AXIOMS.md`, or repo mirrors
- do not reprocess the full history by default
- always update cursor state and write `logs/runs/YYYY-MM-DD_daily.md`
- track a per-session processed-through event boundary in
  `dialogs/session_manifest.jsonl`

## Weekly repo-maintenance loop

Responsibilities:

- consume `state/repo_maintenance_queue.json` plus unresolved gaps from prior
  weekly logs
- update repo-memory docs automatically when the queued review shows they
  should change
- restrict edits to documentation files only
- preserve valid note archetypes instead of forcing every note into one
  runbook template
- complete `## Cross-document review` outcomes in touched notes
- write `logs/runs/YYYY-MM-DD_weekly.md`

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

Validation phase:

- start with a bounded validation scope controlled by `state/weekly_rollout.json`
- limit automatic edits to representative fixture notes plus the directly
  corresponding `ANALYSIS_INDEX.md` or `docs/LESSONS.md` updates
- defer non-scope items back into the queue and record them in the weekly log
- switch from `validation` to `full` only after the validation checks pass

## Monthly axiom-review loop

Responsibilities:

- run on a weekly schedule but execute the full monthly cycle only when 28 or
  more days have elapsed since `state/monthly_cycle.json.last_successful_cycle`
- read new observations, weekly logs, repo lessons, and dialog extracts since
  the last successful monthly cycle
- promote `OBSERVATIONS.md -> REFLECTIONS.md -> AXIOMS.md` only when the
  recurrence and stability thresholds are met
- update repo-facing mirror candidates for later weekly consumption
- write `logs/runs/YYYY-MM-DD_monthly.md`

Required guardrails:

- do not edit repos directly
- do not copy raw dialogs
- do not rerun full-history promotion passes by default
- preserve provenance for every promoted reflection or axiom

## Incremental processing

Use cursor files in the external workspace.

### Dialog cursor

Track:

- last successful run
- last processed session updated-at value
- whether bootstrap is complete

Use the stable dialog archive as the source of truth. Use a lightweight session
index only to discover new or updated sessions.

Use `dialogs/session_manifest.jsonl` to store session-level progress such as the
processed-through event boundary, last distilled timestamp, and distilled event
count so updated sessions can be resumed without redistilling covered content.

### Repo cursors

Track per repo:

- last processed commit and/or mtime
- known unresolved gaps from earlier runs
- whether bootstrap is complete

Process only changed files plus unresolved gaps recorded in earlier logs.

### Maintenance queue

Use `state/repo_maintenance_queue.json` as the handoff between the daily and
weekly loops.

Each queue item should carry enough context to prevent weekly rescans:

- repo
- branch root
- note archetype
- issue type
- suggested target file
- confidence
- provisional flag
- source pointers

The daily loop appends or deduplicates queue items. The weekly loop consumes,
defers, or resolves them.

## First-run bootstrap

The first successful daily run is the only time the system should backfill
broadly.

Even then:

- process incrementally
- favor the most relevant or recent material first
- distill instead of copying
- establish the cursors and manifest so later runs can stay small
- cap the first pass so it finishes and writes progress instead of trying to
  absorb the full archive at once

The first weekly repo-maintenance run should start in bounded validation mode:

- validate a child-variant family
- validate a chronology or legacy note
- validate a synthesis note
- confirm that note archetypes are preserved before widening to full coverage

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

Use separate log files per loop so same-day runs do not overwrite each other.

## Worktrees

Treat the main repo worktree as canonical for automated repo updates.

Extra worktrees may be read for signal collection, but:

- their signals should be marked provisional
- they should not trigger direct repo doc edits until merged or independently
  repeated

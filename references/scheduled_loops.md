# Scheduled Loops

Use this reference when pairing project memory with automation.

Use the [writing style rules](../SKILL.md#writing-style) for maintained notes,
narrative run logs, and final reports. Keep detailed receipts in linked files.
Preserve required counts, attribution, coverage gaps, and validation failures.

The local controller uses POSIX file locks to serialize runs and lock recovery.
Its guard file stays in place; the operating system releases the lock when a
process exits. A legacy marker is reclaimed only for a confirmed dead local
process. Live, unreadable, or foreign-host markers require inspection. Lock age
alone never permits recovery. Do not delete the guard file.

## Recommended model

Separate learning from document upkeep:

1. daily personal L1 Observer using completed dialog turns and decision notes
2. weekly L2 reflection and a monthly L3 eligibility review
3. weekly repo-documentation collection/maintenance through the existing queue

Read [decision_memory.md](decision_memory.md) for the personal loop contract.
Monthly gating applies only to L3, never to observation intake, backlog processing,
or weekly reflection. Read automation configuration AND run artifacts before
claiming a schedule is active or that a run succeeded. Preserve a paused task
unless the user asks to resume it.

Keep one central collector workspace outside the monitored repos. Give the
collector read-only access to registered repo-memory files and write access only
to its own workspace. Do not duplicate the same cross-repo automation across
each monitored repo.

Use a hybrid controller such as `scripts/memoryctl.py`:

1. deterministic collection creates a bounded source packet
2. an LLM produces a structured semantic proposal
3. deterministic validation checks provenance, paths, schema, and state
4. deterministic application updates collector state atomically

The LLM should propose semantic conclusions. It should not directly mutate
collector state or canonical repo files.

## Weekly layer

### Phase A: central collection

Run once from the collector workspace.

Responsibilities:

- acquire a single-run lock
- verify read access to every registered repo and write access to the collector
- read only changed repo-memory files since the last successful cursor
- prioritize changed files by their current modification time, newest first;
  repository and path break ties deterministically
- reserve a small bounded share of each packet for unchanged legacy quality
  reviews using `state/quality_audit_v1.json`; an empty state creates the
  one-time backlog, and successful applies advance the round-robin audit cursor
- record each monitored repo's Git HEAD, branch, and dirty state in the packet
- prepare a bounded packet from `AGENTS.md`, `ANALYSIS_INDEX.md`,
  `.gitignore`, `docs/LESSONS.md`, `docs/pipelines/*.md`, and maintained
  `NOTES.md`
- ask the LLM to classify and distill candidate signals
- assess every collected `NOTES.md` and `docs/LESSONS.md` for current-state
  findability, including changed sources that were not selected by the
  round-robin audit
- use `notes_chronology_drift`, `lesson_not_distilled`,
  `stale_runbook_state`, and `oversized_memory_doc` for source-backed quality
  findings; line count or dates alone are not enough to queue an issue
- validate that every candidate has source IDs and recoverable provenance
- append repo observations and create or deduplicate maintenance queue items
- before proposing a missing-manifest item, inspect existing deferred items for
  the same repo, target, and issue type. If the analytical variant and unmet
  next-rerun dependency are unchanged, cite that item in the run log instead of
  requeuing it merely because note wording or its source hash changed. A distinct
  variant or materially changed dependency needs its own source-backed assessment.
- update cursors only after proposal validation and atomic state writes succeed
- write a unique weekly collector log containing the run ID

Do not:

- edit monitored repos
- read raw data or generated outputs
- copy full dialogs
- update reflections, axioms, or repo mirrors
- advance cursors after a partial or failed apply

Use `memoryctl` as follows:

```bash
python scripts/memoryctl.py doctor --workspace /path/to/long-term-memory
python scripts/memoryctl.py collect \
  --workspace /path/to/long-term-memory \
  --output /path/to/long-term-memory/runs/<run-id>/packet.json \
  --quality-audit-files 2
# LLM writes proposal.json from packet.json.
python scripts/memoryctl.py validate \
  --workspace /path/to/long-term-memory \
  --packet /path/to/long-term-memory/runs/<run-id>/packet.json \
  --proposal /path/to/long-term-memory/runs/<run-id>/proposal.json
python scripts/memoryctl.py apply \
  --workspace /path/to/long-term-memory \
  --packet /path/to/long-term-memory/runs/<run-id>/packet.json \
  --proposal /path/to/long-term-memory/runs/<run-id>/proposal.json
```

### Phase B: repo-local maintenance

Run at most once per monitored repo after central collection. Each run may read
only its own queue items and its own repo. It must not inspect sibling repos or
write collector promotion files.

Responsibilities:

- claim open queue items assigned to the repo
- process the newest target documents first, using the order returned by
  `queue-list` (current target modification time, descending). Recheck the
  source evidence before editing; recency establishes priority, not correctness.
- use the registered short name for queue commands, for example
  `queue-list --workspace <collector> --repo cross-species-analysis --status open`.
  Exact registered roots are accepted and normalized; unknown or unmaintained
  repos must fail instead of silently returning an empty queue.
- run `bootstrap_repo_memory.py --mode monitored --audit-only` to detect global
  contract and manifest drift before branch cleanup
- run `validate_analysis_manifest.py --repo <repo>` when manifests exist
- For a current result under review, use `validate_analysis_manifest.py
  <specific-manifest> --verify-files` to check declared files with bounded hashing.
  Report schema, file identity, reconstructability and scientific validation
  separately. A passing schema does not authorize deleting legacy facts.
- Check existing deferred items before proposing a missing-manifest migration.
  If repo, target, issue and unresolved prerequisite are the same, reference the
  existing item instead of requeuing it after a note hash changes.
- review only the source-linked repo docs needed for those items
- propose or apply allowed documentation changes
- process at most one or two large-note quality cleanups per run
- before rewriting chronology, preserve attributed decision evidence and derive a rewrite brief containing purpose,
  current claim, canonical artifacts, trust basis, kill list, and missing
  evidence
- rewrite the note as question -> current answer -> evidence -> selected
  analytical variant -> limitations -> next decision; retain only a compact
  provenance appendix when sequence itself changes interpretation
- rewrite new or migrated lessons with literal `Default:`, `Check:`, `Trap:`,
  or `Preference:` prefixes plus a trigger, action, and reason
- choose the note shape that best serves the current purpose; existing
  chronology and legacy shape are not preservation requirements
- identify active provenance-sensitive variants missing a native manifest;
  never fabricate execution facts, and defer native creation to the next real
  pipeline run when exact legacy facts are unavailable
- remove commands, complete parameter maps, input inventories, and artifact
  inventories from notes only after a valid manifest owns those facts
- complete `## Cross-document review` in touched notes
- resolve, defer, or reject every claimed queue item with evidence
- write a unique repo-maintenance log

Allowed targets:

- `AGENTS.md`
- `ANALYSIS_INDEX.md`
- `docs/LESSONS.md`
- `docs/pipelines/*.md`
- maintained `NOTES.md`
- `.gitignore`, but only for narrow rules that keep `NOTES.md` and
  `analysis_manifest.json` trackable under ignored output roots

Do not edit code, data, generated outputs, manifests, or raw dialog archives.
Maintenance may validate manifests and queue pipeline changes, but a pipeline
must write its own native manifest after a real execution.

## Protected `AGENTS.md` information

`AGENTS.md` may evolve, but changes to the following require explicit user
permission:

- environment names, paths, versions, activation commands, and interpreters
- security and secret-handling rules
- execution requirements, mandatory commands, and validation gates
- deployment, remote-access, or infrastructure instructions
- user-authored prohibitions or approval requirements

An unattended run cannot supply that permission. It must defer the queue item
and record the exact proposed change. Permission may come from the current user
request or a previously recorded approval tied to the exact change. General
permission to "clean up" or "update" `AGENTS.md` is not sufficient.

Before editing `AGENTS.md`:

1. extract the protected facts before and after the proposed change
2. fail if a protected fact is removed, weakened, or materially rewritten
   without explicit permission
3. preserve unrelated sections byte-for-byte when practical
4. record the permission source in the run log

## Queue lifecycle

Use explicit queue states:

- `open`: available for a repo-local run
- `claimed`: owned by one run ID
- `resolved`: applied or confirmed unnecessary, with evidence
- `deferred`: blocked by scope, permissions, missing context, or an overlapping
  edit that cannot be reconciled safely
- `rejected`: invalid or obsolete, with evidence

Each item should include:

- idempotency key
- repo and branch root
- issue type and suggested target
- source IDs and source hashes
- status, attempt count, and owning run ID
- resolution evidence or deferral reason
- protected-information impact, if `AGENTS.md` is involved
- quality evidence for memory-quality issue types
- a narrative rewrite brief for a `NOTES.md` quality cleanup

The weekly layer owns queue lifecycle. Do not leave resolved items permanently
open for a future collector to rediscover.

Deferred work is revisited only when its recorded dependency materially changes,
such as a real analysis rerun producing the required native manifest. Use
`queue-reopen --workspace <collector> --repo <registered-name> --idempotency-key
<key> --run-id <unique-review-id> --evidence "<changed dependency and evidence>"`,
then claim and assess it normally. Reopening preserves the previous status,
resolution, and owner in `status_history`; it neither proves resolution nor grants
permission to change protected guidance. Do not reopen because time passed or a
note hash changed. Expired claimed items still need explicit owner-aware recovery;
there is no automatic lease reclamation.

When the user explicitly waives unimportant or unrecoverable historical debt, use
`queue-dismiss --workspace <collector> --repo <registered-name> --key <key>
--run-id <review-id> --evidence "<user authorization and reason>"`.
Only open/deferred items can move to rejected with disposition
`user_waived_historical`; their complete previous fields remain in status_history.
This closes debt without claiming a repair or authorizing protected edits.
Phase A suppresses later proposals for the same canonical repo/target/issue even
when source hashes change, and records suppression in its run log. Material new
facts can justify a new linked item only when a proposal supplies both
`requeue_closed_item` (the dismissed idempotency key) and `requeue_evidence` (the
specific new facts). The controller checks the pair and matching issue identity;
the reviewer must assess whether those facts genuinely change the decision.
Passing time, changing note hashes, or repeating an old rationale is insufficient.

## Personal learning loops

The personal Observer and Reflector use `decision_memory.py`; the Phase A/B
sections above remain documentation operations. Their output counts are not
personal-memory yield. Do not send maintenance automation logs through the
human-confirmation promotion ladder.

Observer: collect one bounded packet, read every selected source in context,
propose attributed decision events or concrete no-signal/deferred reasons,
validate and apply. Keep active-session completed tails eligible. Report
coverage gaps, backlog and the oldest unreviewed period; do not call a partial
bootstrap complete. A remote failure must not silently become "no new signals".

Reflector: compare new events weekly and re-evaluate existing candidates for
counterexamples and changed scope. Keep first occurrences as candidates. Two
independent human episodes can support a reflection even within one repo. Three
human episodes spanning 28 days support automatic axiom eligibility, subject to
semantic review. Actual confirmation dates establish stability; repeated agent
compliance and no-change logs do not.

Run axiom eligibility monthly without skipping reflection in other weeks. New
principles must predict a concrete future decision and state boundaries and costs.
Keep scientific findings, personal choices, and automation operations distinct.
Prepare relevant mirrors for repo-local review; never edit monitored repos from
the personal collector. See `personal_memory_bridge.md` for retrieval and mirrors.

## Bootstrap and rollout

Bootstrap only once and keep it bounded:

- process recent maintained notes first
- cap files and dialog sessions per run
- establish cursors before widening coverage
- leave bootstrap incomplete while backlog remains

Start repo-local auto-edits in validation mode. Require consecutive successful
runs with no protected-information regression, no duplicate run, and no stale
queue recurrence before widening coverage.

Do not wait for files to change before reviewing legacy quality. Finish the
initial `quality_audit_v1` backlog incrementally, then use the same state to
avoid re-auditing unchanged files that were already reviewed. A content change
makes the file eligible again through the normal changed-file cursor.

## Logs and worktrees

Name every run log with a timestamp and run ID so concurrent attempts cannot
overwrite one another.

Do not require a clean main worktree. Weekly repo-local maintenance should run
against the current main checkout even when it contains uncommitted work. Record
the starting Git status and read the target's current content before rewriting
it. `NOTES.md`, `docs/LESSONS.md`, the index, and pipeline docs may be
substantially rewritten to serve their current purpose; do not preserve log
structure merely because it is present. Never reset, discard, commit, or alter
unrelated files. Protected `AGENTS.md` information remains permission-gated.

Treat detached HEADs and extra worktrees as provisional. Do not edit them until
the work is on the canonical main checkout or independently confirmed.

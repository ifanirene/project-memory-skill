# Plan 004: Gate the collector automation as an optional, advanced module

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan in
> `plans/README.md`.
>
> **Drift check (run first)**:
> `git diff --stat c320c14..HEAD -- SKILL.md`
> Plans 001–003 edit `SKILL.md` before this plan; that is expected. This plan
> replaces whole sections identified by their `##` headings, so line-number
> drift is harmless. If a named heading is missing, STOP.

## Status

- **Priority**: P2
- **Effort**: M
- **Risk**: MED (rewrites two `SKILL.md` sections; the replacement text is given
  verbatim, so risk is mis-scoping the section range, not authoring)
- **Depends on**: 003 (which depends on 001, 002). Run after 003 so there is a
  single `SKILL.md` writer at a time and the `$SKILL_DIR` convention from Plan
  002 is already in place.
- **Category**: tech-debt / architecture (scope framing)
- **Planned at**: commit `c320c14`, 2026-07-11
- **Addresses**: Finding 4 (design review), and the size half of Finding 1.

## Why this matters

The skill fuses two products: (a) the **core** repo-documentation contract
(repo guide → index → notes → lessons), and (b) a heavy **cross-repo automation
collector** (a 966-line deterministic controller, weekly/monthly scheduling, and
an external `OBSERVATIONS/REFLECTIONS/AXIOMS` ontology). In `SKILL.md` the
automation is presented at the same altitude as the core, with its full
operational procedure inlined — even though it serves a minority of users and
already has a complete reference in `references/scheduled_loops.md`.

The cost: a first-time reader (human or model) can't tell that the automation is
optional, and the inlined procedure duplicates the reference. This plan reframes
the automation and the external personal-memory bridge as an **explicitly
opt-in advanced module**, and condenses the inlined procedure to an overview
plus a pointer — shrinking `SKILL.md` and making the core purpose primary.
It does **not** delete any capability or touch any script.

## Current state

- `SKILL.md` contains, in order, these top-level sections (among others):
  - `## External personal-memory bridge` — begins `When an external workspace
    is configured, keep it outside the repo and use it for:`.
  - `## Scheduled maintenance` — begins `Use two maintenance layers:` and runs
    until the next top-level heading, `## Repository modes`. It inlines the
    weekly/monthly procedure, the LLM-vs-controller split, the
    validation-phase rollout, the live-test instruction, and a
    `smoke_test_project_memory.py` command (which Plan 002 rewrote to use
    `$SKILL_DIR`).
- The full automation protocol already lives in
  `references/scheduled_loops.md`; the personal-memory detail in
  `references/personal_memory_bridge.md`; the live test in
  `references/live_maintenance_test.md`. Those references are **canonical** and
  are not touched here.
- The core sections above `## External personal-memory bridge` (the contract,
  repo organization, minimal mode, bootstrap, workflow, note archetypes,
  promotion ladder, memory-aware protocols) are the primary purpose and stay.

## Commands you will need

| Purpose | Command | Expected on success |
|---------|---------|---------------------|
| Opt-in gate present | `grep -c 'optional, advanced' SKILL.md` | `1` |
| Skip-unless gate present | `grep -c 'Skip this section unless' SKILL.md` | `2` |
| Inlined procedure removed | `grep -c 'bounded round-robin sample of unchanged' SKILL.md` | `0` |
| Reference pointer present | `grep -c 'references/scheduled_loops.md' SKILL.md` | ≥ `1` |
| SKILL.md got smaller | `wc -l < SKILL.md` | fewer lines than before this plan (record the before-count first) |
| Regression: tests pass | `uv run --no-project --with pytest python -m pytest tests/ -q` | `15 passed` |

Before Step 1, record the current size: `wc -l < SKILL.md` and note the number.

## Scope

**In scope** (the only file you should modify):
- `SKILL.md` — the `## External personal-memory bridge` and
  `## Scheduled maintenance` sections only.

**Out of scope** (do NOT touch):
- `references/scheduled_loops.md`, `references/personal_memory_bridge.md`,
  `references/live_maintenance_test.md` — canonical; keep the detail there.
- Any `scripts/` or `tests/` file — no capability changes, no code.
- Any `SKILL.md` section other than the two named ones. In particular, do not
  touch `## Core contract`, `## Promotion ladder`, or `## Repository modes`.

## Git workflow

- Branch: `advisor/004-gate-collector-automation`
- One commit. Message style matches repo `git log`
  (e.g. `Gate collector automation as an optional advanced module`).
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Add an opt-in gate to the personal-memory bridge section

In `SKILL.md`, find the `## External personal-memory bridge` heading. Insert,
immediately below the heading and before its first paragraph, this line:

```
Skip this section unless the user has asked to pair the repo with an external
long-term-memory workspace. The core contract above stands on its own without it.
```

### Step 2: Replace the `## Scheduled maintenance` section with a gated overview

Replace **everything** from the line `## Scheduled maintenance` up to (but not
including) the next top-level heading `## Repository modes` with exactly the
block below. (Selecting by heading makes this robust to line-number drift from
earlier plans.)

```
## Scheduled maintenance (optional, advanced)

Skip this section unless the user has explicitly asked to pair the repo with an
external long-term-memory collector. It is not required for the core repo-memory
contract above.

When configured, run two layers from one external collector workspace that has
read-only access to monitored repos and write access only to its own state:

- weekly: collect changed memory docs, obtain a structured semantic proposal
  from the LLM, and use `scripts/memoryctl.py` to validate and apply
  observations, cursors, and queue state. Repo-local maintenance may then edit
  only its own repo's docs.
- monthly: promote reflections and axioms and prepare repo-mirror proposals
  without editing repos directly.

Load-bearing rules (the full protocol is in `references/scheduled_loops.md`):

- Keep semantic judgment in the LLM and deterministic control in the controller
  (`memoryctl`): file discovery, bounded inputs, locking, schema/provenance/path
  validation, cursor and queue lifecycle, and atomic writes.
- The weekly collector must not edit monitored repos. Repo-local maintenance
  must resolve or defer its own queue items, not leave them open.
- Any protected `AGENTS.md` change without explicit permission must be deferred.
- Start repo-local auto-edits in a bounded validation phase; widen coverage only
  after consecutive clean runs.

When the user asks whether maintenance genuinely works, run a live maintenance
test — real collector state, genuine repo edits left uncommitted for review —
following `references/live_maintenance_test.md`. For a controller-only safety
check (restores its own writes, uses temporary state, and is not evidence of
useful semantic maintenance):

​```bash
python "$SKILL_DIR/scripts/smoke_test_project_memory.py" --repo /path/to/project
​```
```

(The `​```` markers are literal triple backticks — keep them so the code block
renders.)

**Verify**: `grep -c 'optional, advanced' SKILL.md` → `1`.
**Verify**: `grep -c 'Skip this section unless' SKILL.md` → `2` (Steps 1 and 2).
**Verify**: `grep -c 'bounded round-robin sample of unchanged' SKILL.md` → `0`
(the verbose inlined detail is gone; it remains in `references/scheduled_loops.md`).
**Verify**: `grep -c 'references/scheduled_loops.md' SKILL.md` → ≥ `1`.

### Step 3: Confirm size reduction and regression

**Verify**: `wc -l < SKILL.md` → fewer lines than the before-count you recorded.
**Verify**: `uv run --no-project --with pytest python -m pytest tests/ -q` → `15 passed`.

## Test plan

No unit test covers `SKILL.md` prose. Verification is the grep + `wc` gates plus
the regression suite. Additionally confirm no capability was lost: the smoke and
live-test entry points still exist —
`grep -c 'smoke_test_project_memory.py' SKILL.md` → ≥ 1 and
`grep -c 'live_maintenance_test.md' SKILL.md` → ≥ 1.

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `grep -c 'optional, advanced' SKILL.md` → `1`.
- [ ] `grep -c 'Skip this section unless' SKILL.md` → `2`.
- [ ] `grep -c 'bounded round-robin sample of unchanged' SKILL.md` → `0`.
- [ ] `grep -c 'references/scheduled_loops.md' SKILL.md` → ≥ `1`.
- [ ] `grep -c 'smoke_test_project_memory.py' SKILL.md` → ≥ `1` (entry point kept).
- [ ] `wc -l < SKILL.md` is less than the pre-edit count.
- [ ] `uv run --no-project --with pytest python -m pytest tests/ -q` → `15 passed`.
- [ ] `git status --porcelain` shows only `SKILL.md` modified.
- [ ] `plans/README.md` status row for 004 updated to DONE.

## STOP conditions

Stop and report back (do not improvise) if:

- The `## Scheduled maintenance` or `## Repository modes` heading is missing
  (cannot bound the replacement range) — do not guess the range.
- The section between the two headings contains content you do not recognize
  from "Current state" and that looks load-bearing (e.g. a rule not reflected in
  the replacement block) — report it so it isn't silently dropped.
- The smoke command in the section uses `$CODEX_HOME` rather than `$SKILL_DIR` —
  that means Plan 002 did not run; STOP and run 002 first.

## Maintenance notes

- This is the reversible, docs-only version of "separate the two products." If
  the maintainer later decides to fully split the collector into its own skill
  (design option D1 from the review), this gating makes that extraction cleaner:
  the automation is already self-contained in `references/scheduled_loops.md` +
  `scripts/memoryctl.py` + `scripts/smoke_test_project_memory.py`.
- A reviewer should confirm every load-bearing automation rule in the old
  inlined section is still stated either in the condensed block or in
  `references/scheduled_loops.md` (nothing was lost, only relocated).
- If Plan 001's description still advertises the collector, keep it — the
  feature remains, just gated. If the collector is ever removed, update both the
  description (Plan 001) and this section.

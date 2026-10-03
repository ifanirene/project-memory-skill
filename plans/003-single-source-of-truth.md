# Plan 003: Establish single sources of truth for duplicated contract blocks

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan in
> `plans/README.md`.
>
> **Drift check (run first)**:
> `git diff --stat c320c14..HEAD -- SKILL.md references/doc_contract.md references/personal_memory_bridge.md references/scheduled_loops.md templates/AGENTS.md`
> Plans 001 and 002 will have changed `SKILL.md` and some references before this
> plan runs — that is expected. Locate each edit target by the **quoted text**
> in "Current state," not by line number. If a quoted anchor string cannot be
> found, STOP.

## Status

- **Priority**: P2
- **Effort**: M
- **Risk**: MED (editing shared contract prose; the risk is dropping a rule that
  exists in only one copy — mitigated by only *deleting* a block proven
  near-identical to its canonical twin, and otherwise only *adding* pointers)
- **Depends on**: 001, 002 (both edit `SKILL.md`; run them first so there is a
  single writer at a time)
- **Category**: tech-debt / docs
- **Planned at**: commit `c320c14`, 2026-07-11
- **Addresses**: Finding 1 (design review) — the drift-hazard half. The
  size half is addressed by Plan 004.

## Why this matters

The skill preaches "keep the memory system minimal; don't maintain overlapping
docs," yet several load-bearing contract blocks exist as **multiple full copies
that can silently drift**:

- The `NOTES.md` template is embedded **verbatim twice** — in
  `references/doc_contract.md` and in `templates/AGENTS.md` — and the two have
  already begun to diverge (fence style and one line of wording differ today).
- The **promotion ladder** and the **protected-`AGENTS.md` rule** are each
  stated at length in two or more files with no indication of which is
  authoritative.

When an editor updates one copy, the others rot, and a future agent can't tell
which is correct. This plan gives every duplicated block **one labeled owner**.
It does the one *safe deletion* (the near-identical template) and otherwise only
*adds* canonical-source pointers — it does not attempt to merge reworded prose,
which is a human editorial judgment, not a mechanical edit (see Maintenance
notes).

## Current state

- `templates/AGENTS.md` — the scaffold copied verbatim into a user repo's
  `AGENTS.md` by the bootstrap helper. It contains the `NOTES.md` template under
  a ` ```md ` fence, beginning `## Status` and including the line
  `branch runbook | child variant | synthesis/staging | provenance appendix`.
  **This is the canonical template** (it is a real artifact users receive; it
  cannot point elsewhere). Leave it unchanged.

- `references/doc_contract.md` — an internal reference (never copied into a
  project). It contains a **second, near-identical** copy of that template under
  a `## Suggested notes template` heading, inside a ` ````md ` fence
  (four backticks), lines currently:

```
## Suggested notes template

````md
## Status
ACTIVE | FINAL | ARCHIVED — last updated: YYYY-MM-DD

## Note archetype
branch runbook | child variant | synthesis/staging | provenance appendix
... (full template) ...
## Provenance appendix
[include only when sequence itself is needed to understand the current state]
````

Rewrite these sections as one coherent current narrative instead of appending a
dated section. Use the rewrite brief and kill-list protocol in
`references/memory_quality.md`; keep a compact provenance appendix only when
sequence itself changes interpretation.
```

  A diff against `templates/AGENTS.md` shows the only differences are the fence
  style and one line (`what variations belong in this file` vs `belong here`) —
  i.e. it is a redundant copy, safe to replace with a pointer.

- `SKILL.md` — contains `## Promotion ladder` (a 5-rung ladder ending with the
  `AXIOMS.md -> docs/LESSONS.md` mirror step) and, in its `## Core contract`
  section, a paragraph beginning `Allow `AGENTS.md` to evolve, but require
  explicit user permission before...`.
- `references/personal_memory_bridge.md` — contains `## Promotion model` (the
  same ladder, repo + personal). **Designated canonical owner of the promotion
  ladder.**
- `references/scheduled_loops.md` — contains `## Protected `AGENTS.md`
  information` with the full operational before/after-extraction procedure.
  **Designated canonical owner of the protected-`AGENTS.md` rule.**
- `references/analysis_manifest.md` — `## Decision rule` is already the
  canonical manifest rule, and `SKILL.md` already points to it
  (`Apply the selective manifest rule in `references/analysis_manifest.md`.`).
  **No manifest change needed** — this plan only verifies that pointer still
  exists.

## Commands you will need

| Purpose | Command | Expected on success |
|---------|---------|---------------------|
| Template exists once (canonical) | `grep -rc 'branch runbook | child variant | synthesis/staging' templates/AGENTS.md references/doc_contract.md SKILL.md` | `templates/AGENTS.md:1`, `references/doc_contract.md:0`, `SKILL.md:0` |
| Canonical pointers present | `grep -rn 'Canonical' SKILL.md references/doc_contract.md` | ≥ 3 matches |
| Manifest pointer intact | `grep -n 'Apply the selective manifest rule in' SKILL.md` | 1 match |
| Regression: tests still pass | `uv run --no-project --with pytest python -m pytest tests/ -q` | `15 passed` |

## Scope

**In scope** (the only files you should modify):
- `references/doc_contract.md`
- `SKILL.md`

**Out of scope** (do NOT touch):
- `templates/AGENTS.md` — the canonical template lives here; changing it changes
  what every future repo is scaffolded with.
- `references/personal_memory_bridge.md`, `references/scheduled_loops.md`,
  `references/analysis_manifest.md` — these are the canonical owners; do not
  edit them, only point *to* them.
- Any Python or test file.
- Do **not** delete or reword the promotion ladder or protected-`AGENTS.md`
  prose. This plan only adds pointer lines to them. Deleting reworded prose is
  explicitly deferred (Maintenance notes).

## Git workflow

- Branch: `advisor/003-single-source-of-truth`
- One or two commits. Message style matches repo `git log`
  (e.g. `Deduplicate NOTES template and label canonical contract sources`).
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Replace the duplicated template in `doc_contract.md` with a pointer

In `references/doc_contract.md`, replace the entire `## Suggested notes
template` section (the heading, the four-backtick ` ````md ` fenced template
block, AND the trailing "Rewrite these sections..." paragraph — everything shown
in the Current state excerpt for this file) with exactly:

```
## Suggested notes template

The canonical `NOTES.md` template lives in `templates/AGENTS.md` — the same
block the bootstrap helper scaffolds into a repo's guide. Do not keep a second
copy here; edit `templates/AGENTS.md` so the two cannot drift.

When rewriting a note, shape its sections as one coherent current narrative
instead of appending a dated section. Use the rewrite brief and kill-list
protocol in `references/memory_quality.md`; keep a compact provenance appendix
only when sequence itself changes interpretation.
```

**Verify**: `grep -c 'branch runbook | child variant | synthesis/staging' references/doc_contract.md` → `0`.
**Verify**: `grep -c 'templates/AGENTS.md' references/doc_contract.md` → ≥ `1`.

### Step 2: Label the promotion ladder's canonical owner

In `SKILL.md`, find the `## Promotion ladder` heading line. Immediately below it
(before the first list item), insert this blockquote line:

```
> Canonical source: `references/personal_memory_bridge.md` (`## Promotion
> model`). Keep this summary in sync with it.
```

**Verify**: `grep -n 'Canonical source' SKILL.md` → ≥ 1 match near "Promotion ladder".

### Step 3: Label the protected-`AGENTS.md` rule's canonical owner

In `SKILL.md`, find the paragraph in `## Core contract` beginning `Allow
`AGENTS.md` to evolve, but require explicit user permission`. Immediately
**after** that paragraph (after the sentence ending `...is not sufficient.`),
insert:

```
> Canonical source: `references/scheduled_loops.md` (`## Protected `AGENTS.md`
> information`) holds the full procedure. Keep this summary in sync with it.
```

Then in `references/doc_contract.md`, find the paragraph beginning ``AGENTS.md`
may be maintained, but require explicit user permission` and insert immediately
after it:

```
> Canonical source: `references/scheduled_loops.md` (`## Protected `AGENTS.md`
> information`).
```

**Verify**: `grep -rn 'Canonical source' SKILL.md references/doc_contract.md` → ≥ 3 total matches.

### Step 4: Confirm the manifest rule's existing pointer is intact

No edit — just confirm the manifest decision rule still delegates to its
canonical owner.

**Verify**: `grep -n 'Apply the selective manifest rule in' SKILL.md` → 1 match
referencing `references/analysis_manifest.md`. If it is missing (an earlier
plan removed it), STOP and report.

### Step 5: Regression check

**Verify**: `uv run --no-project --with pytest python -m pytest tests/ -q` → `15 passed`.

## Test plan

No unit test covers reference prose. Verification is the grep gates above plus
the regression suite. Additionally, confirm the canonical template is byte-for-
byte reachable: `grep -A1 '## Note archetype' templates/AGENTS.md` still prints
the `branch runbook | child variant | synthesis/staging | provenance appendix`
line (the canonical copy is intact and was not collateral-damaged).

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `grep -c 'branch runbook | child variant | synthesis/staging' references/doc_contract.md` → `0`.
- [ ] `grep -c 'branch runbook | child variant | synthesis/staging' templates/AGENTS.md` → `1` (canonical intact).
- [ ] `grep -rn 'Canonical source' SKILL.md references/doc_contract.md` → ≥ 3 matches.
- [ ] `grep -n 'Apply the selective manifest rule in' SKILL.md` → 1 match.
- [ ] `uv run --no-project --with pytest python -m pytest tests/ -q` → `15 passed`.
- [ ] `git status --porcelain` shows only `SKILL.md` and `references/doc_contract.md` modified.
- [ ] `plans/README.md` status row for 003 updated to DONE.

## STOP conditions

Stop and report back (do not improvise) if:

- The `## Suggested notes template` block in `doc_contract.md` is **not**
  near-identical to the one in `templates/AGENTS.md` (run
  `diff <(sed -n '/## Note archetype/,/Provenance appendix/p' references/doc_contract.md) <(sed -n '/## Note archetype/,/Provenance appendix/p' templates/AGENTS.md)`
  — if it shows more than fence-style and the single `belong in this file` /
  `belong here` wording difference, the copies have meaningfully diverged and a
  human must reconcile them before deletion).
- Any anchor string in "Current state" cannot be found.
- A verification fails twice after a reasonable fix attempt.

## Maintenance notes

- **Deferred on purpose**: the promotion ladder and protected-`AGENTS.md` rule
  still exist as reworded copies in more than one file. This plan labels the
  owner but does not merge the prose, because collapsing differently-worded
  rules without dropping a unique clause is an editorial judgment better made by
  a human maintainer than a mechanical pass. A follow-up could shorten the
  `SKILL.md` copies to a one-line summary + the pointer once a human confirms
  the canonical copies are complete.
- A reviewer should confirm no rule text was lost in Step 1 — specifically that
  the "Rewrite these sections..." guidance survived (reworded) in the
  replacement.
- Plan 004 reduces `SKILL.md`'s size by moving automation detail into
  references; these two plans together address both halves of Finding 1.

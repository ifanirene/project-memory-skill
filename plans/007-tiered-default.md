# Plan 007: Make the memory system tiered, with Tier 1 as the default

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan in
> `plans/README.md`.
>
> **Drift check (run first)**:
> `git diff --stat c320c14..HEAD -- SKILL.md scripts/bootstrap_repo_memory.py tests/test_bootstrap_repo_memory.py references/doc_contract.md`
> Plans 001–004 will have edited `SKILL.md` before this runs — expected. Anchor
> every edit on the **quoted text / symbol names** in "Current state," not line
> numbers. If an anchor is missing, STOP.

## Status

- **Review 2026-10-03**: TODO. Bootstrap has no `--tier` option; new mode still
  creates the full biology scaffold. Recommend deferring this default change until
  a smaller scaffold is needed. It does not reduce current daily or weekly report
  length. See the [current review](README.md#current-review--2026-10-03).

- **Priority**: P2
- **Effort**: M
- **Risk**: MED (changes bootstrap's default output and an existing test's
  expectations; behavior change is the point, but it must be deliberate)
- **Depends on**: 004 (shares `SKILL.md`; run the core-cleanup track first)
- **Category**: direction (D2) / dx
- **Planned at**: commit `c320c14`, 2026-07-11
- **Addresses**: Design review direction option **D2 (tiered default)**.

## Why this matters

The skill's thesis is "keep the memory system minimal," but its default
new-repo scaffold creates the full apparatus at once — pipeline-doc homes,
manifest gitignore machinery, the whole tree — so the *default* contradicts the
*advice*. This plan makes the tiering explicit and makes the **smallest tier the
default**, so a repo opts *up* into complexity only when a real need appears:

- **Tier 1 (default)** — the pure memory system: a repo guide, `ANALYSIS_INDEX.md`,
  `docs/LESSONS.md`, and per-branch `NOTES.md`. Nothing else.
- **Tier 2 (opt-in)** — adds execution provenance: the `analysis_manifest.json`
  contract (validator + `.gitignore` exceptions) and `docs/pipelines/`.
- **Tier 3 (opt-in)** — adds the external collector (the companion skill; see
  Plan 009).

## Current state

- `SKILL.md` — has a `## Minimal mode` section beginning `Keep the repo memory
  system minimal.` It already lists the three core evolving docs but does not
  frame them as an explicit default tier or name Tier 2/3.
- `scripts/bootstrap_repo_memory.py`:
  - `parse_args()` defines `--audit-only`, `--yes`, `--with-pipeline-docs`,
    `--mode`. No `--tier`.
  - `build_audit(repo, *, mode, with_pipeline_docs=False)` appends a
    `docs/pipelines` scaffold action when
    `(with_pipeline_docs or mode == "new")`. In `mode == "new"` it also creates
    `NEW_REPO_DIRECTORIES` and a `.gitignore`.
  - `main()` calls `build_audit(repo, mode=mode, with_pipeline_docs=args.with_pipeline_docs)`.
- `tests/test_bootstrap_repo_memory.py` —
  `test_bootstrap_empty_repo_audit_then_scaffold` runs `--repo <r> --yes` (auto
  mode → new for an empty repo) and asserts `docs/pipelines` **is** created and
  `.gitignore` contains `analysis_manifest.json`. Under the new default (Tier 1)
  those would not be created, so this test must be updated.

## Commands you will need

| Purpose | Command | Expected on success |
|---------|---------|---------------------|
| Byte-compile | `python3 -m py_compile scripts/bootstrap_repo_memory.py` | exit 0 |
| Bootstrap tests | `uv run --no-project --with pytest python -m pytest tests/test_bootstrap_repo_memory.py -q` | all pass |
| Full suite | `uv run --no-project --with pytest python -m pytest tests/ -q` | all pass |
| Tier-1 default omits pipelines | see Step 4 verification | `docs/pipelines` absent |
| SKILL documents tiers | `grep -c 'Tier 1' SKILL.md` | ≥ `1` |

## Scope

**In scope**:
- `scripts/bootstrap_repo_memory.py`
- `tests/test_bootstrap_repo_memory.py`
- `SKILL.md` (the `## Minimal mode` section only)
- `references/doc_contract.md` (its `## Minimal mode` section only)

**Out of scope**:
- The comp-bio directory list itself (`NEW_REPO_DIRECTORIES`) — Plan 008 turns
  that into a preset. This plan only gates *pipeline/manifest* extras by tier.
- `scripts/memoryctl.py` and the collector — Tier 3 is documented here but
  implemented by Plan 009.
- Templates content (Plan 008 owns template changes).

## Git workflow

- Branch: `advisor/007-tiered-default`
- One or two commits. Message style matches repo `git log`
  (e.g. `Add memory tiers with Tier 1 default to bootstrap`).

## Steps

### Step 1: Add a `--tier` flag

In `parse_args()`, add:

```python
    parser.add_argument(
        "--tier",
        type=int,
        choices=(1, 2, 3),
        default=1,
        help=(
            "Memory tier to scaffold in new mode: 1 = repo guide + index + "
            "lessons (default); 2 = + manifests and docs/pipelines; 3 = + "
            "external collector (companion skill, set up separately)."
        ),
    )
```

### Step 2: Thread `tier` into `build_audit`

Change the signature to
`def build_audit(repo, *, mode, with_pipeline_docs=False, tier=1)` and change the
pipelines gate from:

```python
    if (
        (with_pipeline_docs or mode == "new")
        and
        item_map["pipelines_home"].status == "missing"
        and item_map["docs_home"].status != "manual_review"
    ):
```

to:

```python
    if (
        (with_pipeline_docs or (mode == "new" and tier >= 2))
        and
        item_map["pipelines_home"].status == "missing"
        and item_map["docs_home"].status != "manual_review"
    ):
```

In `main()`, pass the tier:
`build_audit(repo, mode=mode, with_pipeline_docs=args.with_pipeline_docs, tier=args.tier)`.

### Step 3: Gate the `.gitignore` manifest exceptions by tier

In `build_audit`, the `mode == "new"` block creates `.gitignore` from the
`.gitignore` template unconditionally. Leave the `.gitignore` creation, but note
its manifest exceptions are a Tier-2 concept. Keep it simple and testable:
create `.gitignore` only when `tier >= 2` in new mode. Wrap the existing
`.gitignore` scaffold-action append in `if tier >= 2:`.

(Rationale: at Tier 1 there are no manifests to protect, so the manifest-aware
`.gitignore` is premature. A Tier-1 repo can add one later, or the user can pass
`--tier 2`.)

### Step 4: Update the bootstrap test for the new default

In `tests/test_bootstrap_repo_memory.py`, split
`test_bootstrap_empty_repo_audit_then_scaffold` behavior:

1. Keep a Tier-1 default test that runs `--repo <r> --yes` and now asserts:
   - `AGENTS.md`, `ANALYSIS_INDEX.md`, `docs/LESSONS.md` **exist**
   - `docs/pipelines` does **not** exist: `assert not (repo / "docs" / "pipelines").exists()`
   - `.gitignore` does **not** exist: `assert not (repo / ".gitignore").exists()`
2. Add `test_bootstrap_tier2_adds_pipelines_and_gitignore` that runs
   `--repo <r> --yes --tier 2` and asserts `docs/pipelines` **is** a dir and
   `.gitignore` contains `analysis_manifest.json`.

**Verify**: `uv run --no-project --with pytest python -m pytest tests/test_bootstrap_repo_memory.py -q` → all pass.
**Verify** (manual): in a temp dir,
`python3 scripts/bootstrap_repo_memory.py --repo <tmp> --yes` then
`test ! -e <tmp>/docs/pipelines && echo TIER1_OK` → prints `TIER1_OK`.

### Step 5: Document the tiers in `SKILL.md` and `doc_contract.md`

In `SKILL.md`, rename the `## Minimal mode` heading to `## Memory tiers` and add,
right under it (before the existing "Keep the repo memory system minimal." text),
this block:

```
The default is **Tier 1** — the smallest system that works. Opt up only when a
concrete need appears.

- **Tier 1 (default):** repo guide, `ANALYSIS_INDEX.md`, `docs/LESSONS.md`, and
  per-branch `NOTES.md`.
- **Tier 2 (opt-in):** adds `analysis_manifest.json` provenance and
  `docs/pipelines/`. Scaffold with `--tier 2`.
- **Tier 3 (opt-in):** adds the external long-term-memory collector, which is a
  separate companion skill. Set it up only when pairing multiple repos.
```

In `references/doc_contract.md`, under its `## Minimal mode` section, add one
line: `The bootstrap default is Tier 1; add manifests and pipelines with
`--tier 2` only when provenance or shared workflows demand them.`

**Verify**: `grep -c 'Tier 1' SKILL.md` → ≥ 1.

### Step 6: Full regression

**Verify**: `python3 -m py_compile scripts/bootstrap_repo_memory.py` → exit 0.
**Verify**: `uv run --no-project --with pytest python -m pytest tests/ -q` → all pass.

## Test plan

- Rewrite `test_bootstrap_empty_repo_audit_then_scaffold` to assert Tier-1
  default omits `docs/pipelines` and `.gitignore`.
- Add `test_bootstrap_tier2_adds_pipelines_and_gitignore`.
- All other tests unchanged.
- Verification: `uv run --no-project --with pytest python -m pytest tests/ -q` → all pass.

## Done criteria

- [ ] `python3 -m py_compile scripts/bootstrap_repo_memory.py` → exit 0.
- [ ] `python3 scripts/bootstrap_repo_memory.py --help` lists `--tier`.
- [ ] Tier-1 default scaffold omits `docs/pipelines` and `.gitignore` (Step 4 manual check).
- [ ] `grep -c 'Tier 1' SKILL.md` → ≥ 1.
- [ ] `uv run --no-project --with pytest python -m pytest tests/ -q` → all pass.
- [ ] `git status --porcelain` shows only the four in-scope files modified.
- [ ] `plans/README.md` status row for 007 updated to DONE.

## STOP conditions

Stop and report if:
- `build_audit`'s pipelines gate or the `NEW_REPO_DIRECTORIES`/`.gitignore`
  logic does not match "Current state" (Plan 008 may have already refactored it;
  reconcile before editing).
- Making Tier 1 the default breaks a test you cannot cleanly update within this
  plan's scope.

## Maintenance notes

- Tier and preset (Plan 008) are orthogonal axes that compose:
  `--preset general --tier 1` is the leanest scaffold. If Plan 008 lands first,
  its refactor of the directory logic may relocate the `.gitignore`/pipelines
  code — re-anchor accordingly.
- Reviewer should confirm the default really is Tier 1 (a fresh `--yes` run
  produces only the three memory docs plus the structural homes, no pipelines).

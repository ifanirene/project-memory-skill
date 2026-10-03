# Plan 008: Offer a general preset alongside comp-bio, and make it the user's choice

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan in
> `plans/README.md`.
>
> **Drift check (run first)**:
> `git diff --stat c320c14..HEAD -- scripts/bootstrap_repo_memory.py tests/test_bootstrap_repo_memory.py templates/ references/repo_modes.md SKILL.md`
> This plan runs after Plan 007, which already added `--tier` and changed the
> bootstrap default and one test. Re-read the live `bootstrap_repo_memory.py`
> and `test_bootstrap_repo_memory.py` before editing; anchor on **symbol names**
> (`build_audit`, `NEW_REPO_DIRECTORIES`, `read_template`), not line numbers.

## Status

- **Priority**: P2
- **Effort**: M–L
- **Risk**: MED (refactors the scaffold directory logic and template selection;
  changes the default scaffold flavor)
- **Depends on**: 007 (both edit `bootstrap_repo_memory.py`, `SKILL.md`, and the
  same bootstrap test; run 007 first). Also assumes 002 (LICENSE/portability)
  and 003 (canonical NOTES-template pointer to `templates/AGENTS.md`) have run.
- **Category**: direction (D3)
- **Planned at**: commit `c320c14`, 2026-07-11
- **Addresses**: Design review direction option **D3 (general vs comp-bio)**.

## Why this matters

The skill's prose promises to serve "long-lived research, analysis, and
**engineering** projects," but its only new-repo scaffold is a hardcoded
**computational-biology** tree (`data/raw|external|interim|processed`,
`scripts/preprocessing|analysis|visualization|utils`, `notebooks/`, single-cell
vocabulary). A web-app or data-engineering repo gets a scaffold full of folders
it will never use. This plan turns the domain into an explicit **preset the user
chooses**:

- **`general` (default):** minimal, domain-neutral homes.
- **`compbio`:** today's expandable computational-biology tree.

The memory contract (guide, index, notes, lessons, manifests) is identical
across presets — only the directory scaffold and the guide's "Project Structure"
section differ.

## Current state

- `scripts/bootstrap_repo_memory.py`:
  - `NEW_REPO_DIRECTORIES` is a module-level list of `(relpath, reason)` tuples —
    the comp-bio subtree (`config`, `data/raw`, …, `notebooks`, `docs/pipelines`,
    `tests`).
  - `build_audit(...)`'s `if mode == "new":` block iterates `NEW_REPO_DIRECTORIES`
    to append scaffold actions, and appends the repo-guide action with
    `template_name="AGENTS.md"`.
  - `read_template(name)` loads `templates/<name>`.
  - `parse_args()` now has `--tier` (from Plan 007) but no `--preset`.
- `templates/AGENTS.md` — the scaffolded repo guide. Its `## Project Structure &
  Module Organization` section embeds the comp-bio tree. Its `## `NOTES.md`
  Template` section is the canonical NOTES template that Plan 003 points to.
- `references/repo_modes.md` — its `## New repository` section shows only the
  comp-bio tree.
- `tests/test_bootstrap_repo_memory.py` — after Plan 007, the default-scaffold
  test asserts Tier-1 behavior; it still asserts the comp-bio subtree
  (`data/raw`, `scripts/analysis`, `config`, `notebooks`), which the new
  `general` default will not create.

## Commands you will need

| Purpose | Command | Expected on success |
|---------|---------|---------------------|
| Byte-compile | `python3 -m py_compile scripts/bootstrap_repo_memory.py` | exit 0 |
| `--preset` exists | `python3 scripts/bootstrap_repo_memory.py --help` | lists `--preset` |
| Bootstrap tests | `uv run --no-project --with pytest python -m pytest tests/test_bootstrap_repo_memory.py -q` | all pass |
| Full suite | `uv run --no-project --with pytest python -m pytest tests/ -q` | all pass |
| General default omits comp-bio subtree | Step 5 manual check | `data/raw` absent |

## Scope

**In scope**:
- `scripts/bootstrap_repo_memory.py`
- `tests/test_bootstrap_repo_memory.py`
- `templates/AGENTS_general.md` (create)
- `templates/AGENTS.md` (keep as the comp-bio guide; do not rename — Plan 003
  points at this path)
- `references/repo_modes.md`
- `SKILL.md` (repo-modes / bootstrap sections), `references/repo_structure.md`

**Out of scope**:
- The tier logic (Plan 007) beyond composing with it.
- The collector/companion skill (Plan 009).
- The `## `NOTES.md` Template` block inside the templates — keep it identical in
  both preset guides (it is contract, not domain).

## Git workflow

- Branch: `advisor/008-general-vs-compbio-preset`
- Commits per logical unit (preset dirs, template, docs, tests) or one commit.
  Message style matches repo `git log`.

## Steps

### Step 1: Turn the directory list into presets

Replace the `NEW_REPO_DIRECTORIES = [ ... ]` definition with a preset map. Keep
the comp-bio entries **except `docs/pipelines`** (pipelines are tier-controlled
by Plan 007, so remove them from the directory list to avoid double-creation):

```python
PRESET_DIRECTORIES = {
    "general": [
        ("tests", "test home"),
    ],
    "compbio": [
        ("config", "analysis configuration home"),
        ("data/raw", "immutable source-data home"),
        ("data/external", "imported reference-data home"),
        ("data/interim", "restartable intermediate-data home"),
        ("data/processed", "analysis-ready data home"),
        ("scripts/preprocessing", "preprocessing code home"),
        ("scripts/analysis", "analysis code home"),
        ("scripts/visualization", "visualization code home"),
        ("scripts/utils", "shared utility code home"),
        ("notebooks", "exploratory notebook home"),
        ("tests", "test home"),
    ],
}
```

### Step 2: Add a `--preset` flag defaulting to general

In `parse_args()`:

```python
    parser.add_argument(
        "--preset",
        choices=("general", "compbio"),
        default="general",
        help=(
            "New-repo scaffold flavor: general (minimal, domain-neutral; "
            "default) or compbio (expandable computational-biology tree)."
        ),
    )
```

### Step 3: Use the preset in `build_audit`

Change `build_audit`'s signature to accept `preset="general"`. In the
`if mode == "new":` block, iterate `PRESET_DIRECTORIES[preset]` instead of
`NEW_REPO_DIRECTORIES`, and select the repo-guide template by preset:

```python
    guide_template = "AGENTS.md" if preset == "compbio" else "AGENTS_general.md"
```

Use `guide_template` as the `template_name` for the repo-guide `ScaffoldAction`
(the `AGENTS.md` **destination** filename stays `AGENTS.md`; only the source
template differs). In `main()`, pass `preset=args.preset` to `build_audit`.

**Verify**: `python3 -m py_compile scripts/bootstrap_repo_memory.py` → exit 0.

### Step 4: Create the general repo-guide template

Create `templates/AGENTS_general.md`. Start from `templates/AGENTS.md`, keep the
`## Instructions`, `## Analysis Documentation Convention`, and the entire
`## `NOTES.md` Template` block **verbatim** (contract sections — must match the
comp-bio guide), and replace only the `## Project Structure & Module
Organization` tree with a neutral one:

```
## Project Structure & Module Organization

- Keep one durable home for each kind of artifact; avoid new top-level folders
  unless an existing home truly cannot fit the artifact type.

  ```text
  repo/
  ├── AGENTS.md
  ├── ANALYSIS_INDEX.md
  ├── src/ or scripts/     # code and CLIs (one home)
  ├── data/                # inputs and reference material
  ├── results/             # outputs, organized by branch root
  │   └── <branch-root>/runs/<variant>/
  ├── docs/
  │   └── LESSONS.md
  └── tests/
  ```

- Organize outputs by branch root: `results/<branch-root>/` for the maintained
  branch, with child variants under `results/<branch-root>/runs/<variant>/`.
- Variant names should encode the provenance-changing choice, not `v2`/`rerun`.
- Add `docs/pipelines/` and `analysis_manifest.json` only at Tier 2, when shared
  workflows or provenance-sensitive reruns actually appear.
```

### Step 5: Update the bootstrap tests for presets

In `tests/test_bootstrap_repo_memory.py`:

1. Update the default-scaffold test (Tier-1, from Plan 007) so it reflects the
   `general` default: assert `AGENTS.md`, `ANALYSIS_INDEX.md`,
   `docs/LESSONS.md`, `scripts/`, `data/`, `results/`, `tests/` exist, and
   assert the comp-bio subtree does **not**:
   `assert not (repo / "data" / "raw").exists()` and
   `assert not (repo / "scripts" / "analysis").exists()`.
2. Add `test_bootstrap_compbio_preset_creates_subtree` running
   `--repo <r> --yes --preset compbio --tier 2` and asserting `data/raw`,
   `data/processed`, `scripts/analysis`, `scripts/preprocessing`, `notebooks`,
   `config`, `docs/pipelines` all exist, and the scaffolded `AGENTS.md` contains
   a comp-bio marker (e.g. `assert "preprocessing" in (repo / "AGENTS.md").read_text()`).
3. Add `test_bootstrap_general_preset_guide` asserting a default (general) run's
   `AGENTS.md` does **not** contain `data/raw` in its structure section
   (`assert "data/raw" not in (repo / "AGENTS.md").read_text()`).

**Verify**: `uv run --no-project --with pytest python -m pytest tests/test_bootstrap_repo_memory.py -q` → all pass.
**Verify** (manual): `python3 scripts/bootstrap_repo_memory.py --repo <tmp> --yes`
then `test ! -e <tmp>/data/raw && echo GENERAL_OK` → `GENERAL_OK`.

### Step 6: Document the preset choice

- In `references/repo_modes.md` `## New repository`, add a short "Choose a
  preset" subsection with both trees (label the existing tree "compbio preset"
  and add the general tree from Step 4), and state the default is `general`.
- In `SKILL.md`, in the bootstrap/`## Repository modes` area, add:
  `Ask the user whether the repo is general-purpose or computational-biology,
  then scaffold with `--preset general` (default) or `--preset compbio`. The
  memory contract is identical across presets; only the directory scaffold and
  the guide's structure section differ.`
- In `references/repo_structure.md`, note that the branch-root output model
  applies to both presets.

**Verify**: `grep -c 'preset' SKILL.md references/repo_modes.md` → each ≥ 1.

### Step 7: Full regression

**Verify**: `uv run --no-project --with pytest python -m pytest tests/ -q` → all pass.

## Test plan

- Rewrite the default test for the `general` default (no comp-bio subtree).
- Add `test_bootstrap_compbio_preset_creates_subtree` and
  `test_bootstrap_general_preset_guide`.
- Verification: `uv run --no-project --with pytest python -m pytest tests/ -q` → all pass.

## Done criteria

- [ ] `python3 -m py_compile scripts/bootstrap_repo_memory.py` → exit 0.
- [ ] `python3 scripts/bootstrap_repo_memory.py --help` lists `--preset`.
- [ ] `templates/AGENTS_general.md` exists and contains the `## `NOTES.md` Template` block.
- [ ] Default (general) scaffold omits `data/raw` / `scripts/analysis` (Step 5 manual check).
- [ ] `--preset compbio` scaffold creates the comp-bio subtree.
- [ ] `grep -c 'preset' SKILL.md` and `references/repo_modes.md` each ≥ 1.
- [ ] `uv run --no-project --with pytest python -m pytest tests/ -q` → all pass.
- [ ] `git status --porcelain` shows only in-scope files (six modified + one new template).
- [ ] `plans/README.md` status row for 008 updated to DONE.

## STOP conditions

Stop and report if:
- `NEW_REPO_DIRECTORIES` is not present as a module-level list (Plan 007 or a
  prior run may have altered it) — reconcile before refactoring.
- Renaming/selecting the template would move or break the canonical NOTES
  template that Plan 003 points to (`templates/AGENTS.md`). This plan must keep
  `templates/AGENTS.md` at that path; if it has already been renamed, STOP.
- A comp-bio assertion and a general assertion cannot both pass — indicating the
  preset switch is not actually gating the directory list.

## Maintenance notes

- The `## `NOTES.md` Template` block now exists in **both** preset guides — that
  is intentional duplication of a scaffold artifact (each guide is copied
  verbatim into a repo). If it changes, update both; a future refactor could
  extract it to a shared `templates/NOTES_TEMPLATE.md` that both include, and
  update Plan 003's canonical pointer accordingly.
- Default preset is `general`; comp-bio users must pass `--preset compbio`. If
  most real users are comp-bio, reconsider the default (but the review's point
  is that the skill claims broader scope than comp-bio).
- Reviewer should confirm the memory contract sections are byte-identical
  between `templates/AGENTS.md` and `templates/AGENTS_general.md` (only the
  structure tree differs).

# Plan 009: Split the collector automation into a companion skill

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan in
> `plans/README.md`.
>
> **Drift check (run first)**:
> `git diff --stat c320c14..HEAD -- SKILL.md README.md scripts/ references/ tests/`
> This plan runs LAST, after 001–008 have reshaped the core skill. Re-read the
> live files named in each step before editing; anchor on headings/symbols, not
> line numbers. Use `git mv` for every move so history is preserved.

## Status

- **Review 2026-10-03**: TODO. The collector remains in the core package; no
  companion skill directory exists. Recommend deferring these file and installation
  changes. The July move list also predates the separate decision-memory controller
  and is incomplete for the current package. See the
  [current review](README.md#current-review--2026-10-03).

- **Priority**: P3
- **Effort**: L
- **Risk**: MED-HIGH (moves files across a new skill boundary; the risk is a
  broken cross-skill reference or a test that no longer resolves its script)
- **Depends on**: 004 (automation section gated in core `SKILL.md`), 006 (lock
  fix lands in `memoryctl.py` before it moves), 008 (core finalized). Run after
  the whole core-cleanup + direction track.
- **Category**: direction (D1) / architecture
- **Planned at**: commit `c320c14`, 2026-07-11
- **Addresses**: Design review direction option **D1 (split into two companion
  skills)**.

## Why this matters

The repo fuses two products with different audiences: the **core** repo-memory
contract (used by every adopter) and a heavy **cross-repo collector automation**
(a 966-line controller, weekly/monthly scheduling, an external
`OBSERVATIONS/REFLECTIONS/AXIOMS` ontology) used only by people pairing many
repos. Plan 004 gated the automation as optional; this plan finishes the
separation by extracting it into a **companion skill**, `project-memory-collector`,
so the core skill is small and single-purpose and the collector can be installed
(and reasoned about) on its own.

## Architecture decisions (do not deviate)

1. **Layout**: the **core skill stays at the repo root** (its `SKILL.md`,
   `scripts/`, `references/`, `templates/`, `tests/` keep their paths). The
   companion is a **new subdirectory** `project-memory-collector/` with its own
   `SKILL.md`, `scripts/`, `references/`, `tests/`.
2. **Boundary — moves to the companion** (via `git mv`):
   - `scripts/memoryctl.py`
   - `scripts/smoke_test_project_memory.py`
   - `references/scheduled_loops.md`
   - `references/personal_memory_bridge.md`
   - `references/live_maintenance_test.md`
   - `tests/test_memoryctl.py`
   - `tests/test_smoke_test_project_memory.py`
3. **Stays in core**: `bootstrap_repo_memory.py`, `validate_analysis_manifest.py`
   and their tests; `doc_contract.md`, `repo_structure.md`, `repo_modes.md`,
   `memory_quality.md`, `analysis_manifest.md`; all `templates/`.
4. **Cross-skill dependency**: `smoke_test_project_memory.py` uses the core's
   `bootstrap_repo_memory.py`. The companion **depends on the core skill being
   installed**; the smoke test locates it via `PROJECT_MEMORY_SKILL_DIR`, falls
   back to the parent repo (dev), and **skips** the bootstrap-audit step if
   neither resolves (rather than failing).
5. **Naming**: companion skill `name:` is `project-memory-collector`.

## Current state

- After Plan 004, `SKILL.md` has a condensed `## Scheduled maintenance (optional,
  advanced)` section and a gated `## External personal-memory bridge` section,
  plus a `## Promotion ladder` whose rungs mix repo-facing
  (`NOTES.md -> docs/LESSONS.md`) and personal (`OBSERVATIONS -> REFLECTIONS ->
  AXIOMS`) promotions, and a `## Reference` list naming `scheduled_loops.md`,
  `personal_memory_bridge.md`, and `live_maintenance_test.md`.
- `scripts/smoke_test_project_memory.py` defines
  `SKILL_ROOT = Path(__file__).resolve().parents[1]`,
  `MEMORYCTL = SKILL_ROOT / "scripts" / "memoryctl.py"`, and
  `BOOTSTRAP = SKILL_ROOT / "scripts" / "bootstrap_repo_memory.py"`. It does
  **not** currently `import os`. Its `main()` runs the bootstrap audit via
  `require_success(audit, "real-repo bootstrap audit")`.
- `tests/test_smoke_test_project_memory.py` and `tests/test_memoryctl.py`
  resolve their scripts via `Path(__file__).resolve().parents[1] / "scripts" / ...`
  — a repo-root-relative path that will still resolve after both test and script
  move into `project-memory-collector/` together.

## Commands you will need

| Purpose | Command | Expected on success |
|---------|---------|---------------------|
| Core tests (bootstrap + validate) | `uv run --no-project --with pytest python -m pytest tests/ -q` | all pass |
| Companion tests (memoryctl + smoke) | `uv run --no-project --with pytest python -m pytest project-memory-collector/tests/ -q` | all pass |
| Both suites | `uv run --no-project --with pytest python -m pytest tests/ project-memory-collector/tests/ -q` | all pass |
| Companion controller works | `python3 project-memory-collector/scripts/memoryctl.py --help` | prints usage |
| No stale refs in core | `grep -rn 'scheduled_loops\|personal_memory_bridge\|live_maintenance_test' SKILL.md references/` | only companion pointers, if any |

## Scope

**In scope**:
- Create `project-memory-collector/` and move the seven files listed above.
- `project-memory-collector/SKILL.md` (create), `project-memory-collector/agents/openai.yaml` (create, optional adapter).
- Edit moved `scripts/smoke_test_project_memory.py` (BOOTSTRAP resolution).
- Core `SKILL.md`, core `README.md`, and any core reference that pointed at the
  moved files.

**Out of scope**:
- Any logic change to `memoryctl.py` beyond its relocation (Plan 006 already
  fixed the lock).
- The core contract, bootstrap, tiers, presets, or templates.

## Git workflow

- Branch: `advisor/009-split-companion-skills`
- Use `git mv` for every relocation (preserve history). Commit in stages:
  (1) create companion + move files, (2) fix smoke cross-ref, (3) rewrite core
  pointers, (4) companion SKILL.md. Message style matches repo `git log`.

## Steps

### Step 1: Create the companion tree and move files

```bash
mkdir -p project-memory-collector/scripts project-memory-collector/references project-memory-collector/tests project-memory-collector/agents
git mv scripts/memoryctl.py project-memory-collector/scripts/memoryctl.py
git mv scripts/smoke_test_project_memory.py project-memory-collector/scripts/smoke_test_project_memory.py
git mv references/scheduled_loops.md project-memory-collector/references/scheduled_loops.md
git mv references/personal_memory_bridge.md project-memory-collector/references/personal_memory_bridge.md
git mv references/live_maintenance_test.md project-memory-collector/references/live_maintenance_test.md
git mv tests/test_memoryctl.py project-memory-collector/tests/test_memoryctl.py
git mv tests/test_smoke_test_project_memory.py project-memory-collector/tests/test_smoke_test_project_memory.py
```

**Verify**: `uv run --no-project --with pytest python -m pytest project-memory-collector/tests/test_memoryctl.py -q` → all pass (memoryctl resolves at its new path).

### Step 2: Fix the smoke test's cross-skill reference to core

In `project-memory-collector/scripts/smoke_test_project_memory.py`:

1. Add `import os` to the imports.
2. Replace the `BOOTSTRAP = SKILL_ROOT / "scripts" / "bootstrap_repo_memory.py"`
   line with a resolver:

```python
def _find_core_bootstrap() -> Path | None:
    """Locate the core project-memory skill's bootstrap helper. The collector is
    a companion skill; the core may be installed elsewhere."""
    candidates = []
    env = os.environ.get("PROJECT_MEMORY_SKILL_DIR")
    if env:
        candidates.append(Path(env) / "scripts" / "bootstrap_repo_memory.py")
    candidates.append(SKILL_ROOT.parent / "scripts" / "bootstrap_repo_memory.py")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None
```

3. In `main()`, replace the unconditional bootstrap-audit block with a guarded
   one that skips when core isn't found:

```python
    bootstrap = _find_core_bootstrap()
    if bootstrap is not None:
        audit = run_command(sys.executable, str(bootstrap), "--repo", str(repo), "--audit-only")
        require_success(audit, "real-repo bootstrap audit")
        checks.append("real repo audit")
    else:
        checks.append("real repo audit (skipped: core skill not found — set PROJECT_MEMORY_SKILL_DIR)")
```

(Delete the old `BOOTSTRAP` constant and the old audit block that referenced it.)

**Verify**: `uv run --no-project --with pytest python -m pytest project-memory-collector/tests/test_smoke_test_project_memory.py -q` → all pass (the dev fallback finds core at the repo root).

### Step 3: Write the companion `SKILL.md`

Create `project-memory-collector/SKILL.md` with this frontmatter:

```yaml
---
name: project-memory-collector
description: Runs the optional external long-term-memory collector that pairs
  with the project-memory skill — a weekly/monthly automation that distills
  changed repo-memory docs and agent dialogs into observations, reflections,
  and axioms without editing monitored repos directly. Use only when pairing
  multiple repos with a shared external memory workspace; it requires the
  project-memory skill to be installed.
---
```

Body must cover (move the prose from the relocated references; do not
re-invent): the two-layer weekly/monthly model, the LLM-proposes /
controller-applies split, the `memoryctl.py` command sequence, the
weekly-must-not-edit-repos rule, protected-`AGENTS.md` deferral, queue
lifecycle, the personal promotion ladder (`OBSERVATIONS -> REFLECTIONS ->
AXIOMS`), and the live-maintenance-test protocol. Point to
`references/scheduled_loops.md`, `references/personal_memory_bridge.md`, and
`references/live_maintenance_test.md` (now inside this companion) for detail,
and state that `PROJECT_MEMORY_SKILL_DIR` should point at the installed core
skill.

**Verify**: `grep -c 'project-memory-collector' project-memory-collector/SKILL.md` → ≥ 1.

### Step 4: Trim the core `SKILL.md` to a companion pointer

In the core `SKILL.md`:

1. Replace the `## Scheduled maintenance (optional, advanced)` section (from its
   heading to the next top-level heading) with:

```
## Companion skill: external collector (optional)

The weekly/monthly cross-repo collector is a **separate companion skill**,
`project-memory-collector`. Install and use it only when pairing multiple repos
with a shared external long-term-memory workspace. It reads this repo's memory
docs read-only and never edits monitored repos directly. The core contract above
needs none of it.
```

2. Replace the `## External personal-memory bridge` section similarly with a
   one-paragraph pointer to the companion skill (the bridge lives there now).
3. In `## Promotion ladder`, keep the repo rung
   (`NOTES.md -> docs/LESSONS.md`) and replace the personal rungs
   (`OBSERVATIONS`, `REFLECTIONS`, `AXIOMS`) with one line: `Personal-memory
   promotion (observations -> reflections -> axioms) is handled by the
   `project-memory-collector` companion skill.`
4. In the `## Reference` list, remove the `scheduled_loops.md`,
   `personal_memory_bridge.md`, and `live_maintenance_test.md` entries (they
   moved) and add one line pointing to the companion skill.

**Verify**: `grep -rn 'references/scheduled_loops.md\|references/personal_memory_bridge.md\|references/live_maintenance_test.md' SKILL.md` → no output (no stale core references to moved files).
**Verify**: `grep -c 'project-memory-collector' SKILL.md` → ≥ 1.

### Step 5: Update the core README install for two skills

In the core `README.md`, update the Install and Repository-Layout sections to
describe **two** skills: install `project-memory` (this root) and, optionally,
`project-memory-collector` (the subdirectory), noting the companion needs the
core installed and `PROJECT_MEMORY_SKILL_DIR` set. Update the repository-layout
tree to show the `project-memory-collector/` subdirectory.

Also update the core `agents/openai.yaml` `default_prompt` to drop the
"maintenance contract" clause (that capability moved), and create a minimal
`project-memory-collector/agents/openai.yaml` adapter mirroring it for the
companion.

**Verify**: `grep -c 'project-memory-collector' README.md` → ≥ 1.

### Step 6: Full regression across both skills

**Verify**: `uv run --no-project --with pytest python -m pytest tests/ project-memory-collector/tests/ -q` → all pass.
**Verify**: `python3 project-memory-collector/scripts/memoryctl.py doctor --workspace .` runs (it will error on a missing registry, but must not crash on import) — confirm it prints a `memoryctl:`-prefixed error, not a Python traceback.

## Test plan

- No test logic changes — the two moved test files must pass unchanged at their
  new paths (they use repo-root-relative script resolution that survives the
  move alongside their scripts).
- The smoke test must still pass via the dev fallback in `_find_core_bootstrap`
  (core is the parent repo).
- Verification: both suites green (Step 6). Core suite now contains only
  bootstrap + validate tests; companion suite contains memoryctl + smoke tests.

## Done criteria

- [ ] `project-memory-collector/` contains `SKILL.md`, `scripts/memoryctl.py`,
      `scripts/smoke_test_project_memory.py`, the three moved references, and the
      two moved tests.
- [ ] `git status` shows the moves as renames (history preserved), not delete+add.
- [ ] `grep -rn 'references/scheduled_loops.md\|references/personal_memory_bridge.md\|references/live_maintenance_test.md' SKILL.md` → no output.
- [ ] `grep -c 'project-memory-collector' SKILL.md README.md` → each ≥ 1.
- [ ] `uv run --no-project --with pytest python -m pytest tests/ project-memory-collector/tests/ -q` → all pass.
- [ ] `python3 project-memory-collector/scripts/memoryctl.py --help` prints usage.
- [ ] `plans/README.md` status row for 009 updated to DONE.

## STOP conditions

Stop and report if:
- Any moved test fails at its new path for a path-resolution reason (the
  `parents[1]` assumption broke) — report before hand-patching.
- The core `SKILL.md` no longer has a recognizable `## Scheduled maintenance` /
  `## External personal-memory bridge` section to replace (Plan 004 did not run,
  or the headings differ) — reconcile first.
- `smoke_test_project_memory.py`'s `main()` structure differs from "Current
  state" such that the guarded-audit insertion doesn't fit cleanly.
- You are tempted to move `bootstrap_repo_memory.py` or
  `validate_analysis_manifest.py` — do not; they are core.

## Maintenance notes

- The companion now **requires the core skill**. Document
  `PROJECT_MEMORY_SKILL_DIR` prominently; without it (and outside the dev repo)
  the smoke test's audit step self-skips.
- If the two skills are ever published as separate repos, this subdirectory
  layout makes extraction a clean `git subtree`/copy of `project-memory-collector/`.
- A reviewer should confirm no capability was lost — every automation rule that
  was in the core `SKILL.md` now lives in the companion `SKILL.md` or its moved
  references, and both test suites still pass.
- The `.gitignore`/`.pytest_cache` at the repo root still covers both skills;
  no per-skill ignore files are needed.

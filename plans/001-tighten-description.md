# Plan 001: Tighten the skill's triggering `description` and add a negative signal

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan in
> `plans/README.md`.
>
> **Drift check (run first)**:
> `git diff --stat c320c14..HEAD -- SKILL.md`
> If `SKILL.md` changed since this plan was written, compare the "Current state"
> excerpt below against the live frontmatter before proceeding; on a mismatch,
> treat it as a STOP condition.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: dx
- **Planned at**: commit `c320c14`, 2026-07-11
- **Addresses**: Finding 5 (design review)

## Why this matters

An Agent Skill's YAML `description` is the *only* text the host model sees when
deciding whether to load the skill. The current description is a single 54-word
run-on that crams ~10 triggers together and gives the model **no negative
signal** — nothing that says when *not* to fire. Dense positive-only
descriptions cause both missed triggers (the model can't parse which case
applies) and over-triggering (it fires on unrelated refactor/writing tasks).
A shorter description with an explicit "not for…" clause improves trigger
precision at essentially zero risk.

## Current state

- `SKILL.md` — the skill manifest. Its YAML frontmatter (lines 1–9) is the
  entire triggering surface. It currently reads:

```yaml
---
name: project-memory
description: Use when a user wants to scaffold or clean up the durable memory
  and repo-organization system for a long-lived project, especially to define
  clear roles for repo rules, an analysis index, branch notes, reusable
  lessons, selective analysis manifests, shared pipeline docs, new-repo
  computational-biology structure, monitored-repo drift repair, and an
  optional external personal-memory bridge.
---
```

- Convention: the frontmatter uses `name:` + `description:` (Anthropic Agent
  Skill format). `name:` must stay exactly `project-memory` — it is referenced
  by `agents/openai.yaml` (`$project-memory`) and by every command path in the
  docs. Do **not** change `name:`.

## Commands you will need

| Purpose | Command | Expected on success |
|---------|---------|---------------------|
| Regression: tests still pass | `uv run --no-project --with pytest python -m pytest tests/ -q` | `15 passed` |
| Confirm frontmatter parses | `uv run --no-project --with pyyaml python -c "import yaml,pathlib; t=pathlib.Path('SKILL.md').read_text().split('---')[1]; d=yaml.safe_load(t); print(d['name']); print(len(d['description'].split()),'words')"` | prints `project-memory` and a word count `< 75` |

If `uv` is unavailable: `pip install pytest pyyaml` then replace `uv run
--no-project --with pytest python` with `python3`, and `--with pyyaml python`
with `python3`.

## Scope

**In scope** (the only file you should modify):
- `SKILL.md` — frontmatter block only (between the first two `---` lines).

**Out of scope** (do NOT touch):
- The `name:` field value.
- Any line of `SKILL.md` *below* the closing `---` of the frontmatter. This
  plan changes the description string only; Plan 002 and 003 edit the body.
- Any other file.

## Git workflow

- Branch: `advisor/001-tighten-description`
- One commit. Message style (match repo `git log`, e.g. `Clarify project-memory
  docs...`): `Tighten project-memory skill description and add negative signal`.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Replace the description string

Replace the entire frontmatter block shown in "Current state" with exactly this
(keep `name:` unchanged; this only rewrites `description:`):

```yaml
---
name: project-memory
description: Sets up and maintains a durable repo-memory system for long-lived
  research and analysis projects — a repo guide, an analysis index, per-branch
  notes, distilled lessons, and optional execution manifests. Use when
  scaffolding memory in a new repo, repairing documentation drift in an
  existing one, deciding where a new file or note belongs, promoting durable
  lessons, or pairing a repo with an external long-term-memory collector. Not
  for general code refactoring, one-off writing tasks, or short-lived repos
  that need no durable cross-session memory.
---
```

**Verify**: run the "Confirm frontmatter parses" command → prints
`project-memory` and a word count under 75.

**Verify**: `grep -c "Not for" SKILL.md` → `1` (the negative signal is present).

## Test plan

No unit test applies to frontmatter prose. Verification is the two commands
above plus the regression suite:

- `uv run --no-project --with pytest python -m pytest tests/ -q` → `15 passed`
  (proves no accidental edit broke the scripts/tests).

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `SKILL.md` frontmatter `name:` is still exactly `project-memory`.
- [ ] `grep -c "Not for" SKILL.md` returns `1`.
- [ ] The frontmatter `description` is under 75 words (parse command above).
- [ ] `uv run --no-project --with pytest python -m pytest tests/ -q` → `15 passed`.
- [ ] `git status --porcelain` shows only `SKILL.md` modified.
- [ ] `plans/README.md` status row for 001 updated to DONE.

## STOP conditions

Stop and report back (do not improvise) if:

- The live frontmatter does not match the "Current state" excerpt (SKILL.md
  drifted since this plan was written).
- The frontmatter parse command errors (YAML is malformed after your edit) and
  a single fix attempt does not resolve it.
- You find `name:` is referenced with a different value anywhere — do not
  rename it; report instead.

## Maintenance notes

- If the skill later drops the external-collector feature (see Plan 004), the
  "pairing a repo with an external long-term-memory collector" clause should be
  removed from this description to keep triggers honest.
- Reviewer should confirm the description still reads as third-person "what it
  does + when to use," matching Anthropic skill-description conventions.

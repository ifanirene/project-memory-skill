# Project Memory Skill

Shareable Codex skill for setting up durable repo memory in long-lived research,
analysis, and engineering projects, with an optional external long-term-memory
bridge for distilled dialog and user-specific patterns.

It helps a repo converge on a small, maintainable documentation system:

- `AGENTS.md` or an equivalent repo guide for global rules
- `ANALYSIS_INDEX.md` for the repo-wide map of active analyses or workstreams
- per-analysis `NOTES.md` files for scientific narrative and variant decisions
- selective `analysis_manifest.json` records for complex analytical variants
- `docs/LESSONS.md` for distilled repo-facing lessons and preferences
- `docs/pipelines/` for reusable workflow docs when a shared pipeline is large
  enough to justify one
- a new-repo computational-biology scaffold and monitored-repo drift audit

It can also be paired with an external personal-memory workspace that distills:

- user corrections and stable preferences
- troubleshooting strategies and decision rules
- accepted or rejected solution patterns from Codex dialogs
- mirror candidates that should eventually become repo-facing lessons

## What This Skill Does

The skill is meant for projects where people keep asking:

- Where should this file go?
- Which analysis is the current one?
- What do I rerun?
- What should I trust?
- What mistake should we not repeat?

It pushes the repo toward a minimal memory system rather than a pile of
overlapping status docs, while still making room for longer-term personal
memory outside the repo.

## Core Ideas

- Keep repo memory minimal: `ANALYSIS_INDEX.md`, branch `NOTES.md`, and
  `docs/LESSONS.md` should usually be enough.
- Keep execution provenance in `analysis_manifest.json` for parameter sweeps,
  repeated analytical reruns, inferential workflows, and result-changing
  choices. Keep scientific comparison and selection in `NOTES.md`.
- Promote deliberately: `NOTES.md -> docs/LESSONS.md` only when a branch-local
  observation can be rewritten as a durable `Default`, `Check`, `Trap`, or
  `Preference`.
- Distill, do not copy: raw Codex dialog logs and one-off session chatter stay
  out of repo docs and out of the external memory workspace.
- Use automation incrementally: prioritize new or updated signals, reserve only
  a small bounded share for round-robin legacy quality review, and always write
  a unique decision log.
- Reserve a bounded weekly round-robin for unchanged legacy memory documents so
  chronology drift and undistilled lessons are eventually reviewed even when
  their files stop changing.
- Keep semantic judgment in the LLM and deterministic workflow control in
  `memoryctl`: access checks, bounded collection, locking, validation, cursors,
  queue state, and atomic writes.

## Automation Model

The skill is designed to work with two maintenance layers:

- weekly central collection plus repo-local memory maintenance
- monthly dialog distillation, cross-repo axiom review, and mirror generation

The monthly loop is implemented as a weekly-scheduled automation with a 28-day
gate when native monthly scheduling is unavailable.

The collector runs once from an external workspace with read-only access to
registered repo-memory files and write access only to its own state. It does
not directly edit monitored repos.

## Bootstrap Helper

The skill includes a reusable helper:

```bash
python "$CODEX_HOME/skills/project-memory/scripts/bootstrap_repo_memory.py" \
  --repo /path/to/repo --mode new --audit-only
```

New mode scaffolds an expandable computational-biology workspace. Monitored
mode reports contract, structure, documentation, and manifest drift without
reorganizing the existing repository:

```bash
python "$CODEX_HOME/skills/project-memory/scripts/bootstrap_repo_memory.py" \
  --repo /path/to/repo --mode monitored --audit-only
```

The core audit covers:

- `AGENTS.md`
- `ANALYSIS_INDEX.md`
- `docs/LESSONS.md`
- `docs/pipelines/`
- `scripts/` or `src/`
- `data/`
- `results/`
- `docs/`

It does not rewrite existing files. The skill uses its monitored-mode findings
to make bounded, protected-information-aware repairs.

## Live functional test

Ask Codex to run the real maintenance workflow and leave its changes for
inspection:

```text
Use $project-memory to run a live maintenance test in this repository with the
production collector at /Volumes/IF_PHAGE/long-term-memory. Take real semantic
and maintenance actions, apply validated collector state, and leave genuine
repo documentation changes uncommitted for my review. Do not create synthetic
lessons, use a shadow repo, roll back the changes, or commit them. Finish by
showing the collector artifacts and the focused git diff.
```

This runs the production collector, creates a source-backed semantic proposal,
advances real cursors and queues, writes a run log, and makes only genuine
repo-memory repairs. The repo changes remain uncommitted so they can be judged
with `git diff`.

For a deterministic controller safety check, run:

```bash
python "$CODEX_HOME/skills/project-memory/scripts/smoke_test_project_memory.py" \
  --repo /path/to/project
```

That smoke harness restores its writes and uses temporary collector state. It
tests workflow mechanics and rollback safety, not useful live maintenance.

## Repository Layout

```text
project-memory-skill/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── doc_contract.md
│   ├── analysis_manifest.md
│   ├── live_maintenance_test.md
│   ├── memory_quality.md
│   ├── personal_memory_bridge.md
│   ├── repo_structure.md
│   ├── repo_modes.md
│   └── scheduled_loops.md
├── scripts/
│   ├── bootstrap_repo_memory.py
│   ├── memoryctl.py
│   ├── smoke_test_project_memory.py
│   └── validate_analysis_manifest.py
├── templates/
│   ├── AGENTS.md
│   ├── ANALYSIS_INDEX.md
│   └── LESSONS.md
└── tests/
    ├── test_bootstrap_repo_memory.py
    ├── test_memoryctl.py
    ├── test_validate_analysis_manifest.py
    └── test_smoke_test_project_memory.py
```

## Install

Copy this folder into your Codex skills directory as `project-memory`:

```bash
mkdir -p "$CODEX_HOME/skills"
cp -R project-memory-skill "$CODEX_HOME/skills/project-memory"
```

If you already have a local version, rename or back it up first.

## Use

Ask Codex to use the skill when you want to:

- scaffold project memory in a new repo
- clean up repo organization drift
- add selective pipeline manifests and validate their provenance
- add or repair `ANALYSIS_INDEX.md`
- tighten `NOTES.md` and `LESSONS.md` roles
- define stable homes for scripts, data, outputs, and docs
- audit or scaffold the minimal repo-memory skeleton in a new or drifting repo
- add a note-to-lessons promotion rule
- pair repo memory with an external long-term-memory workspace
- define weekly and monthly memory-maintenance layers

Example prompt:

```text
Use $project-memory to clean up this repo's analysis documentation contract,
make file placement predictable, promote durable lessons from notes, and pair
the repo with an external long-term-memory collector using weekly and monthly
maintenance without bloating repo docs.
```

## Included References

- `references/doc_contract.md`: repo-memory roles, templates, and suggested
  wording
- `references/repo_structure.md`: branch-root file placement guidance
- `references/repo_modes.md`: new-repo setup versus monitored-repo drift repair
- `references/analysis_manifest.md`: selective manifest policy and schema
- `references/personal_memory_bridge.md`: external observations, reflections,
  axioms, and mirror rules
- `references/scheduled_loops.md`: two-layer weekly/monthly automation,
  controller boundaries, protected-info rules, and queue lifecycle
- `templates/`: conservative scaffold templates used by the bootstrap helper

## Sharing Notes

This repo contains a rewritten, shareable implementation of the skill and its
reference templates. Before publishing publicly, choose the license you want to
use for your copy.

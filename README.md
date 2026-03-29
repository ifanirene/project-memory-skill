# Project Memory Skill

Shareable Codex skill for setting up durable repo memory in long-lived research,
analysis, and engineering projects, with an optional external long-term-memory
bridge for distilled dialog and user-specific patterns.

It helps a repo converge on a small, maintainable documentation system:

- `AGENTS.md` or an equivalent repo guide for global rules
- `ANALYSIS_INDEX.md` for the repo-wide map of active analyses or workstreams
- per-analysis `NOTES.md` files for rerun and extension context
- `docs/LESSONS.md` for distilled repo-facing lessons and preferences
- `docs/pipelines/` for reusable workflow docs when a shared pipeline is large
  enough to justify one

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
- Promote deliberately: `NOTES.md -> docs/LESSONS.md` only when a branch-local
  observation can be rewritten as a durable `Default`, `Check`, `Trap`, or
  `Preference`.
- Distill, do not copy: raw Codex dialog logs and one-off session chatter stay
  out of repo docs and out of the external memory workspace.
- Use automation incrementally: daily or weekly maintenance loops should process
  only new or updated signals after bootstrap, and should always write a clear
  decision log.

## Repository Layout

```text
project-memory-skill/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── references/
    ├── doc_contract.md
    ├── personal_memory_bridge.md
    └── repo_structure.md
    └── scheduled_loops.md
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
- add or repair `ANALYSIS_INDEX.md`
- tighten `NOTES.md` and `LESSONS.md` roles
- define stable homes for scripts, data, outputs, and docs
- add a note-to-lessons promotion rule
- pair repo memory with an external long-term-memory workspace

Example prompt:

```text
Use $project-memory to clean up this repo's analysis documentation contract,
make file placement predictable, promote durable lessons from notes, and pair
the repo with an external long-term-memory workspace without bloating repo docs.
```

## Included References

- `references/doc_contract.md`: repo-memory roles, templates, and suggested
  wording
- `references/repo_structure.md`: branch-root file placement guidance
- `references/personal_memory_bridge.md`: external observations, reflections,
  axioms, and mirror rules
- `references/scheduled_loops.md`: daily and weekly automation guidance for
  incremental maintenance and logging

## Sharing Notes

This repo contains a rewritten, shareable implementation of the skill and its
reference templates. Before publishing publicly, choose the license you want to
use for your copy.

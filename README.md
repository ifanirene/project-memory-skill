# Project Memory Skill

Shareable Codex skill for setting up durable repo memory in long-lived research,
analysis, and engineering projects.

It helps a repo converge on a small, maintainable documentation system:

- `AGENTS.md` or an equivalent repo guide for global rules
- `ANALYSIS_INDEX.md` for the repo-wide map of active analyses or workstreams
- per-analysis `NOTES.md` files for rerun and extension context
- `docs/LESSONS.md` for distilled cross-run lessons and preferences
- `docs/pipelines/` for reusable workflow docs when a shared pipeline is large
  enough to justify one

## What This Skill Does

The skill is meant for projects where people keep asking:

- Where should this file go?
- Which analysis is the current one?
- What do I rerun?
- What should I trust?
- What mistake should we not repeat?

It pushes the repo toward a minimal memory system rather than a pile of
overlapping status docs.

## Repository Layout

```text
project-memory-skill/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── references/
    ├── doc_contract.md
    └── repo_structure.md
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

Example prompt:

```text
Use $project-memory to clean up this repo's analysis documentation contract,
make file placement predictable, and keep the memory system minimal.
```

## Sharing Notes

This repo contains a rewritten, shareable implementation of the skill and its
reference templates. Before publishing publicly, choose the license you want to
use for your copy.

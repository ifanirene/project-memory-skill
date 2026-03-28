---
name: project-memory
description: Use when a user wants to scaffold or repair a durable repo memory
  system with clear roles for repo rules, analysis indexing, branch notes,
  lessons learned, pipeline docs, and stable file placement.
---

# Project Memory

Use this skill to make a long-lived repo easier to resume, extend, and trust.
The goal is not to create more documentation. The goal is to make each durable
document answer one clear question.

## Core Contract

Treat these as the main long-lived layers unless the repo already has an
equivalent naming scheme:

- `AGENTS.md`: global repo rules and the documentation contract
- `ANALYSIS_INDEX.md`: repo-wide map of active maintained analyses
- `output/.../NOTES.md` or `results/.../NOTES.md`: branch-level rerun and
  validation notes
- `docs/LESSONS.md`: distilled cross-run lessons, defaults, preferences, and
  recurring traps
- `docs/pipelines/*.md`: shared workflow docs only when a pipeline is reused or
  operationally complex

When a repo already uses `docs/LESSONS.md` as its memory document, do not add a
second memory file under another name.

## Structure Contract

Favor a small set of durable homes:

- runnable code in `scripts/` or `src/`
- inputs under `data/`
- generated outputs under one predictable root such as `output/` or `results/`
- durable documentation under `docs/`

Avoid:

- new top-level dumping grounds
- mixing the same artifact type across unrelated roots
- burying active outputs in ad hoc scratch directories
- proliferating status docs that answer the same question

## Minimal Mode

Most repos only need:

1. `ANALYSIS_INDEX.md`
2. per-analysis `NOTES.md`
3. `docs/LESSONS.md`

Use pipeline docs only when branch notes are no longer the right home for
workflow mechanics.

## Workflow

1. Inspect the repo guide, top-level structure, index, lessons, and any
   existing notes.
2. Decide whether the repo needs new documents or clearer role statements in
   the documents it already has.
3. Write the documentation contract into the repo guide first.
4. Make each long-lived doc answer one question:
   - index: what exists and where
   - notes: how to rerun or extend one maintained analysis
   - lessons: what future work should do differently
   - pipeline docs: how a reusable workflow operates
5. Make directory placement rules explicit enough that future files have one
   obvious home.
6. Prefer concise, durable text over session narration.
7. When updating a branch `NOTES.md`, deliberately review whether the index and
   lessons also need updates.

## Content Tests

Keep content only if it helps a future contributor answer at least one of:

- What should I run?
- What should I trust?
- What should I check first?
- What should I avoid repeating?
- Where does the current version live?

If it does not answer one of those, it probably does not belong in a long-lived
repo memory document.

## Common Repairs

- Add explicit document-role statements when people cannot tell where updates
  belong.
- Collapse diary-style notes into concise branch runbooks.
- Move branch-specific history out of lessons.
- Keep the index focused on maintained analyses instead of minor reruns.
- Add placement rules when outputs keep landing in inconsistent locations.
- Add pipeline docs only when the workflow is genuinely shared or multi-step.

## Included References

- `references/doc_contract.md`: copy-ready templates and wording for repo
  memory docs
- `references/repo_structure.md`: copy-ready repo structure and placement rules

# Live Maintenance Test

Use this protocol when the user wants evidence that project memory and its
maintenance loop can perform useful work. Do not substitute a rollback smoke
test.

## Required outcome

Leave inspectable evidence in both layers:

- production collector state: packet, validated proposal, observations,
  cursors, queue changes, and run log
- project repository: genuine maintenance edits left uncommitted for review

Do not add synthetic lessons or placeholder notes merely to create a diff.
Do not restore the repo changes at the end. Do not commit them automatically.

## Protocol

1. Record the project repository's current branch, HEAD, and Git status. A
   committed baseline is sufficient for recovery. Preserve unrelated existing
   changes and do not edit overlapping files without first reconciling them.
2. Run the bootstrap helper in audit-only mode against the actual project.
3. Run `memoryctl doctor` against the configured production collector.
4. Run a bounded `memoryctl collect` into a uniquely named production run
   directory. Do not use a temporary collector for this live test.
5. Review every collected source semantically. Write a real structured
   proposal with source-backed observations and maintenance items; an empty
   candidate list is acceptable when the sources contain no durable signal.
6. Run `memoryctl validate`, then `memoryctl apply`. This must advance real
   cursors and write a permanent decision log even when no observations are
   promoted.
7. Inspect a recent or active project branch by reviewing its index row,
   `NOTES.md`, and relevant lessons together. Make only genuine maintenance
   changes, such as repairing a stale status, missing rerun provenance,
   incomplete cross-document review, or an outdated maintenance contract.
8. Leave those project edits uncommitted. Show `git status` and a focused
   `git diff` so the user can judge whether the maintenance was useful.
9. Report collector artifacts, queue items, project files changed, validation
   results, and any defect discovered by the live run.

Uncommitted work on the canonical main checkout does not block the live test.
Record the starting status and read each target's current content. Memory docs
may be substantially rewritten when their current form does not serve their
purpose; only protected `AGENTS.md` information has a preservation guarantee.
Never reset, discard, or commit unrelated work.

## Copy-ready Codex prompt

```text
Use $project-memory to run a live maintenance test in this repository with the
production collector at /Volumes/IF_PHAGE/long-term-memory. Take real semantic
and maintenance actions, apply validated collector state, and leave genuine
repo documentation changes uncommitted for my review. Do not create synthetic
lessons, use a shadow repo, roll back the changes, or commit them. Finish by
showing the collector artifacts and the focused git diff.
```

## Controller-only safety check

Use `scripts/smoke_test_project_memory.py` only to test deterministic mechanics
and restoration safety. It intentionally uses temporary collector state and
restores controlled repo writes, so it is not evidence of useful live
maintenance.

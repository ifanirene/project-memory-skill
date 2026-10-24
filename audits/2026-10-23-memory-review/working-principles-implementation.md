# Working principles: implementation receipt

Completed 2026-10-23, America/Los_Angeles. Installation receipt timestamp:
2026-10-24T04:08:35Z.

## Delivered

- [Design plan](../../plans/010-working-principles-and-core-values.md): L1 signal
  selection, L2 use during work, L3 core commitments, and staged migration checks.
- [Task index](/Volumes/IF_PHAGE/long-term-memory/principles/INDEX.md): routes to
  the existing five reflections, two candidates, the current domain-specific
  axiom, and the borrowed library. Existing status labels and source limitations
  remain visible.
- [Borrowed working principles](/Volumes/IF_PHAGE/long-term-memory/principles/BORROWED_WORKING_PRINCIPLES.md):
  nine English adaptations, each with a trigger, action, rationale/cost, boundary,
  source, and first-use test. Their benefits have not yet been tested in projects.
- A small change to `decision_memory.render` adds the task-index link to the
  generated reflection and axiom views when the index exists. The link survives
  regeneration. Workspaces without an index retain the previous rendering.

The shared `.agents` and Claude skill routes resolve to this checkout. The Codex
compatibility script has the same filesystem identity as the source runtime, so
the renderer change is available through those installed routes. This does not
prove that a future agent will retrieve or apply a principle appropriately.

## Verification and preservation

- No-index rendering is byte-identical to the pre-change renderer for all three
  generated views, using the current production ledger in a temporary workspace.
- With an index, exactly two navigation paragraphs are added; the decision view
  is unchanged. A second render is identical, and the in-memory state is unchanged.
- Installation ran under the existing workspace lock. The production ledger hash
  is unchanged: **343 events and eight personal interpretations**. Borrowed cards
  did not create support episodes or personal axioms.
- All nine card anchors resolve. Twelve source URLs match the pinned source
  receipt. Twenty-five local document links resolve. New plan/library prose is
  English; original personal evidence and wording were preserved.
- Existing source edits, including the Claude dialogue work, remain intact. The
  isolated [renderer patch](working-principles-render.patch) shows this request's
  runtime change without attributing earlier edits to it.

See [verification and installation details](working-principles-verification.json)
and the [pinned Yage sources](yage-source-receipt.json). The external installation
also has its own [run receipt](/Volumes/IF_PHAGE/long-term-memory/logs/runs/working-principles-20261024T040835Z.json).

## Still planned

The full schema migration, semantic episode grouping, correction/supersession
repair, source-continuity changes, retrieval pilots, and schedule-prompt changes
remain in the design plan. Current schedules and their older eligibility rules
are unchanged. No L3 core-value interpretation was added.

This delivery establishes availability and preserves evidence. It does not yet
establish improved scientific decisions, reduced corrections, or successful use
by a later scheduled run. Those are the outcomes the planned use receipts must
test.

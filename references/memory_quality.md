# Memory Quality

Use this reference when a note or lessons file is long, chronological, or hard
to navigate. Size and dates trigger review; they do not prove that a document
is bad.

## Branch runbooks

Draft or rewrite a note using the narrative logic from `paper-narrative`:

1. Derive the brief from the work: purpose, current claim, canonical artifacts,
   trust basis, and missing evidence.
2. Choose the shortest useful arc: question -> current answer -> evidence ->
   selected analytical variant -> limitations -> next decision.
3. Build a kill list. Delete redundant updates, superseded commands, cosmetic
   iterations, repeated summaries, and details that do not support the arc.
   Preserve user-attributed choices, rejected alternatives, reasons, accepted
   costs, changes of mind and their source boundaries in a compact decision record.
4. Rewrite the note as one coherent current document; do not append another
   session section.

A future contributor should find these quickly:

- why the branch exists
- what the current answer or claim is
- which evidence supports it
- which analytical variant is preferred and where its manifest lives
- why the result is trustworthy and where it is limited
- what decision or evidence comes next

Chronology is not a protected note shape. Keep a compact decision/provenance
record when sequence explains the current result or the investigator's evolving
judgment. Do not delete the only evidence of a choice before its attributed
distillation is stored and linked; an agent-written summary is not user endorsement.
When a valid manifest exists, remove duplicated commands, parameters, input
inventories, and artifact inventories from the note. In a legacy branch with a
required manifest missing, do not delete the only recoverable execution facts;
queue manifest migration or retain only that irreducible provenance until a
native rerun records it.

## Lessons

Write every new or rewritten lesson with a literal type prefix:

```md
- Default: When <trigger>, <action>, because <reason>.
- Check: Before <decision or trust point>, verify <evidence>, because <risk>.
- Trap: Avoid <failure mode> when <trigger>, because <consequence>.
- Preference: When <choice recurs>, prefer <option>, because <reason>.
```

Include a trigger, action, and reason. Put optional date or source-branch
provenance at the end; do not organize lessons as a dated feed.

## Quality issue types

- `notes_chronology_drift`: current state is buried under dated updates.
- `lesson_not_distilled`: lessons are stored as dated findings rather than
  typed decision guidance.
- `stale_runbook_state`: the current run, trust status, or next action is
  absent or contradicted by later entries.
- `oversized_memory_doc`: size makes the current state hard to find. Line count
  alone is not enough to queue this issue.
- `missing_required_manifest`: a provenance-sensitive active variant relies on
  prose, defaults, or ad hoc metadata instead of a valid native manifest.
- `manifest_contract_drift`: the repo contract does not require, validate, or
  Git-track selective manifests.

Every queued quality issue needs evidence about findability. A `NOTES.md`
quality item must also include a rewrite brief with purpose, current claim,
canonical artifacts, trust basis, kill list, and missing evidence.

## Rewrite test

Do not preserve text merely because it already exists. Keep only content that
helps the note answer:

- What is this analysis trying to establish?
- What is the current answer?
- What evidence supports that answer?
- Which analytical variant should I inspect, and why?
- What should I trust, and with what caveat?
- What is the next unresolved decision?

Delete or demote everything else. Process at most one or two large-note
rewrites per repo-maintenance run. Preserve information by rule only in
`AGENTS.md`, where protected environment, security, execution, validation,
infrastructure, and approval requirements still require explicit permission to
change.

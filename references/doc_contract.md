# Project Memory Doc Contract

Use these snippets when setting up or cleaning up a long-lived project.

`doc_contract.md` is an internal reference bundled with the skill. It should
not be copied into the project as another maintained doc type.

## Minimal mode

Default recommendation for the evolving project memory:

- `ANALYSIS_INDEX.md` or equivalent
- `results/.../NOTES.md` or equivalent
- `docs/LESSONS.md` or equivalent

`AGENTS.md` or the repo guide still holds the rules and documentation contract.
Add `docs/pipelines/*.md` only when a shared workflow is too complex to live in
branch notes.

If the workflow also uses personal long-term memory, keep that in an external
workspace rather than adding more repo-local doc types.

On every new or continuing analysis session, review the branch `NOTES.md`,
`ANALYSIS_INDEX.md`, and `docs/LESSONS.md` together. Not every session should
change all three, but unchanged files should stay unchanged by decision after
review, not by omission.

For repo layout and file-placement rules, pair this reference with
`references/repo_structure.md`.

## Memory-aware protocols

- Before analysis work, identify the branch in `ANALYSIS_INDEX.md`, then read
  that branch's `NOTES.md` and the relevant part of `docs/LESSONS.md`.
- Before creating a new directory, note file, or index row, confirm that an
  existing maintained branch does not already cover the work.
- After new information appears, decide which memory layer owns it:
  branch-local detail -> `NOTES.md`; repo-map change -> `ANALYSIS_INDEX.md`;
  durable repo-local heuristic -> `docs/LESSONS.md`; recurring user-specific
  or dialog-derived pattern -> external personal memory.
- Promote `NOTES.md -> docs/LESSONS.md` only when the observation can be
  rewritten as a `Default`, `Check`, `Trap`, or `Preference` without
  branch-specific nouns.
- At closeout, review all three repo layers together and record the result in
  the branch note's `## Cross-document review` section. If personal memory is
  active, record that review too.

## Role summary

- `AGENTS.md` or equivalent: repo-wide operating rules and the documentation
  contract.
- `ANALYSIS_INDEX.md` or equivalent: the map of maintained analyses or
  workstreams.
- `results/.../NOTES.md` or equivalent: the branch-level runbook.
- `docs/LESSONS.md` or equivalent: distilled repo-facing project memory,
  including reusable heuristics, stable repo preferences, and recurring checks
  that should influence future work here.
- `docs/pipelines/*.md` or equivalent: shared workflow mechanics.
- external personal-memory workspace: observations, reflections, and axioms for
  user-specific preferences, troubleshooting strategies, and decision rules
  that should stay outside the repo until a repo-facing mirror is warranted.

If the repo uses `docs/LESSONS.md` (or another established equivalent), treat
that file as the memory document for the project. Do not add a second
`memory.md` unless the repo already uses that naming.

## Valid note archetypes

Do not assume every durable `NOTES.md` is a plain runbook. Common valid
archetypes include:

- branch runbook
- child variant note
- synthesis or staging note
- chronology hub or legacy note

Preserve the archetype that answers the durable question. Add a short scope
statement when the note shape might otherwise confuse future contributors.

## New-project bootstrap order

Use this order when setting up a fresh repo:

1. Put the documentation contract in `AGENTS.md` or the repo guide first.
2. Create `ANALYSIS_INDEX.md` or equivalent as the map of maintained analyses.
3. Create `docs/LESSONS.md` or equivalent as the distilled project memory.
4. Put the `NOTES.md` template in the repo guide so new analyses inherit the
   same structure.
5. Create `docs/pipelines/` only once a workflow is shared, multi-step, or
   expected to live beyond one analysis.
6. If personal long-term memory is part of the workflow, scaffold it outside
   the repo rather than introducing new repo-local memory files.

## Bootstrap guardrails

Do not:

- create placeholder `NOTES.md` files for analyses that do not exist yet
- create a new `NOTES.md` for every sibling variation inside one branch
- create `doc_contract.md` inside the project
- create a separate `memory.md` when `docs/LESSONS.md` (or another equivalent)
  already serves as the project's memory document
- prefill `LESSONS.md` with generic advice or vague personality notes that do
  not change future work
- add multiple overlapping status docs that answer the same question
- turn pipeline docs into branch-specific diaries
- add index rows for cosmetic revisions or minor reruns
- update a branch `NOTES.md` without deciding whether the index, lessons, or
  personal memory also need changes
- copy raw chat transcripts or full dialog exports into the repo

## Suggested repo-guide wording

```md
Treat `ANALYSIS_INDEX.md`, `NOTES.md`, `docs/LESSONS.md`, and
`docs/pipelines/*.md` as a layered documentation system with distinct roles; do
not let them become interchangeable scratchpads.

- `ANALYSIS_INDEX.md` = repo-wide map. It answers: what exists, where it lives,
  which version is current, and what is superseded.
- `results/.../NOTES.md` = branch-level runbook. One maintained analysis
  branch should usually have one parent note file at the shared root. It
  should capture only the minimum durable context needed to rerun, extend, or
  review that branch.
- `docs/LESSONS.md` = distilled repo-facing project memory across analyses,
  including reusable heuristics, stable repo preferences, and recurring checks
  that should shape future work here.
- If this repo does not maintain a separate `memory.md`, treat
  `docs/LESSONS.md` as the memory document and say so explicitly to avoid
  duplicate memory files.
- `docs/pipelines/*.md` = shared pipeline operations, inputs, outputs, rerun
  impact, and validation expectations.
- If an external personal-memory workspace exists, keep it outside the repo and
  mirror only repo-relevant distilled guidance back into `docs/LESSONS.md`.
- Every analysis session should review all three evolving layers together:
  branch `NOTES.md`, `ANALYSIS_INDEX.md`, and `docs/LESSONS.md`.
```

## Suggested analysis-index intro

```md
> This file is the repo-wide map of maintained analyses.
>
> Use it to answer: what exists, where it lives, which version is current, and
> what has been superseded.
>
> Keep interpretation, rerun rationale, troubleshooting notes, and branch-level
> decisions in the relevant `NOTES.md`, not here.
```

Add a rule like this if the index is drifting:

```md
- Do not add a new row for minor reruns, figure revisions, or small parameter
  tweaks inside an existing analysis; those belong in that analysis's
  `NOTES.md` unless the work becomes a distinct maintained branch.
- Keep same-direction variations, parameter sweeps, and sibling `runs/*`
  outputs under the parent branch's `NOTES.md` unless a variation becomes its
  own maintained branch.
```

## Suggested lessons intro

```md
> This file is a short playbook, not a run log.
>
> Keep only lessons that are durable, reusable, and likely to prevent us from
> repeating a mistake across analyses in this repo.
>
> Use `ANALYSIS_INDEX.md` to find the right analysis and `NOTES.md` to
> understand the active branch; use this file only for distilled heuristics
> that should influence future work across runs here.
```

Add durability rules like these when lessons drift into fact collection:

```md
- Before adding to `docs/LESSONS.md`, rewrite the observation as a `Default`,
  `Check`, `Trap`, or `Preference`. If it cannot be phrased that way without
  naming one branch, one figure, or one dataset-specific result, keep it in
  `NOTES.md` instead.
- Keep personal-only or cross-repo-only interaction patterns in the external
  personal-memory workspace until a repo-facing rewrite is warranted.
```

## Suggested notes template

````md
## Status
ACTIVE | FINAL | ARCHIVED — last updated: YYYY-MM-DD

## Note archetype
branch runbook | child variant | synthesis/staging | chronology hub

## Question
[one sentence: what this analysis is trying to answer]

## Branch scope
[one sentence: what variations belong in this file, and what would count as a new branch]

## Variants tracked here
- `[label]`: [what changed, why it exists, and whether it is current / superseded / exploratory]

## Final run
```bash
python scripts/... --arg1 val --arg2 val \
  --input <path> --output <path>
```

## Key decisions
- [decision]: [why this became the active choice]

## Validation
- [what was checked, what passed, and any caveat that still matters]

## Dead ends
1. [what was tried] — [why it was rejected]

## Cross-document review
- `ANALYSIS_INDEX.md`: [updated | no change — why]
- `docs/LESSONS.md`: [updated | no change — why]
- `Personal memory`: [updated | no change — why]

## Open questions / next steps
- [ ] ...
````

## What not to keep

Remove or summarize content when it is mainly:

- chronological chatter
- command-by-command history
- figure-by-figure cosmetic revisions
- branch-specific results that do not generalize
- repeated parameter sweep outcomes that belong in one local note or summary
- copied chat or dialog transcripts that should instead be distilled

## Fast test

Keep a note only if it helps a future contributor answer one of these:

- What should I run?
- What should I trust?
- What should I check first?
- What should I avoid repeating?
- Where is the current version?

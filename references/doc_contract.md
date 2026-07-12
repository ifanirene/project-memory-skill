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

`AGENTS.md` may be maintained, but require explicit user permission before
removing, weakening, or materially rewriting environment paths and versions,
security rules, execution requirements, mandatory validation commands,
infrastructure instructions, or user-authored approval requirements. An
unattended cleanup run must defer such a change rather than infer permission.

## Note shapes

Do not assume every durable `NOTES.md` is a plain runbook. Useful shapes
include:

- branch runbook
- child variant note
- synthesis or staging note
- compact provenance appendix when sequence changes current interpretation

Choose the shape that answers the durable question now. Existing chronology or
legacy structure is not protected. Rewrite it when the current question,
answer, evidence, reproduction path, limitations, or next decision are hard to
find.

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

If the repo needs the minimal scaffold created, prefer the bundled helper
first:

```bash
python "$CODEX_HOME/skills/project-memory/scripts/bootstrap_repo_memory.py" \
  --repo /path/to/repo --audit-only
```

Then scaffold only the missing items after reviewing the report.

## Suggested repo-guide wording

```md
Treat `ANALYSIS_INDEX.md`, `NOTES.md`, `docs/LESSONS.md`, and
`docs/pipelines/*.md` as a layered documentation system with distinct roles; do
not let them become interchangeable scratchpads.

- `ANALYSIS_INDEX.md` = repo-wide map. It answers: what exists, where it lives,
  which version is current, and what is superseded.
- `results/.../NOTES.md` = scientific narrative and branch-level decision
  record. One maintained analysis branch should usually have one parent note.
- `results/.../runs/<variant>/analysis_manifest.json` = exact execution record
  for provenance-sensitive analytical variants. Keep commands, resolved
  parameters, inputs, outputs, code provenance, and validation there.
- Do not require a separate manifest for presentation-only exports when their
  source analytical variant is clear.
- Use the parent note to identify the current and retained variants and explain
  why one is preferred; do not duplicate manifest fields there.
- If script logic changes in a way that changes output semantics, save the new
  behavior under a new script path/name instead of silently reusing the old
  path.
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
- `AGENTS.md` may evolve, but changes to environment paths or versions,
  security rules, execution requirements, mandatory validation commands, and
  approval requirements need explicit user permission tied to the proposed
  change. Preserve those facts during general cleanup.
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
  outputs under one parent branch. Store execution facts in variant manifests
  and scientific comparison in the parent `NOTES.md`.
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
- Before adding to `docs/LESSONS.md`, start the observation with the literal
  prefix `Default:`, `Check:`, `Trap:`, or `Preference:` and state a trigger,
  action, and reason. If it cannot be phrased that way without
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
branch runbook | child variant | synthesis/staging | provenance appendix

## Question
[one sentence: what this analysis is trying to answer]

## Branch scope
[one sentence: what variations belong in this file, and what would count as a new branch]

## Current answer
[the shortest defensible claim supported by the current artifacts]

## Evidence
- [result or validation that directly supports the current answer]

## Analytical variants
- Current: `runs/<variant>/analysis_manifest.json` — [why it is preferred]
- Retained comparison: `runs/<variant>/analysis_manifest.json` — [why it remains useful]
- Manifest decision: [required | not required — presentation-only or transient reason]

## Trust status
[what is validated and what remains uncertain]

## Decisions shaping the current analysis
- [decision and why it changes interpretation or reproduction]

## Limitations
- [caveat that constrains trust or interpretation]

## Next decision
- [the next evidence or choice needed]

## Cross-document review
- `ANALYSIS_INDEX.md`: [updated | no change — why]
- `docs/LESSONS.md`: [updated | no change — why]
- `Personal memory`: [updated | no change — why]

## Provenance appendix
[include only when sequence itself is needed to understand the current state]
````

Rewrite these sections as one coherent current narrative instead of appending a
dated section. Use the rewrite brief and kill-list protocol in
`references/memory_quality.md`; keep a compact provenance appendix only when
sequence itself changes interpretation.

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

- Which result should I trust or prefer?
- What should I trust?
- What should I check first?
- What should I avoid repeating?
- Where is the current version?

For a provenance-sensitive variant, make sure its manifest answers:

- Which exact command produced this output?
- Which exact inputs did that command use?
- Which resolved parameters produced it?

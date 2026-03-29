---
name: project-memory
description: Use when a user wants to scaffold or clean up the durable memory
  and repo-organization system for a long-lived project, especially to define
  clear roles for repo rules, an analysis index, branch notes, reusable
  lessons, shared pipeline docs, predictable file placement, and an optional
  external personal-memory bridge.
---

# Project Memory

Use this skill to set up or repair a repo's long-term memory and organization
system so documentation stays useful, new files have an obvious home, and
durable lessons can be promoted without turning the repo into a chat archive.

IMPORTANT: System and user instructions always take precedence.

`references/doc_contract.md` is an internal reference bundled with this skill.
It is not a project file to create or maintain.

## Core contract

- Repo guide (`AGENTS.md` or equivalent): global rules and the documentation
  contract.
- Analysis index (`ANALYSIS_INDEX.md` or equivalent): repo-wide map of
  maintained analyses or workstreams.
- Per-analysis notes (`results/.../NOTES.md` or equivalent): the branch-level
  runbook for rerunning, extending, and validating one maintained direction of
  work.
- Lessons (`docs/LESSONS.md` or equivalent): distilled repo-facing heuristics
  that should change future work in this repo.
- Pipeline docs (`docs/pipelines/*.md` or equivalent): reusable workflow
  contracts for shared or long-lived pipelines.
- Repo structure: clear, durable placement rules for code, inputs, outputs, and
  generated artifacts so future files go to the right place by default.
- Optional external personal-memory workspace: distilled user-specific
  preferences, troubleshooting strategies, accepted or rejected solution
  patterns, and decision rules kept outside the repo.

When the repo uses `docs/LESSONS.md` (or another existing equivalent) for
distilled cross-run memory, treat that file as the repo's memory document. Do
not add a separate `memory.md` unless the repo already uses that naming.

If the repo uses different filenames, preserve local naming but keep the same
responsibilities.

If an external personal-memory workspace is configured, keep it outside the
repo and route only distilled, repo-relevant mirrors back into repo docs.

## Repo organization contract

The skill should also make the repo structure predictable enough that a future
contributor can answer "where should this file go?" without guessing.

Prefer a small number of durable homes:

- code and CLIs: one home such as `scripts/` or `src/`
- raw/reference inputs: `data/` or another clearly named input area
- branch outputs: `results/<branch-root>/...`
- branch variants: `results/<branch-root>/runs/<variant>/...`
- reusable docs: `docs/`

Avoid:

- new top-level dumping-ground folders
- splitting the same kind of artifact across multiple roots without a strong
  reason
- saving active analysis figures into a global curation folder
- hiding branch outputs outside the branch root that owns them

## Minimal mode

Keep the repo memory system minimal. In most long-lived analysis repos, the
core evolving docs should be:

1. `ANALYSIS_INDEX.md` or equivalent: repo-wide map of maintained branches.
2. `results/.../NOTES.md` or equivalent: branch-level runbooks.
3. `docs/LESSONS.md` or equivalent: distilled repo-facing defaults, checks,
   traps, and preferences that should shape future work here.

`AGENTS.md` or the repo guide still holds the rules and documentation contract,
but avoid adding more evolving doc layers unless they solve a real maintenance
problem. Only add `docs/pipelines/*.md` when a shared workflow is complex
enough that branch notes are no longer the right place for operating
instructions.

## Workflow

1. Inspect the existing repo docs and naming conventions.
2. Inspect top-level structure and current file-placement patterns.
3. Decide whether the repo needs new files or clearer role statements in the
   files it already has.
   - For a new repo, scaffold the contract early instead of waiting until the
     docs have already drifted.
   - Start from the minimal 3-file mode; add extra doc types only when they
     solve a real maintenance problem.
4. Write the documentation and placement contract into the repo guide first.
5. Make each long-lived doc answer one question:
   - index: what exists and where
   - notes: how to rerun or extend this analysis
   - lessons: what future work should do differently in this repo
   - pipeline docs: how a shared workflow operates
6. Make each directory answer one question:
   - where code lives
   - where inputs live
   - where branch outputs live
   - where branch variants live
   - where durable docs live
7. Tighten templates so they pull toward concise, durable content.
8. Prune low-value text:
   - remove chronological chatter
   - move branch-specific outcomes out of lessons
   - keep minor reruns out of the index
   - keep same-direction variants inside one parent note file
   - avoid command dumps unless they are the final reproducible run
9. On every new or continuing analysis session, review the branch `NOTES.md`,
   `ANALYSIS_INDEX.md`, and `docs/LESSONS.md` together before deciding what to
   update. Not every session should change all three files, but leaving the
   index or lessons unchanged should be a deliberate decision after review, not
   an omission.
10. When a branch `NOTES.md` is created or updated, add a short
    `Cross-document review` section that records whether
    `ANALYSIS_INDEX.md` changed, whether `docs/LESSONS.md` changed, and whether
    personal memory changed; if not, note briefly why no change was needed.
11. If an external personal-memory workspace is configured, capture only
    distilled candidate signals there; do not duplicate repo docs or raw chat.
12. Cross-link the docs so a future reader knows where to go next.
13. When you need copy-ready wording or templates, read
    `references/doc_contract.md`, `references/repo_structure.md`,
    `references/personal_memory_bridge.md`, and
    `references/scheduled_loops.md`.

## Note archetypes

Not every valid `NOTES.md` file is the same shape. Preserve the archetype that
answers the durable question:

- branch runbook: the main rerun or extension guide for one maintained branch
- child variant note: a subordinate note for a focused sidecar or parameter
  family that still belongs under a parent branch of record
- synthesis or staging note: a durable note for manuscript assembly, figure
  staging, or other cross-branch synthesis
- chronology hub or legacy note: a durable note that explains lineage,
  provenance, or historical organization when a branch cannot yet be reduced to
  a pure runbook

Do not flatten valid synthesis or chronology notes into the runbook template
unless that clearly improves maintainability.

## Promotion ladder

Use explicit promotion paths instead of copying raw context forward:

- `NOTES.md -> docs/LESSONS.md`: promote only when a branch-local observation
  can be rewritten as a durable `Default`, `Check`, `Trap`, or `Preference`
  without branch-specific nouns.
- `NOTES.md`, `docs/LESSONS.md`, explicit user corrections, and Codex dialogs
  -> external `OBSERVATIONS.md`
- `OBSERVATIONS.md -> REFLECTIONS.md`: after 2 independent recurrences across
  separate sessions, branch roots, or repos
- `REFLECTIONS.md -> AXIOMS.md`: after 3 confirmations plus 28-day stability or
  explicit user endorsement
- `AXIOMS.md -> docs/LESSONS.md`: only when the axiom is repo-relevant and can
  be rewritten in repo-facing language

Distill; do not copy raw dialog transcripts or full chat histories into repo
docs or the external memory workspace.

## Memory-aware protocols

Use these operating habits whenever analysis work touches long-lived memory:

- Before acting, identify the maintained branch from `ANALYSIS_INDEX.md` and
  open the branch `NOTES.md` plus the relevant section of `docs/LESSONS.md`.
- Before proposing a new output directory, new note file, or new index row,
  confirm that the work is not already covered by an existing maintained
  branch.
- After a meaningful run or decision, decide explicitly which layer it belongs
  in:
  - branch-specific rerun, validation, or variant detail -> `NOTES.md`
  - repo map, branch status, or maintained location change ->
    `ANALYSIS_INDEX.md`
  - durable repo-local heuristic, trap, preference, or reusable check ->
    `docs/LESSONS.md`
  - recurring user preference, troubleshooting strategy, accepted or rejected
    solution pattern, or dialog-derived interaction preference -> external
    `OBSERVATIONS.md`
- At closeout, update the branch `NOTES.md` if the branch changed, then review
  `ANALYSIS_INDEX.md`, `docs/LESSONS.md`, and personal memory and record the
  result in `## Cross-document review`.
- If the index, lessons, or personal memory stay unchanged, record a short
  no-change reason so future readers know the omission was intentional.

## External personal-memory bridge

When an external workspace is configured, keep it outside the repo and use it
for:

- `OBSERVATIONS.md`: append-only candidate signals with provenance
- `REFLECTIONS.md`: deduplicated recurring patterns
- `AXIOMS.md`: stable preferences, troubleshooting strategies, and decision
  rules
- mirrors: repo-facing rewrite candidates for `docs/LESSONS.md`

Store source pointers and distilled extracts from Codex dialogs; do not mirror
full session JSONL files. Process only new or updated dialog or repo signals
after the first bootstrap run. Treat non-main worktrees as provisional sources
until merged or independently repeated.

## Scheduled maintenance

When pairing this skill with automation, prefer three non-overlapping loops:

- daily signal distillation: read only new repo or dialog signals, update
  manifests, extracts, observations, cursor state, repo-maintenance queue
  entries, and a daily log
- weekly repo-memory maintenance: consume the queue plus unresolved gaps,
  update repo docs in canonical main worktrees, apply repo-local
  `NOTES.md -> docs/LESSONS.md` promotions, and complete `## Cross-document
  review`
- monthly axiom review: run on a weekly schedule with a 28-day gate if needed,
  promote observations into reflections and axioms, update repo mirror
  candidates, and write a monthly log

Keep loop ownership explicit:

- the daily loop should not update reflections, axioms, or repo mirrors
- the weekly loop should not update reflections or axioms
- the monthly loop should not edit repo docs directly

Start weekly auto-edits in a bounded validation phase on representative fixture
notes before widening to full coverage. During validation, defer non-scope
items instead of silently expanding the edit surface.

## New-project bootstrap

When the repo is new or only lightly structured, prefer this order:

1. Add the documentation contract to `AGENTS.md` or the repo guide.
2. Define the top-level structure for code, inputs, outputs, and docs before
   generated files start accumulating.
3. Create `ANALYSIS_INDEX.md` (or equivalent) as the repo-wide map.
4. Create `docs/LESSONS.md` (or equivalent) as the distilled project memory.
5. Add the `NOTES.md` template to the repo guide so each analysis gets the same
   runbook shape when it appears.
6. Create `docs/pipelines/` only when a workflow is shared, multi-step, or
   likely to be reused across analyses.
7. If an external personal-memory workspace is part of the workflow, scaffold
   it outside the repo rather than adding repo-local memory docs.

Do not over-scaffold:

- do not create placeholder `NOTES.md` files for analyses that do not exist yet
- do not create a new `NOTES.md` for every sibling variation under one branch
- do not create `doc_contract.md` inside the project; it is a skill reference
- do not create a separate `memory.md` when `docs/LESSONS.md` (or another
  equivalent file) already serves as the repo's memory document
- do not prefill `LESSONS.md` with generic advice that teaches nothing or with
  vague personality notes that will not change future decisions
- do not create multiple overlapping status docs that answer the same question
- do not let pipeline docs become branch diaries
- do not create new top-level folders for one-off outputs when an existing
  branch root or artifact class already has a clear home
- do not create raw-dialog archives inside the repo
- do not promote one-off user comments or one-session troubleshooting details
  directly into lessons or axioms

## Quality bar

- Prefer a layered system, not interchangeable scratchpads.
- Prefer the smallest durable system that works; fewer maintained file types is
  better when the repo can stay organized without extra layers.
- A future generated file should have one obvious home.
- Put a short scope statement near the top of each long-lived doc.
- Keep notes minimal but sufficient to rerun and trust the analysis.
- Keep one parent `NOTES.md` per maintained branch unless a child variation
  truly becomes its own branch of record.
- Require an explicit review decision for the other long-lived docs whenever a
  branch note is updated: `ANALYSIS_INDEX.md` should be reviewed for map-status
  changes, `docs/LESSONS.md` for durable repo heuristics, and personal memory
  for reusable user-specific patterns.
- Keep lessons focused on distilled repo-facing wisdom: recurring heuristics,
  recurring traps, stable repo preferences, and checks that should change
  future work here.
- Rewrite lessons in a durable form such as `Default`, `Check`, `Trap`, or
  `Preference`; if an observation cannot survive that rewrite, it belongs in
  notes or personal memory instead.
- Keep personal memory distilled: source pointers and extracts are fine, raw
  dialogs are not.
- Keep automated maintenance incremental and logged: process only new or
  updated signals after bootstrap and write a decision log every run.

## Content test

Keep content only if it helps a future contributor answer at least one of:

- What should I run?
- What should I trust?
- What should I check first?
- What should I avoid repeating?
- Where does the current version live?

If it does not answer one of those, it probably does not belong in a long-lived
repo memory document.

## Common repairs

- Add explicit document-role statements when people cannot tell where updates
  belong.
- Add `Question` and `Validation` to per-analysis notes when notes drift toward
  diary entries.
- Add an explicit "do not add a new index row for minor reruns" rule when the
  index is bloating.
- Add a short `Cross-document review` section to the `NOTES.md` template when
  sessions are updating branch notes but skipping the index, lessons, or
  personal memory without saying whether that was intentional.
- Collapse sibling variation notes into one branch-level runbook when one
  direction has splintered across many `NOTES.md` files.
- Rewrite the lessons intro so run-specific details go back to notes.
- Add explicit placement rules when people keep asking where new outputs,
  figures, or generated tables should go.
- Add an explicit "this repo's memory document is `docs/LESSONS.md`" line when
  agents might otherwise invent a second memory file.
- Backfill missing local `NOTES.md` files for indexed active analyses before
  polishing legacy archived branches.
- Move shared workflow mechanics from notes into pipeline docs.
- Separate repo-facing lessons from personal-only memory when
  `docs/LESSONS.md` has become a dumping ground for user-specific patterns that
  should live outside the repo.
- Add note-archetype labels or scope statements when valid synthesis or
  chronology notes keep being mistaken for broken runbooks.

## Reference

- `references/doc_contract.md`: copy-ready scope statements, rules, and note
  templates for new projects
- `references/repo_structure.md`: copy-ready repo structure and placement rules
- `references/personal_memory_bridge.md`: shareable guidance for the optional
  external personal-memory workspace and promotion ladder
- `references/scheduled_loops.md`: shareable guidance for incremental daily,
  weekly, and monthly memory-maintenance automations

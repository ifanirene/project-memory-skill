---
name: project-memory
description: Use when a user wants to scaffold or clean up the durable memory
  and repo-organization system for a long-lived project, especially to define
  clear roles for repo rules, an analysis index, branch notes, reusable
  lessons, selective analysis manifests, shared pipeline docs, new-repo
  computational-biology structure, monitored-repo drift repair, and an
  optional external personal-memory bridge.
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
  scientific narrative, variant comparison, and decision record.
- Analysis manifests (`results/.../runs/<variant>/analysis_manifest.json`):
  machine-readable execution provenance for complex or repeatedly tailored
  analytical variants; do not require them for presentation-only outputs.
- Lessons (`docs/LESSONS.md` or equivalent): distilled repo-facing heuristics
  that should change future work in this repo.
- Pipeline docs (`docs/pipelines/*.md` or equivalent): reusable workflow
  contracts for shared or long-lived pipelines.
- Repo structure: clear, durable placement rules for code, inputs, outputs, and
  generated artifacts so future files go to the right place by default.
- Optional external personal-memory workspace: distilled user-specific
  preferences, troubleshooting strategies, accepted or rejected solution
  patterns, and decision rules kept outside the repo.

Allow `AGENTS.md` to evolve, but require explicit user permission before
removing, weakening, or materially rewriting protected information:
environment names, paths, versions, or activation commands; security rules;
execution requirements; mandatory validation commands; infrastructure
instructions; and user-authored approval requirements. An unattended cleanup
run must defer such a change. General permission to clean up documentation is
not sufficient.

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
- branch outputs: `results/<theme>/<branch-root>/...` when the repo groups work
  by theme, otherwise `results/<branch-root>/...`
- branch variants: `results/<theme>/<branch-root>/runs/<variant>/...` when the
  repo groups work by theme, otherwise `results/<branch-root>/runs/<variant>/...`
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
instructions. Conditional `analysis_manifest.json` files are execution records,
not another narrative documentation layer.

## Bootstrap helper

This skill ships a conservative bootstrap/audit helper at
`scripts/bootstrap_repo_memory.py`.

Run it with `--mode new` to scaffold an expandable computational-biology
workspace or `--mode monitored --audit-only` to report contract drift without
reorganizing an established repo. `--mode auto` treats any existing core memory
file as evidence that the repo is monitored.

- repo guide: `AGENTS.md`
- repo map: `ANALYSIS_INDEX.md`
- lessons: `docs/LESSONS.md`
- pipeline-doc home: `docs/pipelines/` in new-repo mode
- code home: `scripts/` or `src/`
- input home: `data/`
- output home: `results/`
- durable docs home: `docs/`

In new-repo mode, also create common homes under `config/`, `data/`, `scripts/`,
`notebooks/`, and `tests/`, and create a `.gitignore` that tracks notes and
manifests while ignoring data and generated outputs. In monitored mode, report
manifest and contract drift and make only missing-core scaffold actions.

The helper must:

- report what is already present
- create only missing core files/directories
- never rewrite existing files
- flag plausible noncanonical equivalents for manual review instead of blindly
  creating duplicates
- avoid placeholder goal, analysis, variant, or `NOTES.md` files

Default behavior is prompting mode before writes. Use `--audit-only` for a
read-only report and `--yes` for noninteractive scaffolding. Read
`references/repo_modes.md` before applying a setup or drift repair.

## Workflow

1. Classify the repo as new or monitored. Read `references/repo_modes.md`.
2. Inspect the existing repo docs, naming conventions, and file placement.
3. For a new repo, create the expandable computational-biology structure and
   list its tree in `AGENTS.md`. For a monitored repo, detect global contract
   drift and repair the smallest governing rule before touching branch docs.
4. Write the documentation and placement contract into the repo guide first.
   Preserve protected `AGENTS.md` information unless the user explicitly
   approves the exact change.
5. Make each record answer one question:
   - index: what exists and where
   - notes: what the analysis currently means and which variant is preferred
   - manifest: exactly what execution produced one analytical variant
   - lessons: what future work should do differently in this repo
   - pipeline docs: how a shared workflow operates
6. Make each directory answer one question:
   - where code lives
   - where inputs live
   - where branch outputs live
   - where branch variants live
   - where durable docs live
7. Tighten templates so they pull toward concise, durable content.
8. Apply the selective manifest rule in `references/analysis_manifest.md`.
   Require a native manifest for new provenance-sensitive runs; do not require
   one for purely decorative outputs. Validate manifests with
   `scripts/validate_analysis_manifest.py`.
9. Prune low-value text:
   - remove chronological chatter
   - move branch-specific outcomes out of lessons
   - keep minor reruns out of the index
   - keep same-direction variants inside one parent note file
   - move commands, resolved parameters, input inventories, and artifact lists
     into required manifests instead of duplicating them in notes
10. On every new or continuing analysis session, review the branch `NOTES.md`,
   `ANALYSIS_INDEX.md`, and `docs/LESSONS.md` together before deciding what to
   update. Not every session should change all three files, but leaving the
   index or lessons unchanged should be a deliberate decision after review, not
   an omission.
11. When a branch `NOTES.md` is created or updated, add a short
    `Cross-document review` section that records whether
    `ANALYSIS_INDEX.md` changed, whether `docs/LESSONS.md` changed, and whether
    personal memory changed; if not, note briefly why no change was needed.
12. If an external personal-memory workspace is configured, capture only
    distilled candidate signals there; do not duplicate repo docs or raw chat.
13. Cross-link the records so a future reader knows where to go next.
14. When you need copy-ready wording or templates, read
    `references/doc_contract.md`, `references/repo_structure.md`,
    `references/personal_memory_bridge.md`, and
    `references/scheduled_loops.md`.
15. When a repo is missing the minimal skeleton, prefer running
    `scripts/bootstrap_repo_memory.py --repo <path> --audit-only` first, then
    scaffold only the missing pieces if the report is clean.

## Note archetypes

Not every valid `NOTES.md` file is the same shape. Choose the shape that best
answers the durable question now:

- branch runbook: the main rerun or extension guide for one maintained branch
- child variant note: a subordinate note for a focused sidecar or parameter
  family that still belongs under a parent branch of record
- synthesis or staging note: a durable note for manuscript assembly, figure
  staging, or other cross-branch synthesis
- provenance appendix: a compact exception used only when sequence itself
  changes the interpretation of the current result

Do not preserve an archetype merely because the file already uses it. Rewrite
chronology and legacy logs into the current question, claim, evidence,
reproduction, limitations, and next decision. Keep a provenance appendix only
when the sequence is necessary to understand the current state.

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

Use two maintenance layers:

- weekly: one central collector reads changed memory docs from all registered
  repos, asks an LLM for a structured semantic proposal, and uses
  `scripts/memoryctl.py` to validate and apply observations, cursors, and queue
  state; later repo-local maintenance runs may edit only their own repo docs
- monthly: collect new dialog signals, compare cross-repo observations, promote
  reflections and axioms, and prepare repo mirror proposals without editing
  repos directly

Within the weekly collector, reserve a bounded round-robin sample of unchanged
legacy `NOTES.md` and `docs/LESSONS.md` files. Use it to create source-backed
quality items even when no recent edit triggered collection. Keep Phase B
bounded to one or two large-note rewrites per run and require a narrative
rewrite brief before chronology is removed or merged.

Do not duplicate one cross-repo job across monitored repos. Run the collector
once from the external workspace with read-only access to monitored repos and
write access only to its own state.

When the user asks whether maintenance is genuinely functional, run a live
maintenance test. Use the production collector, perform semantic review, apply
real collector state, make only genuine repo-memory repairs, and leave the repo
diff uncommitted for inspection. Do not create synthetic lessons or restore the
changes afterward. Read `references/live_maintenance_test.md` and follow its
protocol.

Use the following command only for a controller safety smoke check:

```bash
python "$CODEX_HOME/skills/project-memory/scripts/smoke_test_project_memory.py" \
  --repo /path/to/project
```

The smoke harness restores its controlled writes and uses temporary collector
state. Never present it as proof that semantic maintenance produced useful
project changes.

Keep the semantic and deterministic responsibilities separate:

- LLM: summarize, generalize, classify, compare semantically, and propose
- controller: discover changed files, bound inputs, lock runs, validate schema
  and provenance, enforce path and permission rules, update cursors, manage
  queue lifecycle, and write atomically

The weekly collector must not edit monitored repos. Repo-local maintenance must
claim and resolve or defer its own queue items instead of leaving completed
items permanently open. Any proposed protected `AGENTS.md` change without
explicit permission must be deferred.

Start repo-local auto-edits in a bounded validation phase. Require consecutive
successful runs without protected-information regression, duplicate execution, or
stale queue recurrence before widening coverage. Read
`references/scheduled_loops.md` for the full protocol.

## Repository modes

- New: scaffold the common computational-biology homes and contract, but do not
  invent goal or analysis branches.
- Monitored: preserve established scientific organization, audit drift, repair
  governing contracts, and migrate active branches incrementally. Do not apply
  the new-repo tree wholesale or fabricate historical manifests.

Read `references/repo_modes.md` for the complete behavior.

## Quality bar

- Prefer a layered system, not interchangeable scratchpads.
- Prefer the smallest durable system that works; fewer maintained file types is
  better when the repo can stay organized without extra layers.
- A future generated file should have one obvious home.
- Put a short scope statement near the top of each long-lived doc.
- Keep notes minimal but sufficient to understand and trust the analysis.
- Keep one parent `NOTES.md` per maintained branch unless a child variation
  truly becomes its own branch of record.
- For every provenance-sensitive analytical variant, write a valid
  `analysis_manifest.json` in its own meaningfully named output directory.
- Do not require manifests for presentation-only variants. Link them to their
  source analytical variant instead.
- Keep execution facts in manifests and scientific comparison, current choice,
  and limitations in the parent note. Do not maintain two copies.
- Prefer flat variant output directories: for most runs, save outputs directly
  inside `<variant>/` instead of splitting them into artifact-type subfolders.
- If script logic changes in a way that can change output semantics, save the
  new behavior under a new script path/name rather than silently reusing the
  old path.
- Require an explicit review decision for the other long-lived docs whenever a
  branch note is updated: `ANALYSIS_INDEX.md` should be reviewed for map-status
  changes, `docs/LESSONS.md` for durable repo heuristics, and personal memory
  for reusable user-specific patterns.
- Keep lessons focused on distilled repo-facing wisdom: recurring heuristics,
  recurring traps, stable repo preferences, and checks that should change
  future work here.
- Update runbook current-state sections instead of appending a dated update by
  default. Keep history only for result-changing decisions, supersession,
  indispensable lineage, or provenance gaps.
- Start every new or rewritten lesson with the literal prefix `Default:`,
  `Check:`, `Trap:`, or `Preference:` and include a trigger, action, and reason.
  Keep dates and source branches as optional provenance, not structure.
- Treat line count and dated sections as review triggers, not automatic cleanup
  decisions. For a substantial `NOTES.md` rewrite, use `paper-narrative` when
  available: derive the brief, choose the claim-and-evidence arc, identify
  missing evidence, and delete material on the kill list. Read
  `references/memory_quality.md` for the full protocol.
- Keep personal memory distilled: source pointers and extracts are fine, raw
  dialogs are not.
- Keep automated maintenance incremental and logged: prioritize new or updated
  signals, reserve only a small bounded share for round-robin legacy quality
  review, and write a decision log every run.

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
- Add the selective manifest contract when complex variants rely on note prose,
  script defaults, or ad hoc metadata files for provenance.
- Add a Git ignore exception when manifests under generated output roots are
  not trackable.
- Add a semantic script-versioning rule when reruns are no longer attributable
  to one stable script path.
- Add an explicit "this repo's memory document is `docs/LESSONS.md`" line when
  agents might otherwise invent a second memory file.
- Backfill missing local `NOTES.md` files for indexed active analyses before
  polishing legacy archived branches.
- Move shared workflow mechanics from notes into pipeline docs.
- Separate repo-facing lessons from personal-only memory when
  `docs/LESSONS.md` has become a dumping ground for user-specific patterns that
  should live outside the repo.
- Rewrite chronology-heavy notes around the current question, claim, evidence,
  reproduction path, limitations, and next decision; keep only a compact
  provenance appendix when sequence itself matters.

## Reference

- `references/doc_contract.md`: copy-ready scope statements, rules, and note
  templates for new projects
- `references/repo_structure.md`: copy-ready repo structure and placement rules
- `references/repo_modes.md`: distinct new-repo setup and monitored-repo drift
  repair workflows
- `references/analysis_manifest.md`: manifest decision rule, schema, storage,
  Git tracking, and legacy migration
- `references/personal_memory_bridge.md`: shareable guidance for the optional
  external personal-memory workspace and promotion ladder
- `references/live_maintenance_test.md`: real production collector and
  inspectable repo-diff test protocol
- `references/memory_quality.md`: current-state runbooks, typed lesson syntax,
  quality issue types, and narrative-first rewriting
- `references/scheduled_loops.md`: two-layer weekly/monthly automation,
  controller boundaries, protected-info rules, and queue lifecycle

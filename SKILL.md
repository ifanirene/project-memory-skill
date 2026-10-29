---
name: project-memory
description: Maintain project notes, provenance and lessons; preserve attributed decisions and distill personal judgment through configured memory loops.
metadata:
  version: "0.2.0"
---

# Project Memory

Maintain a small documentation system that tells a future contributor what
exists, what to trust, what to check, and where the current version lives.
Use the repository's existing filenames, organization, and instructions.

Also preserve why consequential choices changed. Project continuity and personal
judgment are different outcomes: a successful documentation audit does not prove
that the system remembers the investigator's reasoning.

## Writing style

Use ASD-STE100 style for `NOTES.md` and scheduled-job reports: simple words,
active voice, consistent terms, and one main idea per sentence. Aim for no more
than 20 words per instruction and 25 words per descriptive sentence. Preserve
scientific terms, exact commands, numbers, attribution, and uncertainty. This
is style guidance; do not claim formal compliance with the STE dictionary.

Start notes with the current answer. Keep evidence, limits, and the next decision
easy to find. Remove repeated summaries and dated task narration. Keep unique
execution facts until a supported manifest owns them.

For scheduled runs, keep the reader summary and narrative run log short. Use
100–150 words for daily summaries and 200–300 for weekly summaries as defaults.
If nothing changed, use a few lines. State the outcome, one useful finding when
present, coverage gaps, and the next action. Preserve required coverage counts
and meaningful validation failures. Put detailed receipts and inventories in
linked artifacts; length limits never justify losing evidence or hiding errors.

## Boundaries

Allow `AGENTS.md` to evolve, but require explicit user permission before
removing, weakening, or materially rewriting protected information:
environment names, paths, versions, or activation commands; security rules;
execution requirements; mandatory validation commands; infrastructure
instructions; and user-authored approval requirements. An unattended cleanup
run must defer such a change. General permission to clean up documentation is
not sufficient.

Preserve unrelated edits and established output locations. Audit findings, note
length, and dated headings are review triggers, not automatic repair decisions.
Never invent historical commands, hashes, results, or manifests to satisfy a
validator. Keep private and cross-repo memory outside the repository; updating
that memory requires authorization under the user's memory policy.

## Document roles

- Repo guide: rules and placement contract.
- Analysis index: maintained branches, locations, and status.
- Branch notes: current question, answer, evidence, variants, limitations, and
  next decision, plus consequential choices and their attribution. Keep one parent
  per direction unless a child has its own scope.
- Analysis manifest: exact execution provenance for a meaningful analytical variant.
- Lessons: reusable repo-facing heuristics. Use the existing lessons document;
  do not introduce a parallel `memory.md`.
- Pipeline docs: shared workflow mechanics when branch notes no longer suffice.

Keep execution facts in manifests and scientific interpretation in notes.
Preserve irreducible legacy provenance until a supported replacement exists.
Index changes follow branch, status, or location changes; minor reruns and figure
polish do not need new rows. Lessons use `Default:`, `Check:`, `Trap:`, or
`Preference:` with a trigger, action, and reason.

For an actual tradeoff, correction, rejected approach, or changed judgment,
keep a compact decision record in the owning note: context; alternatives;
choice; reason and accepted cost; who chose; source/date; scope; unresolved
evidence; and what it supersedes. Distinguish direct user choice, agent proposal,
accepted implementation, and scientific observation. Do not infer a personal
preference from agent compliance or silence. Preserve decision-changing history
during cleanup, including exceptions; do not create empty records for routine work.

Local lessons and personal principles have different scopes. Keep concrete repo
checks in lessons and broader reasoning in the principle library. Record material
principle use in the owning note and briefly identify its ID, changed choice, and
observed outcome in the task handoff. Retrieval alone is not evidence of benefit.

## Choose the operation

- **Setup or structural drift repair:** read
  [repo_modes.md](references/repo_modes.md). Inspect current docs and run
  `scripts/bootstrap_repo_memory.py --repo <path> --mode monitored --audit-only`
  for an established repo. New-repo mode scaffolds missing homes without inventing
  scientific branches. Use `--yes` only for scaffolding already authorized by the
  task. Inspect flagged equivalents before creating duplicate files. When code/output
  ownership or analysis relationships are unclear, use the ownership-repair section
  of [repo_structure.md](references/repo_structure.md).
- **Note or lesson maintenance:** read the relevant index entry, branch note, and
  matching lessons. For substantial narrative rewrites, read
  [memory_quality.md](references/memory_quality.md); derive a brief and kill list
  using `paper-narrative` when available. Preserve evidence and result-changing
  history. A local typo correction needs only local context.
- **Analytical variants or manifest repair:** read
  [analysis_manifest.md](references/analysis_manifest.md). Use manifests for
  provenance-sensitive runs, not source-identifiable presentation-only changes.
  Validate new or changed manifests with
  `scripts/validate_analysis_manifest.py --repo <path>`. For a new or changed
  maintained result, also run its bounded `--verify-files` check on the specific
  manifest. Inspect drift, missing files and unchecked dependencies; schema
  validity alone does not establish fidelity. Preserve executed code (including
  dirty changes), stable inputs, environment identity and output-to-method links.
  State what cannot be recovered; never update historical hashes to today's files.
  A change to script output
  semantics requires a new script path/name. Prefer flat, meaningfully named
  variant directories under the owning branch.
- **Templates or placement rules:** read only the needed parts of
  [doc_contract.md](references/doc_contract.md) or
  [repo_structure.md](references/repo_structure.md). These are bundled references,
  not extra documents to copy wholesale into every project.
- **Authorized external-memory work:** read
  [personal_memory_bridge.md](references/personal_memory_bridge.md) for promotion,
  provenance, and mirror rules. Distill rather than copying raw dialog histories.
- **Use working principles:** read the configured memory workspace's
  `principles/INDEX.md`, then only the entries relevant to the current decision.
  Retrieve selected IDs with `scripts/principle_library.py task-context --workspace
  <root> --ids X01 X02`. It checks the current linked evidence before returning
  complete documents. Select none when the library does not help.
  For new or revised entries, follow the [principle format](templates/PRINCIPLE.md)
  and the [library guidance](references/decision_memory.md#working-principle-library).
- **Personal trajectory, missing axioms, or decision distillation:** also read
  [decision_memory.md](references/decision_memory.md). Use the separate decision
  collector and ledger; document-maintenance queue counts are not learning metrics.
- **Scheduled collection or queue maintenance:** read
  [scheduled_loops.md](references/scheduled_loops.md). The central collector reads
  monitored repos and writes only its own state. Repo-local maintenance owns its
  queue claims and closes them as resolved, deferred, or rejected. Keep scope
  bounded; preserve the protected-information approval boundary.
- **Install or reproduce personal memory:** use
  [personal_memory_workflows.md](references/personal_memory_workflows.md) and
  `scripts/principle_library.py setup`. The skill owns the procedure; generated
  schedule prompts contain only paths and an operation. Rebuild the index from
  authored documents; never repair a generated view by hand. Test a fresh workspace
  when changing collection, review, or task retrieval behavior.
- **A request to prove maintenance works:** read
  [live_maintenance_test.md](references/live_maintenance_test.md). Distinguish a
  production semantic-maintenance test from the reversible controller smoke check
  in `scripts/smoke_test_project_memory.py`; the latter proves only mechanics.
- **A change to personal collection, principle review, or task retrieval:** run
  relevant regression checks and the bounded
  [live personal-memory test](references/live_personal_memory_test.md). Trace real
  dialogue through semantic distillation and a supported principle to an actual
  task action. Do not report the full chain as working from fixture tests,
  configuration readback, or retrieval alone. Fix defects in this shared skill.

## Completion

Finish the authorized repair, check changed links and relevant validators, and
report remaining evidence gaps. When a branch note changes substantively, include
`## Cross-document review` with decisions about the index, lessons, and external
memory, including deliberate no-change reasons. A typo-only correction needs no
new review section unless the repository requires one. Review other layers for actual
impact; do not rewrite them merely to make every file change.

No repo cleanup by itself demonstrates that external collection, scheduled jobs,
or scientific results are correct. Report exactly which operation was executed
and what its checks establish.

For personal-memory work, report source coverage, unavailable sources, backlog,
attribution, independent decision episodes, counterexamples, and one concrete
future decision the memory would change. Zero axioms can be correct; zero signals
requires explaining what was reviewed and why it contains no personal judgment.

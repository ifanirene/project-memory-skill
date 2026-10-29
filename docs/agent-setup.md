# Set up Project Memory with your agent

This guide is for the agent helping a user adopt the skill. Start with one existing repository and make one real workstream easy to resume. Project documentation, private personal memory, and scheduled upkeep are separate choices.

## Install the complete skill

Use an agent that can read and edit local files and run Python 3.10 or later. The Python helpers use the standard library, and collection and file locking require a POSIX host such as macOS or Linux. Dialogue intake reads local Codex and Claude Code session files; do not assume access to cloud-only history.

Reuse an existing installation when present. Otherwise, clone a fixed release of
the maintained source repository:

```sh
git clone --branch v0.2.0 --depth 1 https://github.com/ifanirene/project-memory-skill.git /path/to/project-memory-skill
python3 /path/to/project-memory-skill/scripts/install.py
```

The installer copies the complete runtime package and its usage documentation.
It uses only Python's standard library and creates no memory state or schedules.
Codex uses `$CODEX_HOME/skills/project-memory`, or `~/.codex/skills/project-memory`
when `CODEX_HOME` is unset. The skill is available on the next turn.

Choose another full destination path with `--dest`. For example, for Claude Code:

```sh
python3 /path/to/project-memory-skill/scripts/install.py \
  --dest "$HOME/.claude/skills/project-memory"
```

The installer refuses to overwrite any existing destination, including a symlink.
For upgrades, compare and reconcile local fixes first. Move the existing
installation to a backup location, then install into its original path. Keep
private memory outside both the source checkout and the installed package.
Check `VERSION` in the installed directory to identify the release. See the
[release policy](releases.md) for version numbers and the preserved baseline.

Other agents can consume `SKILL.md` directly or through their own skill layout,
though native integration is not guaranteed for every host. Keep bundled
directories together, and read [SKILL.md](../SKILL.md) before modifying a project.

Verify that both helper entrypoints run:

```sh
skill_dir="${CODEX_HOME:-$HOME/.codex}/skills/project-memory"
python3 "$skill_dir/scripts/bootstrap_repo_memory.py" --help
python3 "$skill_dir/scripts/principle_library.py" --help
```

## Make one project easy to resume

Inspect the repository's existing instructions, index, and notes for one active workstream. For an established repository, start with a read-only audit:

```sh
python3 "$skill_dir/scripts/bootstrap_repo_memory.py" \
  --repo /path/to/project --mode monitored --audit-only
```

Use [repository modes](../references/repo_modes.md) to interpret the output. For a brand-new repository, `--mode new --audit-only` previews the computational-biology-oriented scaffold, and `--yes` creates missing files when authorized. In established repositories, preserve existing conventions and directory structure.

### Organize for a reader who was not there

The project branch answers "What did we do?" through organization and provenance. It adapts [Noble (2009), *A Quick Guide to Organizing Computational Biology Projects*](https://doi.org/10.1371/journal.pcbi.1000424): make the work understandable to an unfamiliar reader, prepare for experiments to be repeated, separate broad code/data/results/documentation roles, and distinguish prose notes from execution details. Where Noble uses chronological experiment folders, this skill uses an analysis index, workstreams organized around analytical questions, and named run variants with selective manifests.

Apply the [repository structure](../references/repo_structure.md) through three connected levels:

1. Give code, inputs, results, and durable documentation stable homes with distinct roles.
2. Give each maintained analytical question one workstream, one index entry, and one parent note. Keep its named variants under that workstream; minor reruns do not become new projects.
3. Keep interpretation and selection in the parent note, and execution facts in each relevant run manifest. Link from the index to the note, then to the result and its provenance.

This lets a reader find the current result and reconstruct how it was produced. Use the [document contract](../references/doc_contract.md) to keep those roles clear as the project changes. Map them onto existing equivalent files:

| Role | Typical home | What it records |
| --- | --- | --- |
| Rules and workstream map | `AGENTS.md`, `ANALYSIS_INDEX.md` | Project conventions, active directions, and where current work lives |
| Current understanding and decisions | Workstream `NOTES.md` | Question, current answer, evidence links, decision reasons, limits, and next decision |
| Selective execution provenance | `analysis_manifest.json` | Code, inputs, parameters, environment, output links, and file hashes for key runs |
| Reusable project lessons | `docs/LESSONS.md` | Repo-specific findings and pitfalls that should shape future tasks |

Here, an "analysis branch" means an analytical workstream in the notes, not permission to create a Git branch. Make the smallest repair that restores continuity, preserving scientific meaning, decision history, and unrelated edits. Changes to protected environment, security, execution, or validation rules remain governed by the skill's [boundaries](../SKILL.md#boundaries).

Follow [manifest guidance](../references/analysis_manifest.md) when a meaningful analytical variant needs execution provenance. Run manifest validation and file-hash verification on the maintained result you touch so broken links or altered outputs are caught; these checks confirm structural integrity and file matches on disk, not full scientific reproducibility, and historical provenance gaps should remain explicit. Use [note-quality guidance](../references/memory_quality.md) when cleaning up sprawling notes.

An audit output alone is not completion. Finish this stage by showing the user the updated files, a traceable path from the current answer to its evidence and decision reasons, any remaining provenance gaps, and the next decision.

## Add private personal memory when requested

Project memory works on its own. When the user also wants cross-project personal memory, follow the [personal-memory workflow](../references/personal_memory_workflows.md). Create a private workspace outside project repositories and outside the skill checkout. Copy the [registry example](../templates/personal-memory/repos.example.json), replace placeholder paths, and register only user-authorized local sources:

- `decision_patterns` select decision-bearing project notes. Use `[]` when only dialogue from that project should be collected.
- `dialog_roots` point to local session directories. Bounded daily collection reads completed turns from both active and archived local sessions; coverage can be partial.
- `maintenance_enabled` controls participation in documentation collection. Scheduling remains a separate step; registering personal sources alone does not enable repo maintenance.

Initialize the workspace with an absolute Python 3.10+ interpreter path:

```sh
python3 "$skill_dir/scripts/principle_library.py" setup \
  --workspace /path/to/private-memory \
  --registry /path/to/repos.json \
  --python /absolute/path/to/python3
```

`setup` writes workspace state, a managed instruction snippet, the principle index, and entry prompts under `config/prompts/`. It preserves existing ledger state, creates no schedules, and does not touch project repositories. Omit `--registry` when refreshing an existing workspace whose registry is already in place.

To let tasks use personal principles in a specific project, explicitly bind that project's instruction file:

```sh
python3 "$skill_dir/scripts/principle_library.py" bind \
  --workspace /path/to/private-memory \
  --instructions /path/to/project/AGENTS.md
```

`bind` inserts a managed instruction block into the named file. During relevant tasks, the agent checks the principle index and calls `task-context` to retrieve selected principles alongside linked-evidence checks.

## Collect, distill, and feed back

The Python helpers handle bounded collection, storage, and structural checks; the reasoning agent evaluates context and writes interpretations.

| Layer | Mechanism and scope | Cadence and ownership |
| --- | --- | --- |
| L1: decision evidence | Capture meaningful choices, reasons, accepted costs, corrections, and source links from local turns and registered notes | Daily bounded observer |
| L2: working principles | Check supporting cases, corrections, and exceptions; distill reusable principles with explicit reasons, examples, and limits | Weekly semantic review; selective `task-context` retrieval and task feedback |
| L3: core commitments | Consider deeper values and outlook that explain priorities under conflict or cost | First successful weekly review each month, discussed with the user |

A single well-reasoned judgment can support a tentative L2 principle; no recurrence threshold is required. Older ledger status labels (`candidate`, `reflection`, `axiom`) track evidence maturity rather than defining L3, and a detailed L3 synthesis method is not yet specified—keep L3 interpretations tentative for user discussion, not autonomous promotion.

For an initial pass, run the daily observer workflow on a bounded packet, inspect cited turns and notes in context, and validate before applying ledger updates. Then run the weekly review workflow to draft or refine principles using [the principle template](../templates/PRINCIPLE.md).

When a retrieved principle shapes a task or gets corrected by new results, record that outcome in the project's registered note so the next collection pass picks it up. Linked corrections can block stale retrieval until weekly review revisits the principle; these structural checks guard against unreviewed drift but do not prove semantic truth or guarantee better decisions. Treat missing source files as explicit gaps, and never treat agent compliance or user silence as personal endorsement.

## Schedule only requested loops

If the user asks for automation, register the generated `daily-observer.txt` and `weekly-review.txt` prompts in the host scheduler using the user's timezone and requested cadence. Preserve existing timing, active/paused state, model, environment, and notification settings unless the user requests a change. Keep scheduler wrappers thin and defer behavior to the [scheduled loops procedure](../references/scheduled_loops.md).

For repository documentation upkeep, schedule `maintenance-<name>.txt` only for repositories with `maintenance_enabled` and follow the [scheduled worker entry](../references/scheduled_loops.md#scheduled-worker-entry). Keep roles separate: the central collector reads monitored repositories and writes only to the private workspace, while repo-local maintenance workers own edits inside their respective projects.

## Verify completion

Before handing off, verify the enabled scope:

- **Project memory:** Show the current answer, its evidence and manifest checks, recorded decision reasons, and the next decision.
- **Personal memory:** Show the registered sources, at least one evidence-backed principle (when sources support one) with its reasons and limits, and a working `task-context` retrieval. Keep private ledgers, raw dialogue, and local paths out of public Git.
- **Schedules:** Confirm the saved schedule configuration and at least one completed run; report offline hosts or unreachable paths as coverage gaps.
- **Live end-to-end validation:** When requested, run the [live personal-memory test](../references/live_personal_memory_test.md) or [live maintenance test](../references/live_maintenance_test.md). For implementation changes, install pytest in the test environment and run `python3 -m pytest tests -q` from the source checkout, plus the live test required by the changed workflow. Consult [GLOSSARY.md](../GLOSSARY.md) for terminology.

# Memory schedules, coverage and deployment audit — 2026-10-23

Read-only audit. No collection, validation/apply, schedule change, production-state edit, branch operation, or scientific analysis was run. One bounded SSH read succeeded using the existing SCG connection. The findings below use current configuration and completed-run receipts, not schedule status alone.

## Main assessment

The redesign is operating, and daily work has become reliable recently. Its biggest weakness is source continuity and visibility, not lack of scheduled execution. Coverage counters are conditional on what remains discoverable; their dramatic decline must not be interpreted as backlog cleared. L1 and L2 now distinguish user judgments from agent proposals, but the collection set still omits some active projects and source histories. The document-maintenance queue is functioning separately and has no abandoned claims.

## Configured schedules and observed execution

All four memory automations are ACTIVE. Times are America/Los_Angeles:

| Component | Configured cadence | Recent evidence |
| --- | --- | --- |
| Daily personal decision observer | Daily 09:00; 24 sources, four session bodies per repository | Applied daily on all 16 dates Oct 8–23. Oct 23 added 14 events after 24 source reviews. |
| Central document collector, Phase A | Friday, after daily L1; at most two ten-file packets | Oct 9, 16, 23 completed. Oct 23 reviewed 15 paths, representing 14 unique contents, and added two queue tasks. |
| topic_analysis maintenance, Phase B | Friday 11:00; at most four tasks/two large rewrites | Oct 23 repaired four notes; two resolved and two deferred; all claims closed. |
| cross-species maintenance, Phase B | Friday 13:00 | Oct 23 ran at 14:35 local; found no queued work or contract repair; preserved all existing edits. |
| Personal L2 reflection | Sunday 10:00 | Oct 11 and 18 successfully applied; Oct 4 failed preflight because IF_PHAGE was unavailable. |
| L3 eligibility review | First successful weekly reflection of each month, or explicit manual request | October review was applied Oct 3; Oct 11/18 explicitly did not repeat it. Next scheduled eligibility review is first successful November weekly run. |

Config paths:

- `/Users/fanxiaochen/.codex/automations/daily-lessons-curation/automation.toml`
- `/Users/fanxiaochen/.codex/automations/monthly-axiom-review/automation.toml` (old ID, current name “Weekly personal judgment reflection”)
- `/Users/fanxiaochen/.codex/automations/repo-memory-audit-6049b99550d3/automation.toml`
- `/Users/fanxiaochen/.codex/automations/repo-memory-audit-e8d9f1c9495a/automation.toml`

October evidence includes 19 applied L1 collection runs, one being the Oct 3 manual/test run. The incomplete Oct 6 directory contains packet/proposal/receipts but no ledger apply entry. Oct 4 and 7 attempts were blocked by the unavailable external volume. Those failures survive in automation `memory.md`, since the hub itself could not be written. A successful daily schedule therefore must not be inferred from existing packet files alone.

Evidence: authoritative `/Volumes/IF_PHAGE/long-term-memory/state/decision_memory_v1.json` → `runs`; daily automation `memory.md`; `/Volumes/IF_PHAGE/long-term-memory/runs/20261006T160224Z_daily_l1_76da25/`; reflection automation `memory.md`; logs under `/Volumes/IF_PHAGE/long-term-memory/logs/runs/`.

## Source continuity: a major coverage break

| Date | Matching local sessions discovered | Local session bodies scanned that run | Local sessions not scanned | Discovered decision sources unselected |
| --- | ---: | ---: | ---: | ---: |
| Oct 14 | 722 | 20 | 659 | 226 |
| Oct 15 | 87 | 9 | 76 | 118 |
| Oct 18 | 83 | — | 70 | 64 |
| Oct 19 | 45 | — | 30 | 72 |
| Oct 21 | 45 | — | 25 | 57 |
| Oct 22, after Claude integration | 144 | — | 118 | 97 |
| Oct 23 | 156 | 14 | 126 | 99 |

Oct 14→15 removed 635 matching local sessions from discovery, an 88% fall. Per project: topic_analysis 191→17; cross-species 113→2; practice 35→0; claude_code_task 326→68; ProgExplorer 52→0; SMC 3→0; perturb_validation 2→0. Only 24 sources were selected Oct 15. This cannot be explained by successful review/consumption: `root_sessions_discovered` is calculated from the file catalog before the consumed-scan filter. Local pending sessions fell by 583 while the underlying catalog vanished. The lower backlog is not a learning improvement.

The four original support/counter contexts for active axiom A01 all became unavailable at the same boundary. They were last successfully verified on Oct 14 at 16:07:04 UTC. Retained quotations and a source-health warning remain. The logs noticed these facts, but continued collection has not repaired source reachability. The archive/recovery cause needs separate evidence; this audit establishes the discovery break, not deletion or permanent loss.

Exact packet evidence:

- `/Volumes/IF_PHAGE/long-term-memory/runs/20261014T155911Z_daily_l1_f9c97b/decision-packet.json`
- `/Volumes/IF_PHAGE/long-term-memory/runs/20261015T160454Z_daily_l1_1b801c/decision-packet.json`
- `/Volumes/IF_PHAGE/long-term-memory/runs/20261019T160047Z_daily_l1_6910a1/decision-packet.json`
- `/Volumes/IF_PHAGE/long-term-memory/runs/20261023T160511Z_daily_l1_facdf4/coverage.json`
- `/Volumes/IF_PHAGE/project-memory-skill/scripts/decision_memory.py`, `inventory_repo` (total catalog before pending filter).

`remaining_discovered_sources` is also a run-local leftover after selection, not a durable census of all outstanding decisions. It changes when different session bodies are sampled or a remote source disappears. The code does not retain a persistent full backlog inventory or calculate the oldest unreviewed period. Most reports correctly say that remote backlog/oldest period is unknown, but a user-facing trend chart must keep inventory size and source availability beside backlog.

## Current coverage and bias

The registry now contains nine local repositories plus one remote repository. All four user-named local projects and SCG are configured for personal learning. Only topic_analysis and cross-species have automated document-maintenance workers. Practice, claude_code_task, and SCG do not receive the same central Phase B maintenance guarantee; their documentation depends on normal project workflows.

Local history roots include live Codex, archived Codex, and native Claude Code. Claude support was installed Oct 21 and first contributes in the daily receipts Oct 22. Oct 23 provider coverage:

| Provider | Discovered | Scanned that run | Pending sessions not scanned | Selected messages |
| --- | ---: | ---: | ---: | ---: |
| Codex | 55 | 10 | 29 | 10 |
| Claude Code | 101 | 4 | 97 | 9 |

The provider-aware balancing code reserves scan slots for each provider when present. Successful installation verification reports 43 tests and bounded live checks of two sessions/provider in two projects. This establishes parser functionality, not complete historical coverage. Nine current ledger events have at least one Claude source (13 Claude evidence pointers). Unclassified root-session counts are 15 live Codex, one archived Codex, and one Claude path; these counts must not be summed once per project.

The current ledger has 343 event records: 115 direct-user and 228 attributed-user. Attributed notes are legitimate weaker evidence, but dominate the event count and can accumulate repeated versions of one decision. The run reports explicitly distinguish event counts from independent episodes. Oct 23’s 14 events were described as eight conservative groups. L2 must continue doing semantic independence review.

`REPO_REGISTRY.md` is stale: its table omits configured `revision-analysis` and `ouroboros-journal`. The active projects `Hepatocyte` and `imaging_analysis` are absent from `config/repos.json`. Because session discovery filters working directories to registered roots/aliases, their own cwd histories are excluded from this collector, even though discussion in a registered project may enter incidentally. OpenCode and ChatGPT histories are explicitly unconfigured. The registry and latest report are clearer than an assumption of “all my work,” but there is no single live coverage dashboard.

Evidence: `/Volumes/IF_PHAGE/long-term-memory/config/repos.json`; `REPO_REGISTRY.md`; `runs/20261021172341Z_claude-observer-support/INSTALLATION.md`; `runs/20261023T160511Z_daily_l1_facdf4/REPORT.md`; authoritative ledger.

## Remote reliability and deployment

SCG succeeded in only four of the 19 applied October collection runs: Oct 5, 15, 16, 17. Other October receipts show authentication failures, DNS failure, or control-socket permission denial. The latter is explicitly visible Oct 13/14/21/22. This is sustained incomplete remote coverage, not zero remote signal. Since Oct 18 the scheduled exporter has not inventoried remote backlog.

A single bounded check in this audit succeeded using the installed `remote-compute-ssh` helper and the existing authenticated connection. It read the repository AGENTS file, checked both Codex history directories, and hashed the remote exporter. Thus SCG exists and is readable now; failure in the scheduled execution context needs investigation rather than assuming credentials or repo absence. The collector invokes plain noninteractive SSH in `decision_memory.py`; the successful check used the skill helper. This difference is a diagnostic lead, not proven root cause. Do not repeatedly authenticate or retry unattended failures.

Local canonical, `.agents`, `.claude`, and Codex compatibility scripts have identical hashes:

- decision_memory.py: `276a6bf226afaa7836c6d9d174538313527e269928e84585b8fd0e6d2b76a5f9`
- memoryctl.py: `e00d9c56986cc1f477e1a2850d51f1bee19fb314161d258e4e4b833a875f7da2`
- decision_memory reference: `d6dc482edb2759784ea14bfe23c97cef7f3375c079bf3689b4932b506fedca13`

Remote decision_memory.py: `a30bca76cc7709cb89bbd8937075a7a509354905009b628552ee54c8c05162ac`. Remote is still the older Codex-only installation; the Oct 21 report explicitly limits it that way. A different hash alone is not proof of a broken remote Codex parser.

All four schedules point at `/Users/fanxiaochen/.codex/skills/project-memory/SKILL.md`, which does not exist. That absence is intentional according to its adjacent README: `.agents` is the discoverable skill and Codex retains script/reference compatibility links to avoid duplicate skill discovery. Recent automation runs repeatedly discover and use the `.agents` fallback. Therefore this is stale schedule text, not missing controller installation. Updating the prompt pointer would remove needless uncertainty.

Both `.agents` and `.claude` resolve to `/Volumes/IF_PHAGE/project-memory-skill`. The source checkout currently has modified decision_memory.py and untracked Claude parser/tests; deployed code is the working checkout, not a fixed committed release. No modification was made during this audit. This also means unavailable IF_PHAGE simultaneously removes the collector, parser, skill entry, and configured Python—a documented single availability dependency.

## Document-maintenance queue

Current state after Oct 23 workers: 83 total items, 31 resolved, 46 rejected, four deferred, two open, zero claimed. Forty rejections have the explicit `user_waived_historical` disposition; do not report them as repaired provenance. The two open items are older topic_analysis lineage sensitivity notes. The four deferred items preserve missing native-provenance constraints rather than inventing manifests. No open/deferred cross-species work remains.

Friday Oct 23 Phase A had no remaining changed-document backlog after its second packet. That is separate from personal decision backlog. Latest topic worker reports 176 direct analytical variants, 47 without direct manifests, 145 passing manifest schemas, 69 notes, and 95 typed lessons. Two bounded checks found 28 matching hashes and 32 existence-only records; this is narrower than reconstructability or scientific validation. It repaired current summaries and retained old execution facts. The cross-species worker reports 69 typed lessons and no dated-feed bullets, but zero manifests; its no-work outcome does not establish historical analytical fidelity.

The topic worker self-reported a scope violation: its manifest verifier followed two declared sibling-repository inputs despite the no-sibling instruction. No sibling edits occurred. This shows the scope boundary depends on callers screening verifier paths. It is an operational correction to make, not evidence that analysis results were changed.

Evidence: `/Volumes/IF_PHAGE/long-term-memory/state/maintenance_queue_v2.json`; `logs/runs/20261023T180223Z-topic_analysis-5da57266.md`; `logs/runs/20261023T213525Z-8fd3b471-cross-species-analysis.md`; `runs/20261023T160511Z_daily_l1_facdf4/REPORT.md`.

## L2/L3 and transparency implications

There is already one active axiom, five reflections, and two candidates. Thus “no axioms” is not literally current state; new promotion has been sparse, and the sole axiom’s source contexts now need review. October 11 promoted two candidates to reflections; October 18 added a scoped diagnostic candidate and refined boundaries. These are real semantic gains. No new October 11/18 axiom is partly the deliberate monthly cadence, not evidence that weekly reflection failed to run.

A concrete freshness gap exists: Oct 23 L1 newly recorded approval of the original sex-stratified report plan, while Phase A noticed the later withdrawal of its p-derived difference test. The report explicitly says a superseding L1 event still needs capture. That means the current ledger may serve a true historical choice without the known later correction. Source selection is bounded, but known reversals should not wait behind undifferentiated backlog if memory is meant to guide current decisions. Evidence: `runs/20261023T160511Z_daily_l1_facdf4/contextual-limit.md`, its REPORT, and event `D20261021-sex-stratified-report-approved-plan`.

Recommended priorities, not applied in this audit:

1. Restore reliable original-source reachability and report dropped/inaccessible sessions independently from consumed backlog.
2. Make known reversals/supersessions a priority input, with an explicit open issue until reconciled.
3. Repair SCG execution-context reliability; a fresh successful check must not erase the scheduled failure history.
4. Publish one compact status view: active source roots/providers, last successful runs, source-health failures, reviewed/remaining counts with inventory denominators, decisions→independent episodes→principles, and one concrete future decision each principle changes.
5. Align the human registry and schedule skill links with actual config. Make explicit whether newly active projects should enter the collector.
6. Keep strict distinction between queue closure, record integrity, recoverable personal evidence, semantic principle quality, and real downstream use. More axioms alone is not the success measure.

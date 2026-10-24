# Project record integrity audit — 23 October 2026

## Assessment

The user's impression is supported: project-level recovery is substantially more useful than a simple activity log. Current notes often state the answer, selected variant, limitations, and why an earlier choice changed. Lessons contain concrete checks that could prevent repeated scientific mistakes. This is stronger evidence for project continuity than for exact reproducibility or demonstrated future adherence.

The remaining weaknesses are uneven maintenance coverage, several legacy provenance gaps, dense central notes, some unowned scientific judgments in older records, and a concrete blind spot in the structural audit. Project notes can also be ahead of the personal decision ledger after a correction.

This was a read-only audit. No repository, memory ledger, automation, Git branch, or analysis output was changed. Only this report and `/tmp/memory-audit-links-20261023.json` were written.

## Scope and method

Inspected the installed project-memory skill and applicable guides; all four requested local analysis indexes and lesson files; current controller registry and queue; the September 17 baseline report; and selected branch records:

- topic_analysis: CRT/program comparison, Figure5i comparison, matched program DE, hypoxia gene DE.
- practice: Fzd4 arterialization, AB521 manual counts, and the maintained analysis map.
- cross-species-analysis: species DE and HIF coding conservation.
- claude_code_task: academic PI country survey, AI-agent tutorial, UPenn application notes/wiki index, and ERC decision register.

Ran the installed bootstrap audit in `--audit-only` mode for all four roots. Checked 343 literal Markdown local links from the sampled notes/index: all destinations exist. The link check ignores anchors, web links, and paths shown only in backticks. The latter are common in older notes; a passing count is therefore a bounded connectivity check, not an exhaustive inventory or proof of completeness.

Validated two exact manifests with the installed `validate_analysis_manifest.py ... --verify-files`: the topic sex-stratified report and practice whole_scene_sma_first_v4. Both passed schema and declared-file verification with zero reported failures. Hashing is bounded to 50 MB per file; many output entries have no declared hash and were existence-only checks. No pipeline was rerun, raw image interpretation reviewed, model validated, or historical environment reconstructed.

## What works now

### 1. Notes explain trust, not just storage

The CRT note opens with the scientific question and says the all-EC comparisons remain diagnostic. It distinguishes threshold-10, guide-count, cycling and inferred-sex adjustments from establishing a calibrated discovery method. It warns about post-perturbation covariates, pooled control averages, and missing animal-level replication. This directly prevents a future agent from confusing a convenient display with a selected discovery method.

Evidence: `/Volumes/IF_PHAGE/topic_analysis/results/artery-vein-fate/crt_program_ucell_no_celltype/NOTES.md:3–45`.

The Figure5i note distinguishes P18 directional consistency from changing statistical support, including the Egln1/P18 calibrated q=.17 exception. The latest direction-aware program selection and its outcome-selection caveat appear at the opening, alongside the older specificity-based alternative. It does not silently choose manuscript columns.

Evidence: `/Volumes/IF_PHAGE/topic_analysis/results/artery-vein-fate/figure5i_cap234_comparison/NOTES.md:3–25,27–52`.

The hypoxia DE note now gives the current cell-level result, variant map, missing sample IDs, and lack of execution manifests. It explicitly says state-paired pseudobulk does not create biological replication. That qualification changes what may be claimed biologically while retaining usable descriptive results.

Evidence: `/Volumes/IF_PHAGE/topic_analysis/results/hypoxia_gene_de/NOTES.md:3–56`.

The practice Fzd4 note and index retain the invalidated full-data measurements and keep pipeline transfer unvalidated. The note distinguishes a curated correction viewer from a reusable prediction pipeline and excludes investigator answer labels from raw replay. It also records unresolved save recovery rather than pretending screenshots recovered editable annotations.

Evidence: `/Volumes/IF_PHAGE/practice/output/fzd4_arterialization/NOTES.md:1–52`; `/Volumes/IF_PHAGE/practice/ANALYSIS_INDEX.md:10–26,56–66`.

### 2. Lesson files contain useful scientific checks

Topic lessons contain specific failure modes: held-out NTC calibration instead of in-sample uniformity; a silent 20,000-control cap; invalid standard errors derived from resampled p-values; native multiple-testing families; explicit co-carrier/reference definitions. These are actionable checks, not generic slogans.

Evidence: `/Volumes/IF_PHAGE/topic_analysis/docs/LESSONS.md:120–147`.

Practice lessons preserve expert judgments that materially affect anatomy: keep faint tubular SMA branches; inspect an approval pilot; distinguish raw replay from answer-label tuning; separate identity from geometry; test missed targets rather than only retained positives; do not treat unclassified scaffolds as accepted anatomy. This is close to the original goal of preserving how the investigator judges evidence.

Evidence: `/Volumes/IF_PHAGE/practice/docs/LESSONS.md:14–23,38–43`.

Cross-species lessons separate accepted coarse labels from exploratory subtypes, preserve statistical families, and warn that placeholder-looking paired summary values should not supply effect sizes. The sampled species-DE note names the all-data baseline, retained sensitivities, concrete source tables and interpretation.

Evidence: `/Volumes/IF_PHAGE/cross-species-analysis/docs/LESSONS.md:26–59`; `/Volumes/IF_PHAGE/cross-species-analysis/output/analysis/species_de/NOTES.md:8–30,64–97`.

The claude_code_task lessons have substantive guidance about mechanism, stage-specific pathways, and evidence networks, but only four entries follow the current literal typed-prefix convention. Most lack direct provenance/attribution. That does not make them useless; it makes them weaker evidence of the user's own preferences and makes automated structural counts poor proxies for content quality.

Evidence: `/Volumes/IF_PHAGE/claude_code_task/docs/LESSONS.md:23–43,60–79`.

No replay experiment was performed to establish whether later agents actually retrieve and follow these lessons. Content utility and operational use must remain separate claims.

### 3. Attributed decisions are much better in recent records

The tutorial note records alternatives, explicit acceptance, cost, scope, and agent-only choices. It preserves the rejected redesign and the investigator's exact request to retain the original style and reduce details. This is a recoverable preference episode with a counterexample, rather than just a record that an image was made.

Evidence: `/Volumes/IF_PHAGE/claude_code_task/output/ai_agent_tutorial/NOTES.md:17–26,40–48`.

The UPenn note owns 37 named decision sections with explicit corrections, accepted costs and source boundaries. Its first sections clarify ownership. The ERC register separately marks accepted scope, implementation choices, advice, unresolved questions, and later revisions. It preserves the investigator's correction that the cardiometabolic project centers human genetic risk/protection across contexts rather than the agent's semaglutide-centered interpretation.

Evidence: `/Volumes/IF_PHAGE/claude_code_task/Applications/UPenn_CVI/NOTES.md:13–23,38–52,265–312,685–713,1011–1038`; `/Volumes/IF_PHAGE/claude_code_task/Grant application/ERC early/wiki/decisions.md:9–40`.

These examples show that lack of axioms is not simply lack of personal judgment in project records.

## What remains unreliable or incomplete

### 1. A project correction can lag in personal memory

The strongest concrete example is the October 21 sex-stratified report:

- The project note preserves the original approval as genuine history.
- It explicitly withdraws p-derived z-difference inference and error bars.
- It records the investigator's correction to soften replication/power-only claims and use all pairs for direct differences.
- It records the later approved exploratory HC3 interaction estimand, with independent-cell and missing-animal-ID limitations.
- The lesson file already distills the invalid-p-derived-SE trap.
- The personal ledger still contains `D20261021-sex-stratified-report-approved-plan`, including exploratory z-difference tests, with no sex-difference supersession event found in the scoped ledger search.

The old event is historically truthful. Its uncertainty even says approval does not validate inference. The risk is treating it as current guidance without the later change of mind. Project integrity here is better than cross-layer temporal consistency.

Evidence: CRT note `:2276–2302,2322–2345,2362–2378`; topic lessons `:128–136`; `/Volumes/IF_PHAGE/long-term-memory/state/decision_memory_v1.json:11426–11460`.

### 2. Structural audit misses output-based repositories

`bootstrap_repo_memory.py` uses `results = repo / 'results'` and discovers manifests, run directories and notes only under that root. It therefore reports zero manifests for practice even though 35 manifests exist directly in `output/fzd4_arterialization/runs/*/analysis_manifest.json`. One was schema/file verified successfully in this audit.

This is an instrumentation defect, not missing project records. The same structural blind spot affects output-based notes in cross-species and claude_code_task. The manifest validator has a separate discovery implementation; do not conflate the two tools.

Evidence: `/Users/fanxiaochen/.agents/skills/project-memory/scripts/bootstrap_repo_memory.py:379–396`; `/Volumes/IF_PHAGE/practice/output/fzd4_arterialization/runs/whole_scene_sma_first_v4/analysis_manifest.json`.

### 3. Scheduled upkeep covers only two of the four requested projects

The registry enables maintenance for topic_analysis and cross-species-analysis. Practice and claude_code_task are decision sources but have `maintenance_enabled: false`. This was already an intentional distinction in the September 17 baseline; it is not proof that their notes are neglected. Their recent notes show task-driven upkeep. It does mean a global statement that weekly maintenance checks all four would be false.

Evidence: `/Volumes/IF_PHAGE/long-term-memory/config/repos.json:5–19,22–36,39–53,56–73`; `/Volumes/IF_PHAGE/long-term-memory/audits/2026-09-17-personal-judgment/REPORT.md:106–110`.

### 4. Some legacy records are recoverable but not reproducible

Current queue: 83 total items; cross-species has 10 resolved/11 rejected, topic has 21 resolved/35 rejected/4 deferred/2 open. Closed counts include waived or rejected historical obligations; they cannot be read as repaired provenance.

The four deferred topic notes have partial navigation repair but preserve execution blocks because native provenance or code recovery is missing. The hypoxia note states this clearly. The two open mediation-note tasks date to August 14 and still lack sufficiently clear current-answer/source maps in the queue assessment. Those are retained debt, not a fresh failure of today's collector.

Evidence: `/Volumes/IF_PHAGE/long-term-memory/state/maintenance_queue_v2.json` (deferred item `0c6ef5b2f3a6d62f8e28dd04` around line 3018; open item `d36148bc77981b6bc15eb779` around line 3144); hypoxia note `:36–56`.

The AB521 record faithfully retains a requested hemisphere-as-independent analysis and duplicate collapse. It is clear enough to reconstruct the statistical choice. That does not establish animal-level independence. If this result is currently used in a manuscript, review the replication unit explicitly rather than silently changing the historical request.

Evidence: `/Volumes/IF_PHAGE/practice/output/AB521_082526/NOTES.md:4–17,28–47`; practice index `:10–14,22`.

### 5. Important notes remain costly to navigate

The CRT note is 2,677 lines and the UPenn note is 1,934 lines. Their openings and decision sections are useful; length alone is not a defect. The cost is that the next reader must distinguish numerous original choices, subsequent corrections, source variants and display variants. Current opening maps reduce this cost but do not replace a concise current-decision projection. Older HIF notes still start with long commands before the question and retain un-attributed “Key decisions.”

Evidence: CRT note `:1–45,2276–2378`; UPenn note `:13–23,38 onward`; `/Volumes/IF_PHAGE/cross-species-analysis/output/analysis/hif_axis_coding_conservation/NOTES.md:1–55`.

## Evidence of meaningful maintenance on October 23

Today's topic maintenance corrected two scientific navigation errors: an overstrong opening claim that power rather than sex explained lost calls, and blanket q<.15 wording that did not cover the new q<.1 reselection variant. It preserved original approvals, withdrawn outputs, P57 correction and outcome-selection caveats. This is useful semantic maintenance.

Evidence: queue items `6fa436532e2a85e63cf3204a` and `a5d1a6dad7a521d0cfffc45a`, `/Volumes/IF_PHAGE/long-term-memory/state/maintenance_queue_v2.json:5488,5537`; current CRT and Figure5i openings cited above.

The second queue resolution also records that a verifier followed two declared sibling-repository inputs despite a no-sibling rule. This audit did not repeat that run. It is a useful sign that operational scope failures are being admitted, and a reason to make file verification path scope enforceable rather than merely verbal.

## Recommended priorities for the main audit

1. Preserve current project-memory architecture. It is producing scientifically useful continuity and explicit limits.
2. Add a correction-aware current projection: retain initial approvals, link later supersession, and test that querying an old choice returns its latest valid scope. Prioritize changes of mind before low-impact new events.
3. Fix the bootstrap audit to inspect each repository's actual maintained output homes, while avoiding raw-data/generated-media traversal. Add a small regression fixture for `output/` manifests and notes.
4. Report project health by separate dimensions: reachable current answer, exact provenance, current scientific trust, note/lesson usability, and maintenance coverage. Do not turn queue closure or schema-valid manifest counts into one “healthy” score.
5. Evaluate lesson use on a few real future decisions: does the agent retain faint branches, preserve native FDR families, or reject p-derived uncertainty without being corrected again? This tests learning more directly than counting lessons.
6. Do not mass-rewrite legacy notes or invent manifests. For any currently used result with an unresolved scientific issue, revisit the specific unit/estimand/provenance. Leave low-value historical obligations honestly waived.

The technical lesson is that recoverability, reproducibility and validity are separate. The biological lesson is that the best recent notes preserve exactly the distinctions most likely to cause overclaiming: cell versus animal replication, direction versus significance, selected concordance versus replication, anatomy versus display quality, and regulatory evidence versus pathway narrative.

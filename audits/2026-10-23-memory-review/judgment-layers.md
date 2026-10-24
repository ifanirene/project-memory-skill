# Personal memory audit — 23 October 2026

Read-only assessment of `/Volumes/IF_PHAGE/long-term-memory`, its installed decision-memory contract, retained L1/L2/L3 evidence, and selected original contexts. No ledger, principles, schedules, repo notes, branches, or installed skills were changed. Counts are a snapshot of the ledger after the 23 October 09:10 PDT L1 apply.

## Assessment

The system is substantially better at preserving human choices and qualifying its interpretations. L2 is doing genuine reasoning: it groups related turns into one episode, preserves exceptions, and revises overbroad interpretations. It is no longer simply treating successful automation as evidence about the user.

It still falls short of the original goal of a transparent, useful account of the investigator's distinctive judgment. Most new records are note-attributed, the small principle set is weighted toward technical work and writing, and there is no measured loop showing that a retrieved principle improved a later decision. Source loss now damages the ability to deepen or reverify earlier interpretations. The lack of new axioms is partly justified caution, partly a consequence of these weaknesses; reducing promotion thresholds alone would not fix it.

There is **one existing axiom**, created in the September repair, rather than zero: prefer retaining faint collateral/arteriole connections over a cosmetically clean image, accepting extra noise and verification. It is a bounded professional judgment, not a generic maxim. There have been **no additional axioms since that repair**. Its four original supporting/counterexample contexts are now unavailable; its retained quotations remain, last fully verified 14 October.

## Current numbers and what they mean

Derived directly from `state/decision_memory_v1.json`:

| Measure | Current | Interpretation |
|---|---:|---|
| Event interpretations | 343 | Not 343 independent choices |
| Direct-user event interpretations | 115 (33.5%) | Source is a retained user message |
| Note-attributed event interpretations | 228 (66.5%) | Human attribution comes through a project note |
| Unique supporting source IDs | 214 | Sources can support several interpretations |
| Unique direct-user source IDs | 137 | Includes multiple turns from one chat |
| Distinct direct-user chat/session IDs | 80 | Controller proxy, not semantic episode count |
| Consumed source reviews | 528 | 214 signal, 314 no-signal; deferred work is not consumed |
| Principles | 8 | 1 axiom, 5 reflections, 2 candidates |
| Principle history entries | 13 | 5 baseline snapshots, 8 later additions/revisions |
| Explicit event supersession links | 6 | Helpful but incomplete trajectory representation |
| Events referenced by any principle as support/counterevidence | 34 | 309 are unlinked; not inherently a failure, but discovery coverage is hard to see |
| Events added after the last L2, 18 October | 61 | Not yet expected to have received the next weekly review |
| Latest remaining discovered sources | 99 | A selected-source backlog, not all undiscovered human judgment |
| Latest local sessions not scanned | 126 | Separate session backlog; remote inventory unavailable |

The September repair began with 12 events, one axiom, two reflections and two candidates. Current status therefore represents a large L1 expansion and real but much smaller L2 growth. See baseline `audits/2026-09-17-personal-judgment/REPORT.md:13,128` and current `logs/runs/20261023T161724Z-20261023T160511Z_daily_l1_facdf4-daily-l1-observer.md:1–5`.

Events are concentrated in claude_code_task (135), topic_analysis (99), practice (41), SCG (24), ProgExplorer (20), revision-analysis (13), cross-species-analysis (6), SMC (2), ERC early (1), perturb_validation (1), and one SCG/topic joint record. This distribution is evidence retained, not a denominator-adjusted measure of project coverage.

153/343 reason fields start with “not stated”; 158/343 tradeoff fields contain “not stated” or “no accepted cost.” These are lexical counts, not a semantic score. Their honesty is valuable. They also show why many choice records cannot yet support a rich explanation of what the user values and what cost she accepts.

## What L2 actually accomplished

The ledger records the September initialization/baseline, a foreground production reflection test on 3 October, and weekly reflections on 11 and 18 October. It does not establish uninterrupted weekly coverage throughout the whole period. Schedule/execution reliability is outside this sub-audit.

| Run | Substantive result | Limitation |
|---|---|---|
| 3 October | Added R03: useful simplicity plus continuity of a working pipeline, from two independent software-design contexts; preserved a real expansion/replacement counterexample | Only two direct episodes; single foreground test does not establish background operation |
| 11 October | Promoted source-by-purpose and endpoint-specific image review from candidates to reflections; added tracing examples→reproducible rules candidate; tightened statistical reflection | 170 interpretations screened; only 21 dialogue pointers and four full notes read semantically; six remote pointers unavailable and ten document versions changed |
| 18 October | Distinguished open writing revision from targeted adaptation; refined calibration/estimand boundaries; added scoped diagnostic candidate | 282 interpretations screened; 15 bounded dialogue contexts, one full CMP note and selected matched-DE sections read; only 28/86 source pointers verified |

Sources: `logs/runs/20261003T085407Z-reflection-test.md:13–48`; `logs/runs/20261011T170235Z_weekly_l2_62f9eb.md:3–11`; `logs/runs/20261018T165717Z_weekly_l2_16e37c.md:3–9`.

The 18 October source check broke down as 28 verified, 33 unavailable local-session pointers, 13 changed document versions, and 12 unavailable remote pointers. These are pointer checks, not independent episodes or distinct humans.

The present principles contain useful boundaries:

- R01 does not turn concern about adjusting away cell state into a ban on covariates. Later sex-adjustment and calibration requests limit it; favored-hit recovery remains an unresolved tension.
- R02 rejects both generic rewriting and grammar-only conservatism. The later CMP task constrains targeted adaptation without prohibiting substantial open revision.
- C02 distinguishes endpoint-specific signal recovery from keeping all pixels/background. A clean-centerline correction remains counterevidence.
- C04 correctly treats three interpretation records from two answer turns as one experimental design episode.

Those are substantive improvements, not merely green validation checks. See `reflections/PERSONAL_JUDGMENT.md:18–45,61–73,102–115`.

## Original-context spot checks

I used installed `decision_memory.py read-context` rather than trusting the generated views alone.

1. **October marker diagnostic:** the 13 October user turn at source line 225 says to keep each method's intended populations/outcome scale and run both control checks. The adjacent assistant questions make “keep” and “both” unambiguous. This confirms C04's bounded interpretation and its one-episode treatment. Original: `/Users/fanxiaochen/.codex/sessions/2026/10/13/rollout-2026-10-13T00-21-42-01a13423-776d-7eb0-be49-5ac8fef6868a.jsonl:218–228`. Hash verified, bounded context untruncated.
2. **Slow Argon/cold review rejection:** the user explicitly said it was too slow and did not seem to improve the answer. Original: `/Users/fanxiaochen/.codex/sessions/2026/10/21/rollout-2026-10-21T00-19-52-01a15d54-ad71-7252-a206-cdfde08b0810.jsonl:650`. Hash verified; context untruncated.
3. **Next-day optional Argon:** the user asked to include the successful rewrite/polish step in the skill, then explicitly said it could be optional. Original: `/Users/fanxiaochen/.codex/sessions/2026/10/22/rollout-2026-10-22T00-48-16-01a16295-065c-7f60-9d25-4059711a8656.jsonl:36,53`. Hash verified; context untruncated. This prevents a false “never use Argon” principle.
4. **Later Argon reuse:** a Claude Code user turn explicitly requested Argon for an email. Original `/Users/fanxiaochen/.claude/projects/-Volumes-IF-PHAGE-claude-code-task/0a716fed-63f6-4059-99be-98c613a00134.jsonl:1058`. Evidence turn is complete and hash verified; one preceding assistant message was truncated, so this is not a full-context certification.
5. **A01 June support and C03 tracing support:** their `read-context` calls failed because the original sessions could not be recovered. I did not substitute a retained quotation or changed source for the missing original.

These spot checks support improved attribution and scope handling. They do not validate all 343 records. Some low-information directives nevertheless become personal-memory events, for example “Request Hif1a on the existing plot” and “Request the copy on disk” (`observations/DECISIONS.md:3748,3598`). Such records may aid project continuity but add little about personal judgment without a genuine alternative or reason. Their presence can dilute L2 attention if all event rows receive equal weight.

## Why no new L3 axioms

The October eligibility review occurred on 3 October, when only 36 events were retained. The 11 and 18 October weekly runs explicitly treated October L3 as complete and deferred the next eligibility check to the first successful November weekly run. This is actual monthly policy, not a failed promotion attempt on every week. It can create delay as new evidence arrives, but currently most existing reflections still lack three verified direct episodes anyway.

The documented actual blockers are appropriate: reflections mostly have two direct supporting episodes; C03 has one; C04's three records describe one episode. R01 adds a note-attributed caliper decision but not a third direct confirmation, and keeps a real desired-result tension. Source loss prevents fresh verification of several older supports. See `reflections/PERSONAL_JUDGMENT.md` and October L2 logs above.

The mechanical rule is stricter and less semantically precise than the plain-language description:

- `scripts/decision_memory.py:439–448` counts only `direct_user` events toward reflection/axiom thresholds. Thus the 228 note-attributed records cannot supply automatic recurrence, however clearly the note attributes the decision. This is a conservative safeguard, but it makes direct-source recovery the bottleneck for two-thirds of L1 output.
- The code counts source `episode_id`, which is a chat/session identifier. A long chat containing genuinely separate decisions cannot automatically provide separate episodes; different chats/forks still require manual lineage judgment. `episode_group` appears in 81 events but is not used by this validation rule.
- New/promoted axioms require original source recovery for all support and counterevidence (`:453–456`). Existing axioms instead retain status with degraded health, avoiding deletion of history.
- Explicit endorsement is strong evidence, but the contract does not automatically bypass the recurrence gate; it requires a separate endorsement review (`references/decision_memory.md:22–25`).

These rules should not be silently loosened to hit an axiom quota. A better design would represent semantic episodes and evidence strength explicitly, and allow honest, provisional L2 hypotheses from attributed notes while prioritizing original-source review.

## Sole axiom's source loss and archive check

`axioms/AXIOMS.md:18–23` currently marks A01 `needs_review`, last fully verified `2026-10-14T16:07:04Z`. All three support sources and its one counterexample are unavailable. The 15 October Observer log already reported matching local sessions collapsing from **722 to 87**, with all four unavailable (`logs/runs/20261015T161145Z-20261015T160454Z_daily_l1_1b801c-daily-l1-observer.md:3`). That is an inventory discontinuity, not successful backlog consumption. Its cause is not established by this audit.

The separate archive was created on 20 October, after this loss. Its README states that originals were read without modification and it retains 210 Codex/589 Claude conversations. Targeted searches for the four A01 session IDs found **no match** in that archive's Markdown, JSONL index or JSON inventory. No waived historical 43-reference search was reopened.

Primary evidence: `/Users/fanxiaochen/long-term-memory/session-archive/README.md:3,9–11,22,30–38`. This rules out the new exporter moving those originals. It does not prove permanent deletion or exclude an unknown backup.

There is a separate integration limitation: the collector's source locator searches native JSONL inside configured/original roots (`scripts/decision_memory.py:230–254`). The archive keeps rendered Markdown without original row hashes/tool traces; merely adding its directory to native roots would not restore the present verification contract. Future retrieval needs an explicit archive evidence adapter with preserved lineage and clearly reduced verification claims, or source capsules that retain the actual hashed evidence row and bounded context. No such change was made here.

## A substantive unpromoted research-direction hypothesis

The retained record contains a promising theme not represented by the current eight principles:

> Organize computational tools, resources and prediction around the biological explanation and next experimental decision they enable. Do not let the tool or resource substitute for the research question.

This is a **proposed L2 hypothesis**, not a verified axiom or an instruction adopted by the user. It is more specific than “biology first”: it ranks the role of mechanistic explanation, experiment selection, prediction, resource construction, and AI in the investigator's program.

Evidence presently resides in attributed notes:

- UCSD: fundamental questions and scientific impact lead; a resource-heavy revision was corrected (`claude_code_task/Grant application/ERC early/wiki/decisions.md:117–123`). Aim order later put biological discoveries before computational development (`:169`). September 18/20 should initially be treated as one UCSD revision trajectory, not multiple independent confirmations.
- Penn: risk mechanisms first, treatment response an extension (`claude_code_task/Applications/UPenn_CVI/NOTES.md:174–177`). Agent-assisted mechanism prioritization and validation precede predictive modeling (`:1030–1036`). Causal data availability, not architecture alone, is identified as a modeling limitation (`:1048–1054`). October 8/11 could be one continuing Penn program-design trajectory; independence needs original-context review.
- Important boundary: the same notes retain genome-wide resources, computational models, AI agents and prediction as substantive products (`decisions.md:119,135,171,179`; Penn `NOTES.md:1011–1028`). The user is not rejecting tool-building or quantitative prediction.
- The August Piezo “biology-led report” event concerns communication, not automatically a third research-priority episode. It should be a boundary/comparison until original context supports deeper relevance.

The selected quotations remain in current notes, but their retained historical full-file hashes no longer match. Current hashes at this audit: decisions.md `eb2f002eb1fe4ca44057b5c064628b182331c37c0f2806f8f5c4e13b842ae99d`; Penn NOTES.md `ca93ae34ef6448168df50133f3c527ebdc41708e4797ecbc3bd2e9cae333db53`. I read the relevant current sections; this is corroboration, not revalidation of the earlier file versions.

Why useful: a future lab-plan draft should first show which mechanism or physiological question the system resolves and which experiment it changes, then justify the tools. A tool-focused proposal may still be right when that is explicitly the task. Before promotion, recover the actual decisions/annotated investigator inputs, check whether UCSD and Penn are separate choices or reused framing, and identify a later independent test/counterexample. The existing L2 summaries do not document a specific rejection or retirement of this cluster; absence from the eight principles is not proof no agent noticed it.

A second recent trajectory is also promising: slow cold review rejected on 21 October, successful Argon workflow retained optionally on 22 October, then reused for another task on 23 October. It suggests evaluating extra agent steps by demonstrated task benefit, rather than global tool loyalty or a permanent ban. It is recent, partly the same writing lineage, and not 28-day evidence. It should not be forced into an axiom.

## Transparency and future usefulness remain incomplete

The contracts explicitly require a concrete future decision and warn that successful processing is not successful learning (`references/decision_memory.md:145–156`). Current principles do contain predicted choices. The logs offer sensible next actions. I found no retained field or audit result recording a later task, principle actually retrieved, predicted alternative, chosen action, and outcome/user correction. Thus **predictive usefulness is specified, not measured**. A later task happening to agree with the principle does not prove memory caused an improvement.

The generated `AXIOMS.md` routes only A01; candidates remain explicitly unendorsed. This protects against overgeneralization but leaves potentially useful qualified reflections less visible. L2's 18 October record also reports health only in prose/receipts for reflections; automatic per-principle health is retained for A01 alone. Six event supersession links show some trajectory preservation. The 23 October log, however, openly records a newer correction still waiting for a superseding event: the sex-report p-derived difference test was withdrawn after the historical plan was approved. That is a current bounded-collection lag, not evidence the old plan remains current advice (`logs/runs/20261023T161724Z-20261023T160511Z_daily_l1_facdf4-daily-l1-observer.md:3`).

High-value next changes would be: a short per-layer dashboard with last real run/coverage/health; explicit semantic episode grouping; provisional research-priority hypotheses with open evidence questions; archival evidence integration; and one lightweight follow-through record when a relevant principle is used or contradicted. These are recommendations only. Source-loss and measurement gaps should take priority over increasing the number of axioms.

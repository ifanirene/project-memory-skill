# Personal Memory Bridge

Use the existing external workspace for authorized personal and cross-project
memory. Repositories retain their project notes and decisions; the external
workspace owns comparison across episodes. Do not create a second repo-local
memory file or copy full dialogues.

## Distinct outcomes

Project memory answers what the project found and what to trust. Personal memory
answers how the investigator chose among plausible alternatives and how that
judgment developed. A source may serve both, but an agent-written project lesson
is not automatically evidence of a personal belief.

The repo ladder remains branch note → reusable repo lesson. The personal ladder
is first attributable decision → recurring bounded pattern → stable principle.
Do not require cross-repo recurrence before recording a first observation.

## Loop ownership

- L1 Observer: daily completed-dialog tails and changed decision-bearing notes;
  capture choices, costs, corrections, rejection and uncertainty.
- L2 Reflector: weekly comparison of independent human decision episodes,
  including counterexamples, changed context and unprocessed history.
- L3 Axiom: monthly eligibility review without blocking L1/L2; three independent
  human episodes over at least 28 days for automatic promotion. Explicit
  endorsement is evidence to review, not permission to invent generality.
- Document collector/maintenance: separate operational queue, never counted as
  repeated human confirmation merely because an agent followed its instructions.

Use [decision_memory.md](decision_memory.md) and `scripts/decision_memory.py` for
source collection, attribution validation, an atomic decision ledger and views.
Use `scripts/memoryctl.py` only for the existing repo-documentation queue.

## Evidence and trajectory

Record context, alternatives, choice, stated reason, accepted cost, attribution,
source path/session/message boundary/hash, date, scope, uncertainty and next test.
Mark unstated motives as inference. Copies, regenerated notes, forked messages,
subagent output, and automation replays remain one source lineage.

Direct user corrections are especially informative when they select a priority
over another plausible option. Preserve changes of mind with the previous choice,
what changed, and the new scope. Do not replace a trajectory with a timeless slogan.
Missing original sources lower confidence; a summary cannot repair lost evidence.

Repo notes can contain user-attributed decisions without being global personal
memory. Preserve those records during cleanup. External writes follow the user's
authorization; an authorized scheduled personal-memory workflow can operate within
its registered scope without asking for approval for every observation.

## Retrieval and mirrors

Keep active principles indexed by the decisions they help make. Load only relevant
ones and subordinate them to current instructions and evidence. A candidate is
not an endorsed preference. Never silently inject an unreviewed personal inference
into all projects.

Mirror an established principle to `docs/LESSONS.md` only when a repo-facing
Default, Check, Trap or Preference would change future work in that repo. Keep
source lineage, scope and exceptions. The mirror is not an independent confirmation.
Personal-only principles stay external. Operations remain operations unless the
user explicitly endorses them as a personal decision rule.

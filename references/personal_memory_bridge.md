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

The repo ladder remains branch note → reusable repo lesson. Personal memory
distinguishes decision evidence (L1), usable working principles (L2), and proposed
core commitments (L3). One meaningful judgment can support L2 when its reusable
reasoning and boundaries are clear. A specific arrangement can remain a case.

## Loop ownership

- L1 Observer: daily completed-dialog tails and changed decision-bearing notes;
  capture choices, costs, corrections, rejection and uncertainty.
- L2 Reflector: weekly comparison of independent human decision episodes,
  including counterexamples, changed context, useful applications, and corrections.
  Maintain the readable library and summarize meaningful additions and changes.
- L3 core commitments: monthly interpretation of values and outlook, reviewed
  with the user. Frequency and elapsed time do not establish depth. Do not
  automatically promote technical rules into core values.
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

Setup and task instructions are reproducible from
[personal_memory_workflows.md](personal_memory_workflows.md). Use `task-context`
with selected stable IDs to check current evidence and load full documents.
Record material use or correction in a registered project note, so the existing
daily collector can bring it back into evidence review. No separate use ledger is needed.

Start at `principles/INDEX.md` in the configured workspace. Open only relevant
principle documents, not the whole library or generated evidence history. L2 is
available without individual approval; current instructions and evidence prevail.
Origin and tentative scope stay inside each document. A candidate is not an
endorsed preference. Do not turn tentative guidance into global instructions.
See [the library guidance](decision_memory.md#working-principle-library) for the
shared format, merging, and brief feedback in existing project notes.

Mirror an established principle to `docs/LESSONS.md` only when a repo-facing
Default, Check, Trap or Preference would change future work in that repo. Keep
source lineage, scope and exceptions. The mirror is not an independent confirmation.
Personal-only principles stay external. Operations remain operations unless the
user explicitly endorses them as a personal decision rule.

# Plan 002: Make the skill genuinely shareable (portable paths, harness-neutral naming, LICENSE)

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan in
> `plans/README.md`.
>
> **Drift check (run first)**:
> `git diff --stat c320c14..HEAD -- SKILL.md README.md references/ templates/AGENTS.md`
> If Plan 001 has already run, `SKILL.md` frontmatter will differ from
> c320c14 — that is expected and fine; this plan does not touch the frontmatter.
> For every other file, locate each edit target by the **quoted text** in
> "Current state" (not by line number) before changing it. If a quoted string
> cannot be found at all, treat it as a STOP condition.

## Status

- **Review 2026-10-03**: PARTIAL. Shared live-test examples now use `<memory-workspace>`. Private
  scheduled-job paths are preserved. Codex-specific setup and licensing remain
  open; the full portability plan is not complete.
  See the [current review](README.md#current-review--2026-10-03).

- **Priority**: P1
- **Effort**: M
- **Risk**: MED (touches many docs; risk is leaving a broken command or a
  half-renamed reference, not data loss)
- **Depends on**: 001 (shares `SKILL.md`; run 001 first so there is a single
  writer at a time)
- **Category**: docs / dx (portability)
- **Planned at**: commit `c320c14`, 2026-07-11
- **Addresses**: Findings 2, 3, 6 (design review)

## Why this matters

The skill's headline promise is that it is **shareable**, but three things make
it not actually portable to anyone but the author:

1. **Finding 2** — 8 documented commands hardcode
   `python "$CODEX_HOME/skills/project-memory/scripts/..."`. `$CODEX_HOME` is an
   OpenAI-Codex-only variable; in Claude Code (where this skill also runs) it is
   undefined and the install path differs, so every copy-paste command silently
   breaks. The prose also calls it a "Codex skill" (20 mentions) even though it
   ships in the harness-neutral Agent-Skill `SKILL.md` format.
2. **Finding 3** — the live-maintenance-test prompt hardcodes the author's
   private absolute path `/Volumes/IF_PHAGE/long-term-memory` as "the production
   collector," which is meaningless (and leaks local layout) for any other user.
3. **Finding 6** — the README's "Sharing Notes" tells the reader to choose a
   license "before publishing publicly," but no `LICENSE` file exists, so the
   repo is not legally redistributable.

After this plan, every command works regardless of harness, no private path
appears, the prose is harness-neutral, and the repo carries a license.

## Current state

Files and the exact strings to change (find each by text, not line number):

- `SKILL.md` — skill body. Contains one `$CODEX_HOME` command and two
  "Codex dialogs" references:
  - `python "$CODEX_HOME/skills/project-memory/scripts/smoke_test_project_memory.py" \`
  - `` - `NOTES.md`, `docs/LESSONS.md`, explicit user corrections, and Codex dialogs ``
  - `Store source pointers and distilled extracts from Codex dialogs; do not mirror`
- `README.md` — user-facing readme. Contains:
  - line ~3: `Shareable Codex skill for setting up durable repo memory in long-lived research,`
  - `- accepted or rejected solution patterns from Codex dialogs`
  - `- Distill, do not copy: raw Codex dialog logs and one-off session chatter stay`
  - two bootstrap commands and one smoke command using `$CODEX_HOME/skills/project-memory/scripts/...`
  - `Ask Codex to run the real maintenance workflow and leave its changes for`
  - inside a fenced prompt block: `production collector at /Volumes/IF_PHAGE/long-term-memory. Take real semantic`
  - the Install section: `Copy this folder into your Codex skills directory as `project-memory`:` followed by
    `mkdir -p "$CODEX_HOME/skills"` and `cp -R project-memory-skill "$CODEX_HOME/skills/project-memory"`
  - `Ask Codex to use the skill when you want to:`
  - the Sharing Notes section (last section): `Before publishing publicly, choose the license you want to use for your copy.`
- `references/doc_contract.md` — one bootstrap command using `$CODEX_HOME/...`.
- `references/personal_memory_bridge.md` — three "Codex dialogs" mentions:
  `..., troubleshooting strategies, and Codex dialogs.`, `- Codex dialogs`,
  `Distill Codex dialogs. Do not copy raw session bodies.`
- `references/live_maintenance_test.md` — heading `## Copy-ready Codex prompt`
  and a fenced prompt with `production collector at /Volumes/IF_PHAGE/long-term-memory. Take real semantic`.
- `templates/AGENTS.md` — the validate command that gets scaffolded into user
  repos:
  `` `python "$CODEX_HOME/skills/project-memory/scripts/validate_analysis_manifest.py" --repo .`. ``

**Convention to adopt** (used consistently by every edit below):
- Script invocations use a `SKILL_DIR` shell variable the reader sets once to
  their install path, e.g. `python "$SKILL_DIR/scripts/<script>.py" ...`.
- Install uses a `SKILLS_DIR` variable, harness-neutral.
- The author's private path becomes the placeholder `/path/to/long-term-memory`
  (the README already uses `/path/to/repo` elsewhere — match that style).
- "Codex" (as the assistant) becomes "your agent"; "Codex dialogs" becomes
  "agent dialogs". Leave `agents/openai.yaml` and the word "Codex" inside it
  untouched — that file is a legitimate Codex-specific adapter (see Out of
  scope).

## Commands you will need

| Purpose | Command | Expected on success |
|---------|---------|---------------------|
| No CODEX_HOME left in docs | `grep -rn 'CODEX_HOME' . --include='*.md'` | no output (exit 1) |
| No private path left | `grep -rn '/Volumes/IF_PHAGE' . --include='*.md'` | no output (exit 1) |
| No stray "Codex" as assistant | `grep -rin 'codex' . --include='*.md'` | no output (exit 1) |
| LICENSE exists | `test -f LICENSE && head -1 LICENSE` | prints `MIT License` |
| Regression: tests still pass | `uv run --no-project --with pytest python -m pytest tests/ -q` | `15 passed` |

(`grep` exits non-zero when there are no matches; "no output" is success here.)

## Scope

**In scope** (the only files you should modify):
- `SKILL.md` (body only — not the frontmatter)
- `README.md`
- `references/doc_contract.md`
- `references/personal_memory_bridge.md`
- `references/live_maintenance_test.md`
- `templates/AGENTS.md`
- `LICENSE` (create)

**Out of scope** (do NOT touch, even though they look related):
- `agents/openai.yaml` — this is the OpenAI-Codex adapter manifest; its
  `$project-memory` prompt and Codex framing are correct *for that adapter*.
  Renaming it would break Codex installs. Leave it exactly as-is.
- Any Python file under `scripts/` — the scripts already self-locate via
  `Path(__file__)`; this is a docs-only portability fix. Do not edit code.
- The `SKILL.md` frontmatter (Plan 001 owns it).
- Do not restructure or de-duplicate any content — that is Plan 003. Only make
  the minimal string substitutions specified here.

## Git workflow

- Branch: `advisor/002-make-shareable`
- Commit in logical units (e.g. one commit for path/command portability, one
  for naming, one for LICENSE) or a single commit — your choice. Message style
  matches repo `git log` (e.g. `Make project-memory skill portable and add
  license`).
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Replace `$CODEX_HOME` script paths with a `SKILL_DIR` convention

In `SKILL.md`, `README.md`, `references/doc_contract.md`, and
`templates/AGENTS.md`, replace every occurrence of the literal path prefix
`$CODEX_HOME/skills/project-memory` with `$SKILL_DIR` **inside script-invocation
commands**. Concretely, each command of the form

```bash
python "$CODEX_HOME/skills/project-memory/scripts/<script>.py" ...
```

becomes

```bash
python "$SKILL_DIR/scripts/<script>.py" ...
```

Then, at the **first** such command in `SKILL.md` and the **first** in
`README.md`, add a one-line note immediately above the code fence:

> Set `SKILL_DIR` to wherever you installed this skill (for example
> `~/.claude/skills/project-memory` or your agent's equivalent).

For `templates/AGENTS.md`, the validate line becomes (keep the surrounding
bullet wording):

```
  `python "$SKILL_DIR/scripts/validate_analysis_manifest.py" --repo .` (where
  `$SKILL_DIR` is your project-memory install path).
```

**Verify**: `grep -rn 'CODEX_HOME' . --include='*.md'` → no output.
**Verify**: `grep -rc 'SKILL_DIR' SKILL.md README.md references/doc_contract.md templates/AGENTS.md` → each file reports ≥ 1.

### Step 2: Rewrite the Install section to be harness-neutral

In `README.md`, replace the Install prose + command block. The block currently
reads (find by text):

```
Copy this folder into your Codex skills directory as `project-memory`:

​```bash
mkdir -p "$CODEX_HOME/skills"
cp -R project-memory-skill "$CODEX_HOME/skills/project-memory"
​```
```

Replace with:

```
Copy this folder into your agent's skills directory as `project-memory`
(Claude Code uses `~/.claude/skills`; other agents use their own skills path):

​```bash
SKILLS_DIR="$HOME/.claude/skills"   # set to your agent's skills directory
mkdir -p "$SKILLS_DIR"
cp -R project-memory-skill "$SKILLS_DIR/project-memory"
​```
```

(The `​```` fences above are literal triple backticks in the file — keep them.)

**Verify**: `grep -n 'SKILLS_DIR' README.md` → at least 2 matches.

### Step 3: Remove the hardcoded private path

In `README.md` and `references/live_maintenance_test.md`, inside the copy-ready
prompt block, replace:

```
production collector at /Volumes/IF_PHAGE/long-term-memory. Take real semantic
```

with:

```
production collector at /path/to/long-term-memory. Take real semantic
```

**Verify**: `grep -rn '/Volumes/IF_PHAGE' . --include='*.md'` → no output.

### Step 4: Neutralize "Codex" assistant naming

Make these substitutions (assistant references only). In each file, change the
word **Codex** to **your agent** / **agent** as it reads naturally:

- `SKILL.md`:
  - `... explicit user corrections, and Codex dialogs` → `... explicit user corrections, and agent dialogs`
  - `Store source pointers and distilled extracts from Codex dialogs;` → `Store source pointers and distilled extracts from agent dialogs;`
- `README.md`:
  - `Shareable Codex skill for setting up durable repo memory` → `Shareable agent skill for setting up durable repo memory`
  - `raw Codex dialog logs` → `raw agent dialog logs`
  - `accepted or rejected solution patterns from Codex dialogs` → `accepted or rejected solution patterns from agent dialogs`
  - `Ask Codex to run the real maintenance workflow` → `Ask your agent to run the real maintenance workflow`
  - `Ask Codex to use the skill when you want to:` → `Ask your agent to use the skill when you want to:`
- `references/personal_memory_bridge.md`:
  - `troubleshooting strategies, and Codex dialogs.` → `troubleshooting strategies, and agent dialogs.`
  - `- Codex dialogs` → `- agent dialogs`
  - `Distill Codex dialogs. Do not copy raw session bodies.` → `Distill agent dialogs. Do not copy raw session bodies.`
- `references/live_maintenance_test.md`:
  - heading `## Copy-ready Codex prompt` → `## Copy-ready prompt`

**Verify**: `grep -rin 'codex' . --include='*.md'` → no output.

### Step 5: Add a LICENSE file

Create `LICENSE` at the repo root with the MIT license text below. MIT is the
conventional default for shareable developer tooling; the operator may swap it
before publishing (see Maintenance notes).

```
MIT License

Copyright (c) 2026 ifanirene

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Then, in `README.md`, update the Sharing Notes section. Replace:

```
This repo contains a rewritten, shareable implementation of the skill and its
reference templates. Before publishing publicly, choose the license you want to
use for your copy.
```

with:

```
This repo contains a rewritten, shareable implementation of the skill and its
reference templates. It is released under the MIT License (see `LICENSE`).
```

**Verify**: `test -f LICENSE && head -1 LICENSE` → `MIT License`.
**Verify**: `grep -n 'MIT License' README.md` → 1 match.

### Step 6: Regression check

**Verify**: `uv run --no-project --with pytest python -m pytest tests/ -q` → `15 passed`.

## Test plan

This is a docs/portability change with no unit-testable logic. Verification is
the grep gates in each step plus:

- The full suite still passes (no accidental edit to a script/template that a
  test reads): `uv run --no-project --with pytest python -m pytest tests/ -q` →
  `15 passed`.
- Manual spot-check: pick one edited command, set `SKILL_DIR` to the repo root,
  and confirm it runs, e.g.
  `SKILL_DIR=$PWD python "$SKILL_DIR/scripts/validate_analysis_manifest.py" --repo .`
  → prints `No analysis_manifest.json files found.` (exit 0).

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `grep -rn 'CODEX_HOME' . --include='*.md'` → no output.
- [ ] `grep -rn '/Volumes/IF_PHAGE' . --include='*.md'` → no output.
- [ ] `grep -rin 'codex' . --include='*.md'` → no output.
- [ ] `test -f LICENSE && head -1 LICENSE` → `MIT License`.
- [ ] `grep -n 'MIT License' README.md` → 1 match.
- [ ] `SKILL_DIR=$PWD python "$SKILL_DIR/scripts/validate_analysis_manifest.py" --repo .` exits 0.
- [ ] `uv run --no-project --with pytest python -m pytest tests/ -q` → `15 passed`.
- [ ] `git status --porcelain` shows only the seven in-scope files (six modified
      + `LICENSE` added), nothing else.
- [ ] `plans/README.md` status row for 002 updated to DONE.

## STOP conditions

Stop and report back (do not improvise) if:

- Any quoted "Current state" string cannot be found in its file (drift, or an
  earlier plan already changed it in a way this plan didn't anticipate).
- `grep -rin 'codex'` still returns matches that are **not** the assistant name
  and **not** in `agents/openai.yaml` — e.g. a new meaning of "Codex" you are
  unsure how to neutralize. Report the lines instead of guessing.
- The operator has indicated they want a license other than MIT, or the
  copyright holder is not `ifanirene` — pause on Step 5 and ask, since license
  choice and the copyright name are legal decisions.

## Maintenance notes

- **License is a real decision.** MIT is a safe default for shareable tooling,
  but the operator may prefer Apache-2.0 (patent grant) or a proprietary/no
  license. The copyright line uses `ifanirene` (the repo's git user); update it
  to the legal name/entity before publishing. Flag this in the PR description.
- A reviewer should verify no command was left half-substituted (e.g. a
  `$SKILL_DIR` path with a stray `skills/project-memory` segment still in it).
- `agents/openai.yaml` intentionally still says "Codex"; that is correct. If the
  project later adds a Claude-specific adapter, mirror it as a sibling file
  rather than editing the OpenAI one.

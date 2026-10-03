# Plan 005: Make the documented manifest schema match (and be tested against) the validator

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan in
> `plans/README.md`.
>
> **Drift check (run first)**:
> `git diff --stat c320c14..HEAD -- references/analysis_manifest.md scripts/validate_analysis_manifest.py tests/test_validate_analysis_manifest.py`
> If any of these changed since c320c14, compare the "Current state" excerpts to
> the live files before editing. On a mismatch you can't reconcile, STOP.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none (independent of the doc-portability chain; can run in
  parallel with Plans 001–004 and 006)
- **Category**: correctness / tests
- **Planned at**: commit `c320c14`, 2026-07-11
- **Addresses**: Finding 7 (design review)

## Why this matters

The skill ships a manifest **validator** (`validate_analysis_manifest.py`) and a
**documented "Required schema"** example in `references/analysis_manifest.md`.
They disagree: the documented example declares `"provenance_mode": "native"`
with `"script_sha256": "<64-character sha256>"`, but for native manifests the
validator requires a real 64-character hex digest — so **the skill's own
canonical example fails the skill's own validator**. Confirmed:

```
$ python scripts/validate_analysis_manifest.py <the documented example>
INVALID
- native execution.script_sha256 must be a SHA-256 hex digest
```

A user who copies the documented schema and runs the recommended validation
command gets an error on the reference itself. Separately, the example lists a
`relationships` field inside the "Required schema" block, but the validator
never requires it — so "required" is misleading.

This plan (1) makes the documented example a genuinely valid native manifest,
(2) clarifies which top-level fields are actually required, and (3) adds a
regression test that extracts the documented example and asserts it validates —
so the doc and the validator can never silently drift apart again.

## Current state

- `scripts/validate_analysis_manifest.py` — the validator. Relevant rule (do not
  change it): for `provenance_mode == "native"`, a present `script_sha256` must
  be exactly 64 hex characters, else it reports
  `native execution.script_sha256 must be a SHA-256 hex digest`. Its
  `TOP_LEVEL_FIELDS` required set is: `schema_version, analysis_id, variant_id,
  created_at, provenance_mode, execution, inputs, parameters, outputs,
  validation` — note `relationships` is **not** in it.
- `references/analysis_manifest.md` — under `## Required schema` it has a
  ```` ```json ```` block. The offending line is:

```
    "script_sha256": "<64-character sha256>",
```

  and the block also contains a trailing `"relationships": { ... }` object. The
  block is followed by the paragraph beginning `Record resolved parameters,
  including defaults, ...`.
- `tests/test_validate_analysis_manifest.py` — two tests today, both invoking
  the validator via `subprocess` (see `test_valid_manifest_passes`). Model the
  new test on that structure.

## Commands you will need

| Purpose | Command | Expected on success |
|---------|---------|---------------------|
| Doc example now validates | `python3 -c "import json,re,subprocess,sys,pathlib,tempfile; b=re.search(r'\`\`\`json\n(.*?)\n\`\`\`', pathlib.Path('references/analysis_manifest.md').read_text(), re.S).group(1); f=tempfile.NamedTemporaryFile('w',suffix='.json',delete=False); f.write(b); f.close(); r=subprocess.run([sys.executable,'scripts/validate_analysis_manifest.py',f.name],capture_output=True,text=True); print(r.stdout.strip()); sys.exit(r.returncode)"` | prints `VALID ...`, exit 0 |
| Full suite (now 16) | `uv run --no-project --with pytest python -m pytest tests/ -q` | `16 passed` |
| Just the manifest tests | `uv run --no-project --with pytest python -m pytest tests/test_validate_analysis_manifest.py -q` | `3 passed` |

If `uv` is unavailable: `pip install pytest`, then use `python3 -m pytest`.

## Scope

**In scope** (the only files you should modify):
- `references/analysis_manifest.md`
- `tests/test_validate_analysis_manifest.py`

**Out of scope** (do NOT touch):
- `scripts/validate_analysis_manifest.py` — the validator is correct; the doc is
  what's wrong. Do not weaken the 64-hex rule to make the bad example pass.
- `templates/AGENTS.md`, `SKILL.md` — they reference the manifest rule but carry
  no full JSON example; leave them to the other plans.

## Git workflow

- Branch: `advisor/005-manifest-schema-ssot`
- One commit. Message style matches repo `git log`
  (e.g. `Fix documented manifest example and test it against the validator`).
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Make the documented example a valid native manifest

In `references/analysis_manifest.md`, inside the `## Required schema` ```` ```json ````
block, replace the line:

```
    "script_sha256": "<64-character sha256>",
```

with (this is the real SHA-256 of the empty string — a genuine 64-hex digest,
so the example validates as-is):

```
    "script_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
```

Leave the other bracketed placeholders (`"<commit sha>"`,
`"/absolute/path/to/python"`, input `"path"`, etc.) unchanged — the validator
accepts them as non-empty strings.

**Verify**: run the "Doc example now validates" command → prints `VALID`, exit 0.

### Step 2: Clarify required vs optional fields

In `references/analysis_manifest.md`, immediately **after** the closing ```` ``` ````
of the `## Required schema` JSON block and **before** the paragraph beginning
`Record resolved parameters, including defaults,`, insert this note:

```
The validator (`validate_analysis_manifest.py`) requires exactly these
top-level fields: `schema_version`, `analysis_id`, `variant_id`, `created_at`,
`provenance_mode`, `execution`, `inputs`, `parameters`, `outputs`,
`validation`. The `relationships` object shown above is optional provenance
that pipelines may add; it is not required. The one bound value is
`execution.script_sha256`, which must be a 64-character hex digest when
`provenance_mode` is `native`.
```

**Verify**: `grep -c 'requires exactly these' references/analysis_manifest.md` → `1`.

### Step 3: Add a regression test that ties the doc to the validator

Append this test to `tests/test_validate_analysis_manifest.py` (it reuses the
module-level `SCRIPT` constant already defined at the top of the file):

```python
def test_documented_example_validates(tmp_path: Path) -> None:
    """The JSON example in references/analysis_manifest.md must pass the
    validator, so the documented schema and the validator cannot drift."""
    import re

    doc = (
        Path(__file__).resolve().parents[1]
        / "references"
        / "analysis_manifest.md"
    ).read_text()
    match = re.search(r"```json\n(.*?)\n```", doc, re.S)
    assert match, "no ```json block found in references/analysis_manifest.md"
    example = json.loads(match.group(1))
    path = tmp_path / "analysis_manifest.json"
    path.write_text(json.dumps(example))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout
    assert "VALID" in result.stdout
```

**Verify**: `uv run --no-project --with pytest python -m pytest tests/test_validate_analysis_manifest.py -q` → `3 passed`.

### Step 4: Full regression

**Verify**: `uv run --no-project --with pytest python -m pytest tests/ -q` → `16 passed`.

## Test plan

- New test: `test_documented_example_validates` in
  `tests/test_validate_analysis_manifest.py`, modeled on the existing
  `test_valid_manifest_passes` (subprocess invocation of the validator). It
  covers the exact regression this plan fixes: the documented example must
  validate. It will keep failing if anyone reintroduces an invalid placeholder
  into the doc's `json` block.
- Existing tests must still pass unchanged.
- Verification: `uv run --no-project --with pytest python -m pytest tests/ -q` →
  `16 passed` (15 prior + 1 new).

## Done criteria

Machine-checkable. ALL must hold:

- [ ] The "Doc example now validates" command prints `VALID` and exits 0.
- [ ] `grep -c 'script_sha256": "<64-character sha256>"' references/analysis_manifest.md` → `0` (placeholder gone).
- [ ] `grep -c 'requires exactly these' references/analysis_manifest.md` → `1`.
- [ ] `uv run --no-project --with pytest python -m pytest tests/ -q` → `16 passed`.
- [ ] `git status --porcelain` shows only `references/analysis_manifest.md` and
      `tests/test_validate_analysis_manifest.py` modified.
- [ ] `plans/README.md` status row for 005 updated to DONE.

## STOP conditions

Stop and report back (do not improvise) if:

- The `## Required schema` `json` block has no `script_sha256` line, or has more
  than one `` ```json `` block (the extraction regex takes the first — confirm
  it's the schema example, not something a later plan added).
- Making the example valid appears to require changing the validator — it does
  not; if you believe it does, STOP (you may be editing the wrong field).
- The new test fails for a reason other than the placeholder (e.g. the block
  isn't valid JSON) — report the parse error.

## Maintenance notes

- After this lands, the documented schema is enforced by a test. If a future
  change intentionally alters the required field set, update **both** the
  validator's `TOP_LEVEL_FIELDS` and the doc note in Step 2, and the test will
  confirm they agree.
- The chosen digest is the SHA-256 of the empty string — recognizable as
  illustrative to a careful reader while still being a valid 64-hex value. If
  you prefer, any 64-hex string works.
- Reviewer should check that no real secret or hash from an actual run was
  pasted in — the example must stay synthetic.

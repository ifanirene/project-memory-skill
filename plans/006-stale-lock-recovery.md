# Plan 006: Add stale-lock recovery to memoryctl's workspace lock

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan in
> `plans/README.md`.
>
> **Drift check (run first)**:
> `git diff --stat c320c14..HEAD -- scripts/memoryctl.py tests/test_memoryctl.py`
> If either changed since c320c14, compare the "Current state" excerpt of
> `workspace_lock` against the live code before editing. On a mismatch, STOP.

## Status

- **Priority**: P3
- **Effort**: S–M
- **Risk**: LOW-MED (concurrency code; the change only *adds* a reclaim path for
  provably-dead/expired locks and is covered by new tests)
- **Depends on**: none (independent of every other plan; touches only
  `scripts/memoryctl.py` and `tests/test_memoryctl.py`)
- **Category**: dx / robustness
- **Planned at**: commit `c320c14`, 2026-07-11
- **Addresses**: Finding 8 (design review). Only relevant while the collector
  automation is retained (see Plan 004).

## Why this matters

`memoryctl` serializes runs with an exclusive lock file
(`state/memoryctl.lock`, created `O_CREAT | O_EXCL`). If a run **crashes or is
killed**, the lock file is never removed, and *every* future run fails
permanently with "Another memoryctl run owns …" — there is no automatic
recovery and no `--force`. For an unattended weekly/monthly collector, one
killed process wedges all subsequent runs until a human manually deletes the
file. This plan makes lock acquisition reclaim a lock **only** when its owner is
provably gone: the recorded PID is no longer alive, or the lock is older than a
safety timeout, or its payload is unreadable. A live, recent lock is still
respected exactly as today.

## Current state

- `scripts/memoryctl.py` — the deterministic controller. It already imports
  `os`, `json`, and `from datetime import datetime, timedelta, timezone`, and
  defines `utc_now()`, `canonical_json_bytes()`, and the `MemoryCtlError`
  exception. Module constants end with `NOTE_REWRITE_BRIEF_FIELDS = { ... }`.
  The lock is:

```python
@contextmanager
def workspace_lock(workspace: Path) -> Iterable[None]:
    lock_path = workspace / "state" / "memoryctl.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise MemoryCtlError(
            f"Another memoryctl run owns {lock_path}; inspect it before retrying"
        ) from exc
    try:
        payload = {
            "pid": os.getpid(),
            "started_at": utc_now().isoformat(),
        }
        os.write(fd, canonical_json_bytes(payload))
        os.close(fd)
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
```

- `workspace_lock` is used by `command_collect`, `command_apply`,
  `command_queue_claim`, and `command_queue_finish` as
  `with workspace_lock(workspace):`. The new signature keeps a default argument,
  so those call sites need no change.
- `tests/test_memoryctl.py` — currently defines **7** tests and a
  `make_workspace(tmp_path)` helper that creates `workspace/state/` and a
  registry, plus a `run_memoryctl(*args)` subprocess helper. Model new tests on
  the existing `test_doctor_and_incremental_collection`.

## Commands you will need

| Purpose | Command | Expected on success |
|---------|---------|---------------------|
| memoryctl tests (now 10) | `uv run --no-project --with pytest python -m pytest tests/test_memoryctl.py -q` | `10 passed` |
| Full suite still green | `uv run --no-project --with pytest python -m pytest tests/ -q` | all pass (count = prior + 3) |
| Byte-compile check | `python3 -m py_compile scripts/memoryctl.py` | exit 0, no output |

If `uv` is unavailable: `pip install pytest`, then `python3 -m pytest`.

## Scope

**In scope** (the only files you should modify):
- `scripts/memoryctl.py` — add one constant, one helper, and rewrite
  `workspace_lock`.
- `tests/test_memoryctl.py` — add three tests.

**Out of scope** (do NOT touch):
- The four command functions that call `workspace_lock` — no changes needed.
- Any other locking or state logic (cursors, queue, atomic writes).
- No new CLI flag. Automatic staleness recovery replaces the need for `--force`;
  a manual override is deferred (Maintenance notes).

## Git workflow

- Branch: `advisor/006-stale-lock-recovery`
- One commit. Message style matches repo `git log`
  (e.g. `Reclaim stale memoryctl locks from dead or expired runs`).
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Add the staleness timeout constant

In `scripts/memoryctl.py`, immediately after the
`NOTE_REWRITE_BRIEF_FIELDS = { ... }` block, add:

```python
# A lock older than this, or owned by a dead PID, is treated as abandoned.
LOCK_MAX_AGE_MINUTES = 360
```

**Verify**: `grep -c 'LOCK_MAX_AGE_MINUTES' scripts/memoryctl.py` → `2` (the
definition here and its use in Step 3).

### Step 2: Add the `_lock_is_stale` helper

Immediately **above** the `@contextmanager` line of `workspace_lock`, add:

```python
def _lock_is_stale(payload: dict[str, Any], max_age: timedelta) -> bool:
    """True when a lock's owner is provably gone: bad payload, dead PID, or age
    beyond max_age. Conservative — a live, recent, well-formed lock is not stale."""
    pid = payload.get("pid")
    if not isinstance(pid, int):
        return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        pass  # Process exists but is owned by another user; treat as alive.
    except (OverflowError, OSError):
        return True
    started_at = payload.get("started_at")
    if not isinstance(started_at, str):
        return True
    try:
        started = datetime.fromisoformat(started_at)
        if started.tzinfo is None:
            return True
        return (utc_now() - started) > max_age
    except (ValueError, TypeError):
        return True
```

**Verify**: `python3 -m py_compile scripts/memoryctl.py` → exit 0.

### Step 3: Rewrite `workspace_lock` to reclaim stale locks

Replace the entire `workspace_lock` function shown in "Current state" with:

```python
@contextmanager
def workspace_lock(
    workspace: Path, *, max_age_minutes: int = LOCK_MAX_AGE_MINUTES
) -> Iterable[None]:
    lock_path = workspace / "state" / "memoryctl.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    max_age = timedelta(minutes=max_age_minutes)

    def acquire() -> int:
        return os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)

    try:
        fd = acquire()
    except FileExistsError as exc:
        try:
            existing = json.loads(lock_path.read_text())
        except (OSError, json.JSONDecodeError):
            existing = {}
        if not _lock_is_stale(existing, max_age):
            raise MemoryCtlError(
                f"Another memoryctl run owns {lock_path} "
                f"(pid {existing.get('pid')}, started {existing.get('started_at')}); "
                "inspect it before retrying, or wait for it to finish"
            ) from exc
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
        try:
            fd = acquire()
        except FileExistsError as exc2:
            raise MemoryCtlError(
                f"Stale lock at {lock_path} was reclaimed by another run; retry"
            ) from exc2
    try:
        payload = {
            "pid": os.getpid(),
            "started_at": utc_now().isoformat(),
        }
        os.write(fd, canonical_json_bytes(payload))
        os.close(fd)
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
```

**Verify**: `python3 -m py_compile scripts/memoryctl.py` → exit 0.

### Step 4: Add tests

Append these three tests to `tests/test_memoryctl.py`. They use the existing
`make_workspace` and `run_memoryctl` helpers already defined at the top of that
file (do not redefine them). If either helper's name differs in the live file,
STOP and report.

```python
def _write_lock(workspace: Path, pid: int, started_at: str) -> Path:
    lock_path = workspace / "state" / "memoryctl.lock"
    lock_path.write_text(json.dumps({"pid": pid, "started_at": started_at}))
    return lock_path


def test_collect_reclaims_lock_from_dead_pid(tmp_path: Path) -> None:
    from datetime import datetime, timezone

    workspace, _ = make_workspace(tmp_path)
    # 999999999 is a valid int PID that is not a live process.
    _write_lock(workspace, 999999999, datetime.now(timezone.utc).isoformat())
    result = run_memoryctl(
        "collect",
        "--workspace",
        str(workspace),
        "--output",
        str(workspace / "runs" / "packet.json"),
        "--quality-audit-files",
        "0",
    )
    assert result.returncode == 0, result.stderr


def test_collect_reclaims_expired_lock_from_live_pid(tmp_path: Path) -> None:
    import os
    from datetime import datetime, timedelta, timezone

    workspace, _ = make_workspace(tmp_path)
    old = (datetime.now(timezone.utc) - timedelta(hours=10)).isoformat()
    # This test's own PID is alive, but the lock is far past the age limit.
    _write_lock(workspace, os.getpid(), old)
    result = run_memoryctl(
        "collect",
        "--workspace",
        str(workspace),
        "--output",
        str(workspace / "runs" / "packet.json"),
        "--quality-audit-files",
        "0",
    )
    assert result.returncode == 0, result.stderr


def test_collect_respects_live_recent_lock(tmp_path: Path) -> None:
    import os
    from datetime import datetime, timezone

    workspace, _ = make_workspace(tmp_path)
    # Alive PID + recent timestamp → held; the run must refuse.
    _write_lock(workspace, os.getpid(), datetime.now(timezone.utc).isoformat())
    result = run_memoryctl(
        "collect",
        "--workspace",
        str(workspace),
        "--output",
        str(workspace / "runs" / "packet.json"),
        "--quality-audit-files",
        "0",
    )
    assert result.returncode == 2
    assert "owns" in result.stderr
```

**Verify**: `uv run --no-project --with pytest python -m pytest tests/test_memoryctl.py -q` → `10 passed`.

### Step 5: Full regression

**Verify**: `uv run --no-project --with pytest python -m pytest tests/ -q` → all pass.

## Test plan

- Three new tests in `tests/test_memoryctl.py`, modeled on the existing
  subprocess-based tests:
  - `test_collect_reclaims_lock_from_dead_pid` — dead PID → lock reclaimed, run
    succeeds (the core crash-recovery case).
  - `test_collect_reclaims_expired_lock_from_live_pid` — live PID but past the
    age limit → reclaimed (guards hung runs and PID reuse).
  - `test_collect_respects_live_recent_lock` — live PID + recent → still
    refused (proves the fix did not weaken real mutual exclusion).
- Existing 7 memoryctl tests must still pass.
- Verification: `uv run --no-project --with pytest python -m pytest tests/test_memoryctl.py -q` → `10 passed`.

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `python3 -m py_compile scripts/memoryctl.py` → exit 0.
- [ ] `grep -c 'LOCK_MAX_AGE_MINUTES' scripts/memoryctl.py` → `2`.
- [ ] `grep -c '_lock_is_stale' scripts/memoryctl.py` → `2` (definition + use).
- [ ] `uv run --no-project --with pytest python -m pytest tests/test_memoryctl.py -q` → `10 passed`.
- [ ] `uv run --no-project --with pytest python -m pytest tests/ -q` → all pass.
- [ ] `git status --porcelain` shows only `scripts/memoryctl.py` and
      `tests/test_memoryctl.py` modified.
- [ ] `plans/README.md` status row for 006 updated to DONE.

## STOP conditions

Stop and report back (do not improvise) if:

- The live `workspace_lock` does not match the "Current state" excerpt.
- `make_workspace` or `run_memoryctl` is not defined at the top of
  `tests/test_memoryctl.py`, or `make_workspace` does not create
  `workspace/state/` (the tests write the lock there).
- Any existing memoryctl test starts failing after the rewrite — that means the
  reclaim logic changed behavior for a live lock; revert and report.
- On the test platform, `os.kill(999999999, 0)` raises something other than
  `ProcessLookupError` (e.g. the PID happens to exist) — pick another
  clearly-dead PID or report.

## Maintenance notes

- The 360-minute timeout assumes collector runs finish well within 6 hours. If a
  legitimately long-running mode is added, raise `LOCK_MAX_AGE_MINUTES` or thread
  a `--lock-timeout-minutes` CLI flag through the locking commands.
- A manual `--force-unlock` subcommand was intentionally **not** added; automatic
  staleness recovery covers the real failure mode. Add one only if operators
  report needing to break a live lock deliberately.
- Reviewer should confirm the reclaim path cannot delete a *live* lock: the only
  `unlink` before acquisition is guarded by `_lock_is_stale(...)` returning True.

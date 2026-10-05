"""Exercise real process exit and contention, including legacy lock markers."""
import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from memoryctl import MemoryCtlError, workspace_lock


def marker(workspace, value):
    path = workspace / "state" / "memoryctl.lock"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(value))
    return path


def test_dead_legacy_owner_is_reclaimed(tmp_path):
    process = subprocess.Popen([sys.executable, "-c", "pass"])
    process.wait(timeout=10)
    path = marker(tmp_path, {"pid": process.pid, "started_at": "2000-01-01"})
    with workspace_lock(tmp_path):
        assert json.loads(path.read_text())["pid"] == os.getpid()
    assert not path.exists()
    assert path.with_suffix(".guard").exists()


def test_live_legacy_owner_is_preserved_even_when_old(tmp_path):
    path = marker(tmp_path, {"pid": os.getpid(), "started_at": "2000-01-01"})
    before = path.read_bytes()
    with pytest.raises(MemoryCtlError, match="Another memoryctl run"):
        with workspace_lock(tmp_path):
            pytest.fail("Live owner must not be reclaimed")
    assert path.read_bytes() == before


@pytest.mark.parametrize("value", [None, {"pid": True}, {"pid": -1},
                                  {"pid": os.getpid(), "host": "other-host"}])
def test_unknown_owners_require_inspection(tmp_path, value):
    path = marker(tmp_path, value)
    before = path.read_bytes()
    with pytest.raises(MemoryCtlError, match="Unknown lock owner"):
        with workspace_lock(tmp_path):
            pytest.fail("Unknown owner must not be reclaimed")
    assert path.read_bytes() == before


def test_unreadable_marker_is_preserved(tmp_path):
    path = marker(tmp_path, {})
    path.write_text("partial JSON")
    with pytest.raises(MemoryCtlError, match="Unreadable lock"):
        with workspace_lock(tmp_path):
            pytest.fail("Unreadable owner must not be reclaimed")
    assert path.read_text() == "partial JSON"


def test_replacement_marker_survives_cleanup(tmp_path):
    path = tmp_path / "state" / "memoryctl.lock"
    with workspace_lock(tmp_path):
        replacement = path.with_suffix(".replacement")
        replacement.write_text(json.dumps({"pid": os.getpid(), "host": socket.gethostname()}))
        os.replace(replacement, path)
        before = path.read_bytes()
    assert path.read_bytes() == before


def test_competing_process_is_blocked_and_killed_owner_recovers(tmp_path):
    child = (
        "import sys; sys.path.insert(0, sys.argv[1]); "
        "from pathlib import Path; from memoryctl import workspace_lock\n"
        "with workspace_lock(Path(sys.argv[2])):\n"
        " print('ready', flush=True)\n"
        " sys.stdin.read()\n"
    )
    process = subprocess.Popen([sys.executable, "-c", child, str(SCRIPTS), str(tmp_path)],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True)
    try:
        assert process.stdout.readline().strip() == "ready"
        path = tmp_path / "state" / "memoryctl.lock"
        before = path.read_bytes()
        with pytest.raises(MemoryCtlError, match="Another memoryctl run"):
            with workspace_lock(tmp_path):
                pytest.fail("Competing process entered the protected region")
        assert path.read_bytes() == before
        process.kill()
        process.wait(timeout=10)
        assert path.exists()  # SIGKILL bypasses the old owner's cleanup.
        with workspace_lock(tmp_path):
            assert json.loads(path.read_text())["pid"] == os.getpid()
        assert not path.exists()
    finally:
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=10)

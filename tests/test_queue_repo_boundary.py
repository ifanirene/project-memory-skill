"""Queue repo arguments must not silently hide available work."""
import json

import pytest

from test_memoryctl import make_workspace, run_memoryctl


def seed_queue(workspace):
    path = workspace / "state/maintenance_queue_v2.json"
    path.write_text(json.dumps({"schema_version": 1, "items": [{
        "idempotency_key": "fixture", "repo": "project", "status": "open",
        "suggested_target": "docs/LESSONS.md", "attempts": 0,
    }]}))
    return path


@pytest.mark.parametrize("use_root", [False, True])
def test_known_name_and_exact_root_support_full_queue_lifecycle(tmp_path, use_root):
    workspace, repo = make_workspace(tmp_path)
    queue = seed_queue(workspace)
    argument = str(repo) if use_root else "project"
    common = ["--workspace", str(workspace), "--repo", argument]
    listed = run_memoryctl("queue-list", *common, "--status", "open")
    assert listed.returncode == 0, listed.stderr
    assert len(json.loads(listed.stdout)) == 1
    claimed = run_memoryctl("queue-claim", *common, "--idempotency-key",
                            "fixture", "--run-id", "run")
    assert claimed.returncode == 0, claimed.stderr
    finished = run_memoryctl("queue-finish", *common, "--idempotency-key",
                             "fixture", "--run-id", "run", "--status",
                             "resolved", "--evidence", "Verified fixture")
    assert finished.returncode == 0, finished.stderr
    assert json.loads(queue.read_text())["items"][0]["status"] == "resolved"


@pytest.mark.parametrize("command", ["queue-list", "queue-claim", "queue-finish"])
@pytest.mark.parametrize("wrong_kind", ["unknown", "child", "disabled"])
def test_invalid_or_unmaintained_repo_fails_without_mutation(tmp_path, command, wrong_kind):
    workspace, repo = make_workspace(tmp_path)
    queue = seed_queue(workspace)
    before = queue.read_bytes()
    argument = "typo"
    if wrong_kind == "child":
        argument = str(repo / "results")
    elif wrong_kind == "disabled":
        config_path = workspace / "config/repos.json"
        config = json.loads(config_path.read_text())
        config["repos"][0]["maintenance_enabled"] = False
        config_path.write_text(json.dumps(config))
        argument = "project"
    args = [command, "--workspace", str(workspace), "--repo", argument]
    if command != "queue-list":
        args += ["--idempotency-key", "fixture", "--run-id", "run"]
    if command == "queue-finish":
        args += ["--status", "resolved", "--evidence", "Fixture"]
    result = run_memoryctl(*args)
    assert result.returncode == 2
    assert "Unknown or ambiguous maintenance repo" in result.stderr
    assert queue.read_bytes() == before
    assert not (workspace / "state/memoryctl.lock").exists()

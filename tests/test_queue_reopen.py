"""Deferred queue work can resume without losing its provenance or safeguards."""
import json

import pytest

from test_memoryctl import make_workspace, run_memoryctl


def fixture(tmp_path, status="deferred"):
    workspace, repo = make_workspace(tmp_path)
    item = {
        "idempotency_key": "fixture", "repo": "project", "status": status,
        "suggested_target": "AGENTS.md", "attempts": 2,
        "protected_information": {"impact": "confirmed"},
        "resolution_evidence": "Waiting for explicit approval",
        "owning_run_id": "old-run", "finished_at": "2026-01-01T00:00:00Z",
        "permission_source": None, "status_history": [{"earlier": "preserved"}],
    }
    path = workspace / "state/maintenance_queue_v2.json"
    path.write_text(json.dumps({"schema_version": 1, "items": [item]}))
    args = ["queue-reopen", "--workspace", str(workspace), "--repo", str(repo),
            "--idempotency-key", "fixture", "--run-id", "new-run"]
    return workspace, path, item, args


def test_reopen_preserves_history_and_permission_boundary(tmp_path):
    workspace, path, old, args = fixture(tmp_path)
    result = run_memoryctl(*args, "--evidence", "New evidence is now available")
    assert result.returncode == 0, result.stderr
    item = json.loads(path.read_text())["items"][0]
    assert item["status"] == "open" and item["attempts"] == 2
    assert item["status_history"][0] == {"earlier": "preserved"}
    revision = item["status_history"][1]
    for key in ("status", "resolution_evidence", "owning_run_id", "finished_at"):
        assert revision["previous"][key] == old[key]
    assert revision["run_id"] == "new-run" and revision["evidence"]
    assert item["owning_run_id"] is None and item["resolution_evidence"] is None
    assert item["protected_information"] == old["protected_information"]
    common = ["--workspace", str(workspace), "--repo", "project",
              "--idempotency-key", "fixture", "--run-id", "worker"]
    claimed = run_memoryctl("queue-claim", *common)
    assert claimed.returncode == 0, claimed.stderr
    blocked = run_memoryctl("queue-finish", *common, "--status", "resolved",
                            "--evidence", "Reopen is not approval")
    assert blocked.returncode == 2 and "permission-source" in blocked.stderr
    assert json.loads(path.read_text())["items"][0]["status"] == "claimed"


@pytest.mark.parametrize("status", ["open", "claimed", "resolved", "rejected"])
def test_other_statuses_are_not_reopened(tmp_path, status):
    _, path, _, args = fixture(tmp_path, status)
    before = path.read_bytes()
    result = run_memoryctl(*args, "--evidence", "Dependency changed")
    assert result.returncode == 2 and "not deferred" in result.stderr
    assert path.read_bytes() == before


@pytest.mark.parametrize("evidence_args", [[], ["--evidence", "   "]])
def test_missing_or_blank_evidence_does_not_mutate(tmp_path, evidence_args):
    _, path, _, args = fixture(tmp_path)
    before = path.read_bytes()
    result = run_memoryctl(*args, *evidence_args)
    assert result.returncode == 2
    assert path.read_bytes() == before


def test_wrong_registered_repo_does_not_mutate(tmp_path):
    workspace, path, _, args = fixture(tmp_path)
    config_path = workspace / "config/repos.json"
    config = json.loads(config_path.read_text())
    config["repos"].append({"name": "other", "root": str(tmp_path / "other")})
    config_path.write_text(json.dumps(config))
    args[args.index("--repo") + 1] = "other"
    before = path.read_bytes()
    result = run_memoryctl(*args, "--evidence", "Dependency changed")
    assert result.returncode == 2 and "belongs to project" in result.stderr
    assert path.read_bytes() == before

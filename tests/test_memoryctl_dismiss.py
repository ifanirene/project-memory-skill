"""User-waived historical debt is retained, auditable, and not silently requeued."""
import json
from argparse import Namespace
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import memoryctl as mc
from test_memoryctl import make_workspace, run_memoryctl


def queued_workspace(tmp_path, status="deferred"):
    workspace, repo = make_workspace(tmp_path)
    item = {"idempotency_key": "old-key", "repo": "project", "status": status,
            "suggested_target": "results/branch/NOTES.md",
            "issue_type": "missing_required_manifest", "attempts": 2,
            "resolution_evidence": "Original deferral: no historical inputs",
            "owning_run_id": "original-worker", "permission_source": "old permission",
            "claimed_at": "2026-01-01", "finished_at": "2026-01-02",
            "lease_expires_at": None, "protected_information": {"impact": "possible"},
            "sources": [{"source_id": "old-source", "repo": "project",
                         "relative_path": "results/branch/NOTES.md", "sha256": "old-hash"}]}
    mc.atomic_write_json(workspace / "state/maintenance_queue_v2.json",
                         {"schema_version": 1, "items": [item]})
    return workspace, repo, item


def dismiss(workspace, repo="project", **overrides):
    values = {"workspace": workspace, "repo": repo, "idempotency_key": "old-key",
              "run_id": "user-cleanup", "evidence": "User waived inaccessible historical debt"}
    values.update(overrides)
    return mc.command_queue_dismiss(Namespace(**values))


@pytest.mark.parametrize("status", ["open", "deferred"])
def test_dismiss_preserves_full_previous_state_and_canonical_identity(tmp_path, status):
    workspace, repo, previous = queued_workspace(tmp_path, status)
    dismiss(workspace, str(repo))
    item = mc.load_queue(workspace)[1]["items"][0]
    assert item["status"] == "rejected"
    assert item["disposition"] == "user_waived_historical"
    assert item["status_history"][0]["previous"] == previous
    assert item["status_history"][0]["from_status"] == status
    assert item["suppression_identity"] == {
        "repo": "project", "suggested_target": "results/branch/NOTES.md",
        "issue_type": "missing_required_manifest"}
    assert item["owning_run_id"] is None
    assert item["permission_source"] == "old permission"


@pytest.mark.parametrize("status", ["claimed", "resolved", "rejected"])
def test_dismiss_rejects_nonpending_states_without_mutation(tmp_path, status):
    workspace, _, _ = queued_workspace(tmp_path, status)
    path = workspace / "state/maintenance_queue_v2.json"
    before = path.read_bytes()
    with pytest.raises(mc.MemoryCtlError, match="Only open or deferred"):
        dismiss(workspace)
    assert path.read_bytes() == before


@pytest.mark.parametrize("field", ["repo", "idempotency_key", "run_id", "evidence"])
def test_dismiss_requires_nonempty_arguments(tmp_path, field):
    workspace, _, _ = queued_workspace(tmp_path)
    with pytest.raises(mc.MemoryCtlError, match="non-empty"):
        dismiss(workspace, **{field: " "})


def prepare_changed_proposal(workspace, repo, **override):
    (repo / "results/branch/NOTES.md").write_text("Changed content; same historical debt")
    packet_path = workspace / "packet.json"
    result = run_memoryctl("collect", "--workspace", str(workspace),
                           "--output", str(packet_path))
    assert result.returncode == 0, result.stderr
    packet = mc.read_json(packet_path)
    source = next(s for s in packet["sources"] if s["relative_path"].endswith("NOTES.md"))
    item = {"repo": "project", "suggested_target": "results/branch/NOTES.md",
            "issue_type": "missing_required_manifest", "source_ids": [source["source_id"]],
            "rationale": "Manifest still absent", "protected_information": {"impact": "possible"},
            **override}
    proposal = {"schema_version": 1, "run_id": packet["run_id"], "candidates": [],
                "processed_source_ids": [s["source_id"] for s in packet["sources"]],
                "maintenance_items": [item]}
    proposal_path = workspace / "proposal.json"
    mc.atomic_write_json(proposal_path, proposal)
    return packet, proposal, Namespace(workspace=workspace, packet=packet_path, proposal=proposal_path)


def test_changed_source_hash_does_not_requeue_waived_debt_and_logs_suppression(tmp_path):
    workspace, repo, _ = queued_workspace(tmp_path)
    dismiss(workspace)
    packet, _, args = prepare_changed_proposal(workspace, repo)
    mc.command_apply(args)
    assert len(mc.load_queue(workspace)[1]["items"]) == 1
    log = (workspace / "logs/runs" / f"{packet['run_id']}_weekly-collector.md").read_text()
    assert "User-waived historical proposals suppressed: 1" in log
    assert "old-key" in log and "missing_required_manifest" in log


def test_explicit_material_facts_create_linked_new_item_and_retain_waiver(tmp_path):
    workspace, repo, _ = queued_workspace(tmp_path)
    dismiss(workspace)
    _, _, args = prepare_changed_proposal(
        workspace, repo, requeue_closed_item="old-key",
        requeue_evidence="New archived input and exact generating command have been recovered")
    mc.command_apply(args)
    items = mc.load_queue(workspace)[1]["items"]
    assert len(items) == 2
    assert items[0]["status"] == "rejected"
    assert items[1]["status"] == "open"
    assert items[1]["requeue_closed_item"] == "old-key"
    assert items[1]["protected_information"]["impact"] == "possible"


def test_ordinary_rejected_item_does_not_suppress_changed_proposal(tmp_path):
    workspace, repo, _ = queued_workspace(tmp_path, "rejected")
    _, _, args = prepare_changed_proposal(workspace, repo)
    mc.command_apply(args)
    assert [i["status"] for i in mc.load_queue(workspace)[1]["items"]] == ["rejected", "open"]


def test_dismissal_does_not_grant_protected_agents_resolution_permission(tmp_path):
    workspace, _, old = queued_workspace(tmp_path)
    old["suggested_target"] = "AGENTS.md"
    path = workspace / "state/maintenance_queue_v2.json"
    mc.atomic_write_json(path, {"schema_version": 1, "items": [old]})
    dismiss(workspace)
    queue = mc.load_queue(workspace)[1]
    queue["items"].append({**old, "idempotency_key": "new-protected", "status": "claimed",
                           "owning_run_id": "worker", "permission_source": None})
    mc.atomic_write_json(path, queue)
    with pytest.raises(mc.MemoryCtlError, match="permission-source"):
        mc.command_queue_finish(Namespace(
            workspace=workspace, repo="project", idempotency_key="new-protected",
            run_id="worker", status="resolved", evidence="New facts",
            permission_source=None))


@pytest.mark.parametrize("override", [
    {"requeue_closed_item": "unknown", "requeue_evidence": "New facts"},
    {"requeue_closed_item": "old-key"},
    {"requeue_evidence": "New facts"},
    {"requeue_closed_item": "old-key", "requeue_evidence": " "},
    {"requeue_closed_item": "old-key", "requeue_evidence": "New facts",
     "suggested_target": "docs/LESSONS.md"},
])
def test_unknown_incomplete_or_mismatched_override_rejected(tmp_path, override):
    workspace, repo, _ = queued_workspace(tmp_path)
    dismiss(workspace)
    _, _, args = prepare_changed_proposal(workspace, repo, **override)
    before = mc.load_queue(workspace)[0].read_bytes()
    with pytest.raises(mc.MemoryCtlError):
        mc.command_apply(args)
    assert mc.load_queue(workspace)[0].read_bytes() == before
    assert not (workspace / "state/repo_cursors_v2.json").exists()


def test_dismiss_cli_alias_executes_on_fixture(tmp_path):
    workspace, _, _ = queued_workspace(tmp_path)
    result = run_memoryctl("queue-dismiss", "--workspace", str(workspace),
                           "--repo", "project", "--key", "old-key", "--run-id", "cleanup",
                           "--evidence", "User explicitly waived this historical issue")
    assert result.returncode == 0, result.stderr
    assert mc.load_queue(workspace)[1]["items"][0]["status"] == "rejected"

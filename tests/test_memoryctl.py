from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "memoryctl.py"


def run_memoryctl(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def make_workspace(tmp_path: Path) -> tuple[Path, Path]:
    workspace = tmp_path / "long-term-memory"
    repo = tmp_path / "project"
    (workspace / "config").mkdir(parents=True)
    (workspace / "state").mkdir()
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Rules\n")
    (repo / "ANALYSIS_INDEX.md").write_text("# Index\n")
    (repo / "docs").mkdir()
    (repo / "docs" / "LESSONS.md").write_text("# Lessons\n")
    (repo / "results" / "branch").mkdir(parents=True)
    (repo / "results" / "branch" / "NOTES.md").write_text(
        "## Validation\n- checked\n"
    )
    registry = {
        "schema_version": 1,
        "repos": [
            {
                "name": "project",
                "root": str(repo),
                "patterns": [
                    "AGENTS.md",
                    "ANALYSIS_INDEX.md",
                    "docs/LESSONS.md",
                    "**/NOTES.md",
                ],
            }
        ],
    }
    (workspace / "config" / "repos.json").write_text(json.dumps(registry))
    return workspace, repo


def test_doctor_and_incremental_collection(tmp_path: Path) -> None:
    workspace, _ = make_workspace(tmp_path)
    packet_path = workspace / "runs" / "packet.json"

    doctor = run_memoryctl("doctor", "--workspace", str(workspace))
    assert doctor.returncode == 0, doctor.stderr
    assert "[READ OK] project" in doctor.stdout

    collect = run_memoryctl(
        "collect",
        "--workspace",
        str(workspace),
        "--output",
        str(packet_path),
    )
    assert collect.returncode == 0, collect.stderr
    packet = json.loads(packet_path.read_text())
    assert len(packet["sources"]) == 4
    assert packet["remaining_changed_files"] == 0
    assert packet["repo_provenance"] == [
        {
            "repo": "project",
            "root": str((tmp_path / "project").resolve()),
            "is_git_worktree": False,
        }
    ]

    outside = run_memoryctl(
        "collect",
        "--workspace",
        str(workspace),
        "--output",
        str(tmp_path / "outside-packet.json"),
    )
    assert outside.returncode == 2
    assert "inside the collector workspace" in outside.stderr


def test_collection_prioritizes_newest_changed_file(tmp_path: Path) -> None:
    workspace, repo = make_workspace(tmp_path)
    for path in repo.rglob("*.md"):
        os.utime(path, ns=(1_000_000_000, 1_000_000_000))
    note = repo / "results/branch/NOTES.md"
    os.utime(note, ns=(9_000_000_000, 9_000_000_000))
    packet_path = workspace / "packet.json"
    result = run_memoryctl("collect", "--workspace", str(workspace),
                          "--output", str(packet_path), "--max-files", "1",
                          "--quality-audit-files", "0")
    assert result.returncode == 0, result.stderr
    packet = json.loads(packet_path.read_text())
    assert packet["sources"][0]["relative_path"] == "results/branch/NOTES.md"
    assert packet["remaining_changed_files"] == 3


def test_collection_records_dirty_git_provenance(tmp_path: Path) -> None:
    workspace, repo = make_workspace(tmp_path)
    for command in (
        ("git", "init", "-q"),
        ("git", "config", "user.email", "memoryctl-test@example.invalid"),
        ("git", "config", "user.name", "Memoryctl Test"),
        ("git", "add", "."),
        ("git", "commit", "-qm", "initial fixture"),
    ):
        result = subprocess.run(command, cwd=repo, capture_output=True, check=False)
        assert result.returncode == 0, result.stderr
    (repo / "docs" / "LESSONS.md").write_text("# Lessons\n\nUncommitted change.\n")

    packet_path = workspace / "packet.json"
    collect = run_memoryctl(
        "collect",
        "--workspace",
        str(workspace),
        "--output",
        str(packet_path),
    )

    assert collect.returncode == 0, collect.stderr
    provenance = json.loads(packet_path.read_text())["repo_provenance"][0]
    assert provenance["is_git_worktree"] is True
    assert provenance["dirty"] is True
    assert provenance["head"]
    assert provenance["branch"]
    assert "Dirty main worktrees remain eligible" in json.loads(
        packet_path.read_text()
    )["llm_contract"]["repo_provenance"]


def test_collection_defers_oversized_sources_without_marking_them_processed(
    tmp_path: Path,
) -> None:
    workspace, _ = make_workspace(tmp_path)
    packet_path = workspace / "packet.json"
    collect = run_memoryctl(
        "collect",
        "--workspace",
        str(workspace),
        "--output",
        str(packet_path),
        "--max-chars",
        "5",
    )
    assert collect.returncode == 0, collect.stderr
    packet = json.loads(packet_path.read_text())
    assert packet["sources"] == []
    assert len(packet["deferred_oversized_sources"]) == 4
    assert packet["remaining_changed_files"] == 4
    assert not (workspace / "state" / "repo_cursors_v2.json").exists()


def test_round_robin_quality_audit_reviews_unchanged_legacy_docs(
    tmp_path: Path,
) -> None:
    workspace, repo = make_workspace(tmp_path)
    (repo / "docs" / "LESSONS.md").write_text(
        "# Lessons\n\n"
        "- [2026-01] First chronological lesson.\n"
        "- [2026-02] Second chronological lesson.\n"
    )
    note = repo / "results" / "branch" / "NOTES.md"
    note.write_text(
        "# Branch\n\n## Status\nACTIVE\n\n"
        "## Update 2026-01-01\nOne.\n\n"
        "## Update 2026-02-01\nTwo.\n\n"
        "## Update 2026-03-01\nThree.\n"
    )

    initial_packet_path = workspace / "initial-packet.json"
    initial_proposal_path = workspace / "initial-proposal.json"
    initial_collect = run_memoryctl(
        "collect",
        "--workspace",
        str(workspace),
        "--output",
        str(initial_packet_path),
        "--quality-audit-files",
        "0",
    )
    assert initial_collect.returncode == 0, initial_collect.stderr
    initial_packet = json.loads(initial_packet_path.read_text())
    initial_proposal_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "run_id": initial_packet["run_id"],
                "processed_source_ids": [
                    source["source_id"] for source in initial_packet["sources"]
                ],
                "candidates": [],
                "maintenance_items": [],
            }
        )
    )
    initial_apply = run_memoryctl(
        "apply",
        "--workspace",
        str(workspace),
        "--packet",
        str(initial_packet_path),
        "--proposal",
        str(initial_proposal_path),
    )
    assert initial_apply.returncode == 0, initial_apply.stderr
    quality_state = json.loads(
        (workspace / "state" / "quality_audit_v1.json").read_text()
    )
    assert quality_state["files"] == {}

    lesson_packet_path = workspace / "lesson-quality-packet.json"
    lesson_collect = run_memoryctl(
        "collect",
        "--workspace",
        str(workspace),
        "--output",
        str(lesson_packet_path),
        "--max-files",
        "1",
        "--quality-audit-files",
        "1",
    )
    assert lesson_collect.returncode == 0, lesson_collect.stderr
    lesson_packet = json.loads(lesson_packet_path.read_text())
    assert lesson_packet["remaining_changed_files"] == 0
    assert lesson_packet["remaining_quality_audit_files"] == 1
    assert lesson_packet["sources"][0]["collection_reason"] == "quality_audit"
    assert lesson_packet["sources"][0]["relative_path"] == "docs/LESSONS.md"
    assert "lesson_not_distilled" in lesson_packet["sources"][0][
        "quality_metrics"
    ]["review_reasons"]

    source_id = lesson_packet["sources"][0]["source_id"]
    lesson_proposal_path = workspace / "lesson-quality-proposal.json"
    lesson_proposal_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "run_id": lesson_packet["run_id"],
                "processed_source_ids": [source_id],
                "candidates": [],
                "maintenance_items": [
                    {
                        "repo": "project",
                        "issue_type": "lesson_not_distilled",
                        "suggested_target": "docs/LESSONS.md",
                        "source_ids": [source_id],
                        "rationale": "Chronological bullets hide reusable guidance.",
                        "protected_information": {"impact": "none"},
                        "quality_evidence": {
                            "current_state_findability": "low",
                            "dated_bullet_count": 2,
                            "typed_lesson_count": 0,
                        },
                    }
                ],
            }
        )
    )
    lesson_apply = run_memoryctl(
        "apply",
        "--workspace",
        str(workspace),
        "--packet",
        str(lesson_packet_path),
        "--proposal",
        str(lesson_proposal_path),
    )
    assert lesson_apply.returncode == 0, lesson_apply.stderr
    queue = json.loads((workspace / "state" / "maintenance_queue_v2.json").read_text())
    assert queue["items"][0]["sources"][0]["sha256"]

    note_packet_path = workspace / "note-quality-packet.json"
    note_collect = run_memoryctl(
        "collect",
        "--workspace",
        str(workspace),
        "--output",
        str(note_packet_path),
        "--max-files",
        "1",
        "--quality-audit-files",
        "1",
    )
    assert note_collect.returncode == 0, note_collect.stderr
    note_packet = json.loads(note_packet_path.read_text())
    assert note_packet["sources"][0]["relative_path"] == "results/branch/NOTES.md"
    assert "notes_chronology_drift" in note_packet["sources"][0][
        "quality_metrics"
    ]["review_reasons"]

    note_source_id = note_packet["sources"][0]["source_id"]
    note_proposal = {
        "schema_version": 1,
        "run_id": note_packet["run_id"],
        "processed_source_ids": [note_source_id],
        "candidates": [],
        "maintenance_items": [
            {
                "repo": "project",
                "issue_type": "notes_chronology_drift",
                "suggested_target": "results/branch/NOTES.md",
                "source_ids": [note_source_id],
                "rationale": "Current state is buried under dated updates.",
                "protected_information": {"impact": "none"},
                "quality_evidence": {
                    "current_state_findability": "low",
                    "dated_heading_count": 3,
                },
            }
        ],
    }
    note_proposal_path = workspace / "note-quality-proposal.json"
    note_proposal_path.write_text(json.dumps(note_proposal))
    missing_map = run_memoryctl(
        "validate",
        "--workspace",
        str(workspace),
        "--packet",
        str(note_packet_path),
        "--proposal",
        str(note_proposal_path),
    )
    assert missing_map.returncode == 2
    assert "rewrite_brief" in missing_map.stderr

    note_proposal["maintenance_items"][0]["rewrite_brief"] = {
        "purpose": "Explain the maintained branch and its current answer.",
        "current_claim": "The current result is supported by the latest run.",
        "canonical_artifacts": ["results/branch/current.csv"],
        "trust_basis": ["Focused validation passed."],
        "kill_list": ["Dated session-by-session narration."],
        "missing_evidence": ["Independent rerun."],
    }
    note_proposal_path.write_text(json.dumps(note_proposal))
    valid = run_memoryctl(
        "validate",
        "--workspace",
        str(workspace),
        "--packet",
        str(note_packet_path),
        "--proposal",
        str(note_proposal_path),
    )
    assert valid.returncode == 0, valid.stderr


def test_validate_rejects_unknown_source_and_unsafe_target(tmp_path: Path) -> None:
    workspace, _ = make_workspace(tmp_path)
    packet_path = workspace / "packet.json"
    proposal_path = workspace / "proposal.json"
    collect = run_memoryctl(
        "collect",
        "--workspace",
        str(workspace),
        "--output",
        str(packet_path),
    )
    assert collect.returncode == 0
    packet = json.loads(packet_path.read_text())
    proposal = {
        "schema_version": 1,
        "run_id": packet["run_id"],
        "processed_source_ids": [source["source_id"] for source in packet["sources"]],
        "candidates": [
            {
                "statement": "Candidate",
                "scope": "repo_local",
                "confidence": "high",
                "source_ids": ["unknown"],
                "rationale": "test",
            }
        ],
        "maintenance_items": [
            {
                "repo": "project",
                "issue_type": "unsafe",
                "suggested_target": "scripts/tool.py",
                "source_ids": [packet["sources"][0]["source_id"]],
                "rationale": "test",
                "protected_information": {"impact": "none"},
            }
        ],
    }
    proposal_path.write_text(json.dumps(proposal))

    validate = run_memoryctl(
        "validate",
        "--workspace",
        str(workspace),
        "--packet",
        str(packet_path),
        "--proposal",
        str(proposal_path),
    )
    assert validate.returncode == 2
    assert "unknown source_id" in validate.stderr


def test_apply_updates_only_collector_state_and_rejects_stale_packet(tmp_path: Path) -> None:
    workspace, repo = make_workspace(tmp_path)
    packet_path = workspace / "packet.json"
    proposal_path = workspace / "proposal.json"
    original_repo_files = {
        path.relative_to(repo): path.read_text()
        for path in repo.rglob("*.md")
    }

    collect = run_memoryctl(
        "collect",
        "--workspace",
        str(workspace),
        "--output",
        str(packet_path),
    )
    assert collect.returncode == 0
    packet = json.loads(packet_path.read_text())
    source_ids = [source["source_id"] for source in packet["sources"]]
    proposal = {
        "schema_version": 1,
        "run_id": packet["run_id"],
        "processed_source_ids": source_ids,
        "candidates": [
            {
                "statement": "Validate a maintained artifact before reuse.",
                "scope": "cross_repo_science",
                "confidence": "high",
                "source_ids": [source_ids[-1]],
                "rationale": "The source records a reusable validation rule.",
            }
        ],
        "maintenance_items": [
            {
                "repo": "project",
                "issue_type": "lesson_review",
                "suggested_target": "docs/LESSONS.md",
                "source_ids": [source_ids[-1]],
                "rationale": "Review for a durable repo-facing rewrite.",
                "protected_information": {"impact": "none"},
            }
        ],
    }
    proposal_path.write_text(json.dumps(proposal))

    apply = run_memoryctl(
        "apply",
        "--workspace",
        str(workspace),
        "--packet",
        str(packet_path),
        "--proposal",
        str(proposal_path),
    )
    assert apply.returncode == 0, apply.stderr
    assert (workspace / "state" / "repo_cursors_v2.json").exists()
    queue = json.loads((workspace / "state" / "maintenance_queue_v2.json").read_text())
    assert queue["items"][0]["status"] == "open"
    queue_key = queue["items"][0]["idempotency_key"]
    assert list((workspace / "observations" / "repo_events").glob("*.jsonl"))
    assert original_repo_files == {
        path.relative_to(repo): path.read_text()
        for path in repo.rglob("*.md")
    }

    second_apply = run_memoryctl(
        "apply",
        "--workspace",
        str(workspace),
        "--packet",
        str(packet_path),
        "--proposal",
        str(proposal_path),
    )
    assert second_apply.returncode == 2
    assert "cursor changed" in second_apply.stderr

    claim = run_memoryctl(
        "queue-claim",
        "--workspace",
        str(workspace),
        "--idempotency-key",
        queue_key,
        "--repo",
        "project",
        "--run-id",
        "repo-run-1",
    )
    assert claim.returncode == 0, claim.stderr
    wrong_owner = run_memoryctl(
        "queue-finish",
        "--workspace",
        str(workspace),
        "--idempotency-key",
        queue_key,
        "--repo",
        "project",
        "--run-id",
        "repo-run-2",
        "--status",
        "resolved",
        "--evidence",
        "reviewed",
    )
    assert wrong_owner.returncode == 2
    finish = run_memoryctl(
        "queue-finish",
        "--workspace",
        str(workspace),
        "--idempotency-key",
        queue_key,
        "--repo",
        "project",
        "--run-id",
        "repo-run-1",
        "--status",
        "resolved",
        "--evidence",
        "docs already compliant",
    )
    assert finish.returncode == 0, finish.stderr
    final_queue = json.loads(
        (workspace / "state" / "maintenance_queue_v2.json").read_text()
    )
    assert final_queue["items"][0]["status"] == "resolved"
    assert final_queue["items"][0]["attempts"] == 1


def test_protected_agents_item_requires_permission_source(tmp_path: Path) -> None:
    workspace, _ = make_workspace(tmp_path)
    key = "protected-item"
    queue = {
        "schema_version": 1,
        "items": [
            {
                "idempotency_key": key,
                "repo": "project",
                "status": "open",
                "attempts": 0,
                "suggested_target": "AGENTS.md",
                "protected_information": {"impact": "confirmed"},
            }
        ],
    }
    (workspace / "state" / "maintenance_queue_v2.json").write_text(
        json.dumps(queue)
    )
    claim = run_memoryctl(
        "queue-claim",
        "--workspace",
        str(workspace),
        "--idempotency-key",
        key,
        "--repo",
        "project",
        "--run-id",
        "repo-run-1",
    )
    assert claim.returncode == 0
    blocked = run_memoryctl(
        "queue-finish",
        "--workspace",
        str(workspace),
        "--idempotency-key",
        key,
        "--repo",
        "project",
        "--run-id",
        "repo-run-1",
        "--status",
        "resolved",
        "--evidence",
        "changed environment path",
    )
    assert blocked.returncode == 2
    assert "--permission-source" in blocked.stderr
    approved = run_memoryctl(
        "queue-finish",
        "--workspace",
        str(workspace),
        "--idempotency-key",
        key,
        "--repo",
        "project",
        "--run-id",
        "repo-run-1",
        "--status",
        "resolved",
        "--evidence",
        "changed environment path",
        "--permission-source",
        "user request 2026-07-11 approving the exact patch",
    )
    assert approved.returncode == 0, approved.stderr

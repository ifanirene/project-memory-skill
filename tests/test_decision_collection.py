"""Collector fairness, archive relocation, and deferred-source isolation."""
import json
import os
from argparse import Namespace
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import decision_memory as dm


def write_session(path, repo, number):
    rows = [
        {"type": "session_meta", "payload": {
            "id": f"s{number}", "cwd": str(repo), "source": "cli"}},
        {"type": "response_item", "timestamp": "2026-01-01T00:00:00Z",
         "payload": {"role": "user", "id": f"m{number}", "content": [
             {"type": "input_text", "text": f"Choice {number}"}]}},
        {"type": "event_msg", "payload": {"type": "task_complete"}},
    ]
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))
    os.utime(path, ns=(1_000_000_000 + number, 1_000_000_000 + number))
    return dm.session_records(path, "repo")[0]


def test_deferred_sessions_rotate_without_consuming(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    for n in range(7):
        write_session(sessions / f"{n}.jsonl", repo, n)
    state = {"reviews": {}, "scans": {}, "scan_attempts": {}}
    seen = set()
    for attempt in range(2):
        records, scans, _ = dm.inventory_repo(
            {"name": "repo", "root": str(repo)}, [str(sessions)], state, 4)
        seen.update(r["episode_id"] for r in records)
        for scan in scans:
            state["scan_attempts"][scan["path"]] = str(attempt)
    assert seen == {f"s{n}" for n in range(7)}
    assert not state["reviews"] and not state["scans"]


def test_apply_records_attempts_but_keeps_deferred_pending(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    for n in range(7):
        write_session(sessions / f"{n}.jsonl", repo, n)
    config = {"name": "repo", "root": str(repo)}
    initial = dm.ledger(tmp_path)  # Existing ledgers have no scan_attempts field.
    records, scans, coverage = dm.inventory_repo(config, [str(sessions)], initial, 4)
    packet = {"schema_version": 1, "run_id": "r1", "created_at": dm.now(),
              "state_digest": dm.digest(initial), "sources": records, "scans": scans,
              "coverage": [coverage], "remaining_discovered_sources": 3}
    proposal = {"schema_version": 1, "run_id": "r1", "events": [], "reviews": [
        {"source_id": r["source_id"], "disposition": "deferred", "reason": "Needs context"}
        for r in records]}
    packet_path = tmp_path / "packet.json"
    proposal_path = tmp_path / "proposal.json"
    packet_path.write_text(json.dumps(packet))
    proposal_path.write_text(json.dumps(proposal))
    dm.apply(Namespace(workspace=tmp_path, packet=packet_path,
                       proposal=proposal_path, validate_only=False))
    state = dm.ledger(tmp_path)
    assert len(state["scan_attempts"]) == 4
    assert not state["reviews"] and not state["scans"]
    following, _, _ = dm.inventory_repo(config, [str(sessions)], state, 4)
    assert {r["episode_id"] for r in records + following} == {f"s{n}" for n in range(7)}


@pytest.mark.parametrize("kind", ["documents", "long_session"])
def test_deferred_sources_rotate_between_collect_apply_cycles(tmp_path, kind):
    repo = tmp_path / "repo"
    repo.mkdir()
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    if kind == "documents":
        for n in range(3):
            path = repo / f"note{n}.md"
            path.write_text(f"Decision {n}")
            os.utime(path, ns=(1_000_000_000 + n, 1_000_000_000 + n))
    else:
        path = sessions / "long.jsonl"
        write_session(path, repo, 0)
        with path.open("a") as handle:
            for n in range(1, 3):
                handle.write(json.dumps({"type": "response_item",
                    "timestamp": f"2026-01-0{n + 1}T00:00:00Z", "payload": {
                        "role": "user", "id": f"m{n}", "content": [
                            {"type": "input_text", "text": f"Choice {n}"}]}}) + "\n")
                handle.write(json.dumps({"type": "event_msg", "payload": {
                    "type": "task_complete"}}) + "\n")
    (tmp_path / "config").mkdir()
    (tmp_path / "config/repos.json").write_text(json.dumps({
        "dialog_roots": [str(sessions)], "repos": [
        {"name": "repo", "root": str(repo), "decision_patterns": ["*.md"]}]}))
    seen = set()
    for _ in range(3):
        packet_path = tmp_path / "packet.json"
        dm.collect(Namespace(workspace=tmp_path, output=packet_path, repo=None,
                             session_limit=4, max_sources=1))
        packet = json.loads(packet_path.read_text())
        source = packet["sources"][0]
        seen.add(source["source_id"])
        proposal_path = tmp_path / "proposal.json"
        proposal_path.write_text(json.dumps({"schema_version": 1,
            "run_id": packet["run_id"], "events": [], "reviews": [
                {"source_id": source["source_id"], "disposition": "deferred",
                 "reason": "Needs context"}]}))
        dm.apply(Namespace(workspace=tmp_path, packet=packet_path,
                           proposal=proposal_path, validate_only=False))
    assert len(seen) == 3
    assert dm.ledger(tmp_path)["reviews"] == {}


@pytest.mark.parametrize("configured_roots", [False, True])
def test_archive_move_recovers_original_evidence(tmp_path, configured_roots):
    active = tmp_path / ".codex" / "sessions"
    archive = active.parent / "archived_sessions"
    active.mkdir(parents=True)
    archive.mkdir()
    original = active / "session.jsonl"
    source = write_session(original, tmp_path, 1)
    if configured_roots:
        source["session_roots"] = [str(active), str(archive)]
    moved = archive / original.name
    original.rename(moved)
    assert dm.full_source(source) == "Choice 1"
    moved.write_text(moved.read_text().replace('"id": "s1"', '"id": "other"'))
    with pytest.raises(ValueError, match="missing or changed"):
        dm.full_source(source)
    moved.write_text(moved.read_text().replace('"id": "other"', '"id": "s1"')
                     .replace("Choice 1", "Choice 2"))
    with pytest.raises(ValueError, match="missing or changed"):
        dm.full_source(source)


def test_existing_path_with_wrong_session_id_rejected(tmp_path):
    path = tmp_path / "session.jsonl"
    source = write_session(path, tmp_path, 1)
    path.write_text(path.read_text().replace('"id": "s1"', '"id": "other"'))
    with pytest.raises(ValueError, match="ID changed"):
        dm.full_source(source)


def test_missing_deferred_source_does_not_block_other_reviews(tmp_path):
    good = write_session(tmp_path / "good.jsonl", tmp_path, 1)
    missing = write_session(tmp_path / "missing.jsonl", tmp_path, 2)
    Path(missing["path"]).unlink()
    packet = {"schema_version": 1, "sources": [good, missing]}
    proposal = {"schema_version": 1, "events": [], "reviews": [
        {"source_id": good["source_id"], "disposition": "no_signal", "reason": "Reviewed"},
        {"source_id": missing["source_id"], "disposition": "deferred", "reason": "Missing"},
    ]}
    dm.validate_events(packet, proposal)
    proposal["events"] = [{"id": "e", "attribution": "direct_user",
        **{k: "Explanation" for k in ("context", "choice", "alternative", "reason",
                                      "tradeoff", "scope", "uncertainty", "future_test")},
        "evidence": [{"source_id": missing["source_id"], "quote": "Choice 2"}]}]
    with pytest.raises(ValueError, match="Deferred source"):
        dm.validate_events(packet, proposal)
    proposal["events"] = []
    proposal["reviews"][1]["disposition"] = "no_signal"
    with pytest.raises(ValueError, match="missing or changed"):
        dm.validate_events(packet, proposal)

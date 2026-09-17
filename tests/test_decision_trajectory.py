"""History, correction links, and original-source loss remain visible."""
from argparse import Namespace
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import decision_memory as dm
from decision_history import validate_event_relations


def state_fixture():
    event = {
        "id": "e1", "attribution": "direct_user",
        **{key: "Bounded decision" for key in (
            "context", "choice", "alternative", "reason", "tradeoff", "scope",
            "uncertainty", "future_test")},
        "evidence": [{"source_id": "s1", "quote": "Keep branches", "source": {
            "path": "/fixture/original.jsonl", "line": 2, "episode_id": "episode1",
            "timestamp": "2026-01-01T00:00:00Z", "sha256": "fixture"}}],
    }
    principle = {
        "id": "p1", "status": "candidate", "support_event_ids": ["e1"],
        "counter_event_ids": [], "retrieval_tags": ["imaging"],
        **{key: "Initial interpretation" for key in (
            "statement", "scope", "boundary", "predicted_choice", "cost",
            "counterevidence_search", "review_rationale")},
    }
    return {"schema_version": 1, "events": [event], "principles": [principle],
            "reviews": {}, "scans": {}, "runs": []}


def apply_review(tmp_path, state, updates, validate_only=False):
    dm.atomic_write_json(tmp_path / dm.LEDGER, state)
    path = tmp_path / "review.json"
    dm.atomic_write_json(path, {"run_id": "revision-run", "state_digest": dm.digest(state),
                               "principles": updates})
    dm.apply(Namespace(workspace=tmp_path, proposal=path, packet=None,
                       validate_only=validate_only))
    return dm.ledger(tmp_path)


def test_baseline_then_before_after_and_retirement(tmp_path):
    state = state_fixture()
    revised = deepcopy(state["principles"][0])
    revised.update(statement="Revised interpretation", change_reason="New contrary choice")
    updated = apply_review(tmp_path, state, [revised])
    baseline, revision = updated["principle_revisions"]
    assert baseline["kind"] == "baseline" and baseline["before"] is None
    assert "earlier revisions are unknown" in baseline["reason"]
    assert revision["before"] == state["principles"][0]
    assert revision["after"] == revised
    assert revision["timestamp"] and revision["run_id"] == "revision-run"
    revised["status"] = "retired"
    retired = apply_review(tmp_path, updated, [revised])
    assert len(retired["principle_revisions"]) == 3
    assert retired["principle_revisions"][-1]["before"]["status"] == "candidate"
    view = (tmp_path / "reflections/PERSONAL_JUDGMENT.md").read_text()
    assert "Initial interpretation" in view and "Revised interpretation" in view


def test_empty_review_migrates_baseline_once_and_validation_does_not_write(tmp_path):
    state = state_fixture()
    assert apply_review(tmp_path, state, [], validate_only=True) == state
    migrated = apply_review(tmp_path, state, [])
    assert len(migrated["principle_revisions"]) == 1
    assert len(apply_review(tmp_path, migrated, [])["principle_revisions"]) == 1


def test_supersession_rejects_bad_targets_and_cycles_and_renders(tmp_path):
    state = state_fixture()
    correction = deepcopy(state["events"][0])
    correction.update(id="e2", supersedes_event_ids=["missing"], relation_reason="Changed endpoint")
    with pytest.raises(ValueError, match="supersedes"):
        validate_event_relations(state["events"] + [correction])
    correction["supersedes_event_ids"] = ["e1"]
    state["events"].append(correction)
    validate_event_relations(state["events"])
    dm.render(tmp_path, state)
    view = (tmp_path / "observations/DECISIONS.md").read_text()
    assert "Supersedes: e1" in view and "Superseded by: e2" in view
    assert "2026-01-01T00:00:00Z" in view
    state["events"][0].update(supersedes_event_ids=["e2"], relation_reason="Invalid cycle")
    with pytest.raises(ValueError, match="Cyclic"):
        validate_event_relations(state["events"])


def test_unavailable_existing_axiom_does_not_block_candidate_but_is_visible(tmp_path, monkeypatch):
    state = state_fixture()
    axiom = deepcopy(state["principles"][0])
    axiom.update(id="a1", status="axiom", counter_event_ids=["e1"],
                 counterevidence_resolution="Cleaning is useful unless branches disappear")
    state["principles"].append(axiom)

    def unavailable(source):
        raise FileNotFoundError("Original source unavailable")

    monkeypatch.setattr(dm, "full_source", unavailable)
    updated = apply_review(tmp_path, state, [state["principles"][0]])
    health = updated["principle_source_health"]["a1"]
    assert health["status"] == "needs_review"
    assert health["checks"][0]["status"] == "unavailable"
    view = (tmp_path / "axioms/AXIOMS.md").read_text()
    assert "unavailable" in view and "Retained quotes remain available" in view
    assert axiom["counterevidence_resolution"] in view
    assert axiom["counterevidence_resolution"] in (tmp_path / "reflections/PERSONAL_JUDGMENT.md").read_text()

    def changed(source):
        raise ValueError("Source row changed")

    monkeypatch.setattr(dm, "full_source", changed)
    updated = apply_review(tmp_path, updated, [])
    assert updated["principle_source_health"]["a1"]["checks"][0]["status"] == "changed"
    monkeypatch.setattr(dm, "full_source", lambda source: "Keep branches")
    updated = apply_review(tmp_path, updated, [])
    assert updated["principle_source_health"]["a1"]["status"] == "verified"
    previous = deepcopy(updated["principle_source_health"]["a1"])
    monkeypatch.setattr(dm, "full_source", unavailable)
    updated = apply_review(tmp_path, updated, [])
    current = updated["principle_source_health"]["a1"]
    assert current["last_verified_at"] == previous["last_verified_at"]
    assert current["checks"][0]["last_verified_at"] == previous["checks"][0]["last_verified_at"]


def test_deferred_attempts_rotate_without_consuming_source(tmp_path):
    document = tmp_path / "note.md"
    document.write_text("A choice requiring context")
    source = dm.document_record(document, "fixture", tmp_path)
    packet = {"schema_version": 1, "run_id": "deferred-run", "created_at": "2026-01-01T00:00:00Z",
              "state_digest": dm.digest(dm.ledger(tmp_path)), "sources": [source],
              "scans": [{"path": "session.jsonl", "source_ids": [source["source_id"]], "signature": [1, 2]}],
              "coverage": [], "remaining_discovered_sources": 0}
    proposal = {"schema_version": 1, "run_id": "deferred-run", "events": [],
                "reviews": [{"source_id": source["source_id"], "disposition": "deferred", "reason": "Needs context"}]}
    packet_path, proposal_path = tmp_path / "packet.json", tmp_path / "proposal.json"
    dm.atomic_write_json(packet_path, packet)
    dm.atomic_write_json(proposal_path, proposal)
    dm.apply(Namespace(workspace=tmp_path, proposal=proposal_path, packet=packet_path, validate_only=False))
    state = dm.ledger(tmp_path)
    assert not state["reviews"] and not state["scans"]
    assert state["scan_attempts"]["session.jsonl"] == packet["created_at"]
    assert state["source_attempts"][source["source_id"]] == packet["created_at"]


def test_new_axiom_requires_recoverable_counterevidence(monkeypatch):
    state = state_fixture()
    template = state["events"][0]
    state["events"] = []
    for index in range(4):
        event = deepcopy(template)
        event["id"] = f"e{index}"
        event["evidence"][0]["source"].update(
            episode_id=f"episode{index}", timestamp=f"2026-0{index + 1}-01T00:00:00Z")
        state["events"].append(event)
    principle = state["principles"][0]
    principle.update(status="axiom", support_event_ids=["e0", "e1", "e2"],
                     counter_event_ids=["e3"], counterevidence_resolution="Different scope")

    def read(source):
        if source["episode_id"] == "episode3":
            raise ValueError("Counter source missing")
        return "Keep branches"

    monkeypatch.setattr(dm, "full_source", read)
    with pytest.raises(ValueError, match="Counter source missing"):
        dm.validate_principles(state, [principle])

"""Behavior checks for attribution, tail coverage and promotion safety."""
import copy
import json
from pathlib import Path
import sys
from argparse import Namespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import decision_memory as dm


def session(tmp_path):
    path = tmp_path / "session.jsonl"
    rows = [
        {"type": "session_meta", "payload": {"id": "s1", "cwd": "/repo", "source": "cli"}},
        {"type": "response_item", "timestamp": "2026-01-01T00:00:00Z", "payload": {
            "type": "message", "role": "user", "id": "m1", "content": [
                {"type": "input_text", "text": "Keep faint branches even if background is noisy."}]}},
        {"type": "event_msg", "payload": {"type": "task_complete"}},
        {"type": "response_item", "timestamp": "2026-01-02T00:00:00Z", "payload": {
            "type": "message", "role": "user", "id": "m2", "content": [
                {"type": "input_text", "text": "Unfinished new turn."}]}},
    ]
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return path


def test_only_completed_user_turns_and_append_safe_hash(tmp_path):
    path = session(tmp_path)
    records = dm.session_records(path, "repo")
    assert len(records) == 1
    with path.open("a") as f:
        f.write(json.dumps({"type": "event_msg", "payload": {"type": "task_complete"}}) + "\n")
    assert len(dm.session_records(path, "repo")) == 2
    assert dm.full_source(records[0]).startswith("Keep faint")


def test_context_and_secrets_are_not_user_judgment():
    assert not dm.clean_user("# AGENTS.md instructions for /repo\nAlways write tests")
    assert dm.clean_user("<environment_context>injected</environment_context>\nMy choice") == "My choice"
    assert not dm.clean_user("Add API key abcdefghijklmnopqrstuvwxyz123456 to config")
    assert dm.clean_user('<send_user_message_question_reply>[{"question":"Do X?", "answer":"No"}]</send_user_message_question_reply>') == "No"


def test_subagents_are_not_independent_people(tmp_path):
    path = session(tmp_path)
    text = path.read_text().replace('"source": "cli"', '"source": {"subagent": {}}')
    path.write_text(text)
    assert dm.session_records(path, "repo") == []


def event(source):
    return {"id": "e1", **{k: "A bounded explanation" for k in (
        "context", "choice", "alternative", "reason", "tradeoff", "scope", "uncertainty", "future_test")},
        "attribution": "direct_user", "evidence": [{"source_id": source["source_id"],
        "quote": "Keep faint branches"}]}


def test_invalid_quote_and_false_attribution_fail(tmp_path):
    source = dm.session_records(session(tmp_path), "repo")[0]
    packet = {"schema_version": 1, "sources": [source]}
    proposal = {"schema_version": 1, "reviews": [{"source_id": source["source_id"],
        "disposition": "signal", "reason": "Explicit tradeoff"}], "events": [event(source)]}
    dm.validate_events(packet, proposal)
    proposal["events"][0]["evidence"][0]["quote"] = "Invented quote"
    with pytest.raises(ValueError, match="quote"):
        dm.validate_events(packet, proposal)
    proposal["events"][0] = event(source)
    source["origin"] = "automation"
    with pytest.raises(ValueError, match="direct user"):
        dm.validate_events(packet, proposal)


def principle(status):
    return {"id": "p1", "status": status, "support_event_ids": ["e1", "e2", "e3"],
        "counter_event_ids": [], "retrieval_tags": ["imaging"],
        **{k: "Specific bounded claim" for k in ("statement", "scope", "boundary",
        "predicted_choice", "cost", "counterevidence_search", "review_rationale")}}


def test_repetition_of_same_episode_does_not_promote(monkeypatch):
    monkeypatch.setattr(dm, "full_source", lambda source: "Verified choice")
    state = {"events": [{"id": f"e{i}", "attribution": "direct_user", "evidence": [{
        "quote": "Verified choice",
        "source": {"episode_id": "same", "timestamp": f"2026-0{i}-01T00:00:00Z"}}]}
        for i in range(1, 4)]}
    with pytest.raises(ValueError, match="independent"):
        dm.validate_principles(state, [principle("reflection")])
    for i, e in enumerate(state["events"]):
        e["evidence"][0]["source"]["episode_id"] = str(i)
    dm.validate_principles(state, [principle("axiom")])
    state["events"][0]["attribution"] = "automation_operations"
    with pytest.raises(ValueError, match="three human"):
        dm.validate_principles(state, [principle("axiom")])


def test_source_change_detected_and_fork_message_deduplicates(tmp_path):
    path = session(tmp_path)
    source = dm.session_records(path, "repo")[0]
    clone = tmp_path / "fork.jsonl"
    clone.write_text(path.read_text().replace('"id": "s1"', '"id": "s2"'))
    assert dm.session_records(clone, "repo")[0]["source_id"] == source["source_id"]
    path.write_text(path.read_text().replace("Keep faint", "Delete faint"))
    with pytest.raises(ValueError, match="changed"):
        dm.full_source(source)


def test_atomic_apply_does_not_consume_deferred_and_rejects_replay(tmp_path):
    source = dm.session_records(session(tmp_path), "repo")[0]
    packet = {"schema_version": 1, "run_id": "r1", "state_digest": dm.digest(dm.ledger(tmp_path)),
        "sources": [source], "scans": [], "coverage": [], "remaining_discovered_sources": 1}
    proposal = {"schema_version": 1, "run_id": "r1", "events": [], "reviews": [{
        "source_id": source["source_id"], "disposition": "deferred", "reason": "Needs context"}]}
    packet_path, proposal_path = tmp_path / "packet.json", tmp_path / "proposal.json"
    packet_path.write_text(json.dumps(packet))
    proposal_path.write_text(json.dumps(proposal))
    args = Namespace(workspace=tmp_path, packet=packet_path, proposal=proposal_path, validate_only=True)
    dm.apply(args)
    assert not (tmp_path / dm.LEDGER).exists()
    args.validate_only = False
    dm.apply(args)
    assert source["source_id"] not in dm.ledger(tmp_path)["reviews"]
    before = (tmp_path / dm.LEDGER).read_bytes()
    with pytest.raises(ValueError, match="Stale"):
        dm.apply(args)
    assert (tmp_path / dm.LEDGER).read_bytes() == before


def test_personal_registry_does_not_enqueue_repos_without_workers(tmp_path):
    from memoryctl import load_registry, MemoryCtlError
    (tmp_path / "config").mkdir()
    cfg = {"schema_version": 1, "repos": [
        {"name": "maintained", "root": "/one"},
        {"name": "personal", "root": "/two", "maintenance_enabled": False}]}
    path = tmp_path / "config/repos.json"
    path.write_text(json.dumps(cfg))
    assert [r["name"] for r in load_registry(tmp_path)["repos"]] == ["maintained"]
    cfg["repos"][1]["maintenance_enabled"] = "false"
    path.write_text(json.dumps(cfg))
    with pytest.raises(MemoryCtlError, match="boolean"):
        load_registry(tmp_path)

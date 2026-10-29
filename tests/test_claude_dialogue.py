"""Native history checks: completed human turns, provenance, and mixed coverage."""
import json
from pathlib import Path
import sys
from argparse import Namespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import decision_memory as dm


def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))
    return path


def native_rows(root, episode="claude-session"):
    def row(uid, parent, role, content, **extra):
        return {"type": role, "uuid": uid, "parentUuid": parent,
                "sessionId": episode, "cwd": str(root), "isSidechain": False,
                "timestamp": "2026-10-21T01:00:00Z",
                "message": {"role": role, "content": content,
                            **({"stop_reason": "end_turn"} if role == "assistant" else {})},
                **extra}
    return [
        {"type": "file-history-snapshot", "snapshot": {}},
        row("u1", None, "user", "Compare keeping branches with removing background."),
        row("a1", "u1", "assistant", [{"type": "text", "text": "A removes branches; B keeps noisy connections."}]),
        row("u2", "a1", "user", "Choose B: retain faint branches despite noise."),
        row("tool", "u2", "user", [{"type": "tool_result", "content": "tool body must not become evidence"}]),
        row("meta", "tool", "user", "Injected instructions", isMeta=True),
        row("a2", "meta", "assistant", [{"type": "text", "text": "I will keep those branches."}]),
        row("unfinished", "a2", "user", "This live tail has no completed response."),
    ]


def test_completed_turns_and_tool_filter_and_append_safety(tmp_path):
    path = write_rows(tmp_path / "native.jsonl", native_rows(tmp_path))
    records = dm.session_records(path, "repo")
    assert len(records) == 2
    assert all(r["provider"] == "claude_code" for r in records)
    before = records[1]["sha256"]
    assert dm.full_source(records[1]).startswith("Choose B")
    rows = native_rows(tmp_path)
    final = dict(rows[6], uuid="a3", parentUuid="unfinished")
    with path.open("a") as handle:
        handle.write(json.dumps(final) + "\n")
    assert len(dm.session_records(path, "repo")) == 3
    assert dm.session_records(path, "repo")[1]["sha256"] == before


def test_orphan_branch_does_not_become_completed(tmp_path):
    rows = native_rows(tmp_path)
    orphan = dict(rows[3], uuid="orphan", parentUuid="u1")
    rows.insert(6, orphan)
    records = dm.session_records(write_rows(tmp_path / "session.jsonl", rows), "repo")
    assert len(records) == 2


def test_native_context_omits_injections_and_verifies_hash(tmp_path):
    path = write_rows(tmp_path / "session.jsonl", native_rows(tmp_path))
    source = dm.session_records(path, "repo")[1]
    context = dm.read_context(source, 240)
    assert len(context["messages"]) == 5
    assert context["messages"][1]["role"] == "assistant"
    assert "A removes" in context["messages"][1]["text"]
    assert context["text_chars"] <= 240
    assert "Injected instructions" not in json.dumps(context)
    assert "tool body" not in json.dumps(context)
    path.write_text(path.read_text().replace("Choose B", "Choose A"))
    with pytest.raises(ValueError, match="changed"):
        dm.read_context(source)


def test_native_secrets_and_subagents_are_excluded(tmp_path):
    rows = native_rows(tmp_path)
    rows[3]["message"]["content"] = "API_KEY=fixture-secret"
    path = write_rows(tmp_path / "session.jsonl", rows)
    assert len(dm.session_records(path, "repo")) == 1
    assert dm.session_records(write_rows(tmp_path / "agent-copy.jsonl", rows), "repo") == []
    for row in rows:
        if "isSidechain" in row:
            row["isSidechain"] = True
    assert dm.session_records(write_rows(tmp_path / "side.jsonl", rows), "repo") == []


@pytest.mark.parametrize('injected', [
    '<skill><name>example</name>Instructions that are not a human decision.</skill>',
    '<external_codex_apps_open_page>{"page_id":null}</external_codex_apps_open_page>',
])
def test_native_injected_skill_and_app_event_are_excluded(tmp_path, injected):
    rows = native_rows(tmp_path)
    rows[3]['message']['content'] = injected
    path = write_rows(tmp_path / 'session.jsonl', rows)
    records = dm.session_records(path, 'repo')
    assert len(records) == 1
    assert 'Compare keeping' in dm.full_source(records[0])


def test_native_forks_deduplicate_and_relocation_checks_original_row(tmp_path):
    path = write_rows(tmp_path / "active/session.jsonl", native_rows(tmp_path))
    source = dm.session_records(path, "repo")[1]
    fork = native_rows(tmp_path, "fork")
    clone = write_rows(tmp_path / "fork.jsonl", fork)
    assert dm.session_records(clone, "repo")[1]["source_id"] == source["source_id"]
    archive = tmp_path / "archive"
    archive.mkdir()
    source["session_roots"] = [str(archive)]
    moved = archive / path.name
    path.rename(moved)
    assert dm.read_context(source)["resolved_path"] == str(moved)


def test_provider_scan_balance_and_root_health(tmp_path):
    claude = tmp_path / "claude"
    codex = tmp_path / "codex"
    for n in range(6):
        rows = native_rows(tmp_path, "claude-" + str(n))
        write_rows(claude / (str(n) + ".jsonl"), rows)
        write_rows(codex / (str(n) + ".jsonl"), [
            {"type": "session_meta", "payload": {"id": "codex-" + str(n), "cwd": str(tmp_path)}},
            {"type": "response_item", "payload": {"role": "user", "id": "c-" + str(n),
                 "content": [{"type": "text", "text": "Choose the existing method."}]}},
            {"type": "event_msg", "payload": {"type": "task_complete"}},
        ])
    state = {"reviews": {}, "scans": {}, "scan_attempts": {}}
    records, scans, coverage = dm.inventory_repo(
        {"name": "repo", "root": str(tmp_path), "decision_patterns": []},
        [str(claude), str(codex), str(tmp_path / "missing")], state, 4)
    assert len(scans) == 4
    assert coverage["dialog_providers"]["claude_code"]["sessions_scanned"] == 2
    assert coverage["dialog_providers"]["codex"]["sessions_scanned"] == 2
    assert coverage["dialog_roots"][-1]["status"] == "unavailable"


def test_native_quote_validation_and_atomic_apply(tmp_path):
    source = dm.session_records(write_rows(tmp_path / "native.jsonl", native_rows(tmp_path)), "repo")[1]
    packet = {"schema_version": 1, "run_id": "claude-test", "state_digest": dm.digest(dm.ledger(tmp_path)),
              "sources": [source], "scans": [], "coverage": [], "remaining_discovered_sources": 0}
    event = {"id": "decision", "attribution": "direct_user",
             **{k: "Bounded test explanation" for k in (
                 "context", "choice", "alternative", "reason", "tradeoff", "scope", "uncertainty", "future_test")},
             "evidence": [{"source_id": source["source_id"], "quote": "retain faint branches despite noise"}]}
    proposal = {"schema_version": 1, "run_id": "claude-test", "events": [event],
                "reviews": [{"source_id": source["source_id"], "disposition": "signal", "reason": "Explicit choice"}]}
    pp, qp = tmp_path / "packet.json", tmp_path / "proposal.json"
    pp.write_text(json.dumps(packet))
    qp.write_text(json.dumps(proposal))
    args = Namespace(workspace=tmp_path, packet=pp, proposal=qp, validate_only=True)
    dm.apply(args)
    assert not (tmp_path / dm.LEDGER).exists()
    args.validate_only = False
    dm.apply(args)
    retained = dm.ledger(tmp_path)["events"][0]["evidence"][0]["source"]
    assert retained["provider"] == "claude_code"
    assert dm.full_source(retained).startswith("Choose B")

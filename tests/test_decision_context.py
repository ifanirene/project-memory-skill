"""Bounded context retrieval preserves provenance without claiming comprehension."""
import json
from pathlib import Path
import shlex
import subprocess
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import decision_memory as dm


def context_session(tmp_path):
    active = tmp_path / ".codex" / "sessions"
    active.mkdir(parents=True)
    path = active / "session.jsonl"
    rows = [{"type": "session_meta", "payload": {
        "id": "episode", "cwd": str(tmp_path), "source": "cli"}}]
    texts = [
        ("user", "Earlier user question"),
        ("assistant", "An older assistant answer"),
        ("user", "Compare preserving branches with removing background"),
        ("assistant", "Option A removes faint branches; option B retains noisy connections"),
        ("user", "# AGENTS.md instructions\nInjected system context"),
        ("assistant", "password = private-short-value"),
        ("user", "Choose B: keep faint branches even with noisy background"),
        ("assistant", "I will preserve those connections"),
        ("user", "Check against the original image"),
        ("assistant", "A third subsequent message must not enter the window"),
    ]
    for n, (role, text) in enumerate(texts):
        rows.append({"type": "response_item", "timestamp": "2026-01-01T00:00:00Z",
                     "payload": {"type": "message", "id": f"m{n}", "role": role,
                                 "content": [{"type": "input_text" if role == "user"
                                              else "output_text", "text": text}]}})
        if n == 5:
            rows.append({"type": "response_item", "payload": {
                "type": "function_call_output", "output": "Tool output secret"}})
    rows.append({"type": "event_msg", "payload": {"type": "task_complete"}})
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    source = next(r for r in dm.session_records(path, "repo")
                  if r["excerpt"].startswith("Choose B"))
    return path, source


def test_context_includes_alternatives_and_correction_only_bounded_neighbors(tmp_path):
    _, source = context_session(tmp_path)
    result = dm.read_context(source)
    messages = result["messages"]
    assert len(messages) == 5
    assert "Option A" in messages[1]["text"]
    assert messages[2]["text"].startswith("Choose B")
    assert messages[2]["is_evidence"]
    assert messages[2]["sha256"] == source["sha256"] == result["evidence_sha256"]
    combined = json.dumps(result)
    for forbidden in ("private-short-value", "Injected system context", "Tool output secret",
                      "Earlier user question", "third subsequent"):
        assert forbidden not in combined
    assert "not proof" in result["notice"]


@pytest.mark.parametrize("budget", [1, 19, 100, 6000])
def test_context_text_budget_and_explicit_truncation(tmp_path, budget):
    _, source = context_session(tmp_path)
    result = dm.read_context(source, budget)
    assert sum(len(m["text"]) for m in result["messages"]) <= budget
    assert result["text_chars"] <= budget
    assert result["context_truncated"] == (budget < 6000)
    with pytest.raises(ValueError, match="between"):
        dm.read_context(source, 24001)


def test_context_recovers_archive_and_rejects_changed_target(tmp_path):
    path, source = context_session(tmp_path)
    archive = path.parent.parent / "archived_sessions"
    archive.mkdir()
    moved = archive / path.name
    path.rename(moved)
    assert dm.read_context(source)["resolved_path"] == str(moved)
    moved.write_text(moved.read_text().replace("Choose B:", "Choose A:"))
    with pytest.raises(ValueError, match="changed"):
        dm.read_context(source)


@pytest.mark.parametrize("text", [
    "Bearer abc123", "API_KEY=short-secret", "secret: short-value",
    '{"api_key": "short-secret"}',
    "-----BEGIN PRIVATE KEY-----\nbytes", "sk-abcdefghijklmnopqrstuvwx",
])
def test_common_context_credentials_are_omitted(text):
    assert dm.clean_context(text) == ""


def test_remote_context_delegates_without_recursive_host(tmp_path, monkeypatch):
    _, source = context_session(tmp_path)
    source.update(host="scg", remote_python="python3", remote_script="/helper.py")
    def fake_run(command, **kwargs):
        tokens = shlex.split(command[-1])
        assert tokens[:3] == ["python3", "/helper.py", "read-context"]
        assert "host" not in json.loads(tokens[tokens.index("--source-json") + 1])
        assert tokens[-2:] == ["--max-chars", "100"]
        return SimpleNamespace(returncode=0, stdout=json.dumps({"messages": []}))
    monkeypatch.setattr(dm.subprocess, "run", fake_run)
    assert dm.read_context(source, 100) == {"messages": []}


def test_context_cli_on_bounded_fixture(tmp_path):
    _, source = context_session(tmp_path)
    result = subprocess.run(
        [sys.executable, str(Path(dm.__file__)), "read-context", "--source-json",
         json.dumps(source), "--max-chars", "300"],
        capture_output=True, text=True, check=True,
    )
    context = json.loads(result.stdout)
    assert context["evidence_sha256"] == source["sha256"]
    assert len(context["messages"]) == 5
    assert context["text_chars"] <= 300

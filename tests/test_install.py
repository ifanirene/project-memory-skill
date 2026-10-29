"""Exercise installation as a user, including preservation and runnable helpers."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]


def run_installer(*args, env=None):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts/install.py"), *map(str, args)],
        capture_output=True, text=True, env=env,
    )


def test_complete_install_runs_without_source_checkout(tmp_path):
    destination = tmp_path / "skills with spaces" / "project-memory"
    result = run_installer("--dest", destination)
    assert result.returncode == 0, result.stderr
    version = (ROOT / "VERSION").read_text().strip()
    assert f"v{version}" in result.stdout
    assert (destination / "VERSION").read_bytes() == (ROOT / "VERSION").read_bytes()
    assert f'version: "{version}"' in (destination / "SKILL.md").read_text()
    for directory in ("audits", "plans", "tests", ".git", "__pycache__"):
        assert not (destination / directory).exists()
    assert not list(destination.rglob("*.pyc"))
    for helper in ("bootstrap_repo_memory.py", "principle_library.py", "memoryctl.py"):
        check = subprocess.run(
            [sys.executable, str(destination / "scripts" / helper), "--help"],
            cwd=tmp_path, capture_output=True, text=True,
        )
        assert check.returncode == 0, check.stderr
    workspace = tmp_path / "private memory"
    registry = tmp_path / "repos.json"
    registry.write_text(json.dumps({"schema_version": 1, "repos": [], "dialog_roots": []}))
    setup = subprocess.run(
        [sys.executable, str(destination / "scripts/principle_library.py"), "setup",
         "--workspace", str(workspace), "--registry", str(registry),
         "--python", sys.executable],
        cwd=tmp_path, capture_output=True, text=True,
    )
    assert setup.returncode == 0, setup.stderr
    prompt = (workspace / "config/prompts/daily-observer.txt").read_text()
    assert str(destination) in prompt
    assert str(ROOT) not in prompt


@pytest.mark.parametrize("kind", ["directory", "file", "symlink", "dangling"])
def test_refuses_existing_destination_without_changes(tmp_path, kind):
    destination = tmp_path / "installed"
    original = tmp_path / "local fix.txt"
    original.write_text("Keep this local fix.\n")
    if kind == "directory":
        destination.mkdir()
        (destination / "private-state.json").write_text("private state")
    elif kind == "file":
        destination.write_text("existing file")
    else:
        destination.symlink_to(original if kind == "symlink" else tmp_path / "missing")
    result = run_installer("--dest", destination)
    assert result.returncode != 0
    assert "already exists" in result.stderr
    assert original.read_text() == "Keep this local fix.\n"
    if kind == "directory":
        assert list(destination.iterdir()) == [destination / "private-state.json"]
        assert (destination / "private-state.json").read_text() == "private state"
    elif kind == "file":
        assert destination.read_text() == "existing file"
    else:
        assert destination.is_symlink()


@pytest.mark.parametrize("use_codex_home", [True, False])
def test_default_location_respects_environment(tmp_path, use_codex_home):
    env = {**os.environ, "HOME": str(tmp_path / "home")}
    env.pop("CODEX_HOME", None)
    expected_home = tmp_path / "home" / ".codex"
    if use_codex_home:
        expected_home = tmp_path / "custom codex"
        env["CODEX_HOME"] = str(expected_home)
    result = run_installer(env=env)
    assert result.returncode == 0, result.stderr
    assert (expected_home / "skills/project-memory/SKILL.md").is_file()


def test_refuses_install_inside_source():
    result = run_installer("--dest", ROOT / "scripts" / "nested-install")
    assert result.returncode != 0
    assert "outside the source" in result.stderr
    assert not (ROOT / "scripts" / "nested-install").exists()

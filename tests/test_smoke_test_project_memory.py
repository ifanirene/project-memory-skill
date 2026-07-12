from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "smoke_test_project_memory.py"
)


def run(*command: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def make_committed_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "project"
    (repo / "docs").mkdir(parents=True)
    (repo / "results" / "analysis_a").mkdir(parents=True)
    (repo / "scripts").mkdir()
    (repo / "data").mkdir()
    (repo / "docs" / "pipelines").mkdir()
    (repo / "AGENTS.md").write_text("# Repository guidance\n")
    (repo / "ANALYSIS_INDEX.md").write_text("# Analysis index\n")
    (repo / "docs" / "LESSONS.md").write_text("# Lessons\n")
    (repo / "results" / "analysis_a" / "NOTES.md").write_text(
        "# Analysis A\n\n## Status\nACTIVE\n"
    )

    for command in (
        ("git", "init", "-q"),
        ("git", "config", "user.email", "smoke-test@example.invalid"),
        ("git", "config", "user.name", "Project Memory Smoke Test"),
        ("git", "add", "."),
        ("git", "commit", "-qm", "initial fixture"),
    ):
        result = run(*command, cwd=repo)
        assert result.returncode == 0, result.stderr
    return repo


def test_smoke_harness_changes_real_repo_then_restores_it(tmp_path: Path) -> None:
    repo = make_committed_repo(tmp_path)
    lessons_before = (repo / "docs" / "LESSONS.md").read_bytes()
    agents_before = (repo / "AGENTS.md").read_bytes()

    result = run(
        sys.executable,
        str(SCRIPT_PATH),
        "--repo",
        str(repo),
        cwd=repo,
    )

    assert result.returncode == 0, result.stderr
    assert "Project-memory smoke test: PASS" in result.stdout
    assert "reversible real-repo file changes" in result.stdout
    assert "real repo unchanged" in result.stdout
    assert (repo / "docs" / "LESSONS.md").read_bytes() == lessons_before
    assert (repo / "AGENTS.md").read_bytes() == agents_before
    assert not (repo / "results" / ".project-memory-smoke-test").exists()
    status = run("git", "status", "--porcelain", cwd=repo)
    assert status.returncode == 0
    assert status.stdout == ""


def test_smoke_harness_refuses_dirty_repo(tmp_path: Path) -> None:
    repo = make_committed_repo(tmp_path)
    lessons = repo / "docs" / "LESSONS.md"
    lessons.write_text("# Lessons\n\nUser work in progress.\n")

    result = run(
        sys.executable,
        str(SCRIPT_PATH),
        "--repo",
        str(repo),
        cwd=repo,
    )

    assert result.returncode == 2
    assert "must be clean" in result.stderr
    assert lessons.read_text() == "# Lessons\n\nUser work in progress.\n"

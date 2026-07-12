from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "bootstrap_repo_memory.py"


def run_helper(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def test_bootstrap_empty_repo_audit_then_scaffold(tmp_path: Path) -> None:
    repo = tmp_path / "empty_repo"
    repo.mkdir()

    audit = run_helper("--repo", str(repo), "--audit-only")
    assert audit.returncode == 0
    assert "[MISSING" in audit.stdout
    assert "AGENTS.md" in audit.stdout

    scaffold = run_helper("--repo", str(repo), "--yes")
    assert scaffold.returncode == 0
    assert (repo / "AGENTS.md").exists()
    assert (repo / "ANALYSIS_INDEX.md").exists()
    assert (repo / "docs" / "LESSONS.md").exists()
    assert (repo / "docs" / "pipelines").is_dir()
    assert (repo / "scripts").is_dir()
    assert (repo / "scripts" / "analysis").is_dir()
    assert (repo / "scripts" / "preprocessing").is_dir()
    assert (repo / "data").is_dir()
    assert (repo / "data" / "raw").is_dir()
    assert (repo / "data" / "processed").is_dir()
    assert (repo / "results").is_dir()
    assert (repo / "config").is_dir()
    assert (repo / "notebooks").is_dir()
    assert (repo / "tests").is_dir()
    assert (repo / ".gitignore").exists()
    assert "analysis_manifest.json" in (repo / ".gitignore").read_text()
    assert not any(repo.rglob("NOTES.md"))
    assert (repo / "docs" / "pipelines").is_dir()


def test_bootstrap_existing_repo_prompts_and_respects_manual_review(tmp_path: Path) -> None:
    repo = tmp_path / "partial_repo"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "docs").mkdir()
    (repo / "docs" / "MEMORY.md").write_text("Existing lessons equivalent.\n")
    (repo / "AGENTS.md").write_text("Custom guide.\n")

    result = run_helper("--repo", str(repo), input_text="y\n")

    assert result.returncode == 0
    assert "Create" in result.stdout
    assert "manual review" in result.stdout.lower()
    assert (repo / "AGENTS.md").read_text() == "Custom guide.\n"
    assert (repo / "ANALYSIS_INDEX.md").exists()
    assert (repo / "docs" / "LESSONS.md").exists() is False
    assert (repo / "docs" / "MEMORY.md").exists()
    assert (repo / "results").is_dir()
    assert (repo / "data").is_dir()


def test_src_satisfies_code_home_without_creating_scripts(tmp_path: Path) -> None:
    repo = tmp_path / "src_repo"
    repo.mkdir()
    (repo / "src").mkdir()

    result = run_helper("--repo", str(repo), "--yes", "--mode", "monitored")

    assert result.returncode == 0
    assert "acceptable equivalent" in result.stdout
    assert (repo / "src").is_dir()
    assert not (repo / "scripts").exists()


def test_monitored_mode_reports_contract_and_manifest_drift(tmp_path: Path) -> None:
    repo = tmp_path / "monitored"
    (repo / "docs").mkdir(parents=True)
    (repo / "results" / "goal" / "analysis" / "runs" / "threshold_10").mkdir(
        parents=True
    )
    (repo / "AGENTS.md").write_text("Existing contract.\n")
    (repo / "ANALYSIS_INDEX.md").write_text("# Index\n")
    (repo / "docs" / "LESSONS.md").write_text("# Lessons\n")
    (repo / ".gitignore").write_text("/results/**\n")

    result = run_helper("--repo", str(repo), "--audit-only")

    assert result.returncode == 0
    assert "Mode: monitored" in result.stdout
    assert "AGENTS.md is missing contract terms" in result.stdout
    assert "analysis_manifest.json" in result.stdout
    assert "ignored without an exception" in result.stdout
    assert "1 direct runs/* variant directories" in result.stdout

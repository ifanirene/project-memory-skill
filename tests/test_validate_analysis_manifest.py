from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_analysis_manifest.py"


def valid_manifest() -> dict:
    return {
        "schema_version": 1,
        "analysis_id": "T1-01",
        "variant_id": "shared_control_min200",
        "created_at": "2026-07-11T20:00:00Z",
        "provenance_mode": "native",
        "execution": {
            "command": ["python", "scripts/analysis.py", "--min-cells", "200"],
            "working_directory": "/repo",
            "script": "scripts/analysis.py",
            "script_sha256": "a" * 64,
            "git_commit": "abc123",
            "git_dirty": False,
            "interpreter": "/env/bin/python",
        },
        "inputs": [{"path": "/data/input.h5ad", "role": "input"}],
        "parameters": {"min_cells": 200},
        "outputs": {
            "directory": "results/goal/analysis/runs/shared_control_min200",
            "artifacts": ["summary.csv"],
        },
        "validation": {"status": "passed", "checks": ["row counts"]},
    }


def test_valid_manifest_passes(tmp_path: Path) -> None:
    path = tmp_path / "analysis_manifest.json"
    path.write_text(json.dumps(valid_manifest()))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert "VALID" in result.stdout


def test_missing_execution_provenance_fails(tmp_path: Path) -> None:
    value = valid_manifest()
    del value["execution"]["script_sha256"]
    path = tmp_path / "analysis_manifest.json"
    path.write_text(json.dumps(value))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "script_sha256" in result.stdout


def test_repo_discovers_both_output_roots_and_keeps_explicit_paths(tmp_path: Path) -> None:
    paths = [tmp_path / name / "branch" / "analysis_manifest.json"
             for name in ("results", "output", "legacy")]
    for path in paths:
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(valid_manifest()))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", str(tmp_path), str(paths[2]), str(paths[0])],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0
    assert len(result.stdout.strip().splitlines()) == 3
    for path in paths:
        assert result.stdout.count(str(path)) == 1


def test_output_only_repository_cannot_hide_invalid_manifest(tmp_path: Path) -> None:
    path = tmp_path / "output" / "branch" / "analysis_manifest.json"
    path.parent.mkdir(parents=True)
    path.write_text("{}")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", str(tmp_path)],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 1
    assert f"INVALID {path}" in result.stdout

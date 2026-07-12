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

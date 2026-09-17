"""Opt-in file verification reports real drift without reading large data."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from verify_manifest_files import verify_files
from test_validate_analysis_manifest import valid_manifest, SCRIPT


def fixture(tmp_path):
    manifest = valid_manifest()
    script = tmp_path / "analysis.py"
    script.write_text("pass\n")
    source = tmp_path / "input.csv"
    source.write_text("old\n")
    manifest["execution"].update(working_directory=str(tmp_path), script="analysis.py",
                                 script_sha256=hashlib.sha256(script.read_bytes()).hexdigest())
    manifest["inputs"] = [{"path": "input.csv", "size_bytes": source.stat().st_size,
                           "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}]
    manifest["outputs"] = {"directory": "output", "artifacts": ["result.csv"]}
    return manifest, source


def test_actual_hash_drift_and_missing_output_make_opt_in_cli_fail(tmp_path):
    manifest, source = fixture(tmp_path)
    source.write_text("new\n")
    path = tmp_path / "analysis_manifest.json"
    path.write_text(json.dumps(manifest))
    normal = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
    assert normal.returncode == 0
    result = subprocess.run([sys.executable, str(SCRIPT), str(path), "--verify-files"],
                            capture_output=True, text=True)
    assert result.returncode == 1
    report = json.loads(result.stdout.split("FILE_CHECK ", 1)[1])
    assert report["failures"] == 2
    assert {c["status"] for c in report["checks"]} == {"verified", "drift", "missing"}
    assert "not proof" in report["claim"]


def test_large_file_is_not_read_and_absent_hash_is_not_full_verification(tmp_path, monkeypatch):
    manifest, source = fixture(tmp_path)
    (tmp_path / "output").mkdir()
    (tmp_path / "output/result.csv").write_text("saved result")
    original = Path.open

    def guarded(path, *args, **kwargs):
        if path == source:
            raise AssertionError("Above-limit input was opened")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded)
    report = verify_files(manifest, 2)
    assert report["failures"] == 0
    input_check = next(c for c in report["checks"] if c["role"] == "input")
    assert input_check["status"] == "not_checked" and "byte limit" in input_check["reason"]
    output_check = next(c for c in report["checks"] if c["role"] == "output")
    assert output_check["exists"] is True
    assert output_check["status"] == "not_checked"


def test_directory_artifacts_and_inputs_exist_without_content_verification(tmp_path):
    manifest, _ = fixture(tmp_path)
    (tmp_path / "dataset").mkdir()
    (tmp_path / "output" / "curation").mkdir(parents=True)
    manifest["inputs"] = [{"path": "dataset"}]
    manifest["outputs"]["artifacts"] = ["curation"]
    report = verify_files(manifest, 50_000_000)
    assert report["failures"] == 0
    for check in report["checks"]:
        if check["role"] in {"input", "output"}:
            assert check["status"] == "not_checked" and check["exists"]
            assert "Directory exists" in check["reason"]

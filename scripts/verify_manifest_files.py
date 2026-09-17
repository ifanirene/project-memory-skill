"""Bounded read-only checks of files declared by an analysis manifest.

Inputs: manifest object; outputs: drift/missing/not_checked/verified findings.
Parameters: byte limit for hashing (default supplied by CLI). No scientific rerun.
Dependencies: Python standard library. Usage: validate_analysis_manifest --verify-files.
"""
from __future__ import annotations

import hashlib
from pathlib import Path


def verify_files(manifest: dict, max_hash_bytes: int) -> dict:
    execution = manifest["execution"]
    cwd = Path(execution["working_directory"])
    checks = []

    def inspect(path_value, role, expected_hash=None, expected_size=None):
        path = Path(path_value)
        if not path.is_absolute():
            if not cwd.is_absolute():
                checks.append({"path": str(path), "role": role, "status": "not_checked",
                               "reason": "Working directory is not absolute"})
                return
            path = cwd / path
        result = {"path": str(path), "role": role}
        try:
            if path.is_dir():
                checks.append({**result, "status": "not_checked", "exists": True,
                               "reason": "Directory exists; contents and identity not verified"})
                return
            if not path.is_file():
                checks.append({**result, "status": "missing", "reason": "Declared file absent"})
                return
            size = path.stat().st_size
            result["size_bytes"] = size
            if expected_size is not None and size != expected_size:
                checks.append({**result, "status": "drift", "reason": "Size differs",
                               "expected_size_bytes": expected_size})
                return
            if not expected_hash:
                checks.append({**result, "status": "not_checked", "exists": True,
                               "reason": "No declared content hash; existence verified only"})
                return
            if size > max_hash_bytes:
                checks.append({**result, "status": "not_checked", "exists": True,
                               "reason": "Hash skipped: exceeds byte limit"})
                return
            digest = hashlib.sha256()
            with path.open("rb") as handle:
                for block in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(block)
            actual = digest.hexdigest()
            checks.append({**result, "status": "verified" if actual == expected_hash else "drift",
                           "sha256": actual, "expected_sha256": expected_hash,
                           "reason": "Content hash matches" if actual == expected_hash else "Content hash differs"})
        except OSError as exc:
            checks.append({**result, "status": "not_checked", "reason": str(exc)})

    inspect(execution["script"], "entrypoint", execution["script_sha256"])
    if execution.get("implementation_script"):
        inspect(execution["implementation_script"], "implementation",
                execution.get("implementation_script_sha256"))
    for item in execution.get("step_scripts", []):
        inspect(item["script"], "step_script", item.get("script_sha256"))
    for item in manifest["inputs"]:
        if not isinstance(item, dict) or not item.get("path"):
            checks.append({"role": "input", "status": "not_checked",
                           "reason": "Input record lacks a path"})
            continue
        inspect(item["path"], "input", item.get("sha256"), item.get("size_bytes"))
    directory = Path(manifest["outputs"]["directory"])
    for artifact in manifest["outputs"]["artifacts"]:
        inspect(directory / artifact, "output")
    return {
        "claim": "Declared-file verification only; not proof of reproducibility",
        "max_hash_bytes": max_hash_bytes, "checks": checks,
        "failures": sum(c["status"] in {"missing", "drift"} for c in checks),
        "not_verified": [
            "Historical code recovery from Git, dirty diff, or code snapshots",
            "Dependency/environment identity and external service versions",
            "Parameter completeness and scientific correctness",
            "Output content identity without recorded output hashes",
            "Large input hashes above the configured byte limit",
            "Execution or numerical reproduction of results",
        ],
    }

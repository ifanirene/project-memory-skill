#!/usr/bin/env python3
"""Validate Project Memory analysis manifests with only the standard library."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


TOP_LEVEL_FIELDS = {
    "schema_version",
    "analysis_id",
    "variant_id",
    "created_at",
    "provenance_mode",
    "execution",
    "inputs",
    "parameters",
    "outputs",
    "validation",
}
EXECUTION_FIELDS = {
    "command",
    "working_directory",
    "script",
    "script_sha256",
    "git_commit",
    "git_dirty",
    "interpreter",
}
OUTPUT_FIELDS = {"directory", "artifacts"}


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_manifest(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["manifest must be a JSON object"]

    missing = TOP_LEVEL_FIELDS - set(value)
    if missing:
        errors.append(f"missing top-level fields: {sorted(missing)}")
    if value.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for field in ("analysis_id", "variant_id", "created_at"):
        if not _nonempty_string(value.get(field)):
            errors.append(f"{field} must be a non-empty string")
    created_at = value.get("created_at")
    if _nonempty_string(created_at):
        try:
            datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError:
            errors.append("created_at must be an ISO-8601 timestamp")
    if value.get("provenance_mode") not in {"native", "reconstructed"}:
        errors.append("provenance_mode must be native or reconstructed")

    execution = value.get("execution")
    if not isinstance(execution, dict):
        errors.append("execution must be an object")
    else:
        missing_execution = EXECUTION_FIELDS - set(execution)
        if missing_execution:
            errors.append(f"missing execution fields: {sorted(missing_execution)}")
        command = execution.get("command")
        if not (
            isinstance(command, list)
            and command
            and all(_nonempty_string(part) for part in command)
        ):
            errors.append("execution.command must be a non-empty string array")
        for field in (
            "working_directory",
            "script",
            "script_sha256",
            "git_commit",
            "interpreter",
        ):
            if not _nonempty_string(execution.get(field)):
                errors.append(f"execution.{field} must be a non-empty string")
        script_hash = execution.get("script_sha256")
        if (
            value.get("provenance_mode") == "native"
            and _nonempty_string(script_hash)
            and (
                len(script_hash) != 64
                or any(char not in "0123456789abcdefABCDEF" for char in script_hash)
            )
        ):
            errors.append("native execution.script_sha256 must be a SHA-256 hex digest")
        if not isinstance(execution.get("git_dirty"), bool):
            errors.append("execution.git_dirty must be boolean")

    if not isinstance(value.get("inputs"), list):
        errors.append("inputs must be an array")
    if not isinstance(value.get("parameters"), dict):
        errors.append("parameters must be an object of resolved parameters")

    outputs = value.get("outputs")
    if not isinstance(outputs, dict):
        errors.append("outputs must be an object")
    else:
        missing_outputs = OUTPUT_FIELDS - set(outputs)
        if missing_outputs:
            errors.append(f"missing outputs fields: {sorted(missing_outputs)}")
        if not _nonempty_string(outputs.get("directory")):
            errors.append("outputs.directory must be a non-empty string")
        artifacts = outputs.get("artifacts")
        if not (
            isinstance(artifacts, list)
            and all(_nonempty_string(item) for item in artifacts)
        ):
            errors.append("outputs.artifacts must be a string array")

    validation = value.get("validation")
    if not isinstance(validation, dict):
        errors.append("validation must be an object")
    elif validation.get("status") not in {"passed", "failed", "partial", "not_run"}:
        errors.append("validation.status must be passed, failed, partial, or not_run")
    return errors


def discover(repo: Path) -> list[Path]:
    results = repo / "results"
    if not results.exists():
        return []
    return sorted(results.glob("**/analysis_manifest.json"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--repo", type=Path, help="Validate every manifest under repo/results.")
    args = parser.parse_args()

    paths = [path.expanduser().resolve() for path in args.paths]
    if args.repo:
        paths.extend(discover(args.repo.expanduser().resolve()))
    paths = sorted(set(paths))
    if not paths:
        print("No analysis_manifest.json files found.")
        return 0

    failed = 0
    for path in paths:
        try:
            value = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            errors = [f"could not read valid JSON: {exc}"]
        else:
            errors = validate_manifest(value)
        if errors:
            failed += 1
            print(f"INVALID {path}")
            for error in errors:
                print(f"- {error}")
        else:
            print(f"VALID {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())


#!/usr/bin/env python3
"""Run a reversible controller safety test in a real Git repository.

The repository must start clean. Controlled file changes happen in the real
checkout and are restored from exact byte snapshots without git reset or
checkout. Collector state remains temporary to avoid polluting production
memory. This is not a live semantic maintenance test.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
MEMORYCTL = SKILL_ROOT / "scripts" / "memoryctl.py"
BOOTSTRAP = SKILL_ROOT / "scripts" / "bootstrap_repo_memory.py"
MEMORY_PATTERNS = [
    "AGENTS.md",
    "ANALYSIS_INDEX.md",
    ".gitignore",
    "docs/LESSONS.md",
    "docs/pipelines/*.md",
    "**/NOTES.md",
]


class SmokeTestError(RuntimeError):
    """Raised when an integration assertion fails."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Safety-test the controller against a real repo while performing "
            "controlled writes directly in the checkout and restoring them exactly."
        )
    )
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--max-files", type=int, default=8)
    parser.add_argument("--max-chars", type=int, default=100_000)
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep the temporary test workspace and print its path.",
    )
    return parser.parse_args()


def run_command(*command: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def require_success(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode != 0:
        raise SmokeTestError(
            f"{label} failed with exit {result.returncode}:\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def discover_memory_files(repo: Path) -> list[Path]:
    found: set[Path] = set()
    for pattern in MEMORY_PATTERNS:
        for path in repo.glob(pattern):
            if path.is_file() and not path.is_symlink():
                resolved = path.resolve()
                try:
                    resolved.relative_to(repo)
                except ValueError:
                    continue
                found.add(resolved)
    return sorted(found)


def repo_fingerprint(repo: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    files = discover_memory_files(repo)
    for path in files:
        relative = path.relative_to(repo).as_posix().encode()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        data = path.read_bytes()
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest(), len(files)


def git_status(repo: Path) -> bytes | None:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z"],
        cwd=repo,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def make_collector(workspace: Path, repo: Path) -> None:
    write_json(
        workspace / "config" / "repos.json",
        {
            "schema_version": 1,
            "repos": [
                {
                    "name": repo.name,
                    "root": str(repo),
                    "patterns": MEMORY_PATTERNS,
                }
            ],
        },
    )
    write_json(
        workspace / "state" / "repo_cursors_v2.json",
        {"schema_version": 1, "files": {}},
    )
    write_json(
        workspace / "state" / "maintenance_queue_v2.json",
        {"schema_version": 1, "items": []},
    )


def run_collector_test(
    workspace: Path, repo: Path, *, max_files: int, max_chars: int
) -> dict[str, Any]:
    packet_path = workspace / "runs" / "smoke" / "packet.json"
    proposal_path = workspace / "runs" / "smoke" / "proposal.json"
    second_packet_path = workspace / "runs" / "smoke" / "packet2.json"

    doctor = run_command(
        sys.executable,
        str(MEMORYCTL),
        "doctor",
        "--workspace",
        str(workspace),
    )
    require_success(doctor, "memoryctl doctor")

    collect = run_command(
        sys.executable,
        str(MEMORYCTL),
        "collect",
        "--workspace",
        str(workspace),
        "--output",
        str(packet_path),
        "--max-files",
        str(max_files),
        "--max-chars",
        str(max_chars),
        "--quality-audit-files",
        "0",
    )
    require_success(collect, "memoryctl collect")
    packet = json.loads(packet_path.read_text())
    sources = packet.get("sources", [])
    if not sources:
        raise SmokeTestError("Collector produced no eligible source documents")

    source_ids = [source["source_id"] for source in sources]
    proposal = {
        "schema_version": 1,
        "run_id": packet["run_id"],
        "processed_source_ids": source_ids,
        "candidates": [
            {
                "statement": (
                    "Smoke-test candidate proving structured observation writes; "
                    "do not promote this synthetic operational record."
                ),
                "scope": "automation_operations",
                "confidence": "low",
                "source_ids": [source_ids[0]],
                "rationale": "Synthetic integration record for controller validation only.",
            }
        ],
        "maintenance_items": [],
    }
    write_json(proposal_path, proposal)

    validate = run_command(
        sys.executable,
        str(MEMORYCTL),
        "validate",
        "--workspace",
        str(workspace),
        "--packet",
        str(packet_path),
        "--proposal",
        str(proposal_path),
    )
    require_success(validate, "memoryctl validate")

    apply = run_command(
        sys.executable,
        str(MEMORYCTL),
        "apply",
        "--workspace",
        str(workspace),
        "--packet",
        str(packet_path),
        "--proposal",
        str(proposal_path),
    )
    require_success(apply, "memoryctl apply")

    scrubbed_packet = json.loads(packet_path.read_text())
    if not scrubbed_packet.get("content_scrubbed_after_apply"):
        raise SmokeTestError("Applied packet was not marked as content-scrubbed")
    if any("content" in source for source in scrubbed_packet["sources"]):
        raise SmokeTestError("Applied packet still contains source document content")

    cursor = json.loads((workspace / "state" / "repo_cursors_v2.json").read_text())
    if len(cursor["files"]) != len(sources):
        raise SmokeTestError("Cursor count does not match processed source count")

    collect2 = run_command(
        sys.executable,
        str(MEMORYCTL),
        "collect",
        "--workspace",
        str(workspace),
        "--output",
        str(second_packet_path),
        "--max-files",
        str(max_files),
        "--max-chars",
        str(max_chars),
        "--quality-audit-files",
        "0",
    )
    require_success(collect2, "second memoryctl collect")
    packet2 = json.loads(second_packet_path.read_text())
    repeated = set(source_ids) & {
        source["source_id"] for source in packet2.get("sources", [])
    }
    if repeated:
        raise SmokeTestError(f"Incremental collection repeated sources: {sorted(repeated)}")

    observation_files = list((workspace / "observations" / "repo_events").glob("*.jsonl"))
    logs = list((workspace / "logs" / "runs").glob("*.md"))
    if len(observation_files) != 1 or len(logs) != 1:
        raise SmokeTestError("Collector did not create one observation file and one run log")

    return {
        "source_count": len(sources),
        "memory_file_count": len(discover_memory_files(repo)),
        "deferred_count": packet.get("remaining_changed_files", 0),
        "oversized": [
            source["relative_path"]
            for source in packet.get("deferred_oversized_sources", [])
        ],
        "repeated_source_count": 0,
        "packet_scrubbed": True,
    }


def run_protected_guidance_test(workspace: Path, repo_name: str) -> None:
    queue_path = workspace / "state" / "maintenance_queue_v2.json"
    queue = json.loads(queue_path.read_text())
    key = "smoke-protected-agents"
    queue["items"].append(
        {
            "idempotency_key": key,
            "repo": repo_name,
            "status": "open",
            "attempts": 0,
            "suggested_target": "AGENTS.md",
            "protected_information": {"impact": "confirmed"},
        }
    )
    write_json(queue_path, queue)

    claim = run_command(
        sys.executable,
        str(MEMORYCTL),
        "queue-claim",
        "--workspace",
        str(workspace),
        "--idempotency-key",
        key,
        "--repo",
        repo_name,
        "--run-id",
        "smoke-repo-worker",
    )
    require_success(claim, "protected queue claim")

    forbidden = run_command(
        sys.executable,
        str(MEMORYCTL),
        "queue-finish",
        "--workspace",
        str(workspace),
        "--idempotency-key",
        key,
        "--repo",
        repo_name,
        "--run-id",
        "smoke-repo-worker",
        "--status",
        "resolved",
        "--evidence",
        "synthetic protected change",
    )
    if forbidden.returncode == 0 or "--permission-source" not in forbidden.stderr:
        raise SmokeTestError("Protected AGENTS.md change resolved without permission")

    deferred = run_command(
        sys.executable,
        str(MEMORYCTL),
        "queue-finish",
        "--workspace",
        str(workspace),
        "--idempotency-key",
        key,
        "--repo",
        repo_name,
        "--run-id",
        "smoke-repo-worker",
        "--status",
        "deferred",
        "--evidence",
        "explicit user permission was not supplied",
    )
    require_success(deferred, "protected queue deferral")


def run_actual_write_test(repo: Path) -> None:
    lessons = repo / "docs" / "LESSONS.md"
    agents = repo / "AGENTS.md"
    test_dir = repo / "results" / ".project-memory-smoke-test"
    test_note = test_dir / "NOTES.md"
    if not lessons.is_file() or not agents.is_file():
        raise SmokeTestError("Real repo is missing AGENTS.md or docs/LESSONS.md")
    if test_dir.exists():
        raise SmokeTestError(f"Reserved smoke-test path already exists: {test_dir}")

    lessons_before = lessons.read_bytes()
    agents_before = agents.read_bytes()
    marker = b"\n<!-- project-memory-smoke-test: reversible edit -->\n"
    try:
        lessons.write_bytes(lessons_before + marker)
        test_dir.mkdir(parents=True, exist_ok=False)
        test_note.write_text(
            "## Status\nACTIVE — temporary smoke test\n\n"
            "## Cross-document review\n"
            "- `ANALYSIS_INDEX.md`: no change — smoke test only.\n"
            "- `docs/LESSONS.md`: temporary reversible marker only.\n"
            "- `Personal memory`: no change — smoke test only.\n"
        )

        status = git_status(repo)
        if (
            status is None
            or b"docs/LESSONS.md" not in status
            or b".project-memory-smoke-test" not in status
        ):
            raise SmokeTestError("Git did not detect the controlled real-repo changes")
        if agents.read_bytes() != agents_before:
            raise SmokeTestError("Controlled write test changed AGENTS.md")
    finally:
        lessons.write_bytes(lessons_before)
        if test_note.exists():
            test_note.unlink()
        if test_dir.exists():
            test_dir.rmdir()

    if lessons.read_bytes() != lessons_before or agents.read_bytes() != agents_before:
        raise SmokeTestError("Controlled files were not restored exactly")


def main() -> int:
    args = parse_args()
    repo = args.repo.expanduser().resolve()
    if not repo.is_dir():
        print(f"Repository does not exist: {repo}", file=sys.stderr)
        return 2
    if args.max_files < 1 or args.max_chars < 1:
        print("--max-files and --max-chars must be positive", file=sys.stderr)
        return 2

    fingerprint_before, file_count = repo_fingerprint(repo)
    status_before = git_status(repo)
    if status_before is None:
        print("Repository must be a Git worktree", file=sys.stderr)
        return 2
    if status_before:
        print(
            "Repository must be clean before the smoke test; commit or stash changes first",
            file=sys.stderr,
        )
        return 2
    test_root = Path(tempfile.mkdtemp(prefix="project-memory-smoke-"))
    checks: list[str] = []
    try:
        audit = run_command(
            sys.executable,
            str(BOOTSTRAP),
            "--repo",
            str(repo),
            "--audit-only",
        )
        require_success(audit, "real-repo bootstrap audit")
        checks.append("real repo audit")

        collector = test_root / "collector"
        make_collector(collector, repo)
        collector_result = run_collector_test(
            collector,
            repo,
            max_files=args.max_files,
            max_chars=args.max_chars,
        )
        checks.extend(
            [
                "collector doctor",
                "bounded collect",
                "proposal validation and apply",
                "packet content scrubbing",
                "incremental cursor behavior",
            ]
        )

        run_protected_guidance_test(collector, repo.name)
        checks.append("protected AGENTS.md deferral")

        run_actual_write_test(repo)
        checks.append("reversible real-repo file changes")

        fingerprint_after, after_count = repo_fingerprint(repo)
        status_after = git_status(repo)
        if fingerprint_after != fingerprint_before or after_count != file_count:
            raise SmokeTestError("Real repo memory files changed during the smoke test")
        if status_after != status_before:
            raise SmokeTestError("Real repo Git status changed during the smoke test")
        checks.append("real repo unchanged")

        print("Project-memory smoke test: PASS")
        print(f"Repository: {repo}")
        print(f"Memory files inspected: {collector_result['memory_file_count']}")
        print(f"Sources processed in bounded pass: {collector_result['source_count']}")
        print(f"Sources deferred to later passes: {collector_result['deferred_count']}")
        if collector_result["oversized"]:
            print("Oversized sources deferred:")
            for path in collector_result["oversized"]:
                print(f"- {path}")
        print("Checks:")
        for check in checks:
            print(f"- PASS: {check}")
        print("Semantic lesson quality is not scored by this deterministic harness.")
        if args.keep_temp:
            print(f"Temporary workspace kept at: {test_root}")
        return 0
    except SmokeTestError as exc:
        print(f"Project-memory smoke test: FAIL\n{exc}", file=sys.stderr)
        if args.keep_temp:
            print(f"Temporary workspace kept at: {test_root}", file=sys.stderr)
        return 1
    finally:
        if not args.keep_temp:
            shutil.rmtree(test_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())

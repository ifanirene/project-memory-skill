#!/usr/bin/env python3
"""Deterministic controller for a hybrid project-memory collector.

The controller does not perform semantic distillation. It prepares bounded
source packets for an LLM, validates the LLM's structured proposal, and applies
validated state changes atomically inside the collector workspace.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 1
DEFAULT_PATTERNS = [
    "AGENTS.md",
    "ANALYSIS_INDEX.md",
    ".gitignore",
    "docs/LESSONS.md",
    "docs/pipelines/*.md",
    "**/NOTES.md",
]
ALLOWED_SCOPES = {
    "repo_local",
    "cross_repo_science",
    "user_preference",
    "automation_operations",
}
ALLOWED_CONFIDENCE = {"low", "medium", "high"}
QUEUE_TERMINAL_STATES = {"resolved", "deferred", "rejected"}
QUALITY_ISSUE_TYPES = {
    "notes_chronology_drift",
    "lesson_not_distilled",
    "stale_runbook_state",
    "oversized_memory_doc",
}
NOTE_REWRITE_BRIEF_FIELDS = {
    "purpose",
    "current_claim",
    "canonical_artifacts",
    "trust_basis",
    "kill_list",
    "missing_evidence",
}


class MemoryCtlError(RuntimeError):
    """Raised for a safe, user-facing controller failure."""


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        if default is not None:
            return default
        raise MemoryCtlError(f"Required JSON file is missing: {path}")
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise MemoryCtlError(f"Could not read valid JSON from {path}: {exc}") from exc


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def ensure_workspace(path: Path) -> Path:
    workspace = path.expanduser().resolve()
    if not workspace.is_dir():
        raise MemoryCtlError(f"Collector workspace does not exist: {workspace}")
    return workspace


def ensure_relative_path(value: str, *, label: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise MemoryCtlError(f"{label} must be a safe relative path: {value}")
    return path


def load_registry(workspace: Path) -> dict[str, Any]:
    registry = read_json(workspace / "config" / "repos.json")
    if registry.get("schema_version") != SCHEMA_VERSION:
        raise MemoryCtlError("Unsupported collector registry schema version")
    repos = registry.get("repos")
    if not isinstance(repos, list) or not repos:
        raise MemoryCtlError("Collector registry must contain a non-empty repos list")

    names: set[str] = set()
    for repo in repos:
        if not isinstance(repo, dict):
            raise MemoryCtlError("Each registry repo entry must be an object")
        name = repo.get("name")
        root = repo.get("root")
        if not isinstance(name, str) or not name or name in names:
            raise MemoryCtlError(f"Invalid or duplicate repo name: {name!r}")
        if not isinstance(root, str) or not Path(root).is_absolute():
            raise MemoryCtlError(f"Repo {name} must use an absolute root path")
        if not isinstance(repo.get("maintenance_enabled", True), bool):
            raise MemoryCtlError(f"Repo {name} maintenance_enabled must be boolean")
        patterns = repo.get("patterns", DEFAULT_PATTERNS)
        if not isinstance(patterns, list) or not all(isinstance(p, str) for p in patterns):
            raise MemoryCtlError(f"Repo {name} patterns must be a list of strings")
        for pattern in patterns:
            ensure_relative_path(pattern, label=f"Pattern for repo {name}")
        names.add(name)
    # Additional registered projects can feed personal decision memory without
    # silently creating documentation jobs for repos that have no local worker.
    registry = {**registry, "repos": [
        repo for repo in repos if repo.get("maintenance_enabled", True)
    ]}
    return registry


@contextmanager
def workspace_lock(workspace: Path) -> Iterable[None]:
    lock_path = workspace / "state" / "memoryctl.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise MemoryCtlError(
            f"Another memoryctl run owns {lock_path}; inspect it before retrying"
        ) from exc
    try:
        payload = {
            "pid": os.getpid(),
            "started_at": utc_now().isoformat(),
        }
        os.write(fd, canonical_json_bytes(payload))
        os.close(fd)
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def discover_files(repo: dict[str, Any]) -> list[Path]:
    root = Path(repo["root"]).resolve()
    patterns = repo.get("patterns", DEFAULT_PATTERNS)
    found: set[Path] = set()
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_symlink() or not path.is_file():
                continue
            resolved = path.resolve()
            if is_within(resolved, root):
                found.add(resolved)
    return sorted(found)


def memory_quality_metrics(relative_path: str, content: str) -> dict[str, Any]:
    lines = content.splitlines()
    dated_headings = sum(
        bool(
            re.search(
                r"(?:\b20\d{2}[-/]\d{1,2}(?:[-/]\d{1,2})?\b|\b20\d{6}\b)",
                line,
            )
        )
        for line in lines
        if re.match(r"^#{1,6}\s+", line)
    )
    dated_bullets = sum(
        bool(re.match(r"^\s*[-*]\s+\[20\d{2}(?:-\d{2})?\]", line))
        for line in lines
    )
    typed_lessons = sum(
        bool(
            re.match(
                r"^\s*[-*]\s+(?:`)?(?:Default|Check|Trap|Preference)(?:`)?\s*:",
                line,
            )
        )
        for line in lines
    )
    headings = {
        match.group(1).strip().lower()
        for line in lines
        if (match := re.match(r"^#{2,6}\s+(.+?)\s*$", line))
    }
    current_state_headings = sorted(
        heading
        for heading in headings
        if any(
            token in heading
            for token in (
                "status",
                "current",
                "answer",
                "claim",
                "evidence",
                "final run",
                "canonical run",
                "canonical reproduction",
                "input",
                "output",
                "validation",
                "decision",
                "limitation",
                "next decision",
                "open question",
            )
        )
    )

    reasons: list[str] = []
    if relative_path.endswith("NOTES.md"):
        if dated_headings >= 3:
            reasons.append("notes_chronology_drift")
        if len(lines) >= 400:
            reasons.append("oversized_memory_doc")
        if not current_state_headings:
            reasons.append("stale_runbook_state")
    elif relative_path == "docs/LESSONS.md":
        if dated_bullets and typed_lessons < dated_bullets:
            reasons.append("lesson_not_distilled")
        if len(lines) >= 400:
            reasons.append("oversized_memory_doc")

    return {
        "line_count": len(lines),
        "dated_heading_count": dated_headings,
        "dated_bullet_count": dated_bullets,
        "typed_lesson_count": typed_lessons,
        "current_state_headings": current_state_headings,
        "review_reasons": reasons,
    }


def git_provenance(repo_name: str, root: Path) -> dict[str, Any]:
    base = {"repo": repo_name, "root": str(root)}
    inside = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
        text=True,
        capture_output=True,
        check=False,
    )
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return {**base, "is_git_worktree": False}

    head = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    branch = subprocess.run(
        ["git", "-C", str(root), "symbolic-ref", "--quiet", "--short", "HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    status = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain=v1", "-z"],
        capture_output=True,
        check=False,
    )
    return {
        **base,
        "is_git_worktree": True,
        "head": head.stdout.strip() if head.returncode == 0 else None,
        "branch": branch.stdout.strip() if branch.returncode == 0 else None,
        "dirty": status.returncode != 0 or bool(status.stdout),
    }


def file_record(repo_name: str, root: Path, path: Path, max_chars: int) -> dict[str, Any]:
    data = path.read_bytes()
    decoded = data.decode("utf-8", errors="replace")
    truncated = len(decoded) > max_chars
    content = decoded[:max_chars]
    relative = path.relative_to(root).as_posix()
    source_id = sha256_bytes(f"{repo_name}:{relative}".encode())[:20]
    stat = path.stat()
    return {
        "source_id": source_id,
        "repo": repo_name,
        "relative_path": relative,
        "sha256": sha256_bytes(data),
        "mtime_ns": stat.st_mtime_ns,
        "size": stat.st_size,
        "truncated": truncated,
        "quality_metrics": memory_quality_metrics(relative, decoded),
        "content": content,
    }


def current_cursor(workspace: Path) -> dict[str, Any]:
    default = {"schema_version": SCHEMA_VERSION, "files": {}}
    cursor = read_json(workspace / "state" / "repo_cursors_v2.json", default=default)
    if cursor.get("schema_version") != SCHEMA_VERSION or not isinstance(
        cursor.get("files"), dict
    ):
        raise MemoryCtlError("Invalid repo_cursors_v2.json schema")
    return cursor


def current_quality_audit(workspace: Path) -> dict[str, Any]:
    default = {"schema_version": SCHEMA_VERSION, "files": {}}
    state = read_json(
        workspace / "state" / "quality_audit_v1.json", default=default
    )
    if state.get("schema_version") != SCHEMA_VERSION or not isinstance(
        state.get("files"), dict
    ):
        raise MemoryCtlError("Invalid quality_audit_v1.json schema")
    return state


def cursor_digest(cursor: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(cursor))


def command_doctor(args: argparse.Namespace) -> int:
    workspace = ensure_workspace(args.workspace)
    registry = load_registry(workspace)
    problems: list[str] = []
    print(f"Collector workspace: {workspace}")

    for repo in registry["repos"]:
        root = Path(repo["root"]).resolve()
        if not root.is_dir():
            problems.append(f"{repo['name']}: missing root {root}")
            continue
        try:
            files = discover_files(repo)
            if files:
                files[0].open("rb").close()
            print(f"[READ OK] {repo['name']}: {root} ({len(files)} memory files)")
        except OSError as exc:
            problems.append(f"{repo['name']}: cannot read monitored files: {exc}")

    try:
        test_path = workspace / "state" / ".memoryctl-write-test"
        atomic_write_text(test_path, "ok\n")
        test_path.unlink()
        print(f"[WRITE OK] {workspace}")
    except OSError as exc:
        problems.append(f"collector workspace is not writable: {exc}")

    if problems:
        for problem in problems:
            print(f"[ERROR] {problem}", file=sys.stderr)
        return 1
    return 0


def command_collect(args: argparse.Namespace) -> int:
    workspace = ensure_workspace(args.workspace)
    output = args.output.expanduser().resolve()
    if not is_within(output, workspace):
        raise MemoryCtlError("Collection packets must be written inside the collector workspace")
    registry = load_registry(workspace)

    with workspace_lock(workspace):
        cursor = current_cursor(workspace)
        quality_audit = current_quality_audit(workspace)
        changed: list[dict[str, Any]] = []
        quality_pending: list[dict[str, Any]] = []
        repo_provenance: list[dict[str, Any]] = []
        for repo in registry["repos"]:
            root = Path(repo["root"]).resolve()
            repo_provenance.append(git_provenance(repo["name"], root))
            for path in discover_files(repo):
                record = file_record(repo["name"], root, path, args.max_chars)
                cursor_key = f"{repo['name']}::{record['relative_path']}"
                previous = cursor["files"].get(cursor_key, {})
                record["cursor_key"] = cursor_key
                if previous.get("sha256") != record["sha256"]:
                    record["collection_reason"] = "changed"
                    changed.append(record)
                    continue
                quality_previous = quality_audit["files"].get(cursor_key, {})
                if (
                    args.quality_audit_files
                    and record["quality_metrics"]["review_reasons"]
                    and quality_previous.get("sha256") != record["sha256"]
                ):
                    record["collection_reason"] = "quality_audit"
                    quality_pending.append(record)

        changed.sort(key=lambda item: (item["repo"], item["relative_path"]))
        quality_pending.sort(
            key=lambda item: (item["repo"], item["relative_path"])
        )
        changed_oversized = [item for item in changed if item["truncated"]]
        changed_eligible = [item for item in changed if not item["truncated"]]
        quality_oversized = [
            item for item in quality_pending if item["truncated"]
        ]
        quality_eligible = [
            item for item in quality_pending if not item["truncated"]
        ]
        quality_take = min(
            args.quality_audit_files, args.max_files, len(quality_eligible)
        )
        changed_take = min(args.max_files - quality_take, len(changed_eligible))
        sources = changed_eligible[:changed_take] + quality_eligible[:quality_take]
        remaining_changed = (
            len(changed_eligible) - changed_take + len(changed_oversized)
        )
        remaining_quality = (
            len(quality_eligible) - quality_take + len(quality_oversized)
        )
        oversized = changed_oversized + quality_oversized
        packet = {
            "schema_version": SCHEMA_VERSION,
            "run_id": f"{utc_now().strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}",
            "created_at": utc_now().isoformat(),
            "collector_workspace": str(workspace),
            "cursor_snapshot_sha256": cursor_digest(cursor),
            "quality_audit_snapshot_sha256": cursor_digest(quality_audit),
            "quality_audit_enabled": bool(args.quality_audit_files),
            "repo_provenance": repo_provenance,
            "remaining_changed_files": remaining_changed,
            "remaining_quality_audit_files": remaining_quality,
            "quality_audit_source_count": quality_take,
            "sources": sources,
            "deferred_oversized_sources": [
                {key: value for key, value in item.items() if key != "content"}
                for item in oversized
            ],
            "llm_contract": {
                "repo_provenance": (
                    "Dirty main worktrees remain eligible. Read the current target "
                    "before rewriting memory docs and leave unrelated files alone. "
                    "Treat detached or non-main worktrees as provisional."
                ),
                "memory_quality": {
                    "review_every_notes_or_lessons_source": True,
                    "issue_types": sorted(QUALITY_ISSUE_TYPES),
                    "rule": (
                        "Line count and dates trigger review, not automatic cleanup. "
                        "Queue an issue only when current run, trust, checks, traps, "
                        "or canonical provenance are hard to find."
                    ),
                    "quality_item_required": ["quality_evidence"],
                    "note_cleanup_required": ["rewrite_brief"],
                },
                "processed_source_ids": "List every source_id in this packet exactly once.",
                "candidates": {
                    "required": ["statement", "scope", "confidence", "source_ids", "rationale"],
                    "scope_values": sorted(ALLOWED_SCOPES),
                    "confidence_values": sorted(ALLOWED_CONFIDENCE),
                },
                "maintenance_items": {
                    "required": [
                        "repo",
                        "issue_type",
                        "suggested_target",
                        "source_ids",
                        "rationale",
                        "protected_information",
                    ],
                    "protected_information": {
                        "impact_values": ["none", "possible", "confirmed"],
                        "note": "AGENTS.md changes with possible or confirmed impact require explicit permission before resolution.",
                    },
                },
            },
        }
        atomic_write_json(output, packet)
    print(f"Wrote {len(packet['sources'])} sources to {output}")
    if remaining_changed:
        print(
            f"Deferred {remaining_changed} changed sources to a later bounded run"
        )
    if remaining_quality:
        print(
            f"Deferred {remaining_quality} quality-audit sources to a later bounded run"
        )
    if oversized:
        print(
            f"Deferred {len(oversized)} oversized sources; rerun with a larger --max-chars"
        )
    return 0


def validate_target(target: str) -> None:
    path = ensure_relative_path(target, label="suggested_target")
    posix = path.as_posix()
    allowed = (
        posix == "AGENTS.md"
        or posix == ".gitignore"
        or posix == "ANALYSIS_INDEX.md"
        or posix == "docs/LESSONS.md"
        or (posix.startswith("docs/pipelines/") and posix.endswith(".md"))
        or posix.endswith("/NOTES.md")
        or posix == "NOTES.md"
    )
    if not allowed:
        raise MemoryCtlError(f"Maintenance target is outside the doc allowlist: {target}")


def validate_proposal(
    workspace: Path, packet: dict[str, Any], proposal: dict[str, Any]
) -> None:
    if packet.get("schema_version") != SCHEMA_VERSION:
        raise MemoryCtlError("Unsupported packet schema version")
    if proposal.get("schema_version") != SCHEMA_VERSION:
        raise MemoryCtlError("Unsupported proposal schema version")
    if proposal.get("run_id") != packet.get("run_id"):
        raise MemoryCtlError("Proposal run_id does not match packet run_id")

    source_ids = {source["source_id"] for source in packet.get("sources", [])}
    processed = proposal.get("processed_source_ids")
    if not isinstance(processed, list) or len(processed) != len(set(processed)):
        raise MemoryCtlError("processed_source_ids must be a unique list")
    if set(processed) != source_ids:
        raise MemoryCtlError("Proposal must explicitly process every packet source_id")

    for candidate in proposal.get("candidates", []):
        if not isinstance(candidate, dict):
            raise MemoryCtlError("Each candidate must be an object")
        statement = candidate.get("statement")
        if not isinstance(statement, str) or not statement.strip():
            raise MemoryCtlError("Each candidate needs a non-empty statement")
        if candidate.get("scope") not in ALLOWED_SCOPES:
            raise MemoryCtlError(f"Invalid candidate scope: {candidate.get('scope')}")
        if candidate.get("confidence") not in ALLOWED_CONFIDENCE:
            raise MemoryCtlError("Invalid candidate confidence")
        candidate_sources = candidate.get("source_ids")
        if not isinstance(candidate_sources, list) or not candidate_sources:
            raise MemoryCtlError("Each candidate needs source_ids")
        if not set(candidate_sources).issubset(source_ids):
            raise MemoryCtlError("Candidate cites an unknown source_id")
        if not isinstance(candidate.get("rationale"), str):
            raise MemoryCtlError("Each candidate needs a rationale")

    registry = load_registry(workspace)
    repo_names = {repo["name"] for repo in registry["repos"]}
    _, queue = load_queue(workspace)
    for item in proposal.get("maintenance_items", []):
        if not isinstance(item, dict) or item.get("repo") not in repo_names:
            raise MemoryCtlError("Maintenance item cites an unknown repo")
        validate_target(item.get("suggested_target", ""))
        item_sources = item.get("source_ids")
        if not isinstance(item_sources, list) or not item_sources:
            raise MemoryCtlError("Maintenance item needs source_ids")
        if not set(item_sources).issubset(source_ids):
            raise MemoryCtlError("Maintenance item cites an unknown source_id")
        if not isinstance(item.get("issue_type"), str) or not item["issue_type"]:
            raise MemoryCtlError("Maintenance item needs issue_type")
        if not isinstance(item.get("rationale"), str):
            raise MemoryCtlError("Maintenance item needs rationale")
        override = item.get("requeue_closed_item")
        override_evidence = item.get("requeue_evidence")
        if "requeue_closed_item" in item or "requeue_evidence" in item:
            if not all(isinstance(value, str) and value.strip()
                       for value in (override, override_evidence)):
                raise MemoryCtlError(
                    "Requeue override needs both requeue_closed_item and non-empty "
                    "requeue_evidence describing material new facts"
                )
            previous = find_queue_item(queue, override)
            if (previous.get("status") != "rejected"
                    or previous.get("disposition") != "user_waived_historical"):
                raise MemoryCtlError("Requeue override must reference a dismissed historical item")
            if queue_issue_identity(workspace, previous) != queue_issue_identity(workspace, item):
                raise MemoryCtlError("Requeue override repo/target/issue does not match")
        protected = item.get("protected_information")
        if not isinstance(protected, dict) or protected.get("impact") not in {
            "none",
            "possible",
            "confirmed",
        }:
            raise MemoryCtlError(
                "Maintenance item needs protected_information.impact"
            )
        if item.get("suggested_target") == "AGENTS.md" and protected.get(
            "impact"
        ) == "none":
            protected["review_required"] = True
        if item["issue_type"] in QUALITY_ISSUE_TYPES:
            evidence = item.get("quality_evidence")
            if not isinstance(evidence, dict) or not evidence:
                raise MemoryCtlError(
                    f"Quality issue {item['issue_type']} needs quality_evidence"
                )
            target = item["suggested_target"]
            if target == "NOTES.md" or target.endswith("/NOTES.md"):
                rewrite_brief = item.get("rewrite_brief")
                if not isinstance(rewrite_brief, dict):
                    raise MemoryCtlError(
                        f"Quality issue {item['issue_type']} needs "
                        "rewrite_brief for NOTES.md"
                    )
                missing = NOTE_REWRITE_BRIEF_FIELDS - set(rewrite_brief)
                if missing:
                    raise MemoryCtlError(
                        "NOTES.md rewrite_brief is missing fields: "
                        f"{sorted(missing)}"
                    )


def command_validate(args: argparse.Namespace) -> int:
    workspace = ensure_workspace(args.workspace)
    packet = read_json(args.packet.expanduser().resolve())
    proposal = read_json(args.proposal.expanduser().resolve())
    validate_proposal(workspace, packet, proposal)
    print("Proposal is valid")
    return 0


def append_jsonl_atomic(path: Path, records: list[dict[str, Any]]) -> None:
    existing = path.read_text() if path.exists() else ""
    additions = "".join(json.dumps(record, sort_keys=True) + "\n" for record in records)
    atomic_write_text(path, existing + additions)


def load_queue(workspace: Path) -> tuple[Path, dict[str, Any]]:
    path = workspace / "state" / "maintenance_queue_v2.json"
    queue = read_json(
        path,
        default={"schema_version": SCHEMA_VERSION, "items": []},
    )
    if queue.get("schema_version") != SCHEMA_VERSION or not isinstance(
        queue.get("items"), list
    ):
        raise MemoryCtlError("Invalid maintenance_queue_v2.json schema")
    return path, queue


def find_queue_item(queue: dict[str, Any], key: str) -> dict[str, Any]:
    matches = [item for item in queue["items"] if item.get("idempotency_key") == key]
    if len(matches) != 1:
        raise MemoryCtlError(f"Expected one queue item for idempotency key {key}")
    return matches[0]


def queue_issue_identity(workspace: Path, item: dict[str, Any]) -> dict[str, str]:
    """Stable debt identity, deliberately independent of source content hashes."""
    validate_target(item["suggested_target"])
    return {
        "repo": canonical_queue_repo(workspace, item["repo"]),
        "suggested_target": Path(item["suggested_target"]).as_posix(),
        "issue_type": item["issue_type"].strip(),
    }


def command_apply(args: argparse.Namespace) -> int:
    workspace = ensure_workspace(args.workspace)
    packet = read_json(args.packet.expanduser().resolve())
    proposal = read_json(args.proposal.expanduser().resolve())

    with workspace_lock(workspace):
        validate_proposal(workspace, packet, proposal)
        cursor = current_cursor(workspace)
        if cursor_digest(cursor) != packet.get("cursor_snapshot_sha256"):
            raise MemoryCtlError(
                "Collector cursor changed after packet creation; recollect before applying"
            )
        quality_audit = current_quality_audit(workspace)
        quality_snapshot = packet.get("quality_audit_snapshot_sha256")
        if quality_snapshot and cursor_digest(quality_audit) != quality_snapshot:
            raise MemoryCtlError(
                "Quality-audit state changed after packet creation; recollect before applying"
            )

        now = utc_now()
        run_id = packet["run_id"]
        sources_by_id = {source["source_id"]: source for source in packet["sources"]}
        observation_records: list[dict[str, Any]] = []
        for index, candidate in enumerate(proposal.get("candidates", []), start=1):
            observation_records.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "observation_id": f"{run_id}-obs-{index:03d}",
                    "run_id": run_id,
                    "created_at": now.isoformat(),
                    **candidate,
                    "sources": [
                        {
                            "source_id": source_id,
                            "repo": sources_by_id[source_id]["repo"],
                            "relative_path": sources_by_id[source_id]["relative_path"],
                            "sha256": sources_by_id[source_id]["sha256"],
                        }
                        for source_id in candidate["source_ids"]
                    ],
                }
            )

        observations_path = (
            workspace
            / "observations"
            / "repo_events"
            / f"{now.strftime('%Y-%m')}.jsonl"
        )
        if observation_records:
            append_jsonl_atomic(observations_path, observation_records)

        queue_path, queue = load_queue(workspace)
        existing_keys = {item.get("idempotency_key") for item in queue["items"]}
        dismissed = [item for item in queue["items"]
                     if item.get("status") == "rejected"
                     and item.get("disposition") == "user_waived_historical"]
        suppressed_items = []
        for item in proposal.get("maintenance_items", []):
            identity = queue_issue_identity(workspace, item)
            matching_waivers = [closed for closed in dismissed
                               if queue_issue_identity(workspace, closed) == identity]
            if matching_waivers and not item.get("requeue_closed_item"):
                suppressed_items.append({
                    **identity,
                    "dismissed_item_ids": [closed["idempotency_key"]
                                           for closed in matching_waivers],
                })
                continue
            key_payload = {
                "repo": item["repo"],
                "issue_type": item["issue_type"],
                "suggested_target": item["suggested_target"],
                "sources": sorted(
                    (
                        source_id,
                        sources_by_id[source_id]["sha256"],
                    )
                    for source_id in item["source_ids"]
                ),
            }
            if item.get("requeue_closed_item"):
                key_payload["requeue_closed_item"] = item["requeue_closed_item"]
                key_payload["requeue_evidence"] = item["requeue_evidence"]
            key = sha256_bytes(canonical_json_bytes(key_payload))[:24]
            if key in existing_keys:
                continue
            queue["items"].append(
                {
                    **item,
                    "sources": [
                        {
                            "source_id": source_id,
                            "repo": sources_by_id[source_id]["repo"],
                            "relative_path": sources_by_id[source_id][
                                "relative_path"
                            ],
                            "sha256": sources_by_id[source_id]["sha256"],
                        }
                        for source_id in item["source_ids"]
                    ],
                    "idempotency_key": key,
                    "status": "open",
                    "created_at": now.isoformat(),
                    "attempts": 0,
                    "resolution_evidence": None,
                }
            )
            existing_keys.add(key)

        for source_id in proposal["processed_source_ids"]:
            source = sources_by_id[source_id]
            cursor["files"][source["cursor_key"]] = {
                "sha256": source["sha256"],
                "mtime_ns": source["mtime_ns"],
                "size": source["size"],
                "processed_at": now.isoformat(),
                "run_id": run_id,
            }
            if (
                packet.get("quality_audit_enabled")
                and source.get("quality_metrics", {}).get("review_reasons")
            ):
                quality_audit["files"][source["cursor_key"]] = {
                    "sha256": source["sha256"],
                    "audited_at": now.isoformat(),
                    "run_id": run_id,
                    "collection_reason": source.get("collection_reason"),
                    "metrics": source["quality_metrics"],
                }

        atomic_write_json(queue_path, queue)
        atomic_write_json(workspace / "state" / "repo_cursors_v2.json", cursor)
        atomic_write_json(
            workspace / "state" / "quality_audit_v1.json", quality_audit
        )

        log_lines = [
            f"# Weekly collector run — {run_id}",
            "",
            f"- Processed sources: {len(packet['sources'])}",
            f"- Observation candidates: {len(observation_records)}",
            f"- Maintenance proposals: {len(proposal.get('maintenance_items', []))}",
            f"- User-waived historical proposals suppressed: {len(suppressed_items)}",
            f"- Remaining changed files: {packet.get('remaining_changed_files', 0)}",
            "- Quality-audit sources: "
            f"{packet.get('quality_audit_source_count', 0)}",
            "- Remaining quality-audit files: "
            f"{packet.get('remaining_quality_audit_files', 0)}",
            "- Canonical repo files edited: none",
            "",
        ]
        for suppressed in suppressed_items:
            log_lines.append("- Suppressed historical debt: " + json.dumps(suppressed, sort_keys=True))
        log_path = workspace / "logs" / "runs" / f"{run_id}_weekly-collector.md"
        atomic_write_text(log_path, "\n".join(log_lines))

        packet_path = args.packet.expanduser().resolve()
        if is_within(packet_path, workspace):
            scrubbed_packet = {
                **packet,
                "sources": [
                    {key: value for key, value in source.items() if key != "content"}
                    for source in packet["sources"]
                ],
                "content_scrubbed_after_apply": True,
            }
            atomic_write_json(packet_path, scrubbed_packet)

    print(f"Applied validated proposal for {run_id}")
    print(f"Run log: {log_path}")
    return 0


def canonical_queue_repo(workspace: Path, value: str) -> str:
    """Accept a maintained repo name or its exact root; reject silent misses."""
    repos = load_registry(workspace)["repos"]
    for repo in repos:
        if value == repo["name"]:
            return repo["name"]
    path = Path(value).expanduser()
    matches = [repo["name"] for repo in repos
               if path.is_absolute() and path.resolve() == Path(repo["root"]).resolve()]
    if len(matches) == 1:
        return matches[0]
    raise MemoryCtlError(
        f"Unknown or ambiguous maintenance repo: {value!r}; use a registered "
        "maintenance-enabled name or its exact root"
    )


def command_queue_list(args: argparse.Namespace) -> int:
    workspace = ensure_workspace(args.workspace)
    _, queue = load_queue(workspace)
    items = queue["items"]
    if args.repo:
        repo = canonical_queue_repo(workspace, args.repo)
        items = [item for item in items if item.get("repo") == repo]
    if args.status:
        items = [item for item in items if item.get("status") == args.status]
    print(json.dumps(items, indent=2, sort_keys=True))
    return 0


def command_queue_claim(args: argparse.Namespace) -> int:
    workspace = ensure_workspace(args.workspace)
    repo = canonical_queue_repo(workspace, args.repo)
    with workspace_lock(workspace):
        queue_path, queue = load_queue(workspace)
        item = find_queue_item(queue, args.idempotency_key)
        if item.get("repo") != repo:
            raise MemoryCtlError(
                f"Queue item belongs to {item.get('repo')}, not {args.repo}"
            )
        if item.get("status") != "open":
            raise MemoryCtlError(
                f"Queue item is {item.get('status')}, not open: {args.idempotency_key}"
            )
        item["status"] = "claimed"
        item["owning_run_id"] = args.run_id
        item["claimed_at"] = utc_now().isoformat()
        item["lease_expires_at"] = (
            utc_now() + timedelta(minutes=args.lease_minutes)
        ).isoformat()
        item["attempts"] = int(item.get("attempts", 0)) + 1
        atomic_write_json(queue_path, queue)
    print(f"Claimed {args.idempotency_key} for {args.run_id}")
    return 0


def command_queue_finish(args: argparse.Namespace) -> int:
    workspace = ensure_workspace(args.workspace)
    repo = canonical_queue_repo(workspace, args.repo)
    with workspace_lock(workspace):
        queue_path, queue = load_queue(workspace)
        item = find_queue_item(queue, args.idempotency_key)
        if item.get("repo") != repo:
            raise MemoryCtlError(
                f"Queue item belongs to {item.get('repo')}, not {args.repo}"
            )
        if item.get("status") != "claimed":
            raise MemoryCtlError(
                f"Queue item is {item.get('status')}, not claimed: {args.idempotency_key}"
            )
        if item.get("owning_run_id") != args.run_id:
            raise MemoryCtlError("Only the owning run may finish a claimed queue item")
        protected_impact = item.get("protected_information", {}).get("impact", "none")
        if (
            args.status == "resolved"
            and item.get("suggested_target") == "AGENTS.md"
            and protected_impact in {"possible", "confirmed"}
            and not args.permission_source
        ):
            raise MemoryCtlError(
                "Resolving this protected AGENTS.md item requires --permission-source"
            )
        item["status"] = args.status
        item["resolution_evidence"] = args.evidence
        item["permission_source"] = args.permission_source
        item["finished_at"] = utc_now().isoformat()
        item["lease_expires_at"] = None
        atomic_write_json(queue_path, queue)
    print(f"Marked {args.idempotency_key} as {args.status}")
    return 0


def command_queue_reopen(args: argparse.Namespace) -> int:
    """Revisit a deferred dependency without discarding its previous outcome."""
    workspace = ensure_workspace(args.workspace)
    repo = canonical_queue_repo(workspace, args.repo)
    if not args.evidence.strip() or not args.run_id.strip():
        raise MemoryCtlError("Reopening requires non-empty evidence and run ID")
    with workspace_lock(workspace):
        queue_path, queue = load_queue(workspace)
        item = find_queue_item(queue, args.idempotency_key)
        if item.get("repo") != repo:
            raise MemoryCtlError(
                f"Queue item belongs to {item.get('repo')}, not {args.repo}"
            )
        if item.get("status") != "deferred":
            raise MemoryCtlError(
                f"Queue item is {item.get('status')}, not deferred: {args.idempotency_key}"
            )
        history = item.setdefault("status_history", [])
        if not isinstance(history, list):
            raise MemoryCtlError("Invalid queue status_history")
        timestamp = utc_now().isoformat()
        history.append({
            "from_status": "deferred", "to_status": "open",
            "run_id": args.run_id, "at": timestamp, "evidence": args.evidence,
            "previous": {key: item.get(key) for key in (
                "status", "resolution_evidence", "owning_run_id", "claimed_at",
                "finished_at", "lease_expires_at", "permission_source", "attempts",
            )},
        })
        item["status"] = "open"
        item["reopened_at"] = timestamp
        item["reopened_by_run_id"] = args.run_id
        for key in ("resolution_evidence", "owning_run_id", "claimed_at",
                    "finished_at", "lease_expires_at", "permission_source"):
            item[key] = None
        atomic_write_json(queue_path, queue)
    print(f"Reopened {args.idempotency_key}; prior deferral retained")
    return 0


def command_queue_dismiss(args: argparse.Namespace) -> int:
    """Close explicitly waived historical debt without claiming it was repaired."""
    for label, value in (("repo", args.repo), ("key", args.idempotency_key),
                         ("run ID", args.run_id), ("evidence", args.evidence)):
        if not isinstance(value, str) or not value.strip():
            raise MemoryCtlError(f"Dismissing requires non-empty {label}")
    workspace = ensure_workspace(args.workspace)
    repo = canonical_queue_repo(workspace, args.repo)
    with workspace_lock(workspace):
        queue_path, queue = load_queue(workspace)
        item = find_queue_item(queue, args.idempotency_key)
        if item.get("repo") != repo:
            raise MemoryCtlError(f"Queue item belongs to {item.get('repo')}, not {repo}")
        if item.get("status") not in {"open", "deferred"}:
            raise MemoryCtlError("Only open or deferred historical items can be dismissed")
        history = item.setdefault("status_history", [])
        if not isinstance(history, list):
            raise MemoryCtlError("Invalid queue status_history")
        identity = queue_issue_identity(workspace, item)
        timestamp = utc_now().isoformat()
        # JSON round-trip retains all previous fields without sharing mutable values.
        previous = json.loads(json.dumps({k: v for k, v in item.items()
                                          if k != "status_history"}))
        history.append({
            "from_status": item["status"], "to_status": "rejected",
            "run_id": args.run_id, "at": timestamp, "evidence": args.evidence,
            "disposition": "user_waived_historical", "previous": previous,
        })
        item.update(status="rejected", disposition="user_waived_historical",
                    suppression_identity=identity, resolution_evidence=args.evidence,
                    dismissed_by_run_id=args.run_id, finished_at=timestamp,
                    owning_run_id=None, lease_expires_at=None)
        atomic_write_json(queue_path, queue)
    print(f"Dismissed {args.idempotency_key}; historical debt waived, not repaired")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Control bounded collection and validated memory proposals."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Check collector access and registry")
    doctor.add_argument("--workspace", type=Path, required=True)
    doctor.set_defaults(func=command_doctor)

    collect = subparsers.add_parser("collect", help="Create a bounded LLM input packet")
    collect.add_argument("--workspace", type=Path, required=True)
    collect.add_argument("--output", type=Path, required=True)
    collect.add_argument("--max-files", type=int, default=24)
    collect.add_argument("--max-chars", type=int, default=30_000)
    collect.add_argument(
        "--quality-audit-files",
        type=int,
        default=2,
        help="Reserve up to this many slots for unchanged legacy quality reviews",
    )
    collect.set_defaults(func=command_collect)

    validate = subparsers.add_parser("validate", help="Validate an LLM proposal")
    validate.add_argument("--workspace", type=Path, required=True)
    validate.add_argument("--packet", type=Path, required=True)
    validate.add_argument("--proposal", type=Path, required=True)
    validate.set_defaults(func=command_validate)

    apply = subparsers.add_parser("apply", help="Apply a validated proposal atomically")
    apply.add_argument("--workspace", type=Path, required=True)
    apply.add_argument("--packet", type=Path, required=True)
    apply.add_argument("--proposal", type=Path, required=True)
    apply.set_defaults(func=command_apply)

    queue_list = subparsers.add_parser("queue-list", help="List v2 queue items")
    queue_list.add_argument("--workspace", type=Path, required=True)
    queue_list.add_argument("--repo")
    queue_list.add_argument(
        "--status", choices=["open", "claimed", *sorted(QUEUE_TERMINAL_STATES)]
    )
    queue_list.set_defaults(func=command_queue_list)

    queue_claim = subparsers.add_parser("queue-claim", help="Claim one open item")
    queue_claim.add_argument("--workspace", type=Path, required=True)
    queue_claim.add_argument("--idempotency-key", required=True)
    queue_claim.add_argument("--repo", required=True)
    queue_claim.add_argument("--run-id", required=True)
    queue_claim.add_argument("--lease-minutes", type=int, default=120)
    queue_claim.set_defaults(func=command_queue_claim)

    queue_finish = subparsers.add_parser(
        "queue-finish", help="Resolve, defer, or reject a claimed item"
    )
    queue_finish.add_argument("--workspace", type=Path, required=True)
    queue_finish.add_argument("--idempotency-key", required=True)
    queue_finish.add_argument("--repo", required=True)
    queue_finish.add_argument("--run-id", required=True)
    queue_finish.add_argument("--status", choices=sorted(QUEUE_TERMINAL_STATES), required=True)
    queue_finish.add_argument("--evidence", required=True)
    queue_finish.add_argument("--permission-source")
    queue_finish.set_defaults(func=command_queue_finish)

    queue_reopen = subparsers.add_parser(
        "queue-reopen", help="Reopen a deferred item after its dependency changes"
    )
    queue_reopen.add_argument("--workspace", type=Path, required=True)
    queue_reopen.add_argument("--idempotency-key", required=True)
    queue_reopen.add_argument("--repo", required=True)
    queue_reopen.add_argument("--run-id", required=True)
    queue_reopen.add_argument("--evidence", required=True)
    queue_reopen.set_defaults(func=command_queue_reopen)

    queue_dismiss = subparsers.add_parser(
        "queue-dismiss", help="Reject explicitly user-waived historical debt"
    )
    queue_dismiss.add_argument("--workspace", type=Path, required=True)
    queue_dismiss.add_argument("--key", "--idempotency-key", dest="idempotency_key", required=True)
    queue_dismiss.add_argument("--repo", required=True)
    queue_dismiss.add_argument("--run-id", required=True)
    queue_dismiss.add_argument("--evidence", required=True)
    queue_dismiss.set_defaults(func=command_queue_dismiss)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "max_files") and args.max_files < 1:
        parser.error("--max-files must be positive")
    if hasattr(args, "max_chars") and args.max_chars < 1:
        parser.error("--max-chars must be positive")
    if hasattr(args, "quality_audit_files") and args.quality_audit_files < 0:
        parser.error("--quality-audit-files must be non-negative")
    if hasattr(args, "lease_minutes") and args.lease_minutes < 1:
        parser.error("--lease-minutes must be positive")
    try:
        return args.func(args)
    except MemoryCtlError as exc:
        print(f"memoryctl: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

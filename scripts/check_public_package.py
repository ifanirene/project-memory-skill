#!/usr/bin/env python3
"""Check tracked files, or reachable Git history, for private package material."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess


PRIVATE_PATHS = (
    "audits/", "plans/", "project-memory-skill-structure.png",
    "project-memory-skill-structure.excalidraw",
)
PATTERNS = {
    "personal machine path": re.compile(rb"/(?:Users|Volumes)/[^\s`\"<>]+"),
    "personal email": re.compile(
        rb"[\w.+-]+@(?:gmail\.com|outlook\.com|hotmail\.com|yahoo\.com|stanford\.edu)\b",
        re.I,
    ),
    "personal evidence ID": re.compile(rb"\b[DO]20\d{6}-[A-Za-z]"),
    "private key": re.compile(
        rb"-----BEGIN (?P<kind>(?:RSA |EC |OPENSSH )?PRIVATE KEY)-----\s+"
        rb"[A-Za-z0-9+/=\s]{32,}-----END (?P=kind)-----",
    ),
    "access token": re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
}


def git(repo: Path, *args: str, data: bytes | None = None) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args], input=data)


def check(repo: Path, history: bool = False) -> tuple[int, list[str]]:
    findings = set()

    def inspect(path: str, content: bytes) -> None:
        if path.startswith(PRIVATE_PATHS):
            findings.add(f"private artifact: {path}")
        if b"\x00" in content:
            return
        for label, pattern in PATTERNS.items():
            if pattern.search(content):
                findings.add(f"{label}: {path}")

    if history:
        rows = git(repo, "rev-list", "--objects", "--all").decode().splitlines()
        objects = dict(row.partition(" ")[::2] for row in rows)
        content = git(repo, "cat-file", "--batch", data="".join(
            oid + "\n" for oid in objects
        ).encode())
        offset = 0
        for oid, path in objects.items():
            end = content.index(b"\n", offset)
            _, kind, size = content[offset:end].split()
            offset = end + 1
            size = int(size)
            payload = content[offset:offset + size]
            offset += size + 1
            if kind in {b"blob", b"commit", b"tag"}:
                inspect(path or f"Git {kind.decode()} {oid[:7]}", payload)
        count = len(objects)
    else:
        paths = git(repo, "ls-files", "-z").decode().rstrip("\0").split("\0")
        paths = [path for path in paths if path]
        for path in paths:
            file = repo / path
            if file.is_file():
                inspect(path, file.read_bytes())
        count = len(paths)
    return count, sorted(findings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--history", action="store_true", help="Scan all reachable refs")
    args = parser.parse_args()
    count, findings = check(args.repo.resolve(), args.history)
    for finding in findings:
        print(finding)
    print(f"Checked {count} {'Git objects' if args.history else 'tracked files'}; "
          f"{len(findings)} findings. Binary image contents require visual review.")
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main())

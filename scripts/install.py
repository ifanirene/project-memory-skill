#!/usr/bin/env python3
"""Install the complete runtime package using only Python's standard library."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
FILES = ("SKILL.md", "VERSION", "README.md", "CHANGELOG.md", "GLOSSARY.md")
DIRECTORIES = ("agents", "references", "scripts", "templates", "docs")


def install(destination: Path) -> str:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("VERSION must contain MAJOR.MINOR.PATCH")
    for name in FILES:
        if not (ROOT / name).is_file():
            raise ValueError(f"Incomplete source package: missing file {name}")
    for name in DIRECTORIES:
        if not (ROOT / name).is_dir():
            raise ValueError(f"Incomplete source package: missing directory {name}")
    if destination.resolve().is_relative_to(ROOT):
        raise ValueError("Choose an installation directory outside the source checkout")
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        destination.mkdir()  # Exclusive creation also rejects dangling symlinks.
    except FileExistsError:
        raise ValueError(
            f"Installation already exists: {destination}. Compare local changes, "
            "then move it aside or choose --dest."
        ) from None
    try:
        for name in FILES:
            shutil.copy2(ROOT / name, destination / name)
        for name in DIRECTORIES:
            shutil.copytree(
                ROOT / name, destination / name,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
            )
    except BaseException:
        shutil.rmtree(destination)
        raise
    return version


def main() -> int:
    skill_home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dest", type=Path, default=skill_home / "skills" / "project-memory",
        help="Full installation directory (default: $CODEX_HOME/skills/project-memory "
             "or ~/.codex/skills/project-memory)",
    )
    args = parser.parse_args()
    destination = args.dest.expanduser().absolute()
    try:
        version = install(destination)
    except (OSError, ValueError) as exc:
        print(f"Install failed: {exc}", file=sys.stderr)
        return 1
    print(f"Installed project-memory v{version} at {destination}")
    print("The skill will be available on your next turn.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Set up a new project-memory repo or audit drift in a monitored repo."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = SKILL_ROOT / "templates"


@dataclass(frozen=True)
class AuditItem:
    """Status record for one expected repo-memory item."""

    key: str
    label: str
    canonical: str
    status: str
    detail: str


@dataclass(frozen=True)
class ScaffoldAction:
    """One directory or file to create."""

    relpath: str
    kind: str
    reason: str
    template_name: str | None = None


NEW_REPO_DIRECTORIES = [
    ("config", "analysis configuration home"),
    ("data/raw", "immutable source-data home"),
    ("data/external", "imported reference-data home"),
    ("data/interim", "restartable intermediate-data home"),
    ("data/processed", "analysis-ready data home"),
    ("scripts/preprocessing", "preprocessing code home"),
    ("scripts/analysis", "analysis code home"),
    ("scripts/visualization", "visualization code home"),
    ("scripts/utils", "shared utility code home"),
    ("notebooks", "exploratory notebook home"),
    ("docs/pipelines", "shared pipeline docs home"),
    ("tests", "test home"),
]


def detect_mode(repo: Path) -> str:
    """Choose the conservative setup mode from existing memory-contract files."""
    memory_files = [
        repo / "AGENTS.md",
        repo / "ANALYSIS_INDEX.md",
        repo / "docs" / "LESSONS.md",
    ]
    return "monitored" if any(path.exists() for path in memory_files) else "new"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit a repository for the minimal project-memory skeleton and "
            "optionally scaffold only the missing core items."
        )
    )
    parser.add_argument(
        "--repo",
        type=Path,
        required=True,
        help="Path to the repository root to audit.",
    )
    parser.add_argument(
        "--audit-only",
        action="store_true",
        help="Only report the detected structure; do not create anything.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Create missing scaffoldable items without prompting.",
    )
    parser.add_argument(
        "--with-pipeline-docs",
        action="store_true",
        help="Also create docs/pipelines when it is missing.",
    )
    parser.add_argument(
        "--mode",
        choices=("auto", "new", "monitored"),
        default="auto",
        help=(
            "Use expanded computational-biology setup for a new repo or "
            "contract-drift auditing for a monitored repo (default: auto)."
        ),
    )
    return parser.parse_args()


def existing_paths(repo: Path, candidates: Iterable[str]) -> list[str]:
    """Return candidate relative paths that already exist under the repo."""
    hits: list[str] = []
    for relpath in candidates:
        if (repo / relpath).exists():
            hits.append(relpath)
    return hits


def audit_requirement(
    repo: Path,
    *,
    key: str,
    label: str,
    canonical: str,
    kind: str,
    acceptable: Iterable[str] = (),
    manual_review_candidates: Iterable[str] = (),
) -> AuditItem:
    """Audit one canonical file or directory."""
    canonical_path = repo / canonical
    if canonical_path.exists():
        if kind == "file" and canonical_path.is_file():
            return AuditItem(key, label, canonical, "present", f"found `{canonical}`.")
        if kind == "dir" and canonical_path.is_dir():
            return AuditItem(key, label, canonical, "present", f"found `{canonical}/`.")

    acceptable_hits = existing_paths(repo, acceptable)
    if acceptable_hits:
        joined = ", ".join(f"`{hit}`" for hit in acceptable_hits)
        return AuditItem(
            key,
            label,
            canonical,
            "present",
            f"canonical path missing; using acceptable equivalent {joined}.",
        )

    review_hits = existing_paths(repo, manual_review_candidates)
    if review_hits:
        joined = ", ".join(f"`{hit}`" for hit in review_hits)
        return AuditItem(
            key,
            label,
            canonical,
            "manual_review",
            f"found possible equivalent(s) {joined}; skipping auto-scaffold.",
        )

    return AuditItem(key, label, canonical, "missing", f"`{canonical}` is missing.")


def build_audit(
    repo: Path, *, mode: str, with_pipeline_docs: bool = False
) -> tuple[list[AuditItem], list[ScaffoldAction]]:
    """Audit the repo and determine scaffoldable missing items."""
    items = [
        audit_requirement(
            repo,
            key="repo_guide",
            label="Repo guide",
            canonical="AGENTS.md",
            kind="file",
            manual_review_candidates=[
                "CLAUDE.md",
                "GUIDELINES.md",
                "docs/AGENTS.md",
                ".github/copilot-instructions.md",
                ".cursorrules",
            ],
        ),
        audit_requirement(
            repo,
            key="analysis_index",
            label="Analysis index",
            canonical="ANALYSIS_INDEX.md",
            kind="file",
            manual_review_candidates=[
                "ANALYSIS-INDEX.md",
                "docs/ANALYSIS_INDEX.md",
                "WORKSTREAMS.md",
                "docs/WORKSTREAMS.md",
            ],
        ),
        audit_requirement(
            repo,
            key="docs_home",
            label="Docs home",
            canonical="docs",
            kind="dir",
            manual_review_candidates=["doc"],
        ),
        audit_requirement(
            repo,
            key="lessons",
            label="Lessons doc",
            canonical="docs/LESSONS.md",
            kind="file",
            manual_review_candidates=[
                "LESSONS.md",
                "MEMORY.md",
                "memory.md",
                "docs/MEMORY.md",
                "docs/memory.md",
            ],
        ),
        audit_requirement(
            repo,
            key="pipelines_home",
            label="Pipeline docs home",
            canonical="docs/pipelines",
            kind="dir",
            manual_review_candidates=["pipelines"],
        ),
        audit_requirement(
            repo,
            key="code_home",
            label="Code home",
            canonical="scripts",
            kind="dir",
            acceptable=["src"],
            manual_review_candidates=["app", "lib", "analysis"],
        ),
        audit_requirement(
            repo,
            key="data_home",
            label="Input data home",
            canonical="data",
            kind="dir",
            manual_review_candidates=["datasets", "inputs"],
        ),
        audit_requirement(
            repo,
            key="results_home",
            label="Results home",
            canonical="results",
            kind="dir",
            manual_review_candidates=["output", "outputs"],
        ),
    ]

    item_map = {item.key: item for item in items}
    actions: list[ScaffoldAction] = []

    if item_map["docs_home"].status == "missing":
        actions.append(
            ScaffoldAction(
                relpath="docs",
                kind="dir",
                reason="durable docs home",
            )
        )
    if (
        (with_pipeline_docs or mode == "new")
        and
        item_map["pipelines_home"].status == "missing"
        and item_map["docs_home"].status != "manual_review"
    ):
        actions.append(
            ScaffoldAction(
                relpath="docs/pipelines",
                kind="dir",
                reason="shared pipeline docs home",
            )
        )
    if item_map["code_home"].status == "missing":
        actions.append(
            ScaffoldAction(
                relpath="scripts",
                kind="dir",
                reason="default code and CLI home",
            )
        )
    if item_map["data_home"].status == "missing":
        actions.append(
            ScaffoldAction(
                relpath="data",
                kind="dir",
                reason="raw/reference input home",
            )
        )
    if item_map["results_home"].status == "missing":
        actions.append(
            ScaffoldAction(
                relpath="results",
                kind="dir",
                reason="analysis output home",
            )
        )
    if item_map["repo_guide"].status == "missing":
        actions.append(
            ScaffoldAction(
                relpath="AGENTS.md",
                kind="file",
                reason="repo memory contract",
                template_name="AGENTS.md",
            )
        )
    if item_map["analysis_index"].status == "missing":
        actions.append(
            ScaffoldAction(
                relpath="ANALYSIS_INDEX.md",
                kind="file",
                reason="repo-wide map of maintained analyses",
                template_name="ANALYSIS_INDEX.md",
            )
        )
    if (
        item_map["lessons"].status == "missing"
        and item_map["docs_home"].status != "manual_review"
    ):
        actions.append(
            ScaffoldAction(
                relpath="docs/LESSONS.md",
                kind="file",
                reason="distilled repo memory",
                template_name="LESSONS.md",
            )
        )

    if mode == "new":
        existing_action_paths = {action.relpath for action in actions}
        for relpath, reason in NEW_REPO_DIRECTORIES:
            if not (repo / relpath).exists() and relpath not in existing_action_paths:
                actions.append(
                    ScaffoldAction(relpath=relpath, kind="dir", reason=reason)
                )
        if not (repo / ".gitignore").exists():
            actions.append(
                ScaffoldAction(
                    relpath=".gitignore",
                    kind="file",
                    reason="track memory records while ignoring generated data",
                    template_name=".gitignore",
                )
            )

    return items, actions


def read_template(template_name: str) -> str:
    """Load a bundled scaffold template."""
    template_path = TEMPLATES_DIR / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Missing bundled template: {template_path}")
    return template_path.read_text()


def monitored_drift_findings(repo: Path) -> list[str]:
    """Return deterministic contract-drift findings for an established repo."""
    findings: list[str] = []
    agents = repo / "AGENTS.md"
    if agents.exists():
        agents_text = agents.read_text(errors="replace")
        required_contract_terms = (
            "ANALYSIS_INDEX.md",
            "NOTES.md",
            "docs/LESSONS.md",
            "analysis_manifest.json",
        )
        missing_terms = [term for term in required_contract_terms if term not in agents_text]
        if missing_terms:
            findings.append(
                "AGENTS.md is missing contract terms: " + ", ".join(missing_terms) + "."
            )

    gitignore = repo / ".gitignore"
    if gitignore.exists():
        ignore_text = gitignore.read_text(errors="replace")
        if "/results/**" in ignore_text and "!/results/**/analysis_manifest.json" not in ignore_text:
            findings.append(
                "results are ignored without an exception for analysis_manifest.json."
            )

    results = repo / "results"
    manifests = sorted(results.glob("**/analysis_manifest.json")) if results.exists() else []
    variant_dirs: set[Path] = set()
    if results.exists():
        for runs_dir in results.glob("**/runs"):
            if not runs_dir.is_dir():
                continue
            variant_dirs.update(path for path in runs_dir.iterdir() if path.is_dir())
    missing = sum(not (path / "analysis_manifest.json").exists() for path in variant_dirs)
    if variant_dirs:
        findings.append(
            f"Found {len(variant_dirs)} direct runs/* variant directories; "
            f"{missing} have no analysis_manifest.json. Review selectively; "
            "presentation-only variants may be exempt."
        )
    findings.append(f"Found {len(manifests)} analysis_manifest.json file(s).")

    notes = sorted(results.glob("**/NOTES.md")) if results.exists() else []
    chronology_candidates = 0
    oversized_notes = 0
    for note in notes:
        lines = note.read_text(errors="replace").splitlines()
        dated_headings = sum(
            bool(re.search(r"\b20\d{2}[-/]\d{1,2}(?:[-/]\d{1,2})?\b", line))
            for line in lines
            if line.startswith("#")
        )
        chronology_candidates += dated_headings >= 3
        oversized_notes += len(lines) >= 400
    if notes:
        findings.append(
            f"Found {len(notes)} results NOTES.md files; {chronology_candidates} "
            f"have at least 3 dated headings and {oversized_notes} have at least "
            "400 lines. These are review triggers, not automatic rewrite findings."
        )

    lessons = repo / "docs" / "LESSONS.md"
    if lessons.exists():
        lesson_lines = lessons.read_text(errors="replace").splitlines()
        typed = sum(
            bool(
                re.match(
                    r"^\s*[-*]\s+`?(?:Default|Check|Trap|Preference)`?\s*:",
                    line,
                )
            )
            for line in lesson_lines
        )
        dated = sum(bool(re.match(r"^\s*[-*]\s+\[20\d{2}", line)) for line in lesson_lines)
        findings.append(
            f"docs/LESSONS.md has {typed} typed lessons and {dated} dated-feed bullets."
        )

    if (results / "output").exists():
        findings.append(
            "Legacy results/output exists. Preserve it in monitored mode and route "
            "new branches to the current contract instead of bulk-moving outputs."
        )
    return findings


def print_audit(
    repo: Path,
    mode: str,
    items: list[AuditItem],
    actions: list[ScaffoldAction],
) -> None:
    """Print a readable audit summary."""
    print(f"Project-memory audit for {repo}")
    print(f"Mode: {mode}")
    print("")
    for item in items:
        status = item.status.upper().replace("_", " ")
        print(f"[{status:<13}] {item.label}: {item.detail}")
    print("")
    if actions:
        print("Scaffoldable missing items:")
        for action in actions:
            print(f"- `{action.relpath}` ({action.kind}; {action.reason})")
    else:
        print("No scaffoldable missing items.")
    if mode == "monitored":
        print("")
        print("Contract-drift findings:")
        for finding in monitored_drift_findings(repo):
            print(f"- {finding}")


def confirm_scaffold(actions: list[ScaffoldAction]) -> bool:
    """Prompt before creating missing items."""
    print("")
    try:
        answer = input(
            f"Create {len(actions)} missing project-memory item(s)? [y/N]: "
        ).strip().lower()
    except EOFError:
        print("No prompt response received. Re-run with --yes or --audit-only.")
        return False
    return answer in {"y", "yes"}


def apply_scaffold(repo: Path, actions: list[ScaffoldAction]) -> None:
    """Create scaffoldable directories and files."""
    for action in actions:
        destination = repo / action.relpath
        if destination.exists():
            continue
        if action.kind == "dir":
            destination.mkdir(parents=True, exist_ok=True)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(read_template(action.template_name or ""))


def main() -> int:
    args = parse_args()
    repo = args.repo.expanduser().resolve()
    if not repo.exists():
        print(f"Repository path does not exist: {repo}", file=sys.stderr)
        return 1
    if not repo.is_dir():
        print(f"Repository path is not a directory: {repo}", file=sys.stderr)
        return 1

    mode = detect_mode(repo) if args.mode == "auto" else args.mode
    items, actions = build_audit(
        repo,
        mode=mode,
        with_pipeline_docs=args.with_pipeline_docs,
    )
    print_audit(repo, mode, items, actions)

    if args.audit_only or not actions:
        return 0

    if not args.yes and not confirm_scaffold(actions):
        print("Scaffold cancelled.")
        return 0

    apply_scaffold(repo, actions)
    print("")
    print(f"Scaffolded {len(actions)} item(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

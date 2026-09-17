"""Decision-memory trajectory and evidence-health helpers.

Inputs: in-memory ledger and verified source reader. Outputs: ledger history/health.
Parameters: current run ID and timestamp. Dependencies: Python standard library.
Usage: called by decision_memory.py apply; never edits workspace files directly.
"""
from copy import deepcopy
import subprocess


def validate_event_relations(events):
    """Keep append-only corrections connected without erasing earlier choices."""
    by_id = {event["id"]: event for event in events}
    graph = {}
    for event in events:
        refs = event.get("supersedes_event_ids", [])
        if (not isinstance(refs, list) or any(not isinstance(x, str) for x in refs)
                or len(refs) != len(set(refs)) or not set(refs) <= set(by_id)
                or event["id"] in refs):
            raise ValueError("Invalid supersedes_event_ids")
        if refs and not str(event.get("relation_reason", "")).strip():
            raise ValueError("Supersession needs relation_reason")
        graph[event["id"]] = refs
    visiting, visited = set(), set()

    def visit(key):
        if key in visiting:
            raise ValueError("Cyclic event supersession")
        if key in visited:
            return
        visiting.add(key)
        for parent in graph[key]:
            visit(parent)
        visiting.remove(key)
        visited.add(key)

    for key in graph:
        visit(key)


def retain_principle_history(state, updates, run_id, timestamp):
    """Record observed baseline, then full before/after for every submitted update."""
    history = state.setdefault("principle_revisions", [])
    recorded = {entry["principle_id"] for entry in history}
    current = {p["id"]: p for p in state["principles"]}
    for key, principle in current.items():
        if key not in recorded:
            history.append({
                "principle_id": key, "kind": "baseline", "run_id": run_id,
                "timestamp": timestamp, "before": None, "after": deepcopy(principle),
                "reason": "First retained snapshot; earlier revisions are unknown.",
            })
    for principle in updates:
        key = principle["id"]
        history.append({
            "principle_id": key, "kind": "revision", "run_id": run_id,
            "timestamp": timestamp, "before": deepcopy(current.get(key)),
            "after": deepcopy(principle),
            "reason": principle.get("change_reason", principle["review_rationale"]),
        })


def refresh_axiom_health(state, read_source, timestamp):
    """A lost original does not erase retained quotes or block unrelated updates."""
    health = state.setdefault("principle_source_health", {})
    events = {event["id"]: event for event in state["events"]}
    cache = {}
    for principle in state["principles"]:
        if principle["status"] != "axiom":
            continue
        previous = health.get(principle["id"], {})
        old_checks = {(c["event_id"], c.get("source_id")): c
                      for c in previous.get("checks", [])}
        checks = []
        refs = principle["support_event_ids"] + principle.get("counter_event_ids", [])
        for key in dict.fromkeys(refs):
            for item in events[key]["evidence"]:
                source = item["source"]
                cache_key = (item.get("source_id"), source.get("episode_id"), source.get("host"), source.get("path"),
                             source.get("line"), source.get("sha256"))
                if cache_key not in cache:
                    try:
                        cache[cache_key] = ("verified", read_source(source))
                    except (OSError, ValueError, subprocess.SubprocessError) as exc:
                        message = str(exc).lower()
                        status = "changed" if "changed" in message and "missing" not in message else "unavailable"
                        cache[cache_key] = (status, str(exc))
                status, detail = cache[cache_key]
                if status == "verified" and item["quote"] not in detail:
                    status, detail = "changed", "Retained quote absent from original source"
                checks.append({
                    "event_id": key, "source_id": item.get("source_id"),
                    "status": status,
                    "last_verified_at": timestamp if status == "verified" else
                    old_checks.get((key, item.get("source_id")), {}).get("last_verified_at"),
                    "detail": "Original and retained quote verified" if status == "verified" else detail,
                })
        verified = all(c["status"] == "verified" for c in checks)
        health[principle["id"]] = {
            "checked_at": timestamp,
            "last_verified_at": timestamp if verified else previous.get("last_verified_at"),
            "status": "verified" if verified else "needs_review",
            "checks": checks,
        }

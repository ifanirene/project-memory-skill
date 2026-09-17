#!/usr/bin/env python3
"""Collect and validate personal decision evidence, separately from doc upkeep.

Inputs: config/repos.json, configured Codex sessions and maintained notes.
Outputs: bounded pointer/excerpt packets; one atomic decision ledger; Markdown views.
Parameters: source and session limits bound semantic review, not proof of coverage.
Dependencies: Python 3.10+ standard library; sibling memoryctl.py; SSH for SCG.
Example: python decision_memory.py collect --workspace /path/to/memory --output run.json
"""
from __future__ import annotations

import argparse
from collections import defaultdict, deque
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import uuid

from memoryctl import atomic_write_json, atomic_write_text, workspace_lock
from decision_history import (
    refresh_axiom_health, retain_principle_history, validate_event_relations,
)

LEDGER = "state/decision_memory_v1.json"
SCHEMA = 1


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def ledger(workspace):
    return read(workspace / LEDGER, {
        "schema_version": SCHEMA, "reviews": {}, "scans": {}, "events": [],
        "principles": [], "runs": [],
    })


def clean_user(text):
    """Remove injected context; never interpret it as the person's own words."""
    for tag in ("in-app-browser-context", "recommended_plugins", "environment_context"):
        text = re.sub(rf"<{tag}\b[^>]*>[\s\S]*?</{tag}>", "", text)
    for separator in ("## My request:", "## My request for Codex:"):
        if separator in text:
            text = text.split(separator, 1)[1]
    text = text.strip()
    if text.startswith(("# AGENTS.md instructions", "<environment_context>",
                        "<recommended_plugins>", "<turn_aborted>",
                        "<codex_internal_context", "<subagent_notification")):
        return ""
    if text.startswith("<send_user_message_question_reply>"):
        try:
            body = text.split(">", 1)[1].rsplit("<", 1)[0]
            # Questions/options are assistant text; only answers are human evidence.
            text = "\n".join(str(x["answer"]) for x in json.loads(body))
        except (ValueError, KeyError, TypeError):
            return ""
    if re.search(r"(?i)(api.?key|password|access.?token|secret)", text) and re.search(
        r"[A-Za-z0-9_+/.=-]{20,}", text
    ):
        return ""  # Do not persist credential-bearing source excerpts.
    return text


def session_records(path, repo):
    """Read only completed turns. Row hashes survive later session appends."""
    messages = []
    completed_line = 0
    meta = {}
    for line_number, raw in enumerate(path.open(errors="replace"), 1):
        try:
            row = json.loads(raw)
        except ValueError:
            continue
        body = row.get("payload", {})
        if row.get("type") == "session_meta":
            meta = body
            if isinstance(meta.get("source"), dict):
                return []  # Subagent prompts/copies are not independent user choices.
        if (row.get("type") == "event_msg" and body.get("type") == "task_complete") or (
            row.get("type") == "response_item" and body.get("role") == "assistant"
            and body.get("channel") == "final"
        ):
            completed_line = line_number
        if row.get("type") != "response_item" or body.get("role") != "user":
            continue
        text = clean_user("\n".join(
            item.get("text", "") for item in body.get("content", [])
            if item.get("type") in {"input_text", "text"}
        ))
        if not text:
            continue
        event_key = body.get("id") or digest([row.get("timestamp"), text])
        automatic = bool(re.search(
            r"(?i)(this is phase [ab]|run (?:the )?(?:weekly|monthly|native monthly) "
            r"(?:central|repo|reflection|axiom)|automation context)", text
        ))
        messages.append({
            "source_id": "dialog-" + digest(event_key)[:24], "repo": repo,
            "kind": "user_message", "path": str(path), "line": line_number,
            "sha256": hashlib.sha256(raw.encode()).hexdigest(),
            "timestamp": row.get("timestamp") or meta.get("timestamp"),
            "episode_id": meta.get("id", str(path)), "cwd": meta.get("cwd"),
            "origin": "automation" if automatic else "human_or_unverified",
            "excerpt": text[:900], "excerpt_truncated": len(text) > 900,
        })
    return [m for m in messages if m["line"] < completed_line]


def document_record(path, repo, root):
    data = path.read_bytes()
    content = data.decode(errors="replace")
    sha = hashlib.sha256(data).hexdigest()
    return {
        "source_id": "doc-" + digest([repo, str(path.relative_to(root)), sha])[:24],
        "repo": repo, "kind": "document", "path": str(path), "sha256": sha,
        "timestamp": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
        "episode_id": "unattributed-document:" + str(path),
        "origin": "authorship_unverified", "excerpt": content[:4000],
        "excerpt_truncated": len(content) > 4000,
    }


def inventory_repo(repo, session_roots, state, session_limit):
    root = Path(repo["root"])
    if not root.is_dir():
        raise ValueError("Unavailable repository: " + str(root))
    records = []
    paths = set()
    for pattern in repo.get("decision_patterns", repo.get("patterns", ["**/NOTES.md"])):
        for path in root.glob(pattern):
            if path.is_file() and not path.is_symlink() and ".git" not in path.parts:
                paths.add(path)
    for path in sorted(paths):
        record = document_record(path, repo["name"], root)
        if record["source_id"] not in state["reviews"]:
            records.append(record)
    pending = []
    catalog = {}
    aliases = repo.get("cwd_aliases", [])
    for session_root in session_roots:
        for path in Path(session_root).glob("**/*.jsonl"):
            with path.open(errors="replace") as handle:
                try:
                    meta = json.loads(handle.readline()).get("payload", {})
                except ValueError:
                    continue
            cwd = meta.get("cwd", "")
            if not any(cwd == r or cwd.startswith(r.rstrip("/") + "/")
                       for r in [str(root), *aliases]):
                continue
            if isinstance(meta.get("source"), dict):
                continue
            stat = path.stat()
            signature = [stat.st_size, stat.st_mtime_ns]
            key = meta.get("id") or str(path)
            previous = catalog.get(key)
            if previous is None or signature[1] > previous[1][1]:
                catalog[key] = (path, signature)
    total_sessions = len(catalog)
    for path, signature in catalog.values():
            if state["scans"].get(str(path)) == signature:
                continue
            pending.append((path, signature))
    # Both fresh work and old backlog get capacity; newest-only bootstraps can starve.
    attempts = state.get("scan_attempts", {})
    pending.sort(key=lambda pair: (attempts.get(str(pair[0]), ""), pair[1][1]))
    chosen = []
    while pending and len(chosen) < session_limit:
        oldest_attempt = attempts.get(str(pending[0][0]), "")
        peers = [i for i, pair in enumerate(pending)
                 if attempts.get(str(pair[0]), "") == oldest_attempt]
        chosen.append(pending.pop(peers[-1] if len(chosen) % 2 == 0 else peers[0]))
    scans = []
    for path, signature in chosen:
        found = session_records(path, repo["name"])
        for record in found:
            record["session_roots"] = [str(Path(p).resolve()) for p in session_roots]
        scans.append({"path": str(path), "signature": signature,
                      "source_ids": [r["source_id"] for r in found]})
        records.extend(r for r in found if r["source_id"] not in state["reviews"])
    return records, scans, {
        "repo": repo["name"], "documents_discovered": len(paths),
        "root_sessions_discovered": total_sessions, "sessions_scanned": len(chosen),
        "sessions_not_scanned": len(pending), "status": "available",
    }


def recover_session_path(source):
    """Recover moved sessions within the configured Codex inventory only."""
    roots = source.get("session_roots", [])
    original = Path(source["path"])
    if not roots:
        for parent in original.parents:
            if parent.name in {"sessions", "archived_sessions"}:
                roots = [str(parent.parent / name)
                         for name in ("sessions", "archived_sessions")]
                break
    for root in roots:
        for candidate in Path(root).glob("**/*.jsonl"):
            try:
                with candidate.open(errors="replace") as handle:
                    row = json.loads(handle.readline())
                    if (row.get("type") != "session_meta"
                            or row.get("payload", {}).get("id") != source["episode_id"]):
                        continue
                    handle.seek(0)
                    for number, line in enumerate(handle, 1):
                        if number == source["line"]:
                            if hashlib.sha256(line.encode()).hexdigest() == source["sha256"]:
                                return candidate
                            break
            except (OSError, ValueError):
                continue
    raise ValueError("Source session missing or changed: " + str(original))


def full_source(source):
    if source.get("host"):
        command = [source["remote_python"], source["remote_script"],
                   "read-source", "--source-json", json.dumps(source)]
        result = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", source["host"],
             shlex.join(command)], capture_output=True, text=True, timeout=60,
        )
        if result.returncode:
            raise ValueError("Remote source unavailable: " + source["path"])
        return json.loads(result.stdout)["text"]
    path = Path(source["path"])
    if source["kind"] == "document":
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != source["sha256"]:
            raise ValueError("Source changed: " + str(path))
        return data.decode(errors="replace")
    if not path.exists():
        path = recover_session_path(source)
    with path.open(errors="replace") as handle:
        meta = json.loads(handle.readline())
    if (meta.get("type") != "session_meta"
            or meta.get("payload", {}).get("id") != source["episode_id"]):
        raise ValueError("Source session ID changed: " + str(path))
    for number, line in enumerate(path.open(errors="replace"), 1):
        if number == source["line"]:
            if hashlib.sha256(line.encode()).hexdigest() != source["sha256"]:
                raise ValueError("Source row changed: " + str(path))
            body = json.loads(line)["payload"]
            return clean_user("\n".join(x.get("text", "") for x in body["content"]
                                      if x.get("type") in {"input_text", "text"}))
    raise ValueError("Source row missing: " + str(path))


def clean_context(text):
    """Omit injected context and common credential-bearing messages entirely."""
    text = clean_user(text)
    if re.search(
        r"(?i)(?:\b(?:password|passwd|api[_ -]?key|access[_ -]?token|secret)\b"
        r"[\"']?\s*[:=]\s*\S+|\bBearer\s+\S+|\bsk-[A-Za-z0-9_-]{12,}"
        r"|-----BEGIN [A-Z ]*PRIVATE KEY-----|\bAKIA[A-Z0-9]{16}\b)", text
    ):
        return ""
    return text


def read_context(source, max_chars=6000):
    """Read two retained messages on either side; never certify understanding."""
    if not 1 <= max_chars <= 24000:
        raise ValueError("Context max_chars must be between 1 and 24000")
    if source["kind"] != "user_message":
        raise ValueError("read-context requires a user_message source; read documents directly")
    if source.get("host"):
        remote_source = {k: v for k, v in source.items() if k != "host"}
        command = [source["remote_python"], source["remote_script"], "read-context",
                   "--source-json", json.dumps(remote_source), "--max-chars", str(max_chars)]
        result = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", source["host"],
             shlex.join(command)], capture_output=True, text=True, timeout=60,
        )
        if result.returncode:
            raise ValueError("Remote context unavailable: " + source["path"])
        return json.loads(result.stdout)
    full_source(source)  # Check the unchanged evidence identity before adding context.
    path = Path(source["path"])
    if not path.exists():
        path = recover_session_path(source)
    before, after = deque(maxlen=2), []
    target = None
    with path.open(errors="replace") as handle:
        for number, raw in enumerate(handle, 1):
            try:
                row = json.loads(raw)
            except ValueError:
                continue
            body = row.get("payload", {})
            if number == 1 and body.get("id") != source["episode_id"]:
                raise ValueError("Source session ID changed: " + str(path))
            is_target = number == source["line"]
            sha = hashlib.sha256(raw.encode()).hexdigest()
            if is_target and sha != source["sha256"]:
                raise ValueError("Source row changed: " + str(path))
            if (row.get("type") != "response_item"
                    or body.get("role") not in {"user", "assistant"}
                    or body.get("type", "message") != "message"):
                continue
            content = clean_context("\n".join(
                item.get("text", "") for item in body.get("content", [])
                if item.get("type") in {"input_text", "output_text", "text"}
            ))
            if not content:
                if is_target:
                    raise ValueError("Source context omitted by credential/context filter")
                continue
            message = {"line": number, "role": body["role"], "sha256": sha,
                       "is_evidence": is_target, "text": content}
            if is_target:
                target = message
            elif number < source["line"]:
                before.append(message)
            else:
                after.append(message)
                if len(after) == 2:
                    break
    if target is None:
        raise ValueError("Source row missing: " + str(path))
    messages = [*before, target, *after]
    # Reserve a share for each message so a long target cannot hide all alternatives.
    per_message = max_chars // len(messages)
    remaining = max_chars - per_message * len(messages)
    for message in messages:
        budget = per_message + (remaining if message is target else 0)
        message["text_truncated"] = len(message["text"]) > budget
        message["text"] = message["text"][:budget]
    return {"source_id": source["source_id"], "episode_id": source["episode_id"],
            "resolved_path": str(path), "evidence_sha256": source["sha256"],
            "messages": messages, "max_chars": max_chars,
            "text_chars": sum(len(m["text"]) for m in messages),
            "context_truncated": any(m["text_truncated"] for m in messages),
            "notice": "Bounded context retrieval only; not proof of understanding or full coverage."}


def validate_events(packet, proposal):
    if packet.get("schema_version") != SCHEMA or proposal.get("schema_version") != SCHEMA:
        raise ValueError("Unsupported decision schema")
    sources = {s["source_id"]: s for s in packet["sources"]}
    reviews = proposal.get("reviews", [])
    if len(reviews) != len(sources) or {r["source_id"] for r in reviews} != set(sources):
        raise ValueError("Review each packet source exactly once")
    deferred = {r["source_id"] for r in reviews if r.get("disposition") == "deferred"}
    texts = {key: full_source(s) for key, s in sources.items() if key not in deferred}
    events = proposal.get("events", [])
    if len({e["id"] for e in events}) != len(events):
        raise ValueError("Duplicate event ID")
    required = ("context", "choice", "alternative", "reason", "tradeoff", "scope",
                "attribution", "uncertainty", "future_test")
    used = set()
    for event in events:
        if any(not isinstance(event.get(k), str) or not event[k].strip() for k in required):
            raise ValueError("Decision event missing context, alternatives or limits")
        if event["attribution"] not in {"direct_user", "attributed_user", "agent_inference",
                                        "automation_operations"}:
            raise ValueError("Unknown attribution")
        evidence = event.get("evidence", [])
        if not evidence:
            raise ValueError("Event needs evidence")
        for item in evidence:
            sid, quote = item["source_id"], item["quote"]
            if sid in deferred:
                raise ValueError("Deferred source cannot be event evidence")
            if not 1 <= len(quote) <= 600 or quote not in texts.get(sid, ""):
                raise ValueError("Evidence quote absent from verified source")
            source = sources[sid]
            if event["attribution"] == "direct_user" and (
                source["kind"] != "user_message" or source["origin"] == "automation"
            ):
                raise ValueError("Nonhuman or unattributed source cannot be direct user evidence")
            used.add(sid)
    for review in reviews:
        if review.get("disposition") not in {"signal", "no_signal", "deferred"}:
            raise ValueError("Unknown source disposition")
        if not review.get("reason"):
            raise ValueError("No-signal/deferred reviews need an explanation")
        if review["disposition"] == "signal" and review["source_id"] not in used:
            raise ValueError("Signal review has no event")
        if review["disposition"] != "signal" and review["source_id"] in used:
            raise ValueError("Event evidence contradicts review disposition")
    return sources


def validate_principles(state, principles):
    events = {event["id"]: event for event in state["events"]}
    if len({p["id"] for p in principles}) != len(principles):
        raise ValueError("Duplicate principle ID")
    for principle in principles:
        for key in ("statement", "scope", "boundary", "predicted_choice", "cost",
                    "counterevidence_search", "review_rationale"):
            if not principle.get(key):
                raise ValueError("Principle missing " + key)
        status = principle.get("status")
        if status not in {"candidate", "reflection", "axiom", "retired"}:
            raise ValueError("Unknown principle status")
        refs = principle.get("support_event_ids", [])
        counters = principle.get("counter_event_ids", [])
        if not refs or len(set(refs)) != len(refs) or not set(refs + counters) <= set(events):
            raise ValueError("Invalid principle evidence IDs")
        direct = [events[key] for key in refs if events[key]["attribution"] == "direct_user"]
        episodes = {item["source"]["episode_id"] for e in direct for item in e["evidence"]}
        if status == "reflection" and len(episodes) < 2:
            raise ValueError("Reflection needs two independent human episodes")
        if status == "axiom":
            dates = [datetime.fromisoformat(item["source"]["timestamp"].replace("Z", "+00:00"))
                     for e in direct for item in e["evidence"]]
            # Passage of time/no-change runs never count as confirmation.
            if len(episodes) < 3 or not dates or (max(dates) - min(dates)).days < 28:
                raise ValueError("Axiom needs three human episodes spanning 28 days")
            if counters and not principle.get("counterevidence_resolution"):
                raise ValueError("Axiom has unresolved counterevidence")
            if not principle.get("retrieval_tags"):
                raise ValueError("Axiom needs task retrieval tags")
            for event in [events[key] for key in dict.fromkeys(refs + counters)]:
                for item in event["evidence"]:
                    if item["quote"] not in full_source(item["source"]):
                        raise ValueError("Axiom evidence is no longer recoverable")


def render(workspace, state):
    lines = ["# Personal decision evidence", "", "Generated from state/decision_memory_v1.json.", ""]
    for e in state["events"]:
        lines += [f"## {e['id']} — {e['choice']}", ""]
        for key in ("attribution", "context", "alternative", "reason", "tradeoff", "scope",
                    "uncertainty", "future_test"):
            lines += [f"- **{key}**: {e[key]}"]
        for item in e["evidence"]:
            s = item["source"]
            location = (s.get("host", "") + ":" if s.get("host") else "") + s["path"]
            lines += [f"- Evidence: `{location}` line {s.get('line', 'document')}; "
                      f"date {s.get('timestamp', 'not recorded')}; "
                      f"episode `{s['episode_id']}`; “{item['quote']}”"]
        if e.get("supersedes_event_ids"):
            lines += [f"- Supersedes: {', '.join(e['supersedes_event_ids'])}",
                      f"- Relation reason: {e['relation_reason']}"]
        successors = [other['id'] for other in state['events']
                      if e['id'] in other.get('supersedes_event_ids', [])]
        if successors:
            lines += [f"- Superseded by: {', '.join(successors)} (historical evidence retained)"]
        lines.append("")
    atomic_write_text(workspace / "observations/DECISIONS.md", "\n".join(lines))
    lines = ["# Personal judgment principles", "", "Candidates are interpretations, not endorsed identity.", ""]
    for p in state["principles"]:
        lines += [f"## {p['id']} [{p['status']}] {p['statement']}", ""]
        for key in ("scope", "predicted_choice", "cost", "boundary", "support_event_ids",
                    "counter_event_ids", "counterevidence_search", "counterevidence_resolution",
                    "review_rationale"):
            lines += [f"- **{key}**: {p.get(key, [])}"]
        for revision in state.get("principle_revisions", []):
            if revision['principle_id'] != p['id']:
                continue
            before = revision['before']
            after = revision['after']
            previous = f"{before['status']}: {before['statement']}" if before else "not previously retained"
            lines += [f"- History ({revision['kind']}, {revision['timestamp']}, run `{revision['run_id']}`): "
                      f"{previous} → {after['status']}: {after['statement']}; {revision['reason']}"]
        lines.append("")
    atomic_write_text(workspace / "reflections/PERSONAL_JUDGMENT.md", "\n".join(lines))
    lines = ["# Axioms — task routing", "",
             "Derived from verified human decision episodes, not immutable traits.",
             "Current instructions and evidence take precedence. The JSON ledger is authoritative.", ""]
    for p in state["principles"]:
        if p["status"] == "axiom":
            lines += [f"## {p['id']}", "", p["statement"], "",
                      f"- Scope: {p['scope']}", f"- Cost: {p['cost']}",
                      f"- Boundary: {p['boundary']}",
                      f"- Evidence: {', '.join(p['support_event_ids'])}",
                      f"- Retrieval: {', '.join(p['retrieval_tags'])}", ""]
            if p.get("counter_event_ids"):
                lines += [f"- Counterevidence: {', '.join(p['counter_event_ids'])}",
                          f"- Resolution: {p.get('counterevidence_resolution', 'Not recorded')}"]
            health = state.get("principle_source_health", {}).get(p['id'], {})
            lines += [f"- Source health: {health.get('status', 'unchecked')}; "
                      f"checked at {health.get('checked_at', 'not recorded')}; "
                      f"last fully verified {health.get('last_verified_at') or 'not recorded'}."]
            for check in health.get('checks', []):
                if check['status'] != 'verified':
                    lines += [f"  - {check['event_id']}: {check['status']} — {check['detail']}"]
            if health.get('status') != 'verified':
                lines += ["  Retained quotes remain available; original context is not currently fully verified."]
            lines.append("")
    lines += ["[Decision evidence](../observations/DECISIONS.md) · "
              "[Reflections and candidates](../reflections/PERSONAL_JUDGMENT.md)", ""]
    if (workspace / "axioms/LEGACY_AXIOMS_2026-09-17.md").exists():
        lines += ["[Legacy axioms](LEGACY_AXIOMS_2026-09-17.md) are preserved as historical",
                  "operations/technical guidance with unresolved personal attribution.",
                  "They are not active personal axioms or independent confirmations.", ""]
    atomic_write_text(workspace / "axioms/AXIOMS.md", "\n".join(lines))


def collect(args):
    w = args.workspace.resolve()
    state = ledger(w)
    config = read(w / "config/repos.json")
    groups, scans, coverage = [], [], []
    for repo in config["repos"] + config.get("remote_repos", []):
        if args.repo and repo["name"] not in args.repo:
            continue
        try:
            if repo.get("host"):
                command = [repo["python"], repo["decision_script"], "remote-export",
                           "--repo-json", json.dumps(repo), "--session-limit", str(args.session_limit),
                           "--state-stdin"]
                result = subprocess.run(
                    ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", repo["host"],
                     shlex.join(command)], text=True, capture_output=True, timeout=60,
                    input=json.dumps({"reviews": dict.fromkeys(state["reviews"]),
                                      "scans": state["scans"],
                                      "scan_attempts": state.get("scan_attempts", {})}),
                )
                if result.returncode:
                    raise ValueError("SSH export failed: " + result.stderr[-300:])
                data = json.loads(result.stdout)
                records, remote_scans, report = data["records"], data["scans"], data["coverage"]
                for s in records:
                    s.update(host=repo["host"], remote_python=repo["python"],
                             remote_script=repo["decision_script"])
                records = [s for s in records if s["source_id"] not in state["reviews"]]
                scans.extend(remote_scans)
            else:
                records, new_scans, report = inventory_repo(
                    repo, config.get("dialog_roots", []), state, args.session_limit)
                scans.extend(new_scans)
            # Alternate dialog and note evidence; maintenance docs cannot use all capacity.
            dialogs = sorted([s for s in records if s["kind"] == "user_message"],
                             key=lambda s: s["timestamp"] or "", reverse=True)
            docs = sorted([s for s in records if s["kind"] == "document"],
                          key=lambda s: s["timestamp"], reverse=True)
            # Deferred sources retain eligibility without taking every future slot.
            source_attempts = state.get("source_attempts", {})
            dialogs.sort(key=lambda s: source_attempts.get(s["source_id"], ""))
            docs.sort(key=lambda s: source_attempts.get(s["source_id"], ""))
            group = []
            while dialogs or docs:
                if dialogs:
                    group.append(dialogs.pop(0))
                if docs:
                    group.append(docs.pop(0))
            groups.append(group)
            coverage.append(report)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            coverage.append({"repo": repo["name"], "status": "unavailable", "reason": str(exc)})
    selected = []
    seen = set()
    while any(groups) and len(selected) < args.max_sources:
        for group in groups:
            if group and len(selected) < args.max_sources:
                source = group.pop(0)
                if source["source_id"] not in seen:
                    selected.append(source)
                    seen.add(source["source_id"])
    packet = {"schema_version": SCHEMA, "run_id": now().replace(":", "-") + "-" + uuid.uuid4().hex[:6],
              "state_digest": digest(state), "sources": selected, "scans": scans,
              "coverage": coverage, "remaining_discovered_sources": sum(map(len, groups)),
              "created_at": now()}
    output = args.output.resolve()
    if not output.is_relative_to(w):
        raise ValueError("Packet must stay in the personal workspace")
    atomic_write_json(output, packet)
    print(json.dumps({k: packet[k] for k in ("run_id", "coverage", "remaining_discovered_sources")}, indent=2))
    print(f"Wrote {len(selected)} sources to {output}")


def apply(args):
    w = args.workspace.resolve()
    proposal = read(args.proposal)
    with workspace_lock(w):
        state = ledger(w)
        if args.packet:
            packet = read(args.packet)
            if packet["state_digest"] != digest(state) or proposal.get("run_id") != packet["run_id"]:
                raise ValueError("Stale ledger snapshot or wrong run ID")
            sources = validate_events(packet, proposal)
            existing = {e["id"] for e in state["events"]}
            validate_event_relations(state["events"] + proposal.get("events", []))
            retain_principle_history(state, [], packet["run_id"], now())
            for event in proposal.get("events", []):
                if event["id"] in existing:
                    raise ValueError("Event ID already exists")
                for item in event["evidence"]:
                    item["source"] = {k: v for k, v in sources[item["source_id"]].items()
                                      if k not in {"excerpt", "excerpt_truncated"}}
                state["events"].append(event)
            for review in proposal["reviews"]:
                if review["disposition"] != "deferred":
                    state["reviews"][review["source_id"]] = {**review, "run_id": packet["run_id"]}
            for source in packet["sources"]:
                state.setdefault("source_attempts", {})[source["source_id"]] = packet.get("created_at", now())
            for scan in packet["scans"]:
                state.setdefault("scan_attempts", {})[scan["path"]] = packet.get("created_at", now())
                if set(scan["source_ids"]) <= set(state["reviews"]):
                    state["scans"][scan["path"]] = scan["signature"]
            state["runs"].append({"run_id": packet["run_id"], "at": now(),
                                  "coverage": packet["coverage"],
                                  "events_added": len(proposal.get("events", [])),
                                  "remaining_discovered_sources": packet["remaining_discovered_sources"]})
        else:
            if proposal.get("state_digest") != digest(state):
                raise ValueError("Stale reflection snapshot")
            principles = proposal.get("principles", [])
            validate_principles(state, principles)
            validate_event_relations(state["events"])
            retain_principle_history(state, principles, proposal["run_id"], now())
            # Updates merge by ID; omitted principles are not silently deleted.
            merged = {p["id"]: p for p in state["principles"]}
            merged.update({p["id"]: p for p in principles})
            state["principles"] = list(merged.values())
            state["runs"].append({"run_id": proposal["run_id"], "at": now(), "kind": "reflection"})
        refresh_axiom_health(state, full_source, now())
        if not args.validate_only:
            atomic_write_json(w / LEDGER, state)  # sole authoritative transaction
            render(w, state)  # repairable views; never use views as independent evidence
    print("VALID" if args.validate_only else "APPLIED; ledger committed and views regenerated")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("collect")
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--repo", action="append")
    p.add_argument("--max-sources", type=int, default=24)
    p.add_argument("--session-limit", type=int, default=4)
    p = sub.add_parser("apply")
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--proposal", type=Path, required=True)
    p.add_argument("--packet", type=Path)
    p.add_argument("--validate-only", action="store_true")
    p = sub.add_parser("render")
    p.add_argument("--workspace", type=Path, required=True)
    p = sub.add_parser("remote-export")
    p.add_argument("--repo-json", required=True)
    p.add_argument("--session-limit", type=int, default=4)
    p.add_argument("--state-stdin", action="store_true")
    p = sub.add_parser("read-source")
    p.add_argument("--source-json", required=True)
    p = sub.add_parser("read-context")
    p.add_argument("--source-json", required=True)
    p.add_argument("--max-chars", type=int, default=6000)
    args = parser.parse_args()
    if args.command == "collect":
        collect(args)
    elif args.command == "apply":
        apply(args)
    elif args.command == "render":
        with workspace_lock(args.workspace):
            render(args.workspace, ledger(args.workspace))
    elif args.command == "remote-export":
        repo = json.loads(args.repo_json)
        state = json.load(sys.stdin) if args.state_stdin else {"reviews": {}, "scans": {}}
        records, scans, coverage = inventory_repo(
            repo, repo.get("dialog_roots", []), state, args.session_limit)
        print(json.dumps({"records": records, "scans": scans, "coverage": coverage}))
    else:
        source = json.loads(args.source_json)
        if args.command == "read-context":
            # SSH invokes the same CLI with host removed to avoid recursive routing.
            print(json.dumps(read_context(source, args.max_chars)))
        else:
            source.pop("host", None)
            print(json.dumps({"text": full_source(source)}))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as exc:
        sys.exit(str(exc))

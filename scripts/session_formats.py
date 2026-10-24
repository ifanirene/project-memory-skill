"""Read native dialogue formats without exporting full transcripts."""
import hashlib
import json
import re


def session_header(path):
    """Inspect a bounded header; Claude files can start with metadata rows."""
    if "subagents" in path.parts or path.name.startswith("agent-"):
        return {}
    with path.open(errors="replace") as handle:
        for number, raw in enumerate(handle, 1):
            if number > 256:
                return {}
            try:
                row = json.loads(raw)
            except ValueError:
                continue
            if row.get("type") == "session_meta":
                return {**row.get("payload", {}), "provider": "codex"}
            if row.get("sessionId") and row.get("cwd"):
                if row.get("isSidechain"):
                    return {}
                return {"id": row["sessionId"], "cwd": row["cwd"],
                        "timestamp": row.get("timestamp"), "provider": "claude_code"}
    return {}


def message_body(row, provider):
    if provider != "claude_code":
        return row.get("payload", {}) if row.get("type") == "response_item" else {}
    if (row.get("type") not in {"user", "assistant"}
            or row.get("isSidechain") or row.get("isMeta") or row.get("isCompactSummary")
            or row.get("toolUseResult") is not None):
        return {}
    body = row.get("message", {})
    if not isinstance(body, dict) or body.get("role") != row["type"]:
        return {}
    content = body.get("content", [])
    if isinstance(content, str):
        content = [{"type": "text", "text": content}]
    return {**body, "type": "message", "content": content}


def message_text(body):
    return "\n".join(item.get("text", "") for item in body.get("content", [])
                     if isinstance(item, dict)
                     and item.get("type") in {"input_text", "output_text", "text"})


def claude_text(row, clean):
    text = clean(message_text(message_body(row, "claude_code")))
    if text.startswith(("<local-command-", "<command-name>", "<system-reminder>",
                        "<task-notification>", "<teammate-message>",
                        "[Request interrupted by user", "This session is being continued")):
        return ""
    return text


def claude_records(path, repo, header, digest, clean):
    """Retain user ancestors of completed main-agent turns, with original hashes."""
    parents, messages, completions = {}, {}, []
    with path.open(errors="replace") as handle:
        for number, raw in enumerate(handle, 1):
            try:
                row = json.loads(raw)
            except ValueError:
                continue
            if row.get("isSidechain") or row.get("sessionId") != header["id"]:
                continue
            uid = row.get("uuid")
            if not uid:
                continue
            parents[uid] = row.get("parentUuid")
            body = message_body(row, "claude_code")
            if body.get("role") == "assistant" and body.get("stop_reason") in {"end_turn", "refusal"}:
                completions.append(uid)
            if body.get("role") != "user":
                continue
            text = claude_text(row, clean)
            if not text:
                continue
            origin = row.get("origin")
            origin = origin.get("kind") if isinstance(origin, dict) else origin
            automatic = origin not in {None, "human", "user"} or bool(re.search(
                r"(?i)(automation context|this is phase [ab]|run (?:the )?(?:weekly|monthly|native monthly) "
                r"(?:central|repo|reflection|axiom))", text))
            messages[uid] = {
                "source_id": "dialog-claude-" + digest(uid)[:24], "repo": repo,
                "kind": "user_message", "provider": "claude_code", "path": str(path),
                "line": number, "sha256": hashlib.sha256(raw.encode()).hexdigest(),
                "timestamp": row.get("timestamp"), "episode_id": header["id"],
                "cwd": row.get("cwd", header["cwd"]),
                "origin": "automation" if automatic else "human_or_unverified",
                "excerpt": text[:900], "excerpt_truncated": len(text) > 900,
            }
    completed = set()
    for uid in completions:
        while uid and uid not in completed:
            completed.add(uid)
            uid = parents.get(uid)
    return [message for uid, message in messages.items() if uid in completed]

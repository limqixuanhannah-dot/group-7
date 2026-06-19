#!/usr/bin/env python3
"""SENTRY — Secure File Transfer & Access Log"""
import json, sys
from datetime import datetime, timezone

DATA_FILE = "/home/ubuntu/.openclaw/workspace/projects/sentry-systems.json"

def load():
    with open(DATA_FILE) as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def log_event(action_type, file_name, project, user, classification, recipient):
    """Log a file access/transfer event."""
    data = load()
    if "file_log" not in data:
        data["file_log"] = []
    entry = {
        "id": f"fl-{len(data['file_log']) + 1}",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "action": action_type,
        "file": file_name,
        "project": project,
        "user": user,
        "classification": classification,
        "recipient": recipient
    }
    data["file_log"].append(entry)
    save(data)
    
    action_icons = {
        "CREATED": "📄", "ACCESSED": "👁️", "SHARED": "🔗",
        "DOWNLOADED": "⬇️", "EDITED": "✏️", "DELETED": "🗑️", "TRANSFERRED": "📤"
    }
    icon = action_icons.get(action_type, "📋")
    return f"{icon} Logged: **{file_name}** {action_type.lower()} by {user} — {project} ({classification})"

def project_log(project, limit=10):
    """View file activity log for a project."""
    data = load()
    logs = [e for e in data.get("file_log", []) if e["project"] == project]
    logs.sort(key=lambda e: e["timestamp"], reverse=True)
    logs = logs[:limit]
    
    if not logs:
        return f"No file activity logged for **{project}**."
    
    action_icons = {
        "CREATED": "📄", "ACCESSED": "👁️", "SHARED": "🔗",
        "DOWNLOADED": "⬇️", "EDITED": "✏️", "DELETED": "🗑️", "TRANSFERRED": "📤"
    }
    
    lines = [f"**📋 File Activity Log — {project} (last {len(logs)} events):**"]
    for e in logs:
        icon = action_icons.get(e["action"], "📋")
        recipient_str = f" → {e['recipient']}" if e["recipient"] else ""
        lines.append(f"  {icon} {e['file']} — {e['action'].lower()}{recipient_str}")
        lines.append(f"    By: {e['user']} at {e['timestamp']} | Class: {e['classification']}")
    return "\n".join(lines)

def user_log(user, limit=5):
    """View file activity by user."""
    data = load()
    logs = [e for e in data.get("file_log", []) if e["user"] == user]
    logs.sort(key=lambda e: e["timestamp"], reverse=True)
    logs = logs[:limit]
    
    if not logs:
        return f"No file activity for **{user}**."
    
    action_icons = {
        "CREATED": "📄", "ACCESSED": "👁️", "SHARED": "🔗",
        "DOWNLOADED": "⬇️", "EDITED": "✏️", "DELETED": "🗑️", "TRANSFERRED": "📤"
    }
    
    lines = [f"**👤 File Activity — {user} (last {len(logs)} events):**"]
    for e in logs:
        icon = action_icons.get(e["action"], "📋")
        lines.append(f"  {icon} {e['file']} — {e['action'].lower()} on {e['project']} at {e['timestamp']}")
    return "\n".join(lines)

def recent_activity(limit=15):
    """View most recent file activity across all projects."""
    data = load()
    logs = data.get("file_log", [])
    logs.sort(key=lambda e: e["timestamp"], reverse=True)
    logs = logs[:limit]
    
    if not logs:
        return "No file activity logged."
    
    return project_log(None)  # Reuse project_log logic

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "log" and len(sys.argv) >= 5:
        user = sys.argv[5]
        classification = sys.argv[6] if len(sys.argv) > 6 else "UNCLASSIFIED"
        recipient = sys.argv[7] if len(sys.argv) > 7 else ""
        print(log_event(sys.argv[2], sys.argv[3], sys.argv[4], user, classification, recipient))
    elif cmd == "project" and len(sys.argv) >= 3:
        print(project_log(sys.argv[2]))
    elif cmd == "user" and len(sys.argv) >= 3:
        print(user_log(sys.argv[2]))
    elif cmd == "recent":
        print(recent_activity())
    else:
        print("Commands: log <CREATE/ACCESS/SHARE/EDIT/DELETE/TRANSFER> <file> <project> <user> [classification] [recipient] | project <name> | user <name> | recent")

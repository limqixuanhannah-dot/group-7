#!/usr/bin/env python3
"""SENTRY — Compliance Deadline Tracker"""
import json, sys
from datetime import datetime, timedelta

DATA_FILE = "/home/ubuntu/.openclaw/workspace/projects/sentry-systems.json"

def load():
    with open(DATA_FILE) as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_deadline(name, deadline_date, deadline_type, project, owner, notes=""):
    """Add a compliance deadline."""
    data = load()
    entry = {
        "id": f"comp-{len(data['compliance_deadlines']) + 1}",
        "name": name,
        "deadline": deadline_date,
        "type": deadline_type,
        "project": project,
        "owner": owner,
        "status": "PENDING",
        "notes": notes,
        "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    data["compliance_deadlines"].append(entry)
    save(data)
    return f"✅ Compliance deadline added: **{name}** due {deadline_date}"

def check_due():
    """Check for upcoming/overdue compliance deadlines."""
    data = load()
    now = datetime.utcnow()
    results = {"overdue": [], "due_soon": [], "upcoming": []}
    
    for d in data.get("compliance_deadlines", []):
        if d["status"] == "COMPLETE":
            continue
        try:
            due = datetime.strptime(d["deadline"], "%Y-%m-%d")
            days_left = (due - now).days
            if days_left < 0:
                results["overdue"].append(d)
            elif days_left <= 7:
                results["due_soon"].append(d)
            elif days_left <= 30:
                results["upcoming"].append(d)
        except:
            continue
    return results

def report():
    """Formatted compliance deadline report."""
    due = check_due()
    lines = []
    if due["overdue"]:
        lines.append(f"\n❌ **Overdue:**")
        for d in due["overdue"]:
            lines.append(f"  - {d['name']} ({d['type']}) — Project: {d['project']}, Owner: {d['owner']}")
    if due["due_soon"]:
        lines.append(f"\n⚠️ **Due within 7 days:**")
        for d in due["due_soon"]:
            lines.append(f"  - {d['name']} ({d['type']}) — Due: {d['deadline']}, Project: {d['project']}")
    if due["upcoming"]:
        lines.append(f"\nℹ️ **Upcoming (within 30 days):**")
        for d in due["upcoming"]:
            lines.append(f"  - {d['name']} ({d['type']}) — Due: {d['deadline']}")
    if not any(due.values()):
        lines.append("✅ No compliance deadlines due or overdue.")
    return "\n".join(lines)

def mark_complete(deadline_id):
    """Mark a compliance deadline as complete."""
    data = load()
    for d in data["compliance_deadlines"]:
        if d["id"] == deadline_id:
            d["status"] = "COMPLETE"
            d["completed_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            save(data)
            return f"✅ Marked '{d['name']}' as complete"
    return f"❌ Deadline '{deadline_id}' not found"

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "add" and len(sys.argv) >= 5:
        print(add_deadline(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else "", sys.argv[6] if len(sys.argv) > 6 else ""))
    elif cmd == "report":
        print(report())
    elif cmd == "complete" and len(sys.argv) >= 3:
        print(mark_complete(sys.argv[2]))
    else:
        print("Commands: add <name> <YYYY-MM-DD> <type> [project] [owner] | report | complete <id>")

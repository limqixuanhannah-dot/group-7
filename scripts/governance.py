#!/usr/bin/env python3
"""SENTRY — Meeting Action Item Tracker & Decision Log"""
import json, sys
from datetime import datetime, timezone, timedelta

DATA_FILE = "/home/ubuntu/.openclaw/workspace/projects/sentry-systems.json"

def load():
    with open(DATA_FILE) as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── Action Items ──

def add_action_item(project, description, owner, due_date="", priority="MEDIUM", source_meeting=""):
    """Create an action item from a meeting."""
    data = load()
    if "action_items" not in data:
        data["action_items"] = []
    item = {
        "id": f"ai-{len(data['action_items']) + 1}",
        "project": project,
        "description": description,
        "owner": owner,
        "due_date": due_date,
        "priority": priority,
        "source_meeting": source_meeting,
        "status": "PENDING",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    data["action_items"].append(item)
    save(data)
    
    icon = {"CRITICAL": "❌", "HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
    return f"{icon.get(priority, 'ℹ️')} Action item created: **{description}** → {owner} (due: {due_date if due_date else 'TBD'})"

def extract_from_text(project, text, default_owner="", default_due=""):
    """Extract action items from meeting summary text (simple NLP)."""
    lines = text.split("\n")
    action_items = []
    keywords = ["action item", "todo", "to do", "follow up", "follow-up", "need to", "must", "will", "deadline"]
    
    for line in lines:
        line_lower = line.lower().strip()
        for kw in keywords:
            if kw in line_lower:
                # Try to extract a due date
                due = default_due
                words = line.split()
                for i, w in enumerate(words):
                    # Simple date detection (YYYY-MM-DD or DD Month)
                    w_clean = w.strip(".,:;")
                    if len(w_clean) == 10 and w_clean[4] == "-":
                        try:
                            datetime.strptime(w_clean, "%Y-%m-%d")
                            due = w_clean
                        except:
                            pass
                
                item_text = line.strip("- *").strip()
                if len(item_text) > 5:
                    action_items.append((item_text, default_owner, due))
                break
    
    results = []
    for desc, owner, due in action_items:
        results.append(add_action_item(project, desc, owner, due))
    
    if not results:
        return "No action items detected in the text. Ensure each action item is on its own line with keywords like 'action item' or 'todo'."
    return "\n".join(results)

def my_items(user):
    """View action items assigned to a user."""
    data = load()
    items = data.get("action_items", [])
    user_items = [i for i in items if i["owner"] == user]
    
    if not user_items:
        return f"✅ No action items assigned to **{user}**."
    
    pending = [i for i in user_items if i["status"] == "PENDING"]
    in_progress = [i for i in user_items if i["status"] == "IN_PROGRESS"]
    complete = [i for i in user_items if i["status"] == "COMPLETE"]
    
    lines = [f"**📋 Action Items — {user}:**"]
    now = datetime.now(timezone.utc)
    
    for item in (pending + in_progress):
        if item["status"] == "PENDING":
            icon = {"CRITICAL": "❌", "HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
            lines.append(f"  {icon.get(item['priority'], 'ℹ️')} **{item['description']}** [{item['status']}]")
        else:
            lines.append(f"  🔧 **{item['description']}** [IN PROGRESS]")
        due_str = f" | Due: {item['due_date']}" if item["due_date"] else ""
        meeting_str = f" | Source: {item['source_meeting']}" if item["source_meeting"] else ""
        lines.append(f"    ID: {item['id']}{due_str}{meeting_str}")
        
        # Flag overdue
        if item["due_date"] and item["status"] != "COMPLETE":
            try:
                due = datetime.strptime(item["due_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if due < now:
                    lines.append(f"    ❌ **OVERDUE** (was due {item['due_date']})")
            except:
                pass
    
    if complete:
        lines.append(f"\n✅ **Completed ({len(complete)}):**")
        for item in complete:
            lines.append(f"  ✅ {item['description']}")
    
    return "\n".join(lines)

def update_status(item_id, status):
    """Update action item status."""
    data = load()
    for item in data.get("action_items", []):
        if item["id"] == item_id:
            item["status"] = status
            item["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            save(data)
            return f"✅ Action item **{item['description'][:40]}...** → **{status}**"
    return f"❌ Action item '{item_id}' not found"

# ── Decision Log ──

def log_decision(project, title, decision, rationale, context="", decision_by="", stakeholders=""):
    """Log a project decision for audit trail."""
    data = load()
    if "decisions" not in data:
        data["decisions"] = []
    entry = {
        "id": f"dec-{len(data['decisions']) + 1}",
        "project": project,
        "title": title,
        "decision": decision,
        "rationale": rationale,
        "context": context,
        "decision_by": decision_by,
        "stakeholders": stakeholders,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    data["decisions"].append(entry)
    save(data)
    return f"📝 Decision logged: **{title}** — {decision}"

def decision_log(project, limit=10):
    """View decision log for a project."""
    data = load()
    decisions = data.get("decisions", [])
    project_decisions = [d for d in decisions if d["project"] == project]
    project_decisions.sort(key=lambda d: d["timestamp"], reverse=True)
    project_decisions = project_decisions[:limit]
    
    if not project_decisions:
        return f"No decisions logged for **{project}**."
    
    lines = [f"**📜 Decision Log — {project} (last {len(project_decisions)}):**"]
    for d in project_decisions:
        lines.append(f"\n**{d['title']}**")
        lines.append(f"  Decision: {d['decision']}")
        lines.append(f"  Rationale: {d['rationale']}")
        if d["context"]:
            lines.append(f"  Context: {d['context']}")
        if d["decision_by"]:
            lines.append(f"  By: {d['decision_by']}")
        lines.append(f"  Timestamp: {d['timestamp']} | ID: {d['id']}")
    return "\n".join(lines)

def full_governance_report(project):
    """Combined governance report: action items + decisions."""
    data = load()
    lines = [f"**📋 Governance Report — {project}**"]
    
    # Action items
    items = [i for i in data.get("action_items", []) if i["project"] == project and i["status"] != "COMPLETE"]
    if items:
        lines.append(f"\n**Open Action Items ({len(items)}):**")
        for i in items:
            icon = {"CRITICAL": "❌", "HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
            lines.append(f"  {icon.get(i['priority'], 'ℹ️')} {i['description']} — {i['owner']} (due: {i['due_date'] or 'TBD'})")
    else:
        lines.append(f"\n✅ No open action items.")
    
    # Decisions
    decs = [d for d in data.get("decisions", []) if d["project"] == project]
    decs = decs[-5:]
    if decs:
        lines.append(f"\n**Recent Decisions ({len(decs)}):**")
        for d in decs:
            lines.append(f"  📝 {d['title']} — {d['decision_by'] or 'unknown'} at {d['timestamp']}")
    
    return "\n".join(lines)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "add-action" and len(sys.argv) >= 4:
        print(add_action_item(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else ""))
    elif cmd == "extract" and len(sys.argv) >= 4:
        print(extract_from_text(sys.argv[2], sys.argv[3]))
    elif cmd == "my-items" and len(sys.argv) >= 3:
        print(my_items(sys.argv[2]))
    elif cmd == "status" and len(sys.argv) >= 4:
        print(update_status(sys.argv[2], sys.argv[3].upper()))
    elif cmd == "log-decision" and len(sys.argv) >= 5:
        print(log_decision(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else ""))
    elif cmd == "decisions" and len(sys.argv) >= 3:
        print(decision_log(sys.argv[2]))
    elif cmd == "governance" and len(sys.argv) >= 3:
        print(full_governance_report(sys.argv[2]))
    else:
        print("Commands: add-action <project> <desc> [owner] [due_date] [priority] [source_meeting] | extract <project> <text> | my-items <user> | status <id> <PENDING|IN_PROGRESS|COMPLETE> | log-decision <project> <title> <decision> [rationale] [context] [decision_by] | decisions <project> | governance <project>")

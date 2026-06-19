#!/usr/bin/env python3
"""SENTRY — Incident Response Drills Scheduler & Scorer"""
import json, sys
from datetime import datetime

DATA_FILE = "/home/ubuntu/.openclaw/workspace/projects/sentry-systems.json"

def load():
    with open(DATA_FILE) as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def schedule_drill(name, drill_type, scheduled_date, project, owner, scenario=""):
    """Schedule a tabletop/IR drill."""
    data = load()
    drill = {
        "id": f"drill-{len(data['incident_response_drills']) + 1}",
        "name": name,
        "type": drill_type,
        "scheduled_date": scheduled_date,
        "project": project,
        "owner": owner,
        "scenario": scenario,
        "status": "SCHEDULED",
        "score": None,
        "participants": [],
        "findings": [],
        "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    data["incident_response_drills"].append(drill)
    save(data)
    return f"✅ Drill scheduled: **{name}** ({drill_type}) on {scheduled_date}"

def record_result(drill_id, score, findings=""):
    """Record drill results and score."""
    data = load()
    for d in data["incident_response_drills"]:
        if d["id"] == drill_id:
            d["status"] = "COMPLETE"
            d["score"] = score
            if findings:
                d["findings"] = [f.strip() for f in findings.split(",")]
            d["completed_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            save(data)
            icon = "✅" if score >= 80 else ("⚠️" if score >= 50 else "❌")
            return f"{icon} Drill **{d['name']}** completed — Score: {score}/100"
    return f"❌ Drill '{drill_id}' not found"

def add_participant(drill_id, username):
    """Add a participant to a drill."""
    data = load()
    for d in data["incident_response_drills"]:
        if d["id"] == drill_id:
            if username not in d["participants"]:
                d["participants"].append(username)
                save(data)
                return f"✅ Added {username} to drill '{d['name']}'"
            return f"ℹ️ {username} already registered"
    return f"❌ Drill '{drill_id}' not found"

def upcoming():
    """List upcoming drills."""
    data = load()
    now = datetime.utcnow()
    upcoming_list = []
    for d in data.get("incident_response_drills", []):
        if d["status"] == "SCHEDULED":
            upcoming_list.append(d)
    return upcoming_list

def report():
    """Drill status report."""
    data = load()
    lines = []
    
    upcoming_list = upcoming()
    if upcoming_list:
        lines.append(f"\n📋 **Upcoming Drills ({len(upcoming_list)}):**")
        for d in upcoming_list:
            lines.append(f"  - {d['name']} ({d['type']}) — {d['scheduled_date']}, Project: {d['project']}")
    
    completed = [d for d in data.get("incident_response_drills", []) if d["status"] == "COMPLETE"]
    if completed:
        lines.append(f"\n✅ **Completed Drills ({len(completed)}):**")
        for d in completed:
            icon = "✅" if d.get("score", 0) >= 80 else ("⚠️" if d.get("score", 0) >= 50 else "❌")
            lines.append(f"  {icon} {d['name']} — Score: {d.get('score', 'N/A')}/100")
    
    if not completed and not upcoming_list:
        lines.append("No drills scheduled.")
    
    return "\n".join(lines)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "schedule" and len(sys.argv) >= 5:
        print(schedule_drill(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else "", sys.argv[6] if len(sys.argv) > 6 else ""))
    elif cmd == "result" and len(sys.argv) >= 4:
        print(record_result(sys.argv[2], int(sys.argv[3]), sys.argv[4] if len(sys.argv) > 4 else ""))
    elif cmd == "add-participant" and len(sys.argv) >= 4:
        print(add_participant(sys.argv[2], sys.argv[3]))
    elif cmd == "report":
        print(report())
    else:
        print("Commands: schedule <name> <type> <YYYY-MM-DD> [project] [owner] | result <id> <score> [findings] | add-participant <id> <user> | report")

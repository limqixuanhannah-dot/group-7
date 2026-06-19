#!/usr/bin/env python3
"""SENTRY — Vendor Security Posture Tracker"""
import json, sys
from datetime import datetime

DATA_FILE = "/home/ubuntu/.openclaw/workspace/projects/sentry-systems.json"

def load():
    with open(DATA_FILE) as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_vendor(name, scope, clearance_expiry, assessment_status, projects_attached="", notes=""):
    """Register a third-party vendor/contractor."""
    data = load()
    vendor = {
        "id": f"v-{len(data['vendors']) + 1}",
        "name": name,
        "scope": scope,
        "clearance_expiry": clearance_expiry,
        "assessment_status": assessment_status,
        "projects": [p.strip() for p in projects_attached.split(",") if p.strip()],
        "incidents": [],
        "notes": notes,
        "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    data["vendors"].append(vendor)
    save(data)
    status_icon = {"PASS": "✅", "PENDING": "⏳", "FAIL": "❌", "EXPIRED": "❌"}
    return f"{status_icon.get(assessment_status, 'ℹ️')} Vendor **{name}** registered — Assessment: {assessment_status}"

def log_incident(vendor_id, description, severity="MEDIUM"):
    """Log a security incident for a vendor."""
    data = load()
    for v in data["vendors"]:
        if v["id"] == vendor_id:
            incident = {
                "date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "description": description,
                "severity": severity
            }
            v["incidents"].append(incident)
            save(data)
            sev_icon = {"HIGH": "❌", "MEDIUM": "⚠️", "LOW": "ℹ️"}
            return f"{sev_icon.get(severity, '⚠️')} Incident logged for **{v['name']}**: {description}"
    return f"❌ Vendor '{vendor_id}' not found"

def flag_expired():
    """Check which vendors have expired clearances."""
    data = load()
    now = datetime.utcnow()
    flagged = []
    for v in data.get("vendors", []):
        try:
            expiry = datetime.strptime(v["clearance_expiry"], "%Y-%m-%d")
            if expiry < now:
                flagged.append(v)
        except:
            continue
    return flagged

def report():
    """Vendor posture summary."""
    data = load()
    lines = []
    expired = flag_expired()
    
    if expired:
        lines.append(f"\n❌ **Expired clearances:**")
        for v in expired:
            lines.append(f"  - {v['name']} — expired {v['clearance_expiry']}, status: {v['assessment_status']}")
            if v.get("incidents"):
                for inc in v["incidents"]:
                    lines.append(f"    - Incident ({inc['severity']}): {inc['description']}")
    
    active = [v for v in data.get("vendors", []) if v not in expired]
    if active:
        lines.append(f"\n✅ **Active vendors ({len(active)}):**")
        for v in active:
            icon = "✅" if v["assessment_status"] == "PASS" else ("⚠️" if v["assessment_status"] == "PENDING" else "❌")
            lines.append(f"  {icon} {v['name']} — {v['scope']}, clearance: {v['clearance_expiry']}")
    
    if not data.get("vendors"):
        lines.append("No vendors registered.")
    
    return "\n".join(lines)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "add" and len(sys.argv) >= 4:
        print(add_vendor(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "", sys.argv[5] if len(sys.argv) > 5 else "PENDING", sys.argv[6] if len(sys.argv) > 6 else ""))
    elif cmd == "incident" and len(sys.argv) >= 4:
        print(log_incident(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "MEDIUM"))
    elif cmd == "report":
        print(report())
    else:
        print("Commands: add <name> <scope> [clearance_expiry] [assessment_status] [projects] | incident <id> <description> [severity] | report")

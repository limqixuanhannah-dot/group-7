#!/usr/bin/env python3
"""SENTRY — Threat Landscape Briefings & Vulnerability Disclosure Triage"""
import json, sys
from datetime import datetime

DATA_FILE = "/home/ubuntu/.openclaw/workspace/projects/sentry-systems.json"

def load():
    with open(DATA_FILE) as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── Threat Briefings ──

def add_briefing(project, threat_type, description, severity, source="", recommended_action=""):
    """Add a threat landscape briefing entry linked to a project."""
    data = load()
    briefing = {
        "id": f"threat-{len(data['threat_briefings']) + 1}",
        "project": project,
        "threat_type": threat_type,
        "description": description,
        "severity": severity,
        "source": source,
        "recommended_action": recommended_action,
        "status": "ACTIVE",
        "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    data["threat_briefings"].append(briefing)
    save(data)
    icon = {"CRITICAL": "❌", "HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
    return f"{icon.get(severity, 'ℹ️')} Threat briefing added for **{project}**: {description}"

def correlate_threats(project):
    """Get all active threats relevant to a project."""
    data = load()
    return [b for b in data.get("threat_briefings", []) if b["project"] == project and b["status"] == "ACTIVE"]

def briefing_report(project=None):
    """Formatted threat briefing report."""
    data = load()
    briefings = data.get("threat_briefings", [])
    if project:
        briefings = [b for b in briefings if b["project"] == project]
    
    if not briefings:
        return "✅ No active threats logged." if not project else f"✅ No active threats for **{project}**."
    
    active = [b for b in briefings if b["status"] == "ACTIVE"]
    resolved = [b for b in briefings if b["status"] == "RESOLVED"]
    
    lines = []
    if active:
        icon_map = {"CRITICAL": "❌", "HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
        lines.append(f"**⚠️ Active Threats ({len(active)}):**")
        for b in active:
            lines.append(f"  {icon_map.get(b['severity'], 'ℹ️')} {b['threat_type']} — **{b['project']}**")
            lines.append(f"    {b['description']}")
            if b['recommended_action']:
                lines.append(f"    Action: {b['recommended_action']}")
    
    if resolved:
        lines.append(f"\n✅ **Resolved ({len(resolved)}):**")
        for b in resolved:
            lines.append(f"  - {b['threat_type']} ({b['project']})")
    
    return "\n".join(lines)

def resolve_threat(threat_id):
    """Mark a threat as resolved."""
    data = load()
    for b in data["threat_briefings"]:
        if b["id"] == threat_id:
            b["status"] = "RESOLVED"
            b["resolved_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            save(data)
            return f"✅ Threat '{b['threat_type']}' marked as resolved"
    return f"❌ Threat '{threat_id}' not found"

# ── Vulnerability Disclosure Triage ──

def report_vulnerability(project, vuln_name, severity, affected_asset="", description="", reporter=""):
    """Log a vulnerability disclosure for a project."""
    data = load()
    vuln = {
        "id": f"vuln-{len(data['vulnerability_disclosures']) + 1}",
        "project": project,
        "name": vuln_name,
        "severity": severity,
        "affected_asset": affected_asset,
        "description": description,
        "reporter": reporter,
        "status": "PENDING",
        "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    data["vulnerability_disclosures"].append(vuln)
    save(data)
    icon = {"CRITICAL": "❌", "HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
    return f"{icon.get(severity, 'ℹ️')} Vulnerability **{vuln_name}** reported — {severity} on **{project}**"

def triage_table(project=None):
    """Display vulnerability triage table."""
    data = load()
    vulns = data.get("vulnerability_disclosures", [])
    if project:
        vulns = [v for v in vulns if v["project"] == project]
    
    if not vulns:
        return "✅ No vulnerabilities reported." if not project else f"✅ No vulnerabilities for **{project}**."
    
    pending = [v for v in vulns if v["status"] == "PENDING"]
    in_progress = [v for v in vulns if v["status"] == "IN_PROGRESS"]
    patched = [v for v in vulns if v["status"] == "PATCHED"]
    
    lines = []
    icon_map = {"CRITICAL": "❌", "HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
    
    if pending:
        lines.append(f"**⚠️ Pending triage ({len(pending)}):**")
        for v in pending:
            lines.append(f"  {icon_map.get(v['severity'], 'ℹ️')} **{v['name']}** — {v['severity']} — {v['project']} — {v['affected_asset']}")
    
    if in_progress:
        lines.append(f"\n**🔧 In progress ({len(in_progress)}):**")
        for v in in_progress:
            lines.append(f"  {v['name']} — {v['project']} — {v['affected_asset']}")
    
    if patched:
        lines.append(f"\n✅ **Patched ({len(patched)}):**")
        for v in patched:
            lines.append(f"  {v['name']} — {v['project']}")
    
    return "\n".join(lines)

def update_vuln_status(vuln_id, status):
    """Update vulnerability status."""
    data = load()
    for v in data["vulnerability_disclosures"]:
        if v["id"] == vuln_id:
            v["status"] = status
            v["updated_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            save(data)
            return f"✅ {v['name']} → **{status}**"
    return f"❌ Vulnerability '{vuln_id}' not found"

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "add-threat" and len(sys.argv) >= 5:
        print(add_briefing(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else "MEDIUM"))
    elif cmd == "threats":
        print(briefing_report(sys.argv[2] if len(sys.argv) > 2 else None))
    elif cmd == "resolve-threat" and len(sys.argv) >= 3:
        print(resolve_threat(sys.argv[2]))
    elif cmd == "report-vuln" and len(sys.argv) >= 4:
        print(report_vulnerability(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "MEDIUM"))
    elif cmd == "vulns":
        print(triage_table(sys.argv[2] if len(sys.argv) > 2 else None))
    elif cmd == "vuln-status" and len(sys.argv) >= 4:
        print(update_vuln_status(sys.argv[2], sys.argv[3].upper()))
    else:
        print("Commands: add-threat <project> <type> <desc> [severity] | threats [project] | resolve-threat <id> | report-vuln <project> <name> [severity] | vulns [project] | vuln-status <id> <PENDING|IN_PROGRESS|PATCHED>")

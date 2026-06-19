#!/usr/bin/env python3
"""SENTRY — Hardware/Software Asset Registry"""
import json, sys
from datetime import datetime, timezone

DATA_FILE = "/home/ubuntu/.openclaw/workspace/projects/sentry-systems.json"

def load():
    with open(DATA_FILE) as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def register_asset(name, asset_type, project, owner, expiry="", vendor="", serial="", notes=""):
    """Register a hardware or software asset."""
    data = load()
    if "assets" not in data:
        data["assets"] = []
    asset = {
        "id": f"asset-{len(data['assets']) + 1}",
        "name": name,
        "type": asset_type,
        "project": project,
        "owner": owner,
        "expiry": expiry,
        "vendor": vendor,
        "serial": serial,
        "status": "ACTIVE",
        "notes": notes,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    data["assets"].append(asset)
    save(data)
    return f"✅ Asset **{name}** ({asset_type}) registered for project **{project}**"

def list_by_project(project):
    """List all assets for a project."""
    data = load()
    assets = data.get("assets", [])
    project_assets = [a for a in assets if a["project"] == project]
    if not project_assets:
        return f"No assets registered for **{project}**."
    lines = [f"**📦 Assets — {project}:**"]
    for a in project_assets:
        expiry_str = f" | Expires: {a['expiry']}" if a["expiry"] else ""
        vendor_str = f" | Vendor: {a['vendor']}" if a["vendor"] else ""
        status_icon = "✅" if a["status"] == "ACTIVE" else ("❌" if a["status"] == "RETIRED" else "⚠️")
        lines.append(f"  {status_icon} **{a['name']}** ({a['type']}){expiry_str}{vendor_str}")
        lines.append(f"    Owner: {a['owner']} | ID: {a['id']}")
    return "\n".join(lines)

def flag_expired():
    """Flag assets with expired licenses."""
    data = load()
    now = datetime.now(timezone.utc)
    flagged = []
    for a in data.get("assets", []):
        if a["expiry"]:
            try:
                expiry = datetime.strptime(a["expiry"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if expiry < now and a["status"] == "ACTIVE":
                    flagged.append(a)
            except:
                continue
    return flagged

def report():
    """Full asset report."""
    data = load()
    assets = data.get("assets", [])
    expired = flag_expired()
    
    lines = []
    if expired:
        lines.append(f"❌ **Expired assets ({len(expired)}):**")
        for a in expired:
            lines.append(f"  - {a['name']} ({a['type']}) — {a['project']} — expired {a['expiry']}")
    
    active = [a for a in assets if a["status"] == "ACTIVE"]
    if active:
        lines.append(f"\n✅ **Active assets ({len(active)}):**")
        by_project = {}
        for a in active:
            by_project.setdefault(a["project"], []).append(a)
        for proj, items in sorted(by_project.items()):
            lines.append(f"  **{proj}:** {', '.join([i['name'] for i in items])}")
    
    if not assets:
        lines.append("No assets registered.")
    
    return "\n".join(lines)

def retire_asset(asset_id):
    """Mark asset as retired."""
    data = load()
    for a in data.get("assets", []):
        if a["id"] == asset_id:
            a["status"] = "RETIRED"
            a["retired_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            save(data)
            return f"✅ Asset **{a['name']}** marked as RETIRED"
    return f"❌ Asset '{asset_id}' not found"

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "add" and len(sys.argv) >= 4:
        print(register_asset(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "general", sys.argv[5] if len(sys.argv) > 5 else ""))
    elif cmd == "list" and len(sys.argv) >= 3:
        print(list_by_project(sys.argv[2]))
    elif cmd == "report":
        print(report())
    elif cmd == "retire" and len(sys.argv) >= 3:
        print(retire_asset(sys.argv[2]))
    else:
        print("Commands: add <name> <type> [project] [owner] | list <project> | report | retire <id>")

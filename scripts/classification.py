#!/usr/bin/env python3
"""SENTRY — Security Classification Tagging & Access Control"""
import json, os, sys

DATA_FILE = "/home/ubuntu/.openclaw/workspace/projects/sentry-systems.json"
PROJECTS_DIR = "/home/ubuntu/.openclaw/workspace/projects"
TRACKER_FILE = f"{PROJECTS_DIR}/tracker.json"

LEVELS = {
    "UNCLASSIFIED": 0,
    "RESTRICTED": 1,
    "CONFIDENTIAL": 2,
    "SECRET": 3
}

def load():
    with open(DATA_FILE) as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def tag_project(project_name, level, owner):
    """Tag a project with a classification level."""
    data = load()
    data["classification"]["access_rules"][project_name] = {
        "level": level,
        "level_rank": LEVELS.get(level, 0),
        "owner": owner,
        "collaborators": [],
        "tagged_at": "2026-06-19T01:38:00Z"
    }
    save(data)
    # Add header to project file if exists
    for root, dirs, files in os.walk(PROJECTS_DIR):
        for f in files:
            if project_name in f:
                path = os.path.join(root, f)
                with open(path) as pf:
                    content = pf.read()
                if "**CLASSIFICATION**" not in content:
                    header = f"\n\n---\n**CLASSIFICATION:** {level}\n**OWNER:** {owner}\n**ACCESS:** Owner + authorised collaborators only\n---\n"
                    with open(path, "w") as pf:
                        pf.write(content + header if content.endswith("\n") else content + "\n" + header)
                break
    return f"✅ Project '{project_name}' tagged as **{level}**"

def add_collaborator(project_name, username, level="MEMBER"):
    """Add a collaborator to a classified project."""
    data = load()
    if project_name in data["classification"]["access_rules"]:
        collab_list = data["classification"]["access_rules"][project_name].get("collaborators", [])
        if username not in collab_list:
            collab_list.append({"user": username, "role": level, "added_at": "2026-06-19T01:38:00Z"})
            data["classification"]["access_rules"][project_name]["collaborators"] = collab_list
            save(data)
            return f"✅ Added {username} as {level} to {project_name}"
        return f"ℹ️ {username} already a collaborator on {project_name}"
    return f"❌ Project '{project_name}' not found"

def check_access(project_name, username):
    """Check if a user can access a project."""
    data = load()
    if project_name in data["classification"]["access_rules"]:
        rule = data["classification"]["access_rules"][project_name]
        if rule["owner"] == username:
            return True, "Owner — full access"
        for c in rule.get("collaborators", []):
            if c["user"] == username:
                return True, f"Collaborator ({c['role']})"
        return False, f"Access denied — {rule['level']} project. Not an authorised collaborator."
    return True, "No classification set — open access"

def list_classified():
    """List all classified projects."""
    data = load()
    rules = data["classification"].get("access_rules", {})
    if not rules:
        return "No classified projects."
    output = []
    for name, rule in sorted(rules.items()):
        collabs = ", ".join([c["user"] for c in rule.get("collaborators", [])]) or "none"
        output.append(f"**{name}** — {rule['level']} | Owner: {rule['owner']} | Collaborators: {collabs}")
    return "\n".join(output)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "tag" and len(sys.argv) >= 4:
        print(tag_project(sys.argv[2], sys.argv[3].upper(), sys.argv[4] if len(sys.argv) > 4 else "unknown"))
    elif cmd == "add-collab" and len(sys.argv) >= 4:
        print(add_collaborator(sys.argv[2], sys.argv[3]))
    elif cmd == "check" and len(sys.argv) >= 4:
        ok, msg = check_access(sys.argv[2], sys.argv[3])
        print(f"{'✅' if ok else '❌'} {msg}")
    elif cmd == "list":
        print(list_classified())
    else:
        print("Commands: tag <project> <LEVEL> [owner] | add-collab <project> <user> | check <project> <user> | list")

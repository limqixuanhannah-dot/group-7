#!/usr/bin/env python3
"""SENTRY — Crisis Comms Templates & Risk Scoring"""
import json, sys
from datetime import datetime

DATA_FILE = "/home/ubuntu/.openclaw/workspace/projects/sentry-systems.json"

def load():
    with open(DATA_FILE) as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── Crisis Templates ──

TEMPLATES = {
    "breach_escalation": {
        "name": "Breach Escalation Notification",
        "context": "When a confirmed data breach or security incident is detected",
        "fields": {
            "subject": "[CRITICAL] Security Incident Report — {incident_name}",
            "severity": "{severity}",
            "detected_at": "{timestamp}",
            "affected_systems": "{affected_systems}",
            "data_classes_compromised": "{data_types}",
            "current_status": "{status}",
            "action_taken": "1. Isolated affected systems. 2. Engaged incident response team. 3. Contacting {vendor} security lead.",
            "next_steps": "1. Forensic analysis — {team} 2. Impact assessment due by {deadline} 3. Stakeholder notification pending assessment",
            "escalation_contact": "{escalation_contact}"
        }
    },
    "system_outage": {
        "name": "System Outage Advisory",
        "context": "When a critical project system or service is unavailable",
        "fields": {
            "subject": "[HIGH] Service Outage — {system_name}",
            "system": "{system_name}",
            "outage_start": "{timestamp}",
            "impact": "Project {project_name} — {impact_description}",
            "root_cause": "{root_cause} (investigating)",
            "eta": "{estimated_restoration}",
            "workaround": "{workaround}"
        }
    },
    "operational_disruption": {
        "name": "Operational Disruption Notice",
        "context": "When scheduled operations are delayed or disrupted (non-security)",
        "fields": {
            "subject": "Operational Update — {project_name}",
            "event": "{disruption_event}",
            "impact": "Timeline impact: {delay_days} days",
            "mitigation": "{mitigation_plan}",
            "point_of_contact": "{poc}"
        }
    }
}

def list_templates():
    """List all available crisis templates."""
    lines = ["📋 **Crisis Comms Templates:**"]
    for key, t in TEMPLATES.items():
        lines.append(f"  **{t['name']}** — {t['context']}")
        lines.append(f"    Key fields: {', '.join(t['fields'].keys())}")
    return "\n".join(lines)

def generate_template(template_key, values):
    """Generate a filled template with provided values."""
    if template_key not in TEMPLATES:
        return f"❌ Template '{template_key}' not found. Available: {', '.join(TEMPLATES.keys())}"
    
    t = TEMPLATES[template_key]
    filled = t['fields'].copy()
    for key, val in values.items():
        placeholder = "{" + key + "}"
        for fk in filled:
            filled[fk] = filled[fk].replace(placeholder, val)
    
    lines = [f"**{t['name']}**"]
    for fk, fv in filled.items():
        lines.append(f"  {fk.replace('_', ' ').title()}: {fv}")
    return "\n".join(lines)

# ── Risk Scoring ──

def set_risk(project_name, sensitivity=5, third_party_dependency=5, security_findings=5, timeline_pressure=5):
    """Set risk scores for a project."""
    data = load()
    composite = round((sensitivity * 0.3 + third_party_dependency * 0.2 + security_findings * 0.3 + timeline_pressure * 0.2), 1)
    
    if "risk_scores" not in data:
        data["risk_scores"] = {}
    
    data["risk_scores"][project_name] = {
        "data_sensitivity": sensitivity,
        "third_party_dependency": third_party_dependency,
        "security_findings": security_findings,
        "timeline_pressure": timeline_pressure,
        "composite_risk": composite,
        "band": "CRITICAL" if composite >= 8 else ("HIGH" if composite >= 6 else ("MEDIUM" if composite >= 4 else "LOW")),
        "updated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    save(data)
    
    r = data["risk_scores"][project_name]
    icon = {"CRITICAL": "❌", "HIGH": "⚠️", "MEDIUM": "📊", "LOW": "✅"}
    return f"{icon[r['band']]} Risk score set for **{project_name}**: {composite}/10 — **{r['band']}**"

def risk_summary():
    """Display risk dashboard for all projects."""
    data = load()
    scores = data.get("risk_scores", {})
    if not scores:
        return "No risk scores configured."
    
    lines = ["**📊 Risk Dashboard:**"]
    for name, r in sorted(scores.items(), key=lambda x: x[1]["composite_risk"], reverse=True):
        icon = {"CRITICAL": "❌", "HIGH": "⚠️", "MEDIUM": "📊", "LOW": "✅"}
        lines.append(f"  {icon[r['band']]} **{name}** — {r['composite_risk']}/10 ({r['band']})")
        lines.append(f"    Data sensitivity: {r['data_sensitivity']} | Third-party: {r['third_party_dependency']} | Security: {r['security_findings']} | Timeline: {r['timeline_pressure']}")
    return "\n".join(lines)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "templates":
        print(list_templates())
    elif cmd == "generate" and len(sys.argv) >= 4:
        values = {}
        for pair in sys.argv[3:]:
            if "=" in pair:
                k, v = pair.split("=", 1)
                values[k] = v
        print(generate_template(sys.argv[2], values))
    elif cmd == "risk-set" and len(sys.argv) >= 3:
        kwargs = {"sensitivity": 5, "third_party_dependency": 5, "security_findings": 5, "timeline_pressure": 5}
        for pair in sys.argv[3:]:
            if "=" in pair:
                k, v = pair.split("=", 1)
                kwargs[k] = int(v)
        print(set_risk(sys.argv[2], **kwargs))
    elif cmd == "risk-summary":
        print(risk_summary())
    else:
        print("Commands: templates | generate <key> [field=value] | risk-set <project> [sensitivity= N third_party_dependency= N security_findings= N timeline_pressure=N] | risk-summary")

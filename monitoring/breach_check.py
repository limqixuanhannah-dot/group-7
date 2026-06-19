#!/usr/bin/env python3
"""
SENTRY Hourly Breach & News Monitor
Checks HaveIBeenPwned for new breaches, fetches relevant news.
Outputs JSON with new findings for Discord delivery.
"""

import json
import os
import urllib.request
import urllib.error
import sys
from datetime import datetime, timezone, timedelta

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
STATE_PATH = os.path.join(os.path.dirname(__file__), "breach_state.json")
USER_AGENT = "DarwinSENTRY/1.0 (Hannah's ops agent)"

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"known_breaches": [], "last_check": None}

def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

def fetch_json(url, api_key=None):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    if api_key:
        req.add_header("hibp-api-key", api_key)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []
        print(f"  HTTP {e.code} for {url}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  Error: {e}", file=sys.stderr)
        return None

def check_hibp_domain_breaches(domains, known_breach_names, api_key=""):
    """Check all known HIBP breaches for domain matches."""
    new_findings = []
    
    all_breaches = fetch_json("https://haveibeenpwned.com/api/v3/breaches", api_key)
    if all_breaches is None:
        return new_findings
    
    for domain in domains:
        if not domain.strip():
            continue
        domain_lower = domain.lower().strip()
        matches = [b for b in all_breaches if b.get("Domain", "").lower() == domain_lower]
        
        for breach in matches:
            if breach["Name"] not in known_breach_names:
                new_findings.append({
                    "type": "breach_domain",
                    "domain": domain,
                    "name": breach["Name"],
                    "title": breach.get("Title", breach["Name"]),
                    "date": breach.get("BreachDate", "unknown"),
                    "data_classes": breach.get("DataClasses", []),
                    "description": breach.get("Description", "")[:500]
                })
                known_breach_names.add(breach["Name"])
    
    return new_findings

def check_hibp_email_breaches(emails, known_breach_names, api_key=""):
    """Check specific email addresses."""
    new_findings = []
    
    for email in emails:
        if not email.strip():
            continue
        breaches = fetch_json(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{email.strip()}?truncateResponse=false",
            api_key
        )
        if breaches is None:
            continue
        
        for breach in breaches:
            if breach["Name"] not in known_breach_names:
                new_findings.append({
                    "type": "breach_email",
                    "email": email,
                    "name": breach["Name"],
                    "title": breach.get("Title", breach["Name"]),
                    "date": breach.get("BreachDate", "unknown"),
                    "data_classes": breach.get("DataClasses", []),
                    "description": breach.get("Description", "")[:500]
                })
                known_breach_names.add(breach["Name"])
    
    return new_findings

def fetch_news(topics):
    """Fetch recent cyber security / project news."""
    new_findings = []
    for topic in topics:
        if not topic.strip():
            continue
        # Use Google News RSS for simplicity - this is a lightweight check
        query = urllib.request.quote(f"{topic} cyber security")
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        # For now, we'll note that news fetching requires web_search tool
        # This is handled in the cron agent turn directly
        pass
    return new_findings

def is_within_recency(breach_date_str, max_days=7):
    """Check if a breach date is within the recency window."""
    if not breach_date_str or breach_date_str == "unknown":
        return True  # if date unknown, report it (better safe than sorry)
    try:
        breach_date = datetime.strptime(breach_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        age = now - breach_date
        return age.days <= max_days
    except ValueError:
        return True  # if we can't parse, report it


def assess_severity(finding):
    """Assign colour-coded severity to a finding.
    Returns (colour_label, reason).
    """
    data_classes = finding.get("data_classes", [])
    
    # HIGH-SENSITIVITY data classes = RED
    critical_data = {
        "Passwords", "Password hashes", "Credit cards", "Financial data",
        "Bank account numbers", "Payment history", "Government IDs",
        "National ID", "Passport numbers", "Social Security numbers",
        "Security questions and answers", "Phone numbers"
    }
    
    if any(d in critical_data for d in data_classes):
        return "🔴", "CRITICAL — sensitive data exposed (passwords, financial, or government IDs)"
    
    # MODERATE-SENSITIVITY = AMBER
    if any(d in {"Email addresses", "IP addresses", "Physical addresses",
                 "Names", "Dates of birth", "Usernames"} for d in data_classes):
        return "🟠", "HIGH — personal identifiable information exposed"
    
    # Public website data or unknown = YELLOW
    return "🟡", "MEDIUM — low-sensitivity or unspecified data exposure"


def filter_by_recency(findings, max_days=7):
    """Filter out findings older than max_days."""
    filtered = []
    for f in findings:
        if is_within_recency(f.get("date", ""), max_days):
            filtered.append(f)
    return filtered


def format_discord_message(findings, recency_days=7):
    """Format findings for Discord #group-7 with colour-coded severity."""
    if not findings:
        return None
    
    # Apply recency filter
    current = filter_by_recency(findings, recency_days)
    if not current:
        return None  # all findings were old, nothing to report
    
    lines = []
    has_breach = any(f["type"].startswith("breach") for f in current)
    
    for f in current:
        colour, severity_text = assess_severity(f)
        
        if f["type"] == "breach_domain":
            lines.append(f"{colour} **BREACH DETECTED — {f['domain']}**")
            lines.append(f"**Severity:** {severity_text}")
            lines.append(f"**Breach:** {f['title']}")
            lines.append(f"**Date:** {f['date']}")
            if f.get("data_classes"):
                lines.append(f"**Data exposed:** {', '.join(f['data_classes'])}")
            if f.get("description"):
                lines.append(f"**Summary:** {f['description'][:300]}...")
            lines.append("")
        
        elif f["type"] == "breach_email":
            lines.append(f"{colour} **ACCOUNT BREACHED — {f['email']}**")
            lines.append(f"**Severity:** {severity_text}")
            lines.append(f"**Breach:** {f['title']}")
            lines.append(f"**Date:** {f['date']}")
            if f.get("data_classes"):
                lines.append(f"**Data exposed:** {', '.join(f['data_classes'])}")
            lines.append("")
    
    if not has_breach:
        return None
    
    header = "SENTRY Hourly Scan — BREACH ALERT\n\n"
    return header + "\n".join(lines)

def main():
    config = load_config()
    state = load_state()
    
    known_names = set(b.get("name", "") for b in state.get("known_breaches", []))
    
    domain_targets = config.get("hibp", {}).get("domains", [])
    email_targets = config.get("hibp", {}).get("emails", [])
    api_key = config.get("hibp", {}).get("api_key", "")
    
    findings = []
    
    if domain_targets:
        findings.extend(check_hibp_domain_breaches(domain_targets, known_names, api_key))
    
    if email_targets:
        findings.extend(check_hibp_email_breaches(email_targets, known_names, api_key))
    
    # Update state
    state["known_breaches"] = [{"name": n} for n in known_names]
    state["last_check"] = datetime.now(timezone.utc).isoformat()
    save_state(state)
    
    # Apply recency filter from config
    recency_days = config.get("recency", {}).get("max_age_days", 7)
    recency_enabled = config.get("recency", {}).get("enabled", True)
    
    if recency_enabled:
        original_count = len(findings)
        findings = filter_by_recency(findings, recency_days)
        if original_count > len(findings):
            print(f"  Filtered {original_count - len(findings)} old findings (>{recency_days} days)", file=sys.stderr)
    
    # Output findings as JSON for the cron job to process
    result = {
        "timestamp": state["last_check"],
        "new_findings": findings,
        "total_monitored_domains": len(domain_targets),
        "total_monitored_emails": len(email_targets),
        "recency_filter_days": recency_days if recency_enabled else None
    }
    
    print(json.dumps(result, indent=2))
    
    # Also print formatted Discord message if there are findings
    discord_msg = format_discord_message(findings, recency_days)
    if discord_msg:
        print(f"\n---DISCORD_MESSAGE_START---\n{discord_msg}\n---DISCORD_MESSAGE_END---", file=sys.stderr)

if __name__ == "__main__":
    main()

#!/bin/bash
# SENTRY Breach Monitor — checks Have I Been Pwned for new breaches
# Outputs JSON with new breaches (PwnCount >= 1M) or empty array

STATE_FILE="/home/ubuntu/.openclaw/workspace/breach-monitor-state.json"
TMP_FILE="/tmp/breach-check-$$.json"

# Fetch all breaches
curl -s "https://haveibeenpwned.com/api/v3/breaches" > "$TMP_FILE" 2>/dev/null

python3 << PYEOF
import json, sys, os

state_file = "$STATE_FILE"
tmp_file = "$TMP_FILE"

with open(tmp_file) as f:
    all_breaches = json.load(f)

# Filter for PwnCount >= 1M
big = [b for b in all_breaches if b.get('PwnCount', 0) >= 1000000]
big.sort(key=lambda b: b['AddedDate'], reverse=True)

# Load current state
try:
    with open(state_file) as f:
        state = json.load(f)
except:
    state = {"known_breaches": [], "latest_added_date": "1970-01-01T00:00:00Z"}

known = set(state.get("known_breaches", []))

new_breaches = []
for b in big:
    if b["Name"] not in known:
        new_breaches.append({
            "Name": b["Name"],
            "Title": b["Title"],
            "Domain": b.get("Domain", "N/A"),
            "BreachDate": b["BreachDate"],
            "AddedDate": b["AddedDate"],
            "PwnCount": b["PwnCount"],
            "DataClasses": b.get("DataClasses", []),
            "IsVerified": b.get("IsVerified", False),
            "Description": b.get("Description", "")
        })

if new_breaches:
    # Update state — add new names
    all_known = known | {b["Name"] for b in new_breaches}
    state["known_breaches"] = sorted(list(all_known))
    state["latest_added_date"] = big[0]["AddedDate"]
    state["last_checked"] = "2026-06-18T05:15:00Z"
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

print(json.dumps({"new_breaches": new_breaches, "count": len(new_breaches)}))
PYEOF

rm -f "$TMP_FILE"

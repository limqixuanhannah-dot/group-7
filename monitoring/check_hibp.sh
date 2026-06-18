#!/bin/bash
# HIBP Breach Check Script
# Checks specified domains and emails against HaveIBeenPwned API
# Outputs JSON results for cron job processing

CONFIG_FILE="$(dirname "$0")/config.json"
STATE_FILE="$(dirname "$0")/breach_state.json"
UA="DarwinSENTRY/1.0 (Hannah's ops agent)"

# Read config
DOMAINS=$(python3 -c "import json; d=json.load(open('$CONFIG_FILE')); print('\n'.join(d['hibp']['domains']))" 2>/dev/null)
EMAILS=$(python3 -c "import json; d=json.load(open('$CONFIG_FILE')); print('\n'.join(d['hibp']['emails']))" 2>/dev/null)
API_KEY=$(python3 -c "import json; d=json.load(open('$CONFIG_FILE')); print(d['hibp']['api_key'])" 2>/dev/null)

# Load previous state
KNOWN_BREACHES="[]"
if [ -f "$STATE_FILE" ]; then
    KNOWN_BREACHES=$(cat "$STATE_FILE")
fi

# Current timestamp
NOW=$(date -u +%s)
RESULTS='[]'

# Check all known breaches for domain associations
echo "Checking HIBP all breaches for domain matches..."

ALL_BREACHES=$(curl -s -H "User-Agent: $UA" "https://haveibeenpwned.com/api/v3/breaches" 2>/dev/null)

if [ -n "$DOMAINS" ]; then
    for DOMAIN in $DOMAINS; do
        DOMAIN_MATCHES=$(echo "$ALL_BREACHES" | python3 -c "
import json, sys
breaches = json.load(sys.stdin)
domain = '$DOMAIN'
matches = [b for b in breaches if b.get('Domain','').lower() == domain.lower()]
print(json.dumps(matches, indent=2))
" 2>/dev/null)
        
        if [ "$DOMAIN_MATCHES" != "[]" ] && [ -n "$DOMAIN_MATCHES" ]; then
            echo "Domain $DOMAIN has breaches"
            NEW_BREACHES=$(echo "$DOMAIN_MATCHES" | python3 -c "
import json, sys
breaches = json.load(sys.stdin)
known = json.loads('$KNOWN_BREACHES')
new = []
for b in breaches:
    if b['Name'] not in [k['Name'] for k in known]:
        new.append(b)
print(json.dumps(new, indent=2))
" 2>/dev/null)
            
            if [ "$NEW_BREACHES" != "[]" ] && [ -n "$NEW_BREACHES" ]; then
                echo "NEW BREACHES FOUND for $DOMAIN: $(echo "$NEW_BREACHES" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")"
                RESULTS=$(echo "$RESULTS" | python3 -c "
import json, sys
results = json.load(sys.stdin)
new = json.loads('$NEW_BREACHES')
results.extend(new)
print(json.dumps(results, indent=2))
" 2>/dev/null)
            fi
        fi
    done
fi

# Check specific emails if configured
if [ -n "$EMAILS" ]; then
    for EMAIL in $EMAILS; do
        echo "Checking email: $EMAIL"
        HEADERS="-H \"User-Agent: $UA\""
        if [ -n "$API_KEY" ] && [ "$API_KEY" != "" ]; then
            HEADERS="$HEADERS -H \"hibp-api-key: $API_KEY\""
        fi
        
        EMAIL_RESULT=$(curl -s -H "User-Agent: $UA" "https://haveibeenpwned.com/api/v3/breachedaccount/$EMAIL?truncateResponse=false" 2>/dev/null)
        
        if [ -n "$EMAIL_RESULT" ] && [ "$EMAIL_RESULT" != "[]" ]; then
            NEW_EMAIL_BREACHES=$(echo "$EMAIL_RESULT" | python3 -c "
import json, sys
breaches = json.load(sys.stdin)
known = json.loads('$KNOWN_BREACHES')
new = []
for b in breaches:
    if b['Name'] not in [k['Name'] for k in known]:
        new.append(b)
print(json.dumps(new, indent=2))
" 2>/dev/null)
            
            if [ "$NEW_EMAIL_BREACHES" != "[]" ] && [ -n "$NEW_EMAIL_BREACHES" ]; then
                echo "NEW BREACHES for email $EMAIL"
                RESULTS=$(echo "$RESULTS" | python3 -c "
import json, sys
results = json.load(sys.stdin)
new = json.loads('$NEW_EMAIL_BREACHES')
results.extend(new)
print(json.dumps(results, indent=2))
" 2>/dev/null)
            fi
        fi
    done
fi

# Save new state - merge with known
python3 -c "
import json
known = json.loads('$KNOWN_BREACHES')
# Keep it simple: just save the new results for now
print(json.dumps(known, indent=2))
" > "$STATE_FILE" 2>/dev/null

# Output results
echo "---RESULTS_JSON_START---"
echo "$RESULTS"
echo "---RESULTS_JSON_END---"

#!/usr/bin/env python3
"""Google Sheets OAuth2 setup — device flow."""
import json, os, webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
TOKEN_FILE = "/home/ubuntu/.openclaw/workspace/sheets-token.json"

# OAuth client config for Desktop app (works with device flow)
CLIENT_CONFIG = {
    "installed": {
        "client_id": "994182182849-6pglqj62k9f3tlqr3ts1cls2ljpg7cim.apps.googleusercontent.com",
        "project_id": "sentry-breach-monitor",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
    }
}

flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
creds = flow.run_console()

# Save token
token_data = {
    "token": creds.token,
    "refresh_token": creds.refresh_token,
    "token_uri": creds.token_uri,
    "client_id": creds.client_id,
    "client_secret": creds.client_secret,
    "scopes": creds.scopes
}
with open(TOKEN_FILE, "w") as f:
    json.dump(token_data, f, indent=2)

print(f"\n✅ Token saved to {TOKEN_FILE}")
print(f"Authenticated email: {creds.validated_email if hasattr(creds, 'validated_email') else 'unknown'}")

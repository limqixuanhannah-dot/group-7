#!/usr/bin/env python3
"""Gcloud auth via device flow — interactive prompt for verification code."""
import sys, os, json, subprocess, webbrowser

TOKEN_FILE = "/home/ubuntu/.openclaw/workspace/gcloud-token.json"

# Use gcloud's built-in auth flow via subprocess with proper PTY
# Actually, let's just use the google-auth library directly

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

# OAuth client ID for gcloud SDK (the well-known one used by gcloud)
CLIENT_CONFIG = {
    "installed": {
        "client_id": "32555940559.apps.googleusercontent.com",
        "project_id": "sentry-breach-monitor",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "ZssO5GgHDeLg7eBToBCwBH3v",
        "redirect_uris": ["http://localhost"]
    }
}

flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
flow.run_console()

creds = flow.credentials

# Save token
token = {
    "token": creds.token,
    "refresh_token": creds.refresh_token,
    "token_uri": creds.token_uri,
    "client_id": creds.client_id,
    "client_secret": creds.client_secret,
    "scopes": creds.scopes,
    "expiry": creds.expiry.isoformat() if creds.expiry else None
}
with open(TOKEN_FILE, "w") as f:
    json.dump(token, f, indent=2)

print(f"\n✅ Token saved to {TOKEN_FILE}")

#!/usr/bin/env python3
"""Google Sheets OAuth2 — PKCE auth flow via console."""
import json, os, hashlib, base64, secrets, urllib.request, urllib.parse

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

CLIENT_ID = "764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com"

def generate_pkce():
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).rstrip(b'=').decode()
    state = secrets.token_urlsafe(16)
    return code_verifier, code_challenge, state

def exchange_code(code, code_verifier):
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "redirect_uri": "http://localhost",
        "grant_type": "authorization_code",
        "code_verifier": code_verifier
    }
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=urllib.parse.urlencode(data).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

# Generate PKCE
code_verifier, code_challenge, state = generate_pkce()

# Build auth URL
params = {
    "response_type": "code",
    "client_id": CLIENT_ID,
    "redirect_uri": "http://localhost",
    "scope": " ".join(SCOPES),
    "state": state,
    "code_challenge": code_challenge,
    "code_challenge_method": "S256",
    "access_type": "offline",
    "prompt": "consent"
}

auth_url = "https://accounts.google.com/o/oauth2/auth?" + urllib.parse.urlencode(params)

print("\n" + "="*60)
print("👉 Visit this URL in your browser:")
print("="*60)
print(auth_url)
print("="*60)
print("\nSign in with your Google account, then paste the")
print("authorization code from the redirect URL here and press Enter.")
print("(The code is the 'code=' parameter in the URL you're redirected to)")
print("="*60)

code = input("\nAuthorization code: ").strip()

# Exchange code for tokens
print("\nExchanging code for tokens...")
tokens = exchange_code(code, code_verifier)

print(f"\n✅ Authentication successful!")
print(f"Access token: {tokens['access_token'][:30]}...")
print(f"Refresh token: {'Yes' if 'refresh_token' in tokens else 'No'}")

# Save to ADC well-known location
adc_path = os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
os.makedirs(os.path.dirname(adc_path), exist_ok=True)
with open(adc_path, "w") as f:
    json.dump({
        "client_id": CLIENT_ID,
        "client_secret": tokens.get("client_secret", ""),
        "refresh_token": tokens.get("refresh_token"),
        "type": "authorized_user",
        "universe_domain": "googleapis.com"
    }, f, indent=2)
print(f"ADC saved to {adc_path}")

# Save token for gspread
token_path = "/home/ubuntu/.openclaw/workspace/sheets-token.json"
with open(token_path, "w") as f:
    json.dump({
        "token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token"),
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": CLIENT_ID,
        "client_secret": "",
        "scopes": SCOPES
    }, f, indent=2)
print(f"Token saved to {token_path}")
print("\n✅ Done! You can now use gspread to access the sheet.")

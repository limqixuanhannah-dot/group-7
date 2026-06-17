#!/usr/bin/env python3
"""
Drop this into your Discord, Telegram, or any Python-based agent
to report status to the dashboard.

Usage:
    from integrate_agent import report_status, heartbeat

    report_status("MyBot", "Discord", "reading messages", "#general")
    heartbeat("MyBot", "Discord")
"""

import requests
import json

DASHBOARD_URL = "http://localhost:3456"


def report_status(agent_name, platform, activity, details=""):
    """Report what this agent is currently doing."""
    try:
        r = requests.post(
            f"{DASHBOARD_URL}/api/status",
            json={
                "agent": agent_name,
                "platform": platform,
                "activity": activity,
                "details": details,
            },
            timeout=5,
        )
        return r.ok
    except Exception as e:
        print(f"[Dashboard] Failed to report status: {e}")
        return False


def heartbeat(agent_name, platform):
    """Lightweight ping to show agent is alive."""
    try:
        r = requests.post(
            f"{DASHBOARD_URL}/api/heartbeat",
            json={"agent": agent_name, "platform": platform},
            timeout=5,
        )
        return r.ok
    except Exception as e:
        print(f"[Dashboard] Heartbeat failed: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    report_status("Rex", "OpenClaw", "running integrations", "testing dashboard")

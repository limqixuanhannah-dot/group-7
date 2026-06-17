#!/usr/bin/env bash
# ─── Agent Status Reporter ───────────────────────────────────────────────────
# Usage:
#   ./report.sh "AgentName" "platform" "what they're doing" "details"
#
# Or with all flags:
#   ./report.sh --name "Rex" --platform "OpenClaw" --activity "idle" --details ""
#
# Example:
#   ./report.sh "Rex" "OpenClaw" "writing code" "building dashboard"
#   ./report.sh "DiscordBot" "Discord" "reading messages" "#general"
#   ./report.sh "TeleBot" "Telegram" "replying to user" "Hannah asked about weather"

DASHBOARD_URL="${DASHBOARD_URL:-http://localhost:3456}"

if [ $# -lt 3 ]; then
  echo "Usage: $0 <agent_name> <platform> <activity> [details]"
  echo "   or: $0 --name NAME --platform PLATFORM --activity ACTIVITY [--details DETAILS]"
  exit 1
fi

if [ "$1" = "--name" ]; then
  agent=""
  platform=""
  activity=""
  details=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --name) shift; agent="$1" ;;
      --platform) shift; platform="$1" ;;
      --activity) shift; activity="$1" ;;
      --details) shift; details="$1" ;;
    esac
    shift
  done
else
  agent="$1"
  platform="$2"
  activity="$3"
  details="${4:-}"
fi

curl -s -X POST "$DASHBOARD_URL/api/status" \
  -H 'Content-Type: application/json' \
  -d "$(cat <<EOF
{
  "agent": $(echo "$agent" | jq -R .),
  "platform": $(echo "$platform" | jq -R .),
  "activity": $(echo "$activity" | jq -R .),
  "details": $(echo "$details" | jq -R .)
}
EOF
)" > /dev/null

echo "✓ $agent reported: $activity"

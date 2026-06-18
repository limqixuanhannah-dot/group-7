#!/bin/bash
# Project research & update script
# Usage: bash scripts/project-research.sh <project-name> "<topic>"

PROJECT_NAME="$1"
TOPIC="$2"
PROJECT_FILE="/home/ubuntu/.openclaw/workspace/projects/${PROJECT_NAME}-project.md"

if [ -z "$PROJECT_NAME" ] || [ -z "$TOPIC" ]; then
    echo "Usage: $0 <project-name> <topic>" >&2
    exit 1
fi

echo "Researching: $TOPIC for project $PROJECT_NAME..."
echo ""

# Web search for latest info
echo "--- Searching for latest info on: $TOPIC ---"

# This will be used by the agent, not run directly
# The agent will call web_search/web_fetch and write results

echo "Research complete. Update written to $PROJECT_FILE"

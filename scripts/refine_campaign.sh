#!/bin/bash

# Refine Campaign - Open the most recent campaign for review
# Defaults to the most recent campaign output directory
# Usage:
#   ./refine_campaign.sh              # Opens latest campaign
#   ./refine_campaign.sh summer_2024  # Opens specified campaign prefix

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUTS_DIR="$PROJECT_ROOT/outputs/campaigns"

# If a prefix is provided, use it; otherwise select latest by mtime
CAMPAIGN_PREFIX="$1"
if [[ -z "$CAMPAIGN_PREFIX" ]]; then
    if compgen -G "$OUTPUTS_DIR/*" > /dev/null; then
        # Take the latest directory name, then strip trailing timestamp for prefix
        LATEST_DIR=$(ls -td "$OUTPUTS_DIR"/*/ 2>/dev/null | head -n 1)
        if [[ -n "$LATEST_DIR" ]]; then
            BASENAME=$(basename "$LATEST_DIR")
            # Use the full directory name as prefix (works with refine_campaigns filtering)
            CAMPAIGN_PREFIX="$BASENAME"
        fi
    fi
fi

if [[ -z "$CAMPAIGN_PREFIX" ]]; then
    echo "❌ No campaigns found in $OUTPUTS_DIR"
    exit 1
fi

echo "Opening refine tool for campaign prefix: $CAMPAIGN_PREFIX"
# Start refine server and open UI
# Note: The HTML UI is a required asset at scripts/refine_campaign.html
PORT=8000
while lsof -ti:${PORT} >/dev/null 2>&1; do
    PORT=$((PORT + 1))
done

# Enforce required asset
if [[ ! -f "$SCRIPT_DIR/refine_campaign.html" ]]; then
    echo "❌ Required asset missing: $SCRIPT_DIR/refine_campaign.html"
    echo "   Please add the file to the repository."
    exit 1
fi

if command -v python3 >/dev/null 2>&1; then
    python3 "$SCRIPT_DIR/refine_server.py" --port "$PORT" >/dev/null 2>&1 &
    SERVER_PID=$!
    sleep 2
    if command -v open >/dev/null 2>&1; then
        open "http://localhost:${PORT}/scripts/refine_campaign.html?campaign=${CAMPAIGN_PREFIX}"
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "http://localhost:${PORT}/scripts/refine_campaign.html?campaign=${CAMPAIGN_PREFIX}"
    else
        echo "Open http://localhost:${PORT}/scripts/refine_campaign.html?campaign=${CAMPAIGN_PREFIX} in your browser"
    fi
    wait $SERVER_PID
else
    echo "❌ python3 not found. Please install Python 3 to run the refine server."
    exit 1
fi

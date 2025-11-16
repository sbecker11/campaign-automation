#!/bin/bash

# Refine Campaign - Open the most recent campaign for review
# Defaults to the most recent campaign output directory
# Usage:
#   ./refine_campaign.sh              # Opens latest campaign
#   ./refine_campaign.sh summer_2024  # Opens specified campaign prefix

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUTS_DIR="$SCRIPT_DIR/outputs/campaigns"

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
"$SCRIPT_DIR/refine_campaigns.sh" "$CAMPAIGN_PREFIX"

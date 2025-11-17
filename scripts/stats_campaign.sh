#!/bin/bash

# Stats Campaign - Review status of campaign deletions
# 
# Usage:
#   ./stats_campaign.sh                          # Show campaign_generated.json for latest run
#   ./stats_campaign.sh <campaign_or_run_dir>    # Show campaign_generated.json for specified campaign id or run directory name
#   ./stats_campaign.sh --pretty                  # Pretty print with jq if available (latest)
#   ./stats_campaign.sh --pretty <campaign>       # Pretty print specified

set -e

CAMPAIGN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUTS_DIR="$CAMPAIGN_DIR/outputs/campaigns"
USE_PRETTY="0"
TARGET_ARG=""

# Parse args
for arg in "$@"; do
    if [[ "$arg" == "--pretty" ]]; then
        USE_PRETTY="1"
    else
        TARGET_ARG="$arg"
    fi
done

if [[ ! -d "$OUTPUTS_DIR" ]]; then
    echo "❌ outputs/campaigns not found at: $OUTPUTS_DIR"
    exit 1
fi

resolve_status_file() {
    local target="$1"
    local status_file=""

    if [[ -z "$target" ]]; then
        # latest
        local latest_dir
        latest_dir=$(ls -td "$OUTPUTS_DIR"/*/ 2>/dev/null | head -n 1 || true)
        if [[ -z "$latest_dir" ]]; then
            echo ""; return 1
        fi
        status_file="${latest_dir%/}"
    elif [[ -d "$OUTPUTS_DIR/$target" ]]; then
        # If argument is an absolute or relative path to a dir under outputs/campaigns
        status_file="$OUTPUTS_DIR/$target"
    elif [[ -d "$target" ]]; then
        # Try exact path as given
        status_file="${target%/}"
    else
        # Try prefix match for campaign id/run dir
        local match
        match=$(ls -td "$OUTPUTS_DIR/${target}"* 2>/dev/null | head -n 1 || true)
        if [[ -n "$match" ]]; then
            status_file="${match%/}"
        else
            echo ""; return 1
        fi
    fi
    
    # Construct filename: campaign_generated.json
    echo "${status_file}/campaign_generated.json"
    return 0
}

STATUS_FILE="$(resolve_status_file "$TARGET_ARG" || true)"
if [[ -z "$STATUS_FILE" || ! -f "$STATUS_FILE" ]]; then
    echo "❌ campaign_generated.json not found${TARGET_ARG:+ for '$TARGET_ARG'}"
    exit 1
fi

echo "📄 Status file: $STATUS_FILE"

if [[ "$USE_PRETTY" == "1" ]] && command -v jq >/dev/null 2>&1; then
    jq . "$STATUS_FILE"
else
    cat "$STATUS_FILE"
fi

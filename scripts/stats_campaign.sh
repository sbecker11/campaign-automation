#!/bin/bash

# Stats Campaign - Review status of campaign deletions
# 
# Usage:
#   ./stats_campaign.sh                          # Show status.json for latest run
#   ./stats_campaign.sh <campaign_or_run_dir>    # Show status.json for specified campaign id or run directory name
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

    if [[ -z "$target" ]]; then
        # latest
        local latest_dir
        latest_dir=$(ls -td "$OUTPUTS_DIR"/*/ 2>/dev/null | head -n 1 || true)
        if [[ -z "$latest_dir" ]]; then
            echo ""; return 1
        fi
        echo "${latest_dir%/}/status.json"; return 0
    fi

    # If argument is an absolute or relative path to a dir under outputs/campaigns
    if [[ -d "$OUTPUTS_DIR/$target" ]]; then
        echo "$OUTPUTS_DIR/$target/status.json"; return 0
    fi

    # Try exact path as given
    if [[ -d "$target" ]]; then
        echo "${target%/}/status.json"; return 0
    fi

    # Try prefix match for campaign id/run dir
    local match
    match=$(ls -td "$OUTPUTS_DIR/${target}"* 2>/dev/null | head -n 1 || true)
    if [[ -n "$match" ]]; then
        echo "${match%/}/status.json"; return 0
    fi

    echo ""; return 1
}

STATUS_FILE="$(resolve_status_file "$TARGET_ARG" || true)"
if [[ -z "$STATUS_FILE" || ! -f "$STATUS_FILE" ]]; then
    echo "❌ status.json not found${TARGET_ARG:+ for '$TARGET_ARG'}"
    exit 1
fi

echo "📄 Status file: $STATUS_FILE"

if [[ "$USE_PRETTY" == "1" ]] && command -v jq >/dev/null 2>&1; then
    jq . "$STATUS_FILE"
else
    cat "$STATUS_FILE"
fi

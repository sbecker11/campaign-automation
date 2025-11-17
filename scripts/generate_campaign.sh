#!/bin/bash

# Generate Campaign - Run Campaign Automation Pipeline
# Creates campaign images and campaign_instance.json
# 
# Supported invocations:
# 1) No args: uses latest YAML in inputs/campaigns/ and runs with current timestamp
#    ./generate_campaign.sh
# 2) --output-dir <dir>: reads YAML at given output directory
#    ./generate_campaign.sh --output-dir outputs/campaigns/<campaign_id_or_run>

set -e

# Activate virtual environment
source venv/bin/activate

# Parse arguments (only two modes supported)
MODE="default"
OUTPUT_DIR_ARG=""

if [[ "$1" == "--output-dir" ]]; then
    MODE="output_dir"
    OUTPUT_DIR_ARG="$2"
    if [[ -z "$OUTPUT_DIR_ARG" ]]; then
        echo "❌ Error: --output-dir requires a directory path"
        exit 1
    fi
elif [[ -n "$1" ]]; then
    echo "❌ Error: Unsupported arguments. Use either no args or --output-dir <dir>"
    exit 1
fi

# Helper to find latest YAML in inputs/campaigns
find_latest_yaml() {
    ls -t inputs/campaigns/*.yaml 2>/dev/null | head -n 1
}

# Helper to find a YAML inside a given directory
find_yaml_in_dir() {
    local dir="$1"
    if [[ -f "$dir/campaign.yaml" ]]; then
        echo "$dir/campaign.yaml"
        return 0
    fi
    local first_yaml
    first_yaml=$(ls -t "$dir"/*.yaml 2>/dev/null | head -n 1 || true)
    if [[ -n "$first_yaml" ]]; then
        echo "$first_yaml"
        return 0
    fi
    echo ""
    return 1
}

# Mode 1: Default (no args) – use latest YAML and timestamped run
if [[ "$MODE" == "default" ]]; then
    CAMPAIGN_FILE=$(find_latest_yaml)
    if [[ -z "$CAMPAIGN_FILE" ]]; then
        echo "❌ Error: No campaign YAMLs found in inputs/campaigns/."
        exit 1
    fi

    # Extract campaign_id early and echo
    CAMPAIGN_ID=$(python -c "
import yaml
with open('$CAMPAIGN_FILE', 'r') as f:
    data = yaml.safe_load(f)
    print(data.get('campaign_id', ''))
")

    echo "🚀 Running Campaign Automation Pipeline"
    echo "   Campaign: $CAMPAIGN_FILE"
    echo "   Campaign ID: $CAMPAIGN_ID"
    echo "   Output: Timestamped (each run creates a new directory)"
    echo ""

    # Check logo file if logo_path is defined
    LOGO_PATH=$(python -c "
import yaml
with open('$CAMPAIGN_FILE', 'r') as f:
    data = yaml.safe_load(f)
    logo_path = data.get('brand_guidelines', {}).get('logo_path', '')
    if logo_path:
        print(logo_path)
" 2>/dev/null || echo "")

    if [[ -n "$LOGO_PATH" ]]; then
        if [[ ! -f "$LOGO_PATH" ]]; then
            echo "⚠️  Warning: Logo file not found: $LOGO_PATH"
            echo "   Logo will be skipped. Make sure the file exists if you want to use a logo."
            echo ""
        else
            echo "✓ Logo file found: $LOGO_PATH"
            echo ""
        fi
    fi

    # Always run timestamped
    python -m src.pipeline --campaign "$CAMPAIGN_FILE" --timestamp

    # Find the most recent run directory for this campaign
    CAMPAIGN_OUTPUT_DIR=$(ls -td "outputs/campaigns/${CAMPAIGN_ID}"_* 2>/dev/null | head -n 1)
    echo "   Campaign ID: $CAMPAIGN_ID"
    echo "   Latest run dir: ${CAMPAIGN_OUTPUT_DIR:-'(not found)'}"
    echo ""
    echo "✅ Campaign generation complete for: $CAMPAIGN_ID"
    echo "   Next: ./scripts/refine_campaign.sh"
    exit 0
fi

# Mode 2: --output-dir <dir> – read YAML in dir
if [[ "$MODE" == "output_dir" ]]; then
    if [[ ! -d "$OUTPUT_DIR_ARG" ]]; then
        echo "❌ Error: Output directory not found: $OUTPUT_DIR_ARG"
        exit 1
    fi

    CAMPAIGN_FILE=$(find_yaml_in_dir "$OUTPUT_DIR_ARG") || true
    if [[ -z "$CAMPAIGN_FILE" ]]; then
        echo "❌ Error: No YAML found in: $OUTPUT_DIR_ARG"
        echo "   Expected: campaign.yaml or any *.yaml inside the directory"
        exit 1
    fi

    # Extract campaign_id and echo
    CAMPAIGN_ID=$(python -c "
import yaml
with open('$CAMPAIGN_FILE', 'r') as f:
    data = yaml.safe_load(f)
    print(data.get('campaign_id', ''))
")

    echo "🚀 Running Campaign Automation Pipeline"
    echo "   Campaign: $CAMPAIGN_FILE"
    echo "   Campaign ID: $CAMPAIGN_ID"
    echo "   Output: Timestamped (each run creates a new directory)"
    echo ""

    # Check logo file if logo_path is defined
    LOGO_PATH=$(python -c "
import yaml
with open('$CAMPAIGN_FILE', 'r') as f:
    data = yaml.safe_load(f)
    logo_path = data.get('brand_guidelines', {}).get('logo_path', '')
    if logo_path:
        print(logo_path)
" 2>/dev/null || echo "")

    if [[ -n "$LOGO_PATH" ]]; then
        if [[ ! -f "$LOGO_PATH" ]]; then
            echo "⚠️  Warning: Logo file not found: $LOGO_PATH"
            echo "   Logo will be skipped. Make sure the file exists if you want to use a logo."
            echo ""
        else
            echo "✓ Logo file found: $LOGO_PATH"
            echo ""
        fi
    fi

    # Always run timestamped
    python -m src.pipeline --campaign "$CAMPAIGN_FILE" --timestamp

    echo ""
    echo "✅ Campaign generation complete for Campaign ID: $CAMPAIGN_ID"
    echo "   Next: ./scripts/refine_campaign.sh"
    exit 0
fi

#!/bin/bash

# Generate Campaign - Run Campaign Automation Pipeline
# Creates campaign images and initializes status.json files
# 
# Supported invocations:
# 1) No args: uses latest YAML in inputs/campaigns/ and runs with current timestamp
#    ./generate_campaign.sh
# 2) --output-dir <dir>: reads YAML at given output directory and writes status.json there
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

    echo "🚀 Running Campaign Automation Pipeline"
    echo "   Campaign: $CAMPAIGN_FILE"
    echo "   Output: Timestamped (each run creates a new directory)"
    echo ""

    # Always run timestamped
    python -m src.pipeline --campaign "$CAMPAIGN_FILE" --timestamp

    # Extract campaign_id from YAML file
    CAMPAIGN_ID=$(python -c "
import yaml
with open('$CAMPAIGN_FILE', 'r') as f:
    data = yaml.safe_load(f)
    print(data.get('campaign_id', ''))
")

    # Find the most recent run directory
    CAMPAIGN_OUTPUT_DIR=$(ls -td "outputs/campaigns/${CAMPAIGN_ID}"_* 2>/dev/null | head -n 1)

    # Create status.json with empty deletes array (keeps by default)
    if [[ -d "$CAMPAIGN_OUTPUT_DIR" ]]; then
        echo ""
        echo "📝 Creating status.json file..."
        python -c "
import json
from pathlib import Path
status_file = Path('$CAMPAIGN_OUTPUT_DIR') / 'status.json'
status_data = {'deletes': [], 'timestamp': __import__('datetime').datetime.now().isoformat()}
with open(status_file, 'w') as f:
    json.dump(status_data, f, indent=2)
print(f'  ✓ Created: {status_file}')
"
        echo ""
        echo "✅ Campaign generation complete!"
        echo "   Status.json file created with all images marked as keeps"
    else
        echo "⚠️  Warning: Could not locate output directory for status.json"
    fi
    exit 0
fi

# Mode 2: --output-dir <dir> – read YAML in dir and write status.json into same dir
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

    echo "🚀 Running Campaign Automation Pipeline"
    echo "   Campaign: $CAMPAIGN_FILE"
    echo "   Output: Timestamped (each run creates a new directory)"
    echo ""

    # Always run timestamped
    python -m src.pipeline --campaign "$CAMPAIGN_FILE" --timestamp

    # Write a status.json into the provided output directory (not the new run)
    STATUS_TARGET_DIR="$OUTPUT_DIR_ARG"
    if [[ -d "$STATUS_TARGET_DIR" ]]; then
        echo ""
        echo "📝 Creating status.json in provided output directory..."
        python -c "
import json
from pathlib import Path
status_file = Path('$STATUS_TARGET_DIR') / 'status.json'
status_data = {'deletes': [], 'timestamp': __import__('datetime').datetime.now().isoformat()}
with open(status_file, 'w') as f:
    json.dump(status_data, f, indent=2)
print(f'  ✓ Created: {status_file}')
"
        echo ""
        echo "✅ Status file created in: $STATUS_TARGET_DIR"
    else
        echo "⚠️  Warning: Provided output directory not found for status.json: $STATUS_TARGET_DIR"
    fi
    exit 0
fi

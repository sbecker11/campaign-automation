#!/bin/bash

# Run Campaign Automation Pipeline Multiple Times with Timestamps
# 
# Usage:
#   ./run_campaign_multiple.sh [count] [campaign_file]
#   ./run_campaign_multiple.sh 100                    # Run 100 times with default campaign
#   ./run_campaign_multiple.sh 50 my_campaign.yaml    # Run 50 times with specific campaign

set -e

# Get count from argument or default to 100
COUNT="${1:-100}"

# Get campaign file from second argument or use default
CAMPAIGN_FILE="${2:-inputs/campaigns/example_campaign.yaml}"

# Validate count is a number
if ! [[ "$COUNT" =~ ^[0-9]+$ ]]; then
    echo "❌ Error: Count must be a number"
    echo "Usage: ./run_campaign_multiple.sh [count] [campaign_file]"
    exit 1
fi

# Check if campaign file exists
if [ ! -f "$CAMPAIGN_FILE" ]; then
    echo "❌ Error: Campaign file not found: $CAMPAIGN_FILE"
    echo ""
    echo "Available campaigns:"
    ls -1 inputs/campaigns/*.yaml 2>/dev/null || echo "  (none)"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "🚀 Running Campaign Automation Pipeline $COUNT times"
echo "   Campaign: $CAMPAIGN_FILE"
echo "   Output: Each run will create a timestamped directory"
echo ""

# Extract campaign_id from YAML file (once, before the loop)
CAMPAIGN_ID=$(python -c "
import yaml
import sys
with open('$CAMPAIGN_FILE', 'r') as f:
    data = yaml.safe_load(f)
    print(data.get('campaign_id', ''))
")

# Run the pipeline multiple times
for i in $(seq 1 $COUNT); do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Run $i of $COUNT"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    python -m src.pipeline --campaign "$CAMPAIGN_FILE" --timestamp
    
    # Find the most recently created directory matching the campaign_id pattern
    CAMPAIGN_OUTPUT_DIR=$(ls -td "outputs/campaigns/${CAMPAIGN_ID}"_* 2>/dev/null | head -n 1)
    
    # Create status.json file if campaign output directory exists
    if [ -d "$CAMPAIGN_OUTPUT_DIR" ]; then
        echo ""
        echo "📝 Creating status.json file..."
        
        # Create status.json with empty deletes array (all images are keeps by default)
        STATUS_FILE="${CAMPAIGN_OUTPUT_DIR}/status.json"
        python -c "
import json
import os
from pathlib import Path

campaign_dir = Path('$CAMPAIGN_OUTPUT_DIR')
status_file = Path('$STATUS_FILE')

# Initialize with empty deletes array
status_data = {'deletes': []}

# Write status.json
with open(status_file, 'w') as f:
    json.dump(status_data, f, indent=2)

print(f'  ✓ Created: {status_file}')
"
    fi
    
    echo ""
    echo "✅ Run $i complete!"
    echo ""
    
    # Small delay between runs to avoid rate limiting (optional)
    if [ $i -lt $COUNT ]; then
        sleep 1
    fi
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All $COUNT runs complete!"
echo ""
echo "Output directories created:"
ls -1td outputs/campaigns/*/ 2>/dev/null | head -$COUNT | nl
echo ""
echo "Total output directories:"
ls -1d outputs/campaigns/*/ 2>/dev/null | wc -l
echo ""
echo "View outputs:"
echo "  ls -ltr outputs/campaigns/  # List all runs (oldest first)"
echo "  ls -lt outputs/campaigns/   # List all runs (newest first)"


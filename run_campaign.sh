#!/bin/bash

# Run Campaign Automation Pipeline
# 
# Usage:
#   ./run_campaign.sh                    # Run default campaign
#   ./run_campaign.sh my_campaign.yaml   # Run specific campaign

set -e

# Activate virtual environment
source venv/bin/activate

# Get campaign file from argument or use default
CAMPAIGN_FILE="${1:-inputs/campaigns/example_campaign.yaml}"

# Check if campaign file exists
if [ ! -f "$CAMPAIGN_FILE" ]; then
    echo "❌ Error: Campaign file not found: $CAMPAIGN_FILE"
    echo ""
    echo "Available campaigns:"
    ls -1 inputs/campaigns/*.yaml 2>/dev/null || echo "  (none)"
    exit 1
fi

echo "🚀 Running Campaign Automation Pipeline"
echo "   Campaign: $CAMPAIGN_FILE"
echo ""

# Run the pipeline (using python -m to fix imports)
python -m src.pipeline --campaign "$CAMPAIGN_FILE"

echo ""
echo "✅ Campaign complete!"
echo ""
echo "View outputs:"
echo "  ./view_campaign.sh"

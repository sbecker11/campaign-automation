#!/bin/bash

# Report helper

if [ ! -d "outputs/campaigns" ]; then
    echo "No outputs found. Generate first:"
    echo "  ./generate_campaign.sh --timestamp"
    exit 1
fi

# View Campaign Reports
# 
# Usage:
#   ./report_campaign.sh              # View default campaign reports
#   ./report_campaign.sh campaign_id  # View specific campaign reports

set -e

# Define paths
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Get default campaign ID from the example_campaign.yaml file
DEFAULT_CAMPAIGN="$BASE_DIR/inputs/campaigns/example_campaign.yaml"
if [ -f "$DEFAULT_CAMPAIGN" ]; then
    DEFAULT_CAMPAIGN_ID=$(grep "^campaign_id:" "$DEFAULT_CAMPAIGN" | awk '{print $2}' | tr -d '"' | tr -d "'")
else
    DEFAULT_CAMPAIGN_ID="summer_2024"
fi

# Get campaign ID from argument or use default
CAMPAIGN_ID="${1:-$DEFAULT_CAMPAIGN_ID}"
OUTPUT_DIR="$BASE_DIR/outputs/campaigns/$CAMPAIGN_ID"
STATUS_FILE="$OUTPUT_DIR/campaign_generated.json"

# Colors
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Campaign Status: $CAMPAIGN_ID${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if campaign_generated.json exists
if [ ! -f "$STATUS_FILE" ]; then
    echo -e "${RED}❌ No campaign_generated.json found for campaign: $CAMPAIGN_ID${NC}"
    echo ""
    echo "Looking for: $STATUS_FILE"
    echo ""
    echo "Run a campaign first:"
    echo "  ./run_campaign.sh"
    exit 1
fi

# Display consolidated campaign_generated.json
echo -e "${YELLOW}📄 Consolidated Status (campaign_generated.json):${NC}"
cat "$STATUS_FILE" | python3 -m json.tool 2>/dev/null || cat "$STATUS_FILE"
echo ""

echo -e "${GREEN}✅ Status displayed${NC}"

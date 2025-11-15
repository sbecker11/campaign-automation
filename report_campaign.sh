#!/bin/bash

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
REPORTS_DIR="$BASE_DIR/outputs/campaigns/$CAMPAIGN_ID/reports"

# Colors
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Campaign Reports: $CAMPAIGN_ID${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if reports exist
if [ ! -d "$REPORTS_DIR" ]; then
    echo -e "${RED}❌ No reports found for campaign: $CAMPAIGN_ID${NC}"
    echo ""
    echo "Run a campaign first:"
    echo "  ./run_campaign.sh"
    exit 1
fi

# Generation Report
if [ -f "$REPORTS_DIR/generation_report.json" ]; then
    echo -e "${YELLOW}📄 Generation Report:${NC}"
    cat "$REPORTS_DIR/generation_report.json" | python3 -m json.tool 2>/dev/null || cat "$REPORTS_DIR/generation_report.json"
    echo ""
    echo ""
fi

# Compliance Report
if [ -f "$REPORTS_DIR/compliance_report.json" ]; then
    echo -e "${YELLOW}📄 Compliance Report:${NC}"
    cat "$REPORTS_DIR/compliance_report.json" | python3 -m json.tool 2>/dev/null || cat "$REPORTS_DIR/compliance_report.json"
    echo ""
fi

echo -e "${GREEN}✅ Reports displayed${NC}"

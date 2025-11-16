#!/bin/bash

# View Campaign helper

if [ ! -d "outputs/campaigns" ]; then
    echo "No outputs found. Generate first:"
    echo "  ./generate_campaign.sh --timestamp"
    exit 1
fi

# View Campaign Outputs
# 
# Usage:
#   ./view_campaign.sh              # View default campaign
#   ./view_campaign.sh campaign_id  # View specific campaign

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

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Campaign Output Viewer${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if output directory exists
if [ ! -d "$OUTPUT_DIR" ]; then
    echo -e "${RED}❌ Error: Campaign output not found${NC}"
    echo -e "   Looking for: $OUTPUT_DIR"
    echo ""
    echo "Available campaigns:"
    if [ -d "$BASE_DIR/outputs/campaigns" ]; then
        ls -1 "$BASE_DIR/outputs/campaigns" 2>/dev/null || echo "  (none)"
    else
        echo "  (none - run a campaign first)"
    fi
    echo ""
    echo "Usage:"
    echo "  ./view_campaign.sh              # View default campaign ($DEFAULT_CAMPAIGN_ID)"
    echo "  ./view_campaign.sh campaign_id  # View specific campaign"
    echo ""
    echo "Run a campaign first:"
    echo "  ./run_campaign.sh"
    exit 1
fi

echo -e "${GREEN}📁 Campaign:${NC} $CAMPAIGN_ID"
echo -e "${GREEN}📂 Location:${NC} $OUTPUT_DIR"
echo ""

# Show directory structure
echo -e "${BLUE}Directory Structure:${NC}"
if command -v tree &> /dev/null; then
    tree "$OUTPUT_DIR" -L 3
else
    find "$OUTPUT_DIR" -type f -o -type d | head -30
fi
echo ""

# Count files
TOTAL_IMAGES=$(find "$OUTPUT_DIR/products" -type f -name "*.png" 2>/dev/null | wc -l)
TOTAL_PRODUCTS=$(find "$OUTPUT_DIR/products" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)

echo -e "${GREEN}📊 Summary:${NC}"
echo "  Products: $TOTAL_PRODUCTS"
echo "  Images: $TOTAL_IMAGES"
echo ""

# Show reports if they exist
if [ -d "$OUTPUT_DIR/reports" ]; then
    echo -e "${BLUE}📄 Reports:${NC}"
    ls -lh "$OUTPUT_DIR/reports/"
    echo ""
fi

# Offer to open in Finder/Explorer
echo -e "${YELLOW}View Options:${NC}"
echo "  1. Preview all images at once"
echo "  2. Open in file browser"
echo "  3. List all image files"
echo "  4. Show generation report"
echo "  5. Show compliance report"
echo ""

read -p "Choose option (1-5, or Enter to skip): " choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}Opening all images in Preview...${NC}"
        
        # Find all PNG images
        IMAGES=$(find "$OUTPUT_DIR/products" -type f -name "*.png" | sort)
        IMAGE_COUNT=$(echo "$IMAGES" | wc -l | tr -d ' ')
        
        if [ "$IMAGE_COUNT" -eq 0 ]; then
            echo -e "${RED}No images found${NC}"
        else
            echo "Found $IMAGE_COUNT image(s)"
            
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS - open all at once in Preview
                open $IMAGES
                echo "✅ Opened $IMAGE_COUNT images in Preview"
            elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
                # Linux - try different viewers
                if command -v eog &> /dev/null; then
                    eog $IMAGES &
                    echo "✅ Opened $IMAGE_COUNT images in Eye of GNOME"
                elif command -v feh &> /dev/null; then
                    feh $IMAGES &
                    echo "✅ Opened $IMAGE_COUNT images in feh"
                else
                    xdg-open $(echo "$IMAGES" | head -1) 2>/dev/null
                    echo "✅ Opened first image (install eog or feh for multi-image viewing)"
                fi
            else
                echo "Image preview not available on this platform"
            fi
        fi
        ;;
    2)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open "$OUTPUT_DIR"
            echo "✅ Opened in Finder"
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            xdg-open "$OUTPUT_DIR" 2>/dev/null || echo "Please open: $OUTPUT_DIR"
        else
            echo "Please open: $OUTPUT_DIR"
        fi
        ;;
    3)
        echo ""
        echo -e "${BLUE}All generated images:${NC}"
        find "$OUTPUT_DIR/products" -type f -name "*.png" | sort
        ;;
    4)
        if [ -f "$OUTPUT_DIR/reports/generation_report.json" ]; then
            echo ""
            echo -e "${BLUE}Generation Report:${NC}"
            cat "$OUTPUT_DIR/reports/generation_report.json"
        else
            echo "Generation report not found"
        fi
        ;;
    5)
        if [ -f "$OUTPUT_DIR/reports/compliance_report.json" ]; then
            echo ""
            echo -e "${BLUE}Compliance Report:${NC}"
            cat "$OUTPUT_DIR/reports/compliance_report.json"
        else
            echo "Compliance report not found"
        fi
        ;;
    *)
        echo "Skipped"
        ;;
esac

echo ""
echo -e "${GREEN}✅ Done${NC}"

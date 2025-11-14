#!/bin/bash
# View Campaign Outputs Helper Script

BRAND=${1:-brands/summer_co}
CAMPAIGN=${2:-}

# Remove trailing slash
BRAND="${BRAND%/}"

echo "╔════════════════════════════════════════════════════════╗"
echo "║     Campaign Outputs Viewer                            ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if brand exists
if [ ! -d "$BRAND" ]; then
    echo "❌ Brand not found: $BRAND"
    echo ""
    echo "Available brands:"
    ls -d brands/*/ 2>/dev/null | sed 's|/$||'
    exit 1
fi

# If specific campaign provided
if [ -n "$CAMPAIGN" ]; then
    CAMPAIGN_DIR="$BRAND/outputs/$CAMPAIGN"
    
    if [ ! -d "$CAMPAIGN_DIR" ]; then
        echo "❌ Campaign not found: $CAMPAIGN"
        echo ""
        echo "Available campaigns in $BRAND:"
        ls -1 "$BRAND/outputs/" 2>/dev/null || echo "  (none)"
        exit 1
    fi
    
    echo "📂 Brand: $BRAND"
    echo "📋 Campaign: $CAMPAIGN"
    echo ""
    
    # Show structure
    echo "📁 Campaign Structure:"
    tree "$CAMPAIGN_DIR" -L 3 -I '__pycache__|*.pyc' || find "$CAMPAIGN_DIR" -type d
    echo ""
    
    # Count files
    IMAGE_COUNT=$(find "$CAMPAIGN_DIR" -name "*.png" -not -path "*/reports/*" | wc -l | tr -d ' ')
    echo "📊 Generated: $IMAGE_COUNT images"
    echo ""
    
    # Show reports
    if [ -d "$CAMPAIGN_DIR/reports" ]; then
        echo "📄 Reports available:"
        ls -lh "$CAMPAIGN_DIR/reports/"
        echo ""
    fi
    
    # List all images
    echo "🖼️  Generated Images:"
    find "$CAMPAIGN_DIR" -name "*.png" -not -path "*/reports/*" | sort
    echo ""
    
    # Offer to open
    echo "Commands to open outputs:"
    echo "  open $CAMPAIGN_DIR"
    echo "  open $CAMPAIGN_DIR/reports/generation_report.json"
    echo ""

else
    # Show all campaigns
    echo "📂 Brand: $BRAND"
    echo ""
    
    if [ ! -d "$BRAND/outputs" ] || [ -z "$(ls -A $BRAND/outputs 2>/dev/null)" ]; then
        echo "❌ No campaigns found in $BRAND/outputs/"
        exit 0
    fi
    
    echo "📋 Available Campaigns:"
    echo ""
    
    for campaign in "$BRAND/outputs"/*/ ; do
        if [ -d "$campaign" ]; then
            campaign_name=$(basename "$campaign")
            image_count=$(find "$campaign" -name "*.png" -not -path "*/reports/*" | wc -l | tr -d ' ')
            
            echo "  📁 $campaign_name"
            echo "     Images: $image_count"
            echo "     Path: $campaign"
            
            if [ -f "$campaign/reports/generation_report.json" ]; then
                echo "     Reports: ✓"
            fi
            echo ""
        fi
    done
    
    echo "To view specific campaign:"
    echo "  ./view_outputs.sh $BRAND <campaign_id>"
fi

#!/bin/bash
# Campaign Automation Pipeline Runner

# Default values
BRAND="brands/summer_co/"
BRIEF="inputs/briefs/summer_promo_2024.yaml"
VERBOSE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --brand)
            BRAND="$2"
            shift 2
            ;;
        --brief)
            BRIEF="$2"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE="--verbose"
            shift
            ;;
        --help|-h)
            echo "Usage: ./run_campaign.sh [options]"
            echo ""
            echo "Options:"
            echo "  --brand BRAND     Brand directory (default: brands/summer_co/)"
            echo "  --brief BRIEF     Brief file relative to brand (default: inputs/briefs/summer_promo_2024.yaml)"
            echo "  --verbose, -v     Enable verbose logging"
            echo "  --help, -h        Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run_campaign.sh"
            echo "  ./run_campaign.sh --verbose"
            echo "  ./run_campaign.sh --brand brands/winter_brand/"
            echo "  ./run_campaign.sh --brief inputs/briefs/holiday.yaml"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Remove trailing slash from BRAND early
BRAND="${BRAND%/}"

# Display banner
echo "╔════════════════════════════════════════════════════════╗"
echo "║     Campaign Automation Pipeline                       ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Brand:  $BRAND"
echo "📋 Brief:  $BRIEF"
echo ""

# Check if brand directory exists
if [ ! -d "$BRAND" ]; then
    echo "❌ Error: Brand directory not found: $BRAND"
    exit 1
fi

# Resolve brief path - if relative, make it relative to brand
if [[ "$BRIEF" != /* ]]; then
    # Brief is relative, prepend brand directory
    FULL_BRIEF_PATH="${BRAND}/${BRIEF}"
else
    # Brief is absolute
    FULL_BRIEF_PATH="$BRIEF"
fi

# Check if brief exists
if [ ! -f "$FULL_BRIEF_PATH" ]; then
    echo "❌ Error: Brief not found: $FULL_BRIEF_PATH"
    echo ""
    echo "Available briefs in $BRAND:"
    find "$BRAND/inputs/briefs" -name "*.yaml" 2>/dev/null | sed 's|.*/||'
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Create one with: cp .env.example .env"
    echo "   Then add your OPENAI_API_KEY"
    exit 1
fi

# Check if OpenAI key is set
source .env
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY not set in .env file"
    exit 1
fi

# Extract campaign_id from brief for later use
CAMPAIGN_ID=$(grep "^campaign_id:" "$FULL_BRIEF_PATH" | sed 's/campaign_id: *"\?\([^"]*\)"\?/\1/' | tr -d '"')

# Run the pipeline with full path to brief
PYTHONPATH=src python src/pipeline.py \
    --brand "$BRAND" \
    --brief "$FULL_BRIEF_PATH" \
    $VERBOSE

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║     ✅ Campaign Generated Successfully                 ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo "📂 View outputs: $BRAND/outputs/$CAMPAIGN_ID/"
    echo ""
    
    # Open generated images for each product
    if [ -d "$BRAND/outputs/$CAMPAIGN_ID" ]; then
        echo "🖼️  Opening generated images..."
        
        # Find all product directories (excluding reports)
        for product_dir in "$BRAND/outputs/$CAMPAIGN_ID"/*/ ; do
            if [ -d "$product_dir" ] && [[ ! "$product_dir" =~ /reports/$ ]]; then
                product_name=$(basename "$product_dir")
                echo "   📸 Opening $product_name images..."
                
                # Open all PNG files for this product across all formats
                open "$product_dir"/*/*.png 2>/dev/null || echo "      (No images found for $product_name)"
            fi
        done
        echo ""
    fi
else
    echo ""
    echo "❌ Pipeline failed with exit code: $EXIT_CODE"
    exit $EXIT_CODE
fi

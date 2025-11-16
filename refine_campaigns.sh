#!/bin/bash

# Refine Campaigns - Review and mark images for deletion
# Updates status.json files for each campaign
# No external dependencies - everything is self-contained
#
# Usage:
#   ./refine_campaigns.sh                           # All images with filters
#   ./refine_campaigns.sh summer_2024               # Pre-filter to summer_2024 campaign
#   ./refine_campaigns.sh summer_2024 1x1           # Pre-filter to summer_2024 campaign, 1x1 images

set -e

# Paths
CAMPAIGN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$CAMPAIGN_DIR/outputs/campaigns"
STANDALONE_HTML="$CAMPAIGN_DIR/refine_campaigns.html"

# Parse arguments with defaults (for initial filtering, but all images will be loaded)
CAMPAIGN_PREFIX="${1:-}"
ASPECT_RATIO="${2:-}"

# Initialize selected filter variables with defaults
SELECTED_CAMPAIGN="any"
SELECTED_PRODUCT_FILTER="any"
SELECTED_ASPECT="any"
SELECTED_STATUS_FILTER="any"

# Check if output directory exists
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "❌ Error: Output directory not found: $OUTPUT_DIR"
    echo "   Run some campaigns first with --timestamp flag"
    exit 1
fi

echo "🔍 Finding all images..."

# Find ALL images (we'll filter in the UI)
IMAGES=$(find "$OUTPUT_DIR" -path "*/products/*/*.png" -type f | sort)

IMAGE_COUNT=$(echo "$IMAGES" | grep -c . || echo "0")

if [ "$IMAGE_COUNT" -eq 0 ]; then
    echo "❌ No images found"
    exit 1
fi

echo "   Found $IMAGE_COUNT image(s)"
echo ""

# Prepare image data and collect unique values for filters
declare -a IMAGE_PATHS
declare -a IMAGE_DATA
declare -a UNIQUE_CAMPAIGNS
declare -a UNIQUE_PRODUCTS
declare -a UNIQUE_ASPECT_RATIOS

# Temporary files for collecting unique values
TEMP_CAMPAIGNS=$(mktemp)
TEMP_PRODUCTS=$(mktemp)
TEMP_ASPECTS=$(mktemp)

while IFS= read -r image_path; do
    rel_path="${image_path#$CAMPAIGN_DIR/}"
    timestamp=$(echo "$image_path" | grep -oE '[0-9]{8}_[0-9]{6}' | head -1 || echo "")
    product=$(echo "$image_path" | sed -n 's|.*/products/\([^/]*\)/.*|\1|p')
    campaign=$(echo "$image_path" | sed -n 's|.*/campaigns/\([^/]*\)/.*|\1|p')
    aspect_ratio=$(echo "$image_path" | sed -n 's|.*/products/[^/]*/\([^/]*\)/.*|\1|p')
    
    # Use relative path that will work with HTTP server
    url_path="/$rel_path"
    
    IMAGE_PATHS+=("$rel_path")
    IMAGE_DATA+=("$timestamp|$product|$campaign|$url_path|$aspect_ratio")
    
    # Collect unique values for filters
    [ -n "$campaign" ] && echo "$campaign" >> "$TEMP_CAMPAIGNS"
    [ -n "$product" ] && echo "$product" >> "$TEMP_PRODUCTS"
    [ -n "$aspect_ratio" ] && echo "$aspect_ratio" >> "$TEMP_ASPECTS"
done <<< "$IMAGES"

# Get sorted unique values
UNIQUE_CAMPAIGNS=($(sort -u "$TEMP_CAMPAIGNS" 2>/dev/null || true))
UNIQUE_PRODUCTS=($(sort -u "$TEMP_PRODUCTS" 2>/dev/null || true))
UNIQUE_ASPECT_RATIOS=($(sort -u "$TEMP_ASPECTS" 2>/dev/null || true))

# Clean up temp files
rm -f "$TEMP_CAMPAIGNS" "$TEMP_PRODUCTS" "$TEMP_ASPECTS"

# If no arguments provided, show interactive filter selection
if [ -z "$CAMPAIGN_PREFIX" ] && [ -z "$ASPECT_RATIO" ]; then
    echo "📋 Available filter options:"
    echo ""
    
    # Campaign selection
    echo "Campaigns:"
    echo "   0) any"
    i=1
    for campaign in "${UNIQUE_CAMPAIGNS[@]}"; do
        echo "   $i) $campaign"
        ((i++))
    done
    echo ""
    read -p "Select Campaign (0-$((${#UNIQUE_CAMPAIGNS[@]}))): " campaign_choice
    if [ "$campaign_choice" = "0" ] || [ -z "$campaign_choice" ]; then
        SELECTED_CAMPAIGN="any"
    elif [ "$campaign_choice" -ge 1 ] && [ "$campaign_choice" -le ${#UNIQUE_CAMPAIGNS[@]} ]; then
        SELECTED_CAMPAIGN="${UNIQUE_CAMPAIGNS[$((campaign_choice-1))]}"
    else
        SELECTED_CAMPAIGN="any"
    fi
    echo "   Selected: $SELECTED_CAMPAIGN"
    echo ""
    
    # Product selection
    echo "Products:"
    echo "   0) any"
    i=1
    for product in "${UNIQUE_PRODUCTS[@]}"; do
        echo "   $i) $product"
        ((i++))
    done
    echo ""
    read -p "Select Product (0-$((${#UNIQUE_PRODUCTS[@]}))): " product_choice
    if [ "$product_choice" = "0" ] || [ -z "$product_choice" ]; then
        SELECTED_PRODUCT="any"
    elif [ "$product_choice" -ge 1 ] && [ "$product_choice" -le ${#UNIQUE_PRODUCTS[@]} ]; then
        SELECTED_PRODUCT="${UNIQUE_PRODUCTS[$((product_choice-1))]}"
    else
        SELECTED_PRODUCT="any"
    fi
    echo "   Selected: $SELECTED_PRODUCT"
    echo ""
    
    # Aspect Ratio selection
    echo "Aspect Ratios:"
    echo "   0) any"
    i=1
    for aspect in "${UNIQUE_ASPECT_RATIOS[@]}"; do
        echo "   $i) $aspect"
        ((i++))
    done
    echo ""
    read -p "Select Aspect Ratio (0-$((${#UNIQUE_ASPECT_RATIOS[@]}))): " aspect_choice
    if [ "$aspect_choice" = "0" ] || [ -z "$aspect_choice" ]; then
        SELECTED_ASPECT="any"
    elif [ "$aspect_choice" -ge 1 ] && [ "$aspect_choice" -le ${#UNIQUE_ASPECT_RATIOS[@]} ]; then
        SELECTED_ASPECT="${UNIQUE_ASPECT_RATIOS[$((aspect_choice-1))]}"
    else
        SELECTED_ASPECT="any"
    fi
    echo "   Selected: $SELECTED_ASPECT"
    echo ""
    
    # Status selection
    echo "Status:"
    echo "   0) any"
    echo "   1) keeps"
    echo "   2) deletes"
    echo ""
    read -p "Select Status (0-2): " status_choice
    case "$status_choice" in
        0|"")
            SELECTED_STATUS="any"
            ;;
        1)
            SELECTED_STATUS="keeps"
            ;;
        2)
            SELECTED_STATUS="deletes"
            ;;
        *)
            SELECTED_STATUS="any"
            ;;
    esac
    echo "   Selected: $SELECTED_STATUS"
    echo ""
    
    echo "📊 Selected filters:"
    echo "   Campaign: $SELECTED_CAMPAIGN"
    echo "   Product: $SELECTED_PRODUCT"
    echo "   Aspect: $SELECTED_ASPECT"
    echo "   Status: $SELECTED_STATUS"
    echo ""
    read -p "Press Enter to open slideshow with these filters, or Ctrl+C to cancel... "
    echo ""
    
    # Set the selected values for use in the HTML generation
    CAMPAIGN_PREFIX="$SELECTED_CAMPAIGN"
    ASPECT_RATIO="$SELECTED_ASPECT"
    SELECTED_PRODUCT_FILTER="$SELECTED_PRODUCT"
    SELECTED_STATUS_FILTER="$SELECTED_STATUS"
else
    # Arguments provided - use them for filters
    if [ -n "$CAMPAIGN_PREFIX" ]; then
        SELECTED_CAMPAIGN="$CAMPAIGN_PREFIX"
    fi
    if [ -n "$ASPECT_RATIO" ]; then
        SELECTED_ASPECT="$ASPECT_RATIO"
    fi
fi

echo "📝 Generating standalone HTML with embedded scrolling logic..."

# Generate standalone HTML with all logic embedded
cat > "$STANDALONE_HTML" << 'STANDALONE_HTML_HEAD'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Campaign Slideshow</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        html, body {
            height: 100%;
            overflow: hidden;
            background-color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        #main-container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            width: 100%;
            gap: 0;
        }
        
        .status-bar {
            flex-shrink: 0;
            background: white;
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #ccc;
            z-index: 10000;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            flex-wrap: wrap;
            gap: 15px;
        }
        
        #wrapper-div {
            flex: 1;
            position: relative;
            width: 100%;
            overflow: hidden;
            pointer-events: auto;
            touch-action: none;
            min-height: 0;
        }
        
        #html-content-div {
            position: relative;
            will-change: transform;
        }
        
        .status-left {
            display: flex;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .status-counts {
            display: flex;
            gap: 20px;
            font-size: 13px;
        }
        
        .filters {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .filter-group {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .filter-group label {
            font-size: 12px;
            color: #666;
            font-weight: 500;
        }
        
        .filter-group select {
            padding: 4px 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 12px;
            background: white;
            cursor: pointer;
        }
        
        .filter-group select:hover {
            border-color: #999;
        }
        
        .status-right {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .count {
            display: flex;
            align-items: center;
            gap: 5px;
            color: black;
        }
        
        .export-btn {
            background: #4a9eff;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
        }
        
        .export-btn:hover {
            background: #3a8eef;
        }
        
        .admin {
            --spacing: 1rem;
            display: grid;
            width: 100%;
            min-height: 100%;
            padding: var(--spacing);
            grid-template-rows: 1fr;
            grid-template-columns: 1fr;
            grid-template-areas: "main";
            background-color: white;
        }
        
        .admin__main {
            grid-area: main;
        }
        
        .dashboard {
            --column-count: 1;
            display: grid;
            grid-template-columns: repeat(var(--column-count), 1fr);
            grid-gap: var(--spacing);
            margin: 0;
        }
        
        @media screen and (min-width: 48rem) {
            .dashboard {
                --column-count: 2;
            }
        }
        
        .dashboard__item {
            grid-column-end: span 1;
            padding: calc(var(--spacing) / 2);
            width: 100%;
            box-sizing: border-box;
            min-width: 0;
            background: #ffffff;
            overflow: visible;
        }
        
        .image-card {
            position: relative;
            background: #ffffff;
            color: #000000;
            border: 3px solid #4CAF50;
            border-radius: 8px;
            overflow: visible;
            width: 100%;
            box-sizing: border-box;
            transition: transform 0.2s, border-color 0.2s, opacity 0.2s, box-shadow 0.2s;
            margin: 2px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            display: block;
            opacity: 1;
        }
        
        .image-card.marked-delete,
        .dashboard__item .image-card.marked-delete {
            border: 6px solid #ff0000 !important;
            box-shadow: 0 0 0 4px rgba(255, 0, 0, 0.3), 0 0 20px rgba(255, 0, 0, 0.5) !important;
            opacity: 0.6 !important;
            background: #fff5f5 !important;
        }
        
        .image-card:hover {
            transform: translateY(-2px);
        }
        
        .image-container {
            position: relative;
            width: 100%;
            padding-top: 100%;
            background: #ffffff;
            overflow: hidden;
            border-radius: 5px 5px 0 0;
        }
        
        .image-container img {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: contain;
        }
        
        .image-info {
            padding: 0;
            background: #ffffff;
            color: #000000;
            display: flex;
            flex-direction: column;
            width: 100%;
            box-sizing: border-box;
            overflow-wrap: break-word;
        }
        
        .text-fields {
            display: flex;
            flex-direction: column;
            gap: 5px;
            margin-bottom: 15px;
            width: 100%;
            box-sizing: border-box;
            overflow-wrap: break-word;
            background: #ffffff;
            color: #000000;
            padding: 12px;
            border-radius: 4px;
            border: 2px solid #cccccc;
            min-height: 80px;
        }
        
        .campaign-name {
            font-size: 12px;
            color: #000000;
            background: #ffffff;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .product-name {
            font-size: 12px;
            color: #000000;
            background: #ffffff;
            font-weight: 500;
        }
        
        .aspect-ratio {
            font-size: 12px;
            color: #000000;
            background: #ffffff;
        }
        
        .timestamp {
            font-size: 12px;
            color: #000000;
            background: #ffffff;
        }
        
        .image-path {
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
            font-size: 12px;
            color: #000000;
            background: #ffffff;
            word-break: break-all;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-top: auto;
        }
        
        .btn {
            flex: 1;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .btn-delete {
            background: #f44336;
            color: white;
        }
        
        .btn-delete:hover {
            background: #da190b;
        }
        
        .btn-delete.active {
            background: #c62828;
            box-shadow: 0 0 10px rgba(244, 67, 54, 0.5);
        }
    </style>
</head>
<body>
    <div id="main-container">
        <div class="status-bar">
            <div class="status-left">
                <div class="status-counts">
                    <div class="count count-deletes">
                        <span>❌ Deletes:</span>
                        <strong id="deleteCount">0</strong>
                    </div>
                    <div class="count count-remaining">
                        <span>📋 Keeps:</span>
                        <strong id="remainingCount">0</strong>
                    </div>
                </div>
                <div class="filters">
                    <div class="filter-group">
                        <label for="filter-campaign">Campaign:</label>
                        <select id="filter-campaign">
                            <option value="any">any</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label for="filter-product">Product:</label>
                        <select id="filter-product">
                            <option value="any">any</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label for="filter-aspect">Aspect:</label>
                        <select id="filter-aspect">
                            <option value="any">any</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label for="filter-status">Status:</label>
                        <select id="filter-status">
                            <option value="any">Any</option>
                            <option value="keeps">Keeps</option>
                            <option value="deletes">Deletes</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="status-right">
                <button class="export-btn" id="export-results-btn">💾 Export Campaigns</button>
            </div>
        </div>
        
        <div id="wrapper-div">
        <div id="html-content-div">
            <div class="admin">
                <main class="admin__main">
                    <div class="dashboard" id="dashboard">
STANDALONE_HTML_HEAD

# Generate filter options JavaScript
cat >> "$STANDALONE_HTML" << FILTER_OPTIONS_JS
    <script>
        // Filter options data
        const filterOptions = {
            campaigns: [
FILTER_OPTIONS_JS

# Add campaign options
for campaign in "${UNIQUE_CAMPAIGNS[@]}"; do
    safe_campaign=$(echo "$campaign" | sed "s/'/\\\'/g; s/\"/\\\"/g")
    cat >> "$STANDALONE_HTML" << FILTER_OPTIONS_JS
                "$safe_campaign",
FILTER_OPTIONS_JS
done

cat >> "$STANDALONE_HTML" << FILTER_OPTIONS_JS
            ],
            products: [
FILTER_OPTIONS_JS

# Add product options
for product in "${UNIQUE_PRODUCTS[@]}"; do
    safe_product=$(echo "$product" | sed "s/'/\\\'/g; s/\"/\\\"/g")
    cat >> "$STANDALONE_HTML" << FILTER_OPTIONS_JS
                "$safe_product",
FILTER_OPTIONS_JS
done

cat >> "$STANDALONE_HTML" << FILTER_OPTIONS_JS
            ],
            aspectRatios: [
FILTER_OPTIONS_JS

# Add aspect ratio options
for aspect in "${UNIQUE_ASPECT_RATIOS[@]}"; do
    safe_aspect=$(echo "$aspect" | sed "s/'/\\\'/g; s/\"/\\\"/g")
    cat >> "$STANDALONE_HTML" << FILTER_OPTIONS_JS
                "$safe_aspect",
FILTER_OPTIONS_JS
done

cat >> "$STANDALONE_HTML" << FILTER_OPTIONS_JS
            ]
        };
        
        // Selected filter values from command line
        const selectedFilters = {
            campaign: "${SELECTED_CAMPAIGN:-any}",
            product: "${SELECTED_PRODUCT_FILTER:-any}",
            aspect: "${SELECTED_ASPECT:-any}",
            status: "${SELECTED_STATUS_FILTER:-any}"
        };
    </script>
FILTER_OPTIONS_JS

# Add image cards
for i in "${!IMAGE_PATHS[@]}"; do
    rel_path="${IMAGE_PATHS[$i]}"
    IFS='|' read -r timestamp product campaign url_path aspect_ratio <<< "${IMAGE_DATA[$i]}"
    
    if [ -n "$timestamp" ]; then
        formatted_timestamp=$(echo "$timestamp" | sed 's/\([0-9]\{8\}\)_\([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)/\1 \2:\3:\4/')
    else
        formatted_timestamp="No timestamp"
    fi
    
    safe_path=$(echo "$rel_path" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')
    safe_aspect=$(echo "$aspect_ratio" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')
    
    cat >> "$STANDALONE_HTML" << STANDALONE_CARD
                        <div class="dashboard__item" data-path="$safe_path" data-timestamp="$timestamp" data-product="$product" data-campaign="$campaign" data-aspect-ratio="$safe_aspect">
                            <div class="image-card" id="card-$i">
                                <div class="image-container">
                                    <img src="$url_path" alt="$product" loading="lazy">
                                </div>
                                <div class="image-info">
                                    <div class="text-fields">
                                        <div class="campaign-name">campaign: $campaign</div>
                                        <div class="product-name">product: $product</div>
                                        <div class="aspect-ratio">aspect_ratio: $safe_aspect</div>
                                        <div class="timestamp">timestamp: $formatted_timestamp</div>
                                        <div class="image-path">product_image_path: $safe_path</div>
                                    </div>
                                    <div class="controls">
                                        <button class="btn btn-delete" data-action="delete" data-index="$i" data-path="$safe_path">🗑️ Delete</button>
                                    </div>
                                </div>
                            </div>
                        </div>
STANDALONE_CARD
done

# Add JavaScript with embedded scrolling logic
cat >> "$STANDALONE_HTML" << 'STANDALONE_JS'
                    </div>
                </main>
            </div>
        </div>
        </div>
    </div>
    
    <script>
        // ===== SCROLLING LOGIC (extracted from dual-layer slider) =====
        class SmoothScroller {
            constructor(wrapperDiv, contentDiv) {
                this.wrapperDiv = wrapperDiv;
                this.contentDiv = contentDiv;
                this.current_velocity = 0;
                this.last_translate_y = null;
                this.translate_y_min = null;
                this.translate_y_max = null;
                this.animation_frame_id = null;
                this.is_window_focused = true;
                
                this.setupEventListeners();
            }
            
            setupEventListeners() {
                // Use document-level listener with capture to catch all scroll events
                const handleWheel = (e) => {
                    // Only handle if event is within our wrapper or on the wrapper itself
                    const target = e.target;
                    if (this.wrapperDiv.contains(target) || target === this.wrapperDiv || target === document.body || target === document.documentElement) {
                        this.handleScroll(e);
                    }
                };
                
                // Add to document with capture phase to catch events early
                document.addEventListener('wheel', handleWheel, { passive: false, capture: true });
                
                // Also add to window as fallback
                window.addEventListener('wheel', handleWheel, { passive: false, capture: true });
                
                window.addEventListener('blur', () => {
                    this.is_window_focused = false;
                    if (this.animation_frame_id !== null) {
                        cancelAnimationFrame(this.animation_frame_id);
                        this.animation_frame_id = null;
                    }
                    this.current_velocity = 0;
                });
                
                window.addEventListener('focus', () => {
                    this.is_window_focused = true;
                });
                
                document.addEventListener('visibilitychange', () => {
                    if (document.hidden) {
                        this.is_window_focused = false;
                        if (this.animation_frame_id !== null) {
                            cancelAnimationFrame(this.animation_frame_id);
                            this.animation_frame_id = null;
                        }
                        this.current_velocity = 0;
                    } else {
                        this.is_window_focused = true;
                    }
                });
                
                window.addEventListener('resize', () => this.updateScrollLimits());
            }
            
            setScrollTopLimits(min, max) {
                this.scroll_top_min = min;
                this.scroll_top_max = max;
            }
            
            updateScrollLimits() {
                setTimeout(() => {
                    const rect = this.contentDiv.getBoundingClientRect();
                    const contentHeight = rect.height;
                    // Wrapper div height is now the viewport (since status bar is a sibling in flex layout)
                    const wrapperRect = this.wrapperDiv.getBoundingClientRect();
                    const viewportHeight = wrapperRect.height;
                    
                    // Content starts at translateY = 0 (top of content at top of wrapper)
                    // Scrolling down (wheel down, deltaY > 0) moves content up (translateY becomes negative)
                    // Scrolling up (wheel up, deltaY < 0) moves content down (translateY becomes positive)
                    // 
                    // Since status bar is now a sibling, we don't need topOffset
                    const topOffset = 0;
                    
                    // If content is shorter than viewport, no scrolling needed
                    if (contentHeight <= viewportHeight) {
                        this.translate_y_min = 0;
                        this.translate_y_max = 0;
                    } else {
                        // min is the most negative (scrolled all the way down to see bottom of last row)
                        // max is the most positive (scrolled all the way up to see top of first row)
                        // 
                        // To see full first row: allow positive translateY (scroll up)
                        // To see full last row: allow more negative translateY (scroll down)
                        // 
                        // Calculate the difference between content and viewport
                        const scrollRange = contentHeight - viewportHeight;
                        
                        // Allow extra scrolling to see full first and last rows
                        // Positive max allows scrolling up to see top of first row
                        // More negative min allows scrolling down to see bottom of last row
                        // 
                        // Get actual padding from admin div to account for spacing
                        const adminDiv = document.querySelector('.admin');
                        const adminPaddingTop = adminDiv ? parseFloat(window.getComputedStyle(adminDiv).paddingTop) || 16 : 16;
                        const adminPaddingBottom = adminDiv ? parseFloat(window.getComputedStyle(adminDiv).paddingBottom) || 16 : 16;
                        const extraScroll = 30; // Extra pixels to ensure full visibility
                        const excessTop = 40; // Remove 40px excess at top
                        const excessBottom = 40; // Remove 40px excess at bottom
                        
                        // Reduce max by 40px to remove top excess (less positive = less scrolling up)
                        // Increase min by 40px to remove bottom excess (less negative = less scrolling down)
                        this.translate_y_max = adminPaddingTop + extraScroll - excessTop;
                        this.translate_y_min = -(scrollRange + adminPaddingBottom + extraScroll - excessBottom);
                    }
                    
                    console.log('Scroll limits updated:', {
                        min: this.translate_y_min,
                        max: this.translate_y_max,
                        contentHeight: contentHeight,
                        viewportHeight: viewportHeight,
                        wrapperHeight: wrapperRect.height
                    });
                }, 100);
            }
            
            handleScroll(event) {
                event.preventDefault();
                event.stopPropagation();
                
                // Get current translateY
                if (this.last_translate_y === null) {
                    const transform = window.getComputedStyle(this.contentDiv).transform;
                    if (transform && transform !== 'none') {
                        const matrix = transform.match(/matrix\([^)]+\)/);
                        if (matrix) {
                            const values = matrix[0].match(/-?\d+\.?\d*/g);
                            if (values && values.length >= 6) {
                                this.last_translate_y = parseFloat(values[5]);
                            }
                        }
                    }
                    if (this.last_translate_y === null) {
                        this.last_translate_y = 0;
                    }
                }
                
                // Direct scroll: scroll down (deltaY > 0) moves content up (negative translateY)
                // scroll up (deltaY < 0) moves content down (positive translateY)
                const scroll_delta = -event.deltaY * 0.5; // Direct scroll, no velocity accumulation
                const old_translate_y = this.last_translate_y;
                let new_translate_y = old_translate_y + scroll_delta;
                
                // Clamp to limits
                if (this.translate_y_min !== null && this.translate_y_min !== undefined) {
                    new_translate_y = Math.max(new_translate_y, this.translate_y_min);
                }
                if (this.translate_y_max !== null && this.translate_y_max !== undefined) {
                    new_translate_y = Math.min(new_translate_y, this.translate_y_max);
                }
                
                // Apply transform immediately
                this.contentDiv.style.transform = `translateY(${new_translate_y}px)`;
                this.last_translate_y = new_translate_y;
            }
        }
        
        // ===== CAMPAIGN SLIDESHOW FUNCTIONALITY =====
        const marks = {
            deletes: new Set()
        };
        
        let totalImages = 0;
        let scroller = null;
        
        function updateTotalImages() {
            // Only count visible items (after filtering)
            const visibleItems = Array.from(document.querySelectorAll('.dashboard__item')).filter(
                item => item.style.display !== 'none'
            );
            totalImages = visibleItems.length;
        }
        
        function updateCounts() {
            // Count deletes only from visible items
            const visibleItems = Array.from(document.querySelectorAll('.dashboard__item')).filter(
                item => item.style.display !== 'none'
            );
            const visibleDeletes = visibleItems.filter(item => 
                marks.deletes.has(item.dataset.path)
            ).length;
            
            document.getElementById('deleteCount').textContent = visibleDeletes;
            const remaining = totalImages - visibleDeletes;
            document.getElementById('remainingCount').textContent = remaining;
        }
        
        // Get campaign ID from image path
        function getCampaignIdFromPath(path) {
            // Path format: outputs/campaigns/<campaign_id>/products/...
            const match = path.match(/outputs\/campaigns\/([^\/]+)\//);
            return match ? match[1] : null;
        }
        
        // Load status from all status.json files (single source of truth)
        async function loadState() {
            try {
                marks.deletes = new Set();
                let loadedFromFiles = false;
                
                // Get all unique campaign IDs from images
                const allItems = document.querySelectorAll('.dashboard__item[data-path]');
                const campaignIds = new Set();
                allItems.forEach(item => {
                    const campaignId = getCampaignIdFromPath(item.dataset.path);
                    if (campaignId) campaignIds.add(campaignId);
                });
                
                // Load status from each campaign's status.json (single source of truth)
                for (const campaignId of campaignIds) {
                    try {
                        const statusPath = `outputs/campaigns/${campaignId}/status.json`;
                        const response = await fetch(statusPath);
                        if (response.ok) {
                            const statusData = await response.json();
                            loadedFromFiles = true;
                            
                            // Process deletes
                            if (statusData.deletes && Array.isArray(statusData.deletes)) {
                                statusData.deletes.forEach(path => {
                                    marks.deletes.add(path);
                                    
                                    // Apply visual styles
                                    const card = document.querySelector(`[data-path="${path}"] .image-card`);
                                    if (card) {
                                        card.classList.add('marked-delete');
                                        card.style.border = '6px solid #ff0000';
                                        card.style.boxShadow = '0 0 0 4px rgba(255, 0, 0, 0.3), 0 0 20px rgba(255, 0, 0, 0.5)';
                                        card.style.opacity = '0.6';
                                        card.style.background = '#fff5f5';
                                        const deleteBtn = card.querySelector('.btn-delete');
                                        if (deleteBtn) {
                                            deleteBtn.classList.add('active');
                                            deleteBtn.textContent = 'MARKED FOR DELETION';
                                        }
                                    }
                                });
                            }
                        }
                    } catch (e) {
                        // Campaign status.json doesn't exist yet, that's okay
                        console.log(`No status.json found for campaign: ${campaignId}`);
                    }
                }
                
                // Fallback to localStorage if no status.json files found
                if (!loadedFromFiles) {
                    const saved = localStorage.getItem('campaignSlideshowState');
                    if (saved) {
                        const state = JSON.parse(saved);
                        if (state.deletes && Array.isArray(state.deletes)) {
                            state.deletes.forEach(path => {
                                marks.deletes.add(path);
                                
                                // Apply visual styles
                                const card = document.querySelector(`[data-path="${path}"] .image-card`);
                                if (card) {
                                    card.classList.add('marked-delete');
                                    card.style.border = '6px solid #ff0000';
                                    card.style.boxShadow = '0 0 0 4px rgba(255, 0, 0, 0.3), 0 0 20px rgba(255, 0, 0, 0.5)';
                                    card.style.opacity = '0.6';
                                    card.style.background = '#fff5f5';
                                    const deleteBtn = card.querySelector('.btn-delete');
                                    if (deleteBtn) {
                                        deleteBtn.classList.add('active');
                                        deleteBtn.textContent = 'MARKED FOR DELETION';
                                    }
                                }
                            });
                        }
                    }
                }
            } catch (e) {
                console.error('Error loading state:', e);
            }
            updateCounts();
        }
        
        // Save status to localStorage (cache)
        function saveState() {
            try {
                // Save to localStorage as cache
                const state = {
                    deletes: Array.from(marks.deletes),
                    timestamp: new Date().toISOString()
                };
                localStorage.setItem('campaignSlideshowState', JSON.stringify(state));
            } catch (e) {
                console.error('Error saving state:', e);
            }
        }
        
        window.markDelete = function(index, path) {
            const card = document.getElementById(`card-${index}`);
            if (!card) {
                return;
            }
            
            const deleteBtn = card.querySelector('.btn-delete');
            
            if (marks.deletes.has(path)) {
                marks.deletes.delete(path);
                card.classList.remove('marked-delete');
                // Remove inline styles
                card.style.border = '';
                card.style.boxShadow = '';
                card.style.opacity = '';
                card.style.background = '';
                if (deleteBtn) {
                    deleteBtn.classList.remove('active');
                    deleteBtn.textContent = '🗑️ Delete';
                }
            } else {
                marks.deletes.add(path);
                card.classList.add('marked-delete');
                // Apply inline styles as fallback
                card.style.border = '6px solid #ff0000';
                card.style.boxShadow = '0 0 0 4px rgba(255, 0, 0, 0.3), 0 0 20px rgba(255, 0, 0, 0.5)';
                card.style.opacity = '0.6';
                card.style.background = '#fff5f5';
                if (deleteBtn) {
                    deleteBtn.classList.add('active');
                    deleteBtn.textContent = 'MARKED FOR DELETION';
                }
            }
            
            // Force a reflow to ensure styles apply
            card.offsetHeight;
            
            updateCounts();
            saveState();
        };
        
        window.exportResults = function() {
            // Get only visible dashboard items (after filtering)
            const allItems = Array.from(document.querySelectorAll('.dashboard__item[data-path]')).filter(
                item => item.style.display !== 'none'
            );
            
            // Group images by campaign ID
            const campaignStatuses = {};
            
            allItems.forEach(item => {
                const path = item.dataset.path;
                const campaignId = getCampaignIdFromPath(path);
                const isDeleted = marks.deletes.has(path);
                
                if (campaignId) {
                    if (!campaignStatuses[campaignId]) {
                        campaignStatuses[campaignId] = { deletes: [] };
                    }
                    
                    // Only add to deletes array if marked for deletion
                    // All images not in deletes are considered "keeps"
                    if (isDeleted) {
                        campaignStatuses[campaignId].deletes.push(path);
                    }
                }
            });
            
            // Export one status.json file per campaign
            let downloaded = 0;
            const downloadedFiles = [];
            
            for (const [campaignId, statusData] of Object.entries(campaignStatuses)) {
                const blob = new Blob([JSON.stringify(statusData, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `outputs/campaigns/${campaignId}/status.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                downloaded++;
                downloadedFiles.push(`outputs/campaigns/${campaignId}/status.json`);
            }
            
            // Get the typical Downloads path (browser-dependent, but show what we know)
            const downloadsPath = navigator.platform.toLowerCase().includes('mac') 
                ? '~/Downloads/' 
                : navigator.platform.toLowerCase().includes('win')
                ? '%USERPROFILE%\\Downloads\\'
                : '~/Downloads/';
            
            const filesList = downloadedFiles.join('\n');
            alert(`Exported ${downloaded} campaign status.json file(s)!\n\nFiles:\n${filesList}\n\nPlease save them to the correct locations in your project.`);
        };
        
        // Initialize
        document.addEventListener('DOMContentLoaded', async () => {
            const wrapperDiv = document.getElementById('wrapper-div');
            const contentDiv = document.getElementById('html-content-div');
            
            if (!wrapperDiv || !contentDiv) {
                return;
            }
            
            // Initialize scroller
            scroller = new SmoothScroller(wrapperDiv, contentDiv);
            
            // Initialize translateY to show full top row
            // Status bar is now a sibling in flex layout, so wrapper starts below it
            // Start at max position to show full top of first row
            const initialTranslateY = 0;
            contentDiv.style.transform = `translateY(${initialTranslateY}px)`;
            scroller.last_translate_y = initialTranslateY;
            
            // Update scroll limits after content loads
            setTimeout(() => {
                scroller.updateScrollLimits();
                // Start at max position to show full top of first row
                const maxTranslateY = scroller.translate_y_max !== null ? scroller.translate_y_max : initialTranslateY;
                contentDiv.style.transform = `translateY(${maxTranslateY}px)`;
                scroller.last_translate_y = maxTranslateY;
            }, 500);
            
            // Initialize slideshow
            updateTotalImages();
            await loadState(); // Load status from status.json files (single source of truth)
            
            // Initialize filters
            function populateFilters() {
                const campaignSelect = document.getElementById('filter-campaign');
                const productSelect = document.getElementById('filter-product');
                const aspectSelect = document.getElementById('filter-aspect');
                
                // Populate campaign filter
                filterOptions.campaigns.forEach(campaign => {
                    const option = document.createElement('option');
                    option.value = campaign;
                    option.textContent = campaign;
                    campaignSelect.appendChild(option);
                });
                
                // Populate product filter
                filterOptions.products.forEach(product => {
                    const option = document.createElement('option');
                    option.value = product;
                    option.textContent = product;
                    productSelect.appendChild(option);
                });
                
                // Populate aspect ratio filter
                filterOptions.aspectRatios.forEach(aspect => {
                    const option = document.createElement('option');
                    option.value = aspect;
                    option.textContent = aspect;
                    aspectSelect.appendChild(option);
                });
                
                // Set initial values from selectedFilters (command line selections) or URL params
                const urlParams = new URLSearchParams(window.location.search);
                const initialCampaign = urlParams.get('campaign') || selectedFilters.campaign || 'any';
                const initialProduct = urlParams.get('product') || selectedFilters.product || 'any';
                const initialAspect = urlParams.get('aspect') || selectedFilters.aspect || 'any';
                const initialStatus = urlParams.get('status') || selectedFilters.status || 'any';
                
                campaignSelect.value = initialCampaign;
                productSelect.value = initialProduct;
                aspectSelect.value = initialAspect;
                document.getElementById('filter-status').value = initialStatus;
            }
            
            function applyFilters() {
                const campaignFilter = document.getElementById('filter-campaign').value;
                const productFilter = document.getElementById('filter-product').value;
                const aspectFilter = document.getElementById('filter-aspect').value;
                const statusFilter = document.getElementById('filter-status').value;
                
                const allItems = document.querySelectorAll('.dashboard__item');
                let visibleCount = 0;
                
                allItems.forEach(item => {
                    const campaign = item.dataset.campaign || '';
                    const product = item.dataset.product || '';
                    const aspect = item.dataset.aspectRatio || '';
                    const path = item.dataset.path || '';
                    const isDeleted = marks.deletes.has(path);
                    
                    const matchesCampaign = !campaignFilter || campaignFilter === 'any' || campaign === campaignFilter;
                    const matchesProduct = !productFilter || productFilter === 'any' || product === productFilter;
                    const matchesAspect = !aspectFilter || aspectFilter === 'any' || aspect === aspectFilter;
                    
                    // Status filter: "any", "keeps", or "deletes"
                    let matchesStatus = true;
                    if (statusFilter === 'keeps') {
                        matchesStatus = !isDeleted;
                    } else if (statusFilter === 'deletes') {
                        matchesStatus = isDeleted;
                    }
                    // else statusFilter === 'any', so matchesStatus stays true
                    
                    if (matchesCampaign && matchesProduct && matchesAspect && matchesStatus) {
                        item.style.display = '';
                        visibleCount++;
                    } else {
                        item.style.display = 'none';
                    }
                });
                
                // Update counts based on visible items
                updateTotalImages();
                updateCounts();
                
                // Update scroll limits after filtering
                setTimeout(() => {
                    scroller.updateScrollLimits();
                }, 100);
            }
            
            populateFilters();
            applyFilters();
            
            // Add filter change listeners
            document.getElementById('filter-campaign').addEventListener('change', applyFilters);
            document.getElementById('filter-product').addEventListener('change', applyFilters);
            document.getElementById('filter-aspect').addEventListener('change', applyFilters);
            document.getElementById('filter-status').addEventListener('change', applyFilters);
            
            // Event delegation for buttons
            document.addEventListener('click', (e) => {
                const btn = e.target.closest('.btn-delete');
                if (btn) {
                    e.preventDefault();
                    const action = btn.dataset.action;
                    const index = parseInt(btn.dataset.index);
                    const path = btn.dataset.path;
                    
                    if (action === 'delete') {
                        window.markDelete(index, path);
                    }
                }
                
                if (e.target.id === 'export-results-btn') {
                    e.preventDefault();
                    window.exportResults();
                }
            });
        });
    </script>
</body>
</html>
STANDALONE_JS

echo "✅ Refine campaigns HTML generated: $STANDALONE_HTML"
echo ""

# Find available port
PORT=8000
while lsof -ti:${PORT} >/dev/null 2>&1; do
    PORT=$((PORT + 1))
done

echo "🚀 Starting HTTP server on port $PORT..."
echo "   Serving from: $CAMPAIGN_DIR"
echo "   Open: http://localhost:${PORT}/refine_campaigns.html"
echo "   Press Ctrl+C to stop"
echo ""

# Start server in background
cd "$CAMPAIGN_DIR"
if command -v python3 >/dev/null 2>&1; then
    python3 -m http.server "$PORT" >/dev/null 2>&1 &
    SERVER_PID=$!
    sleep 2
    if command -v open >/dev/null 2>&1; then
        open "http://localhost:${PORT}/refine_campaigns.html"
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "http://localhost:${PORT}/refine_campaigns.html"
    fi
    wait $SERVER_PID
elif command -v python >/dev/null 2>&1; then
    python -m SimpleHTTPServer "$PORT" >/dev/null 2>&1 &
    SERVER_PID=$!
    sleep 2
    if command -v open >/dev/null 2>&1; then
        open "http://localhost:${PORT}/refine_campaigns.html"
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "http://localhost:${PORT}/refine_campaigns.html"
    fi
    wait $SERVER_PID
else
    echo "⚠️  Python not found. Please start a server manually:"
    echo "   cd $CAMPAIGN_DIR"
    echo "   python3 -m http.server $PORT"
    echo "   Then open: http://localhost:${PORT}/refine_campaigns.html"
fi


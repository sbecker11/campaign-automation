#!/bin/bash

# View images from timestamped campaign runs
# Creates an HTML gallery showing images with their timestamped paths
#
# Usage:
#   ./view_timestamped_squares.sh                           # View 1x1 images from all campaigns
#   ./view_timestamped_squares.sh 1x1                       # View 1x1 images (explicit)
#   ./view_timestamped_squares.sh 9x16                      # View 9x16 images
#   ./view_timestamped_squares.sh 16x9                      # View 16x9 images
#   ./view_timestamped_squares.sh summer_2024               # View 1x1 images from specific campaign
#   ./view_timestamped_squares.sh summer_2024 1x1           # View 1x1 images from specific campaign

set -e

# Parse arguments
ASPECT_RATIO="1x1"  # Default to 1x1
CAMPAIGN_FILTER=""

# Check if first argument is an aspect ratio
if [[ "$1" =~ ^[0-9]+x[0-9]+$ ]]; then
    ASPECT_RATIO="$1"
    CAMPAIGN_FILTER="${2:-}"
else
    # First argument is campaign filter (or empty)
    CAMPAIGN_FILTER="${1:-}"
    # Second argument might be aspect ratio
    if [[ "$2" =~ ^[0-9]+x[0-9]+$ ]]; then
        ASPECT_RATIO="$2"
    fi
fi

# Output directory
OUTPUT_DIR="outputs/campaigns"
GALLERY_FILE="outputs/timestamped_squares_gallery.html"

# Check if output directory exists
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "No outputs found. Generate first:"
    echo "  ./scripts/generate_campaign.sh --timestamp current"
    exit 1
fi

echo "🔍 Finding all ${ASPECT_RATIO} images from timestamped runs..."

# Find images with specified aspect ratio in timestamped directories
if [ -z "$CAMPAIGN_FILTER" ]; then
    IMAGES=$(find "$OUTPUT_DIR" -path "*/${ASPECT_RATIO}/*.png" -type f | sort)
else
    IMAGES=$(find "$OUTPUT_DIR" -path "*/${CAMPAIGN_FILTER}_*/*/${ASPECT_RATIO}/*.png" -type f | sort)
fi

# Count images
IMAGE_COUNT=$(echo "$IMAGES" | grep -c . || echo "0")

if [ "$IMAGE_COUNT" -eq 0 ]; then
    echo "❌ No ${ASPECT_RATIO} images found"
    if [ -n "$CAMPAIGN_FILTER" ]; then
        echo "   Campaign filter: $CAMPAIGN_FILTER"
    fi
    echo "   Aspect ratio: ${ASPECT_RATIO}"
    echo ""
    echo "Make sure you've run campaigns with --timestamp flag:"
    echo "  ./generate_campaign.sh --timestamp"
    exit 1
fi

echo "   Found $IMAGE_COUNT ${ASPECT_RATIO} image(s)"
echo ""

# Create gallery directory
mkdir -p "$(dirname "$GALLERY_FILE")"

# Generate HTML gallery
cat > "$GALLERY_FILE" << HTML_HEADER
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Timestamped Campaign ${ASPECT_RATIO} Gallery</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #1a1a1a;
            color: #e0e0e0;
            padding: 20px;
        }
        .header {
            background: #2a2a2a;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        h1 {
            color: #4a9eff;
            margin-bottom: 10px;
        }
        .stats {
            color: #888;
            font-size: 14px;
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .image-card {
            background: #2a2a2a;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .image-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.6);
        }
        .image-container {
            position: relative;
            width: 100%;
            padding-top: 100%; /* 1:1 aspect ratio */
            background: #1a1a1a;
            overflow: hidden;
        }
        .image-container img {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: contain;
            cursor: pointer;
        }
        .image-info {
            padding: 15px;
        }
        .image-path {
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
            font-size: 11px;
            color: #4a9eff;
            word-break: break-all;
            margin-bottom: 8px;
            line-height: 1.4;
        }
        .image-timestamp {
            font-size: 12px;
            color: #888;
            margin-bottom: 5px;
        }
        .copy-btn {
            background: #4a9eff;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            margin-top: 5px;
            transition: background 0.2s;
        }
        .copy-btn:hover {
            background: #3a8eef;
        }
        .copy-btn:active {
            background: #2a7edf;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            cursor: pointer;
        }
        .modal-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            max-width: 90vw;
            max-height: 90vh;
        }
        .modal-content img {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }
        .close {
            position: absolute;
            top: 20px;
            right: 35px;
            color: #fff;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }
        .close:hover {
            color: #4a9eff;
        }
        .filter {
            margin-bottom: 20px;
        }
        .filter input {
            width: 100%;
            padding: 10px;
            background: #2a2a2a;
            border: 1px solid #444;
            border-radius: 4px;
            color: #e0e0e0;
            font-size: 14px;
        }
        .filter input:focus {
            outline: none;
            border-color: #4a9eff;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📸 Timestamped Campaign ${ASPECT_RATIO} Gallery</h1>
        <div class="stats" id="stats"></div>
    </div>
    <div class="filter">
        <input type="text" id="searchInput" placeholder="🔍 Search by timestamp, product, or path...">
    </div>
    <div class="gallery" id="gallery"></div>
    
    <div id="modal" class="modal">
        <span class="close">&times;</span>
        <div class="modal-content">
            <img id="modalImage" src="" alt="">
        </div>
    </div>

    <script>
        const images = [
HTML_HEADER

# Add each image to the gallery
while IFS= read -r image_path; do
    # Extract relative path from outputs/
    rel_path="${image_path#outputs/}"
    
    # Extract timestamp from path (format: campaign_id_YYYYMMDD_HHMMSS)
    timestamp=$(echo "$image_path" | grep -oE '[0-9]{8}_[0-9]{6}' | head -1 || echo "")
    
    # Extract product name
    product=$(echo "$image_path" | sed -n 's|.*/products/\([^/]*\)/.*|\1|p')
    
    # Extract campaign ID
    campaign=$(echo "$image_path" | sed -n 's|.*/campaigns/\([^/]*\)/.*|\1|p')
    
    # Convert to HTML-safe path (for display)
    html_path=$(echo "$rel_path" | sed 's|/|/|g')
    
    echo "            {"
    echo "                path: '$rel_path',"
    echo "                timestamp: '$timestamp',"
    echo "                product: '$product',"
    echo "                campaign: '$campaign'"
    echo "            },"
done <<< "$IMAGES"

cat >> "$GALLERY_FILE" << 'HTML_FOOTER'
        ];

        const gallery = document.getElementById('gallery');
        const stats = document.getElementById('stats');
        const modal = document.getElementById('modal');
        const modalImage = document.getElementById('modalImage');
        const closeBtn = document.querySelector('.close');
        const searchInput = document.getElementById('searchInput');

        function renderGallery(filteredImages) {
            gallery.innerHTML = '';
            stats.textContent = `Showing ${filteredImages.length} of ${images.length} images`;

            filteredImages.forEach((img, index) => {
                const card = document.createElement('div');
                card.className = 'image-card';
                
                const timestampDisplay = img.timestamp ? 
                    `🕐 ${img.timestamp.replace(/_/g, ' ').replace(/(\d{8}) (\d{2})(\d{2})(\d{2})/, '$1 $2:$3:$4')}` : 
                    'No timestamp';
                
                card.innerHTML = `
                    <div class="image-container">
                        <img src="${img.path}" alt="${img.product}" onclick="openModal('${img.path}')">
                    </div>
                    <div class="image-info">
                        <div class="image-timestamp">${timestampDisplay}</div>
                        <div class="image-timestamp">📦 ${img.product || 'Unknown'}</div>
                        <div class="image-path" id="path-${index}">${img.path}</div>
                        <button class="copy-btn" onclick="copyPath('path-${index}')">📋 Copy Path</button>
                    </div>
                `;
                
                gallery.appendChild(card);
            });
        }

        function openModal(imagePath) {
            modalImage.src = imagePath;
            modal.style.display = 'block';
        }

        function closeModal() {
            modal.style.display = 'none';
        }

        function copyPath(elementId) {
            const pathElement = document.getElementById(elementId);
            const text = pathElement.textContent;
            
            navigator.clipboard.writeText(text).then(() => {
                const btn = event.target;
                const originalText = btn.textContent;
                btn.textContent = '✅ Copied!';
                setTimeout(() => {
                    btn.textContent = originalText;
                }, 2000);
            });
        }

        function filterImages() {
            const searchTerm = searchInput.value.toLowerCase();
            const filtered = images.filter(img => 
                img.path.toLowerCase().includes(searchTerm) ||
                img.timestamp.toLowerCase().includes(searchTerm) ||
                (img.product && img.product.toLowerCase().includes(searchTerm)) ||
                (img.campaign && img.campaign.toLowerCase().includes(searchTerm))
            );
            renderGallery(filtered);
        }

        // Event listeners
        closeBtn.onclick = closeModal;
        modal.onclick = closeModal;
        searchInput.oninput = filterImages;

        // Initial render
        renderGallery(images);
    </script>
</body>
</html>
HTML_FOOTER

echo "✅ Gallery created: $GALLERY_FILE"
echo ""
echo "Opening gallery in browser..."
open "$GALLERY_FILE"

echo ""
echo "💡 Tips:"
echo "   - Click any image to view full size"
echo "   - Use search box to filter by timestamp, product, or path"
echo "   - Click 'Copy Path' to copy the timestamped path for favorites"
echo "   - Close modal by clicking outside the image or the X button"


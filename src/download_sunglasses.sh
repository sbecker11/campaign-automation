#!/bin/bash
# Download Pre-existing Product Image
# 
# This script downloads a sample sunglasses product image from Unsplash
# to demonstrate using existing assets instead of AI generation.

echo "╔════════════════════════════════════════════════════════╗"
echo "║     Download Sample Product Image                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📥 Downloading sunglasses product image from Unsplash..."
echo ""

# Create directory
ASSET_DIR="brands/summer_co/inputs/assets/sunglasses"
mkdir -p "$ASSET_DIR"

# Download from Unsplash (aviator sunglasses on white background)
# Photo by Ethan Robertson on Unsplash
curl -L "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=1024&q=80" \
  -o "$ASSET_DIR/product.jpg" \
  --progress-bar \
  --connect-timeout 10 \
  --max-time 30

echo ""

if [ -f "$ASSET_DIR/product.jpg" ]; then
    FILE_SIZE=$(ls -lh "$ASSET_DIR/product.jpg" | awk '{print $5}')
    
    echo "✅ Downloaded successfully!"
    echo ""
    echo "📂 Location: $ASSET_DIR/product.jpg"
    echo "📊 Size: $FILE_SIZE"
    echo ""
    
    # Check image dimensions
    if command -v file &> /dev/null; then
        echo "📐 Details:"
        file "$ASSET_DIR/product.jpg"
        echo ""
    fi
    
    echo "🎯 Next steps:"
    echo "  1. View the image:"
    echo "     open $ASSET_DIR/product.jpg"
    echo ""
    echo "  2. Run campaign using this asset:"
    echo "     ./generate_campaign.sh --timestamp"
    echo ""
else
    echo "❌ Download failed"
    echo ""
    echo "Alternative options:"
    echo "  1. Check your internet connection"
    echo "  2. Manually download from: https://unsplash.com/photos/sunglasses"
    echo "  3. Use your own image: cp your_image.jpg $ASSET_DIR/product.jpg"
    exit 1
fi

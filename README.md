# Creative Automation Pipeline

AI-powered campaign asset generation for social ad campaigns using DALL-E 3, computer vision, and brand compliance validation.

**Built for Fanatics Data Engineering Take-Home Exercise**

---

## Quick Setup

### 1. Clone and Navigate
```bash
cd workspace-campaign-automation
```

### 2. Install Dependencies
```bash
# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Configure API Key
```bash
# Create environment file
cp .env.example .env

# Edit and add your OpenAI API key
nano .env
# Add: OPENAI_API_KEY=sk-proj-your-key-here
```

### 4. Verify Setup
```bash
# Check project structure
tree brands -L 3 -I 'outputs'

# List available campaigns
ls brands/summer_co/inputs/briefs/
```

---

## Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=src --cov-report=html tests/

# View coverage report
open htmlcov/index.html

# Run specific test file
pytest tests/test_brief_parser.py -v

# Run with detailed output
pytest tests/ -v --tb=short
```

---

## Campaign 1: Summer Promotion (AI-Generated)

This campaign demonstrates **AI image generation** using DALL-E 3.

### Review Inputs
```bash
# View campaign brief
cat brands/summer_co/inputs/briefs/summer_promo_2024.yaml

# Check brand logo
open brands/summer_co/brand_logo.png

# View project structure
tree brands/summer_co/inputs
```

**Brief highlights:**
- 2 products: Sunscreen + Beach Towel
- AI generates product images from descriptions
- 3 formats: 1:1, 9:16, 16:9
- Brand colors: #FF6B35, #004E89, #FFFFFF
- Message: "Your summer adventure starts here"

### Run Campaign
```bash
# Run the campaign
./run_campaign.sh --brief inputs/briefs/summer_promo_2024.yaml

# Run with verbose logging
./run_campaign.sh --brief inputs/briefs/summer_promo_2024.yaml --verbose
```

**Expected runtime:** ~50 seconds (2 products × ~20 sec DALL-E generation each)

**Expected cost:** ~$0.08 (2 products × $0.04/image)

### Review Outputs
```bash
# View output structure
tree brands/summer_co/outputs/summer_promo_2024 -L 3

# Open all generated images
open brands/summer_co/outputs/summer_promo_2024/

# View specific formats
open brands/summer_co/outputs/summer_promo_2024/sunscreen_spf50/1x1/
open brands/summer_co/outputs/summer_promo_2024/beach_towel/9x16/

# View generation report
cat brands/summer_co/outputs/summer_promo_2024/reports/generation_report.json | python -m json.tool

# View compliance report
cat brands/summer_co/outputs/summer_promo_2024/reports/compliance_report.json | python -m json.tool

# Count generated files
find brands/summer_co/outputs/summer_promo_2024 -name "*.png" | wc -l
# Expected: 6 images (2 products × 3 formats)
```

**What to look for in outputs:**
- ✅ AI-generated product photos (sunscreen bottle, beach towel)
- ✅ Brand logo in top-right corner (with smart background)
- ✅ Text overlay: "Your summer adventure starts here"
- ✅ Three aspect ratios per product
- ✅ Brand colors present in images

---

## Campaign 2: Sunglasses Promotion (Pre-existing Asset)

This campaign demonstrates using **pre-existing product photos** instead of AI generation.

### Review Inputs
```bash
# Download sample product image
./src/download_sunglasses.sh

# View the pre-existing asset
open brands/summer_co/inputs/assets/sunglasses/product.jpg

# View campaign brief
cat brands/summer_co/inputs/briefs/sunglasses_campaign.yaml

# Check asset directory structure
tree brands/summer_co/inputs/assets
```

**Brief highlights:**
- 1 product: Aviator Sunglasses
- Uses pre-existing product photo (no AI generation)
- 3 formats: 1:1, 9:16, 16:9
- Message: "See your adventure clearly"

### Run Campaign
```bash
# Run the campaign
./run_campaign.sh --brief inputs/briefs/sunglasses_campaign.yaml

# Run with verbose logging
./run_campaign.sh --brief inputs/briefs/sunglasses_campaign.yaml --verbose
```

**Expected runtime:** ~5 seconds (no AI generation, just image processing)

**Expected cost:** $0.00 (uses existing asset)

### Review Outputs
```bash
# View output structure
tree brands/summer_co/outputs/sunglasses_promo_2024 -L 3

# Open all generated images
open brands/summer_co/outputs/sunglasses_promo_2024/aviator_sunglasses/

# Compare: Original vs Processed
open brands/summer_co/inputs/assets/sunglasses/product.jpg
open brands/summer_co/outputs/sunglasses_promo_2024/aviator_sunglasses/1x1/

# View reports
cat brands/summer_co/outputs/sunglasses_promo_2024/reports/generation_report.json | python -m json.tool

# Count generated files
find brands/summer_co/outputs/sunglasses_promo_2024 -name "*.png" | wc -l
# Expected: 3 images (1 product × 3 formats)
```

**What to look for in outputs:**
- ✅ Pre-existing sunglasses photo (resized to each format)
- ✅ Brand logo in top-right corner
- ✅ Text overlay: "See your adventure clearly"
- ✅ Same professional quality as AI-generated campaigns

---

## View All Outputs

### Helper Script
```bash
# View all campaigns for a brand
./view_outputs.sh brands/summer_co

# View specific campaign details
./view_outputs.sh brands/summer_co summer_promo_2024
./view_outputs.sh brands/summer_co sunglasses_promo_2024
```

### Quick Commands
```bash
# List all generated images
find brands/summer_co/outputs -name "*.png" -type f

# Count total images
find brands/summer_co/outputs -name "*.png" | wc -l
# Expected: 9 images (6 summer + 3 sunglasses)

# View by format
find brands/summer_co/outputs -path "*/1x1/*.png"
find brands/summer_co/outputs -path "*/9x16/*.png"
find brands/summer_co/outputs -path "*/16x9/*.png"

# View all reports
find brands/summer_co/outputs -name "*.json"

# Check file sizes
du -sh brands/summer_co/outputs/*/
```

---

## Project Structure
```
workspace-campaign-automation/
├── brands/
│   └── summer_co/                      # Brand directory
│       ├── brand_logo.png              # Brand logo (auto-generated if missing)
│       ├── inputs/
│       │   ├── assets/                 # Pre-existing product images
│       │   │   └── sunglasses/
│       │   │       └── product.jpg
│       │   └── briefs/                 # Campaign briefs (YAML)
│       │       ├── summer_promo_2024.yaml
│       │       └── sunglasses_campaign.yaml
│       └── outputs/                    # Generated campaigns
│           ├── summer_promo_2024/
│           │   ├── sunscreen_spf50/
│           │   │   ├── 1x1/
│           │   │   ├── 9x16/
│           │   │   └── 16x9/
│           │   ├── beach_towel/
│           │   └── reports/
│           └── sunglasses_promo_2024/
│               ├── aviator_sunglasses/
│               └── reports/
├── src/                                # Source code
│   ├── pipeline.py                     # Main orchestrator
│   ├── image_generator.py              # DALL-E 3 integration
│   ├── asset_processor.py              # Image processing
│   ├── brand_validator.py              # CV-based validation
│   ├── content_checker.py              # Content compliance
│   ├── brief_parser.py                 # YAML parsing
│   ├── report_generator.py             # JSON reports
│   ├── utils.py                        # Utilities
│   └── download_sunglasses.sh          # Sample asset downloader
├── tests/                              # Unit tests
├── temp/                               # Temporary files
├── run_campaign.sh                     # Main runner script
├── view_outputs.sh                     # Output viewer script
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment template
└── README.md                           # This file
```

---

## Features

### 🎨 GenAI Image Generation
- DALL-E 3 integration with brand-aware prompts
- Automatic product photography from text descriptions
- Cost: ~$0.04 per product image

### 📐 Multi-Format Support
- **1:1** - Instagram feed, Facebook posts
- **9:16** - Instagram/TikTok Stories, Reels
- **16:9** - YouTube, Facebook video, Display ads

### 💬 Smart Text Overlays
- Automatic text wrapping for long messages
- Contrast detection for readability
- Semi-transparent backgrounds when needed

### 🎯 Adaptive Logo Placement
- Always top-right corner
- Smart background detection
- Adds white/black background when colors clash
- Uses computer vision for color similarity

### ✅ Brand Validation
- Logo detection using template matching
- Color compliance checking
- Brand guidelines enforcement
- Computer vision-based (no ML training required)

### 🔍 Content Safety
- Prohibited words checking
- Configurable word blacklist
- Campaign message validation

### 📊 Detailed Reporting
- Generation report (products, variants, status)
- Compliance report (validation results)
- JSON format for easy integration

### 🏢 Multi-Brand Support
- Brand-centric folder structure
- Each brand has own logo, assets, outputs
- Scales to hundreds of brands

---

## Campaign Brief Format

### Basic Structure
```yaml
campaign_id: "unique_campaign_id"
campaign_name: "Display Name"

products:
  - product_id: "product_id"
    name: "Product Display Name"
    description: "Product description"
    # Choose one:
    generate_new_assets: true              # AI-generate image
    # OR
    use_existing_assets: "assets/path/"    # Use existing photo

target_market: "US"
target_audience: "demographic_description"
campaign_message: "Text overlay message"

brand_guidelines:
  brand_colors:
    - "#HEX_COLOR_1"
    - "#HEX_COLOR_2"
  logo_required: true

aspect_ratios:
  - "1:1"
  - "9:16"
  - "16:9"
```

### Product Configuration Options

**Option 1: Generate with AI**
```yaml
products:
  - product_id: "new_product"
    name: "Product Name"
    description: "Detailed description for AI generation"
    generate_new_assets: true
```

**Option 2: Use existing photo**
```yaml
products:
  - product_id: "existing_product"
    name: "Product Name"
    description: "Product description"
    use_existing_assets: "assets/product_folder/"
```

**Option 3: Mix both approaches**
```yaml
products:
  - product_id: "new_product"
    generate_new_assets: true
  
  - product_id: "existing_product"
    use_existing_assets: "assets/existing/"
```

---

## Adding a New Brand
```bash
# 1. Create brand structure
mkdir -p brands/my_brand/{inputs/{briefs,assets},outputs}

# 2. Add brand logo (200x200px PNG recommended)
cp your_logo.png brands/my_brand/brand_logo.png
# Or let pipeline auto-generate a default logo

# 3. Create campaign brief
cat > brands/my_brand/inputs/briefs/my_campaign.yaml << 'YAML'
campaign_id: "my_campaign_2024"
campaign_name: "My Campaign"

products:
  - product_id: "product_1"
    name: "Product Name"
    description: "Product description"
    generate_new_assets: true

target_market: "US"
target_audience: "target_demographic"
campaign_message: "Your message here"

brand_guidelines:
  brand_colors:
    - "#FF6B35"
  logo_required: true

aspect_ratios:
  - "1:1"
  - "9:16"
YAML

# 4. Run campaign
./run_campaign.sh --brand brands/my_brand/ --brief inputs/briefs/my_campaign.yaml
```

---

## Technical Stack

- **Python 3.9+**
- **OpenAI DALL-E 3** - AI image generation
- **Pillow (PIL)** - Image processing & manipulation
- **OpenCV** - Computer vision (logo detection, color analysis)
- **Click** - CLI interface
- **PyYAML** - Configuration parsing
- **pytest** - Testing framework

---

## Cost & Performance

### Summer Promotion Campaign (AI-Generated)
- **Time:** ~50 seconds
- **Cost:** ~$0.08 (2 products × $0.04)
- **Output:** 6 images (2 products × 3 formats)

### Sunglasses Campaign (Existing Asset)
- **Time:** ~5 seconds
- **Cost:** $0.00
- **Output:** 3 images (1 product × 3 formats)

### Comparison
- **Speed:** 10x faster with existing assets
- **Cost:** $0 vs $0.08 per campaign
- **Quality:** Professional results either way

---

## Design Decisions

1. **Brand-centric folder structure** - Scales to hundreds of brands independently
2. **Computer vision validation** - No ML training required, deterministic results
3. **Smart logo backgrounds** - Automatic contrast detection via color similarity
4. **Multi-line text wrapping** - Handles long messages across all formats
5. **Cached validation** - Logo validated once per pipeline run for efficiency
6. **Modular architecture** - Each component independently testable
7. **Convention over configuration** - Logo path auto-resolved from brand folder
8. **Backward compatibility** - Supports both old and new field names in briefs

---

## Troubleshooting

### "Logo file not found"
```bash
# Check if logo exists
ls -lh brands/summer_co/brand_logo.png

# Let pipeline auto-create default logo
./run_campaign.sh --brief inputs/briefs/summer_promo_2024.yaml
```

### "OPENAI_API_KEY not set"
```bash
# Edit .env file
nano .env
# Add: OPENAI_API_KEY=sk-proj-your-key-here

# Verify it's set
source .env
echo $OPENAI_API_KEY
```

### "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or in virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

### "Asset path not found"
```bash
# Check asset exists
ls -lh brands/summer_co/inputs/assets/sunglasses/

# Download sample asset
./src/download_sunglasses.sh

# Or add your own
cp your_image.jpg brands/summer_co/inputs/assets/sunglasses/product.jpg
```

### Campaign fails with no images
```bash
# Run with verbose logging to see details
./run_campaign.sh --brief inputs/briefs/campaign.yaml --verbose

# Check generation report for errors
cat brands/summer_co/outputs/campaign_id/reports/generation_report.json | python -m json.tool
```

---

## Quick Reference Commands
```bash
# List all campaigns
ls brands/summer_co/inputs/briefs/

# Run default campaign
./run_campaign.sh

# Run specific campaign
./run_campaign.sh --brief inputs/briefs/sunglasses_campaign.yaml

# Run with verbose output
./run_campaign.sh --brief inputs/briefs/summer_promo_2024.yaml --verbose

# View all outputs
./view_outputs.sh brands/summer_co

# Count generated images
find brands/summer_co/outputs -name "*.png" | wc -l

# Open campaign outputs
open brands/summer_co/outputs/summer_promo_2024/

# Run tests
pytest tests/ -v

# Clean outputs (start fresh)
rm -rf brands/summer_co/outputs/*
```

---

## Demo Video Script

For a 2-3 minute demo video, follow this flow:

1. **Show project structure** (20 sec)
```bash
   tree brands -L 3 -I 'outputs'
```

2. **Show Campaign 1 brief** (20 sec)
```bash
   cat brands/summer_co/inputs/briefs/summer_promo_2024.yaml
```

3. **Run Campaign 1** (30 sec)
```bash
   ./run_campaign.sh --brief inputs/briefs/summer_promo_2024.yaml
```

4. **Show Campaign 1 outputs** (30 sec)
   - Open generated images
   - Show different formats side-by-side

5. **Show Campaign 2 asset** (10 sec)
```bash
   open brands/summer_co/inputs/assets/sunglasses/product.jpg
```

6. **Run Campaign 2** (10 sec)
```bash
   ./run_campaign.sh --brief inputs/briefs/sunglasses_campaign.yaml
```

7. **Show Campaign 2 outputs** (20 sec)
   - Compare original vs processed

8. **Highlight features** (20 sec)
   - Multi-brand support
   - AI + existing assets
   - Brand compliance
   - Multiple formats

---

**Built by Shawn Becker for Fanatics Data Engineering Take-Home Exercise**

**GitHub:** https://github.com/sbecker11
**LinkedIn:** https://linkedin.com/in/shawnbecker

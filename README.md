# Campaign Automation Pipeline

AI-powered campaign asset generation for social ad campaigns using DALL-E 3, computer vision, and brand compliance validation.

**Built for Fanatics Data Engineering Take-Home Exercise**

## Refine Campaign UI

The refine campaign interface provides a visual way to review, manage, and commit generated campaign instances:

<div style="display: flex; flex-wrap: wrap; gap: 10px; margin: 20px 0;">
  <img src="docs/all-visible.png" alt="Refine UI - Initial view with all images visible" style="width: 33%; border: 1px solid #ddd; border-radius: 4px;">
  <img src="docs/one-hidden.png" alt="Refine UI - View with hidden image and comment" style="width: 33%; border: 1px solid #ddd; border-radius: 4px;">
  <img src="docs/image-variants.png" alt="Refine UI - Filtering by product" style="width: 33%; border: 1px solid #ddd; border-radius: 4px;">
  <img src="docs/commit-campaign-to-github.png" alt="Refine UI - Commit campaign modal" style="width: 33%; border: 1px solid #ddd; border-radius: 4px;">
</div>

---

## Demo Video

Watch a complete walkthrough of the Campaign Automation Pipeline in action:

**[📹 View Demo Video](https://www.dropbox.com/scl/fi/vtswpa6v5tuvahtna3ar8/DEMO_MOVIE_compressed.mov?rlkey=8csw89ojiyvopt73ehkjx5rfz&st=bc3v919q&dl=0)**

*(Note: The compressed video file is ~96MB. Click the link above to view or download it from DropBox.)*

The demo video demonstrates:
- Setting up the project and configuring your API key
- Reviewing campaign configuration files
- Generating campaign instances with AI-powered image creation
- Using the refine UI to review and manage campaign assets
- Running tests and viewing coverage reports

---


## Getting Started

### Prerequisites

Before you begin, you'll need:

1. **A terminal window** - This is where you'll type commands
   - **macOS**: Press `Cmd+Space`, type "Terminal", press Enter
   - **Windows**: 
     - **Option 1 (Recommended)**: After installing Git, open "Git Bash" from the Start menu
       - Click the Windows Start button
       - Type "Git Bash" and click on it
       - This is the best option for running bash scripts
     - **Option 2**: Press `Win+R`, type `cmd`, press Enter (basic Windows terminal)

2. **Git** - For downloading the project
   - If not installed, visit: https://git-scm.com/downloads
   - **Windows users**: Git for Windows includes "Git Bash" automatically
   - The setup script will check and guide you if Git is missing

3. **Python 3** - Required to run the project
   - If not installed, visit: https://www.python.org/downloads/
   - **Windows users**: Make sure to check "Add Python to PATH" during installation
   - The setup script will check and guide you if Python 3 is missing

### Quick Setup

Once you have the prerequisites, follow these steps:

1. **Open a terminal window** (see above)

2. **Create a directory for your projects and go into it** - Copy and paste this command, then press Enter:
   ```bash
   mkdir -p ~/my-github-projects;
   cd ~/my-github-projects
   ```

3. **Fork the repository on GitHub:**
   - Go to https://github.com/sbecker11/campaign-automation
   - Click the **"Fork"** button in the top-right corner
   - Choose where to fork it (your personal account)
   - Wait for the fork to complete

4. **Clone your fork** - Copy and paste this command, then press Enter (replace YOUR_USERNAME with your GitHub username):
   ```bash
   git clone https://github.com/YOUR_USERNAME/campaign-automation.git
   ```

5. **Go into the project folder** - Copy and paste this command, then press Enter:
   ```bash
   cd campaign-automation
   ```

6. **Run the setup script** - Copy and paste this command, then press Enter:
   ```bash
   ./setup.sh
   ```

The setup script will:
- ✅ Check that Git and Python 3 are installed
- ✅ Create a virtual environment
- ✅ Install all Python dependencies
- ✅ Install the package in editable mode
- ✅ Guide you through configuring your OpenAI API key

**Important:** Create a local `.env` file from `.env.example` and add your `OPENAI_API_KEY`. **Do not commit the `.env` file to GitHub** - it will trigger a security error. The `.env` file is already in `.gitignore` to prevent accidental commits.

**Note:** The project root is `~/my-github-projects/campaign-automation`

---

# View project structure
```
campaign-automation/
├── inputs/
│   └── campaigns/                      # Campaign configuration files (YAML)
│       └── example_campaign.yaml       # Example campaign configuration
├── outputs/                            # Generated campaign instances directory
│   └── campaigns/                      # Campaign instance folders (timestamped)
│       └── summer_2024/
│           ├── campaign_instance.json
│           └── products/               # Product images by aspect ratio
│               ├── sunscreen_spf50/
│               │   ├── 1x1/
│               │   ├── 9x16/
│               │   └── 16x9/
│               └── beach_towel/
│                   ├── 1x1/
│                   ├── 9x16/
│                   └── 16x9/
├── assets/
│   └── spexture.com-logo.png           # Logo file (optional, PNG format)
├── src/                                # Source code
│   ├── pipeline.py                     # Main orchestrator
│   ├── campaign_parser.py              # YAML parsing
│   ├── image_generator.py              # DALL-E 3 integration
│   ├── asset_processor.py              # Image processing
│   ├── campaign_validator.py           # Campaign compliance validation
│   ├── content_checker.py              # Content compliance
│   ├── instance_generator.py           # Campaign instance JSON generation
│   └── utils.py                        # Utilities
├── tests/                              # Unit tests
├── scripts/
│   ├── run_tests_w_coverage.sh         # Runs all unit tests 
│   ├── generate_campaign.sh            # Main campaign instance generator script
│   └── refine_campaign.sh              # Campaign instance refinement UI launcher
├── requirements.txt                    # Python dependencies
├── setup.py                            # Package setup
├── .env                                # Environment variables (create this)
└── README.md                           # This file
```


---

## Run Tests
```bash
# Make sure you're in the project root directory
cd ~/my-github-projects/campaign-automation

# Activate virtual environment (if not already active)
source venv/bin/activate

# Run all tests with coverage
./scripts/run_tests_w_coverage.sh
```

### Test Suite Overview

- **Total Tests**: 131 passing, 2 skipped
- **Code Coverage**: 94%
- **Execution Time**: ~3 seconds

### Coverage Targets
```
Name                        Coverage
------------------------------------
src/__init__.py              100%
src/asset_processor.py        95%
src/campaign_parser.py       100%
src/campaign_validator.py     98%
src/content_checker.py        90%
src/image_generator.py        90%
src/instance_generator.py     95%
src/pipeline.py               91%
src/utils.py                 100%
------------------------------------
TOTAL                         94% (very strong coverage !!)
```

## Interactive Coverage Explorer

An interactive coverage explorer has been created at `htmlcov/index.html`

## Other Pytest Options

```bash
# Run specific test file
pytest tests/test_campaign_parser.py -v

# Run with detailed output
pytest tests/ -v --tb=short

# Run tests without coverage (faster)
pytest tests/
```

---

## Generating a Campaign Instance from a Campaign Configuration

### Step 1: Review the Campaign Configurations

```bash
ls -R inputs/
```

**Important:** Review the campaign configuration file before generating campaign instances.

```bash
# View the example campaign configuration
cat inputs/campaigns/example_campaign.yaml
```

**What to review in the campaign configuration file:**

1. **Campaign Information:**
   - `campaign_id`: Unique identifier for this campaign configuration. Used to create the campaign instance directory path: `outputs/campaigns/{campaign_id}_{timestamp}/` (e.g., `outputs/campaigns/summer_2024_20241116_143022/`). Each generation creates a new timestamped campaign instance, allowing you to generate multiple instances from the same campaign configuration.
   - `campaign_name`: Display name for the campaign
   - `target_market` and `target_audience`: Used for targeting
   - `campaign_tagline`: Campaign tagline that will appear on resized product images

2. **Products:**
   - `product_id`: Unique identifier for each product
   - `name`: Product display name
   - `description`: Product description
   - `generate_new`: Whether to generate new images with AI or use existing assets
   - `existing_assets`: Path to directory containing image files (if using existing assets)
   - For detailed product image configuration options, see [Product Image Configuration](docs/product_image_configuration.md)

3. **Brand Guidelines:**
   - `brand_colors`: Colors used as guidelines for AI image generation and validated in generated images (using css color format #RRGGBB)
   - `logo_path`: Path to your logo file (optional - see [Logo Requirements](docs/logo_requirements.md)) 

4. **Aspect Ratios:**
   - Formats to generate: `1:1` (Instagram), `9:16` (Stories), `16:9` (Landscape)
   - Each product will generate images in all specified formats

5. **Content Safety:**
   - `prohibited_words`: Words that will be flagged if found in generated content

**Example campaign configuration details:**
- 2 products: Sunscreen + Beach Towel
- Both set to `generate_new: true` (AI will create images)
- 3 formats: 1:1, 9:16, 16:9
- Brand colors: #FF6B35, #004E89, #FFFFFF
- Tagline: "Your summer adventure starts here".

**Expected runtime:** ~50 seconds (2 products × ~20 sec DALL-E generation each)

**Expected cost:** (2 products × $0.04/image) = ~$0.08 total DALL-E time

### Step 2: Generate a Campaign Instance

After reviewing the configuration, generate a campaign instance:

```bash
# Generate the default campaign (uses the most recently modified YAML file in inputs/campaigns/)
./scripts/generate_campaign.sh

# Or generate an instance from a specific campaign configuration file
./scripts/generate_campaign.sh inputs/campaigns/example_campaign.yaml
```

This will create a new campaign instance in `outputs/campaigns/` with a timestamp. The campaign instance directory structure will be:
- `outputs/campaigns/{campaign_id}_{timestamp}/` - Main campaign directory
  - `campaign_instance.json` - Campaign instance meta data
  - `products/` - Product images organized by product_id and aspect ratio

Each generation creates a new timestamped campaign instance directory (format: `YYYYMMDD_HHMMSS`), so you can generate multiple instances from the same campaign configuration without overwriting previous results.

### Step 3: Review and Refine Campaign Instances

```bash
# Choose which product images are acceptable by opening the refine UI (defaults to most recently modified campaign instance)
./scripts/refine_campaign.sh

# Or open a specific campaign instance
./scripts/refine_campaign.sh summer_2024_20251116_104032
```

**The `./scripts/refine_campaign.sh` script opens a web-based UI where you can:**

- **HIDE OR SHOW IMAGES** - Mark images as hidden or visible
- **ADD COMMENTS** - Add notes to individual images (max 512 characters)
- **SAVE THE CAMPAIGN** - Use the "💾 Save Campaign" button to persist visibility and comments to `campaign_instance.json`
- **COMMIT CAMPAIGN CHANGES TO GITHUB** - Use the "📦 Commit Campaign" button to commit campaign instances to the `campaign-instances` branch in your fork
- **EXIT THE REFINE UI** - Use the "🚪 Exit" button to close the server and browser window

The UI also provides:
- 📸 Visual grid view of all campaign images with thumbnails
- 🔍 Filtering by product, variant (aspect ratio), and status (visible/hidden)
- 📊 Live counts showing hidden/visible totals
- ✅ Validation indicators showing logo, color, and quality compliance status per image

**What to look for in campaign instances:**
- ✅ AI-generated product photos (sunscreen bottle, beach towel)
- ✅ Brand logo in top-right corner (with smart background)
- ✅ Text overlay tagline: "Your summer adventure starts here"
- ✅ Three aspect ratios per product
- ✅ Brand colors present in images

### Other Ways to Review Campaign Instances

```bash
# View output structure manually
ls -R outputs/campaigns/summer_2024_20251116_104032

# View consolidated campaign data
cat outputs/campaigns/summer_2024_20251116_104032/campaign_instance.json | python -m json.tool

# Count generated files for a specific campaign instance
find outputs/campaigns/summer_2024_20251116_104032 -name "*.png" | wc -l
# Expected: 6 images (2 products × 3 formats)

# List all generated images across all campaigns
find outputs/campaigns -name "*.png" -type f
# Windows alternative (Git Bash): Same command works
# Windows cmd.exe: dir /s /b outputs\campaigns\*.png

# Count total images across all campaigns
find outputs/campaigns -name "*.png" | wc -l
# Windows alternative (Git Bash): Same command works
# Windows cmd.exe: dir /s /b outputs\campaigns\*.png | find /c ".png"

# View images by format
find outputs/campaigns -path "*/1x1/*.png"
find outputs/campaigns -path "*/9x16/*.png"
find outputs/campaigns -path "*/16x9/*.png"
# Windows alternative (Git Bash): Same commands work

# View all campaign instance JSON files
find outputs/campaigns -name "campaign_instance.json"
# Windows alternative (Git Bash): Same command works

# Check file sizes
du -sh outputs/campaigns/*/
# Windows alternative (Git Bash): Same command works
# Windows cmd.exe: for /d %d in (outputs\campaigns\*) do @dir /s "%d" | find "File(s)"
```


### Campaign Generation Flow

The following diagram illustrates the complete campaign generation pipeline:

![Campaign Generation Flow](docs/generate_campaign_flow.png)

This flow shows how a campaign configuration file is processed through image generation, asset processing, validation, and reporting to produce the final campaign instances.

---

## Comprehensive set of Project Features

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
- Logo detection using template matching (computer vision technique that finds logos by comparing image patterns)
- Color compliance checking (verifies brand colors appear in generated images)
- Brand guidelines enforcement
- Computer vision-based (no ML training required - uses image analysis algorithms instead of machine learning)

### 🔍 Content Safety
- Prohibited words checking
- Configurable word blacklist
- Brand tagline validation

### 📊 Detailed Reporting
- Generation report (products, variants, status)
- Compliance report (validation results)
- JSON format for easy integration

### 🎯 Campaign Management
- Simple YAML-based configuration
- Centralized asset management
- Easy to add new campaigns

### Robust Unit testing

---

## Technical Stack

- **Python 3.9+**
- **OpenAI DALL-E 3** - AI image generation
- **Pillow (PIL)** - Image processing & manipulation
- **OpenCV** - Computer vision (logo detection, color analysis)
- **PyYAML** - Configuration parsing
- **pytest** - Testing framework
- **argparse** - Command-line interface

---

## Cost & Performance

### Example Campaign (AI-Generated)
- **Time:** ~50 seconds
- **Cost:** ~$0.08 (2 products × $0.04)
- **Output:** 6 images (2 products × 3 formats)

### Using Existing Assets
- **Time:** ~5 seconds
- **Cost:** $0.00
- **Output:** 3 images (1 product × 3 formats)

### Comparison
- **Speed:** 10x faster with existing assets
- **Cost:** $0 vs $0.08 per campaign
- **Quality:** Professional results either way

---

## Design Decisions

1. **Simple campaign structure** - Easy to organize and scale
2. **Computer vision validation** - No ML training required, deterministic results (uses image analysis algorithms instead of machine learning models)
3. **Smart logo backgrounds** - Automatic contrast detection via color similarity (compares logo colors with background to ensure readability)
4. **Multi-line text wrapping** - Handles long messages across all formats
5. **Cached validation** - Logo validated once per campaign generation for efficiency
6. **Modular architecture** - Each component independently testable
7. **Convention over configuration** - Logo path auto-resolved from assets folder (uses standard location instead of requiring explicit configuration)
8. **Flexible asset sources** - Support for both AI-generated and existing images

---

## For Developers

### Architecture Overview

The pipeline follows a modular architecture with clear separation of concerns:

1. **`campaign_parser.py`** - Parses YAML configuration files, validates structure, applies defaults
2. **`image_generator.py`** - Interfaces with OpenAI DALL-E 3 API for AI image generation
3. **`asset_processor.py`** - Handles image processing: resizing, text overlays, logo placement
4. **`campaign_validator.py`** - Validates brand compliance using computer vision (logo detection, color analysis)
5. **`content_checker.py`** - Validates content safety (prohibited words, message validation)
6. **`instance_generator.py`** - Generates campaign instance JSON files with campaign metadata and validation results
7. **`pipeline.py`** - Main orchestrator that coordinates all components
8. **`utils.py`** - Shared utility functions

### Extension Points

**Adding New Validation Rules:**
- Extend `campaign_validator.py` with new validation methods
- Add validation results to the instance structure in `instance_generator.py`

**Adding New Image Formats:**
- Modify `asset_processor.py` to handle new aspect ratios
- Update `campaign_parser.py` to accept new format strings

**Custom Image Processing:**
- Extend `asset_processor.py` with new processing functions
- Hook into the pipeline via `pipeline.py`


### Code Quality

- **Testing**: pytest with 94% code coverage target
- **Type Hints**: Python type annotations for better IDE support
- **Modularity**: Each component is independently testable
- **Error Handling**: Comprehensive error messages and validation

### API Integration

**OpenAI DALL-E 3:**
- Rate limiting: Handled automatically by OpenAI SDK
- Error handling: Retries and clear error messages
- Cost tracking: ~$0.04 per image generation

**Computer Vision (OpenCV):**
- Logo detection: Template matching algorithm
- Color analysis: HSV color space conversion for similarity checking
- No external API calls required

### Environment Variables

**Important:** Create a local `.env` file from `.env-example` and add your `OPENAI_API_KEY`. **Do not commit the `.env` file to GitHub** - it will trigger a security error. The `.env` file is already in `.gitignore` to prevent accidental commits.

Required:
- `OPENAI_API_KEY` - Your OpenAI API key (stored in `.env` file)

Optional:
- All other configuration via YAML files

### Logging and Debugging

The pipeline uses Python's logging module. To enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass: `pytest tests/ -v`
5. Submit a pull request

---

## Troubleshooting

### "Logo file not found"
```bash
# Check if logo exists (must match logo_path in your campaign YAML)
ls -lh assets/spexture.com-logo.png
# Windows alternative (Git Bash): Same command works
# Windows cmd.exe: dir assets\spexture.com-logo.png

# Logo is optional - only used if logo_path is defined in config AND file exists
# See docs/logo_requirements.md for format and dimension requirements
```

### "OPENAI_API_KEY not set"
```bash
# Create or edit .env file
echo 'OPENAI_API_KEY=sk-your-key-here' > .env

# Or copy from existing location
cp ~/workspace-campaign-automation/campaign-automation/.env .

# Verify it's set
source .env
echo $OPENAI_API_KEY
```

### "Module not found"
```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall package in editable mode
pip install -e .

# Or reinstall dependencies
pip install -r requirements.txt
```

### "Asset path not found"
```bash
# Check asset exists
ls -lh path/to/your/assets/
# Windows alternative (Git Bash): Same command works
# Windows cmd.exe: dir path\to\your\assets\

# Make sure the path in your campaign YAML is correct
cat inputs/campaigns/your_campaign.yaml
# Windows alternative (Git Bash): Same command works
# Windows cmd.exe: type inputs\campaigns\your_campaign.yaml
```

### Campaign fails with no images
```bash
# Check campaign data
cat outputs/campaigns/campaign_id/campaign_instance.json | python -m json.tool

# Verify .env file has valid API key
grep OPENAI_API_KEY .env
```

---

## Quick Reference Commands
```bash
# List all campaign configurations
ls inputs/campaigns/

# Generate default campaign instance
./scripts/generate_campaign.sh

# Generate campaign instance from specific campaign configuration
./scripts/generate_campaign.sh inputs/campaigns/my_campaign.yaml

# View campaign instances
./scripts/refine_campaign.sh

# View specific campaign instance
./scripts/refine_campaign.sh campaign_id_timestamp

# Count generated images
find outputs/campaigns -name "*.png" | wc -l
# Windows alternative (Git Bash): Same command works
# Windows cmd.exe: dir /s /b outputs\campaigns\*.png | find /c ".png"

# Open campaign instance directory (macOS)
open outputs/campaigns/summer_2024/
# Windows alternative: explorer outputs\campaigns\summer_2024
# Linux: xdg-open outputs/campaigns/summer_2024/

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=src --cov-report=html

# Clean campaign instances (start fresh)
rm -rf outputs/campaigns/*
```

---

## Demo Video Script

For a 2-3 minute demo video, follow this flow:

### Part 1: Setup (45 seconds)
- Fork repository on GitHub
- Clone your fork
- Create virtual environment
- Install dependencies
- Configure API key

### Part 2: Project Structure (30 seconds)
```bash
ls -R inputs/
cat inputs/campaigns/example_campaign.yaml
# Show campaign configuration files
```

### Part 3: Generate Campaign Instance (60 seconds)
```bash
./scripts/generate_campaign.sh
```
**While generating:**
- "Step 1: Parsing campaign yaml file..."
- "Step 2: Generating images with DALL-E..."
- "Creating variants for 1:1 Instagram, 9:16 Stories..."
- "Step 3: Validating brand compliance - checking colors, prohibited words..."
- "Generating campaign instance..."

### Part 4: Results (30 seconds)
```bash
./scripts/refine_campaign.sh
# Refine UI opens in browser - show filtering, hiding images, adding comments
cat outputs/campaigns/summer_2024_20251116_104032/campaign_instance.json | head -20
```

### Part 5: Testing & Quality (25 seconds)
```bash
pytest tests/ -v --cov=src --cov-report=html
# An interactive coverage explorer has been created at htmlcov/index.html
```

### Part 6: Wrap Up (15 seconds)
- Highlight key features
- Summary of capabilities

See `DEMO_SCRIPT_COMPLETE.md` for the full detailed demo script.

---

## Glossary

**Computer Vision** - Technology that enables computers to interpret and understand visual information from images, using algorithms to analyze patterns, colors, and shapes.

**Pre-commit Hook** - An automated script that runs before Git commits to check code quality, prevent mistakes, or enforce policies.

**Template Matching** - A computer vision technique that searches for a specific pattern (like a logo) in an image by comparing it pixel-by-pixel.

**Virtual Environment (venv)** - An isolated Python environment that keeps project dependencies separate from your system Python installation.

**YAML** - A human-readable data format used for configuration files. Campaign configurations are written in YAML.

**Aspect Ratio** - The proportional relationship between an image's width and height (e.g., 1:1 is square, 16:9 is wide).

---

**Built by Shawn Becker for Fanatics Data Engineering Take-Home Exercise**

**Repository:** https://github.com/sbecker11/campaign-automation  
**GitHub:** https://github.com/sbecker11  
**LinkedIn:** https://linkedin.com/in/shawnbecker



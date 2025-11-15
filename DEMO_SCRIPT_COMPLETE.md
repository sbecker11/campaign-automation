# Campaign Automation Pipeline - Complete Demo (2-3 minutes)

## Pre-Demo Setup (Do this before recording)
1. **Upgrade pip on your system:** `pip install --upgrade pip` or `python3 -m pip install --upgrade pip`
2. Make sure project is pushed to GitHub: `https://github.com/sbecker11/campaign-automation`
3. Have terminal ready
4. Clear your demo directory: `rm -rf ~/demo-workspace`
5. Practice the git clone URL: `https://github.com/sbecker11/campaign-automation.git`
6. **Set up .env file:** Create `.env` file with OPENAI_API_KEY=sk-* (needed for image generation)
7. **Note:** Local workspace is at `~/workspace-campaign-automation/campaign-automation`

---

## Demo Script - From Scratch

### Part 1: Setup (45 seconds)

**SAY:** "I'll demonstrate my campaign automation pipeline that uses GenAI to create social media ads. Let me start from a fresh setup."

**DO:**
```bash
# Create demo directory (for demo purposes)
mkdir -p ~/demo-workspace;

cd ~/demo-workspace;

# Clone from GitHub (repo name: campaign-automation)
git clone https://github.com/sbecker11/campaign-automation.git;

cd campaign-automation

# Quick look at structure
ls -la
```

**SAY WHILE CLONING:** "This pipeline automates creating ad variants for Instagram, Facebook, TikTok - each platform needs different aspect ratios and brand compliance."

**DO:**
```bash
# Create the virtual environment
python3 -m venv venv;

# Activate the virtual environment
source venv/bin/activate;

# Upgrade the pip installer
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt;

# Install package in editable mode (so imports work)
pip install -e .;
```


**NOTE:** Add my `OPENAI_API_KEY` to the local .env file before running the pipeline:
```bash
grep OPENAI_API_KEY ~/workspace-campaign-automation/campaign-automation/.env
cp  ~/workspace-campaign-automation/campaign-automation/.env .
```

---

### Part 2: Project Structure (30 seconds)

**SAY:** "Let me show you how campaigns are organized."

**DO:**
```bash

# Show each campaign is defined as an input yaml file
tree inputs/ -L 2

# Here's an example campaign yaml file
cat inputs/campaigns/example_campaign.yaml
```

**POINT OUT:**
- "Multiple products"
- "Target audience"
- "Brand colors for compliance"
- "Aspect ratios for different platforms"

---

### Part 3: Run Campaign (60 seconds)

**SAY:** "Let's run this campaign..."

**DO:**
```bash
# Run the campaign pipeline
./run_campaign.sh
```

**SAY WHILE RUNNING:**
- "Step 1: Parsing campaign yaml file..."
- "Step 2: Generating images with DALL-E..."
- "Creating variants for 1:1 Instagram, 9:16 Stories..."
- "Step 3: Validating brand compliance - checking colors, prohibited words..."
- "Generating compliance reports..."

---

### Part 4: Results (30 seconds)

**SAY:** "Here's what we generated...

Multiple variants for each product, each optimized for different platforms, all brand-compliant. We generated 6 images total - 2 products with 3 aspect ratios each."

**DO:**
```bash
# Show the generated campaign product images with variants
./view_campaign.sh
```

**DO:**
```bash
# Show reports
cat outputs/campaigns/summer_2024/reports/generation_report.json | head -20
```

---

### Part 5: Testing & Quality (25 seconds)

**SAY:** "This isn't just a proof-of-concept - it has production-quality testing."

**DO:**
```bash
# Run tests
pytest tests/ -v --cov=src --cov-report=html
```

**SHOW IN TERMINAL:**
- "80 tests passing"
- "75% code coverage"
- "2.5 seconds execution"

**QUICK OPEN:** `open htmlcov/index.html` - show coverage report

**POINT OUT:**
- "95% coverage on brand validator"
- "Comprehensive test suite"

---

### Part 6: Wrap Up (15 seconds)

**SAY:** "This pipeline demonstrates full-stack development with GenAI integration, computer vision for brand compliance, and production-quality testing. Built with Python, DALL-E API, PIL for image processing, and pytest. Thank you!"

**SHOW:** Confidence - smile and be ready for questions!

---

## Exact Commands in Order
```bash
# 1. Setup (45s)
mkdir -p ~/demo-workspace && cd ~/demo-workspace
git clone https://github.com/sbecker11/campaign-automation.git
cd campaign-automation
python3 -m venv venv && source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .  # Install package in editable mode so imports work
# Copy .env file from workspace (if available)
cp ~/workspace-campaign-automation/campaign-automation/.env . 2>/dev/null || echo 'OPENAI_API_KEY=sk-your-key-here' > .env

# 2. Structure (30s)
tree inputs/ -L 2
cat inputs/campaigns/example_campaign.yaml

# 3. Run Campaign (60s)
# Make sure venv is activated (from step 1)
# Make sure .env file exists with OPENAI_API_KEY
./run_campaign.sh

# 4. Results (30s)
tree outputs/campaigns/summer_2024/ -L 3
# View campaign outputs
./view_campaign.sh
cat outputs/campaigns/summer_2024/reports/generation_report.json | head -20

# 5. Testing (25s)
pytest tests/ -v --cov=src --cov-report=html
open htmlcov/index.html

# Total: ~3:05
```

---

## Timing Breakdown
- Setup: 45s
- Structure: 30s  
- Run: 60s
- Results: 30s
- Testing: 25s
- Wrap: 15s
**Total: 3:05** (can cut to 2:30 by speeding up or skipping parts)

---

## Practice Tips

1. **Pre-record a backup:** Have outputs ready in case live demo fails
2. **Test your git clone URL** beforehand: `https://github.com/sbecker11/campaign-automation.git`
3. **Upgrade pip before demo** - already done in pre-demo setup
4. **Speed up install:** Use `pip install -q` for quiet mode
5. **Know your cuts:** If over time, skip the detailed tree commands
6. **Terminal font:** Make sure it's readable on recording
7. **Note:** Demo uses `~/demo-workspace/campaign-automation`, but actual workspace is `~/workspace-campaign-automation/campaign-automation`

---

## Speed Optimization (to hit 2:30)

If you need to cut 35 seconds:
- Skip `tree` commands (-15s)
- Don't open coverage report, just show terminal (-10s)
- Speed through pip install (-10s)

---

## Emergency Backup Plan

If live demo fails:
1. **Have pre-run outputs** in a backup folder
2. Show those instead: `tree backup-outputs/`
3. Focus more on tests and code quality
4. Still looks professional!


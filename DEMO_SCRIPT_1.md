# Campaign Automation Pipeline - Complete Demo (2-3 minutes)

## Pre-Demo Setup (Do this before recording)
1. **Upgrade pip on your system:** `pip install --upgrade pip` or `python3 -m pip install --upgrade pip`
2. Make sure project is pushed to GitHub
3. Have terminal ready
4. Clear your demo directory: `rm -rf ~/demo-workspace`
5. Practice the git clone URL

---

## Demo Script - From Scratch

### Part 1: Setup (45 seconds)

**SAY:** "I'll demonstrate my campaign automation pipeline that uses GenAI to create social media ads. Let me start from a fresh setup."

**DO:**
```bash
# Create parent directory
mkdir -p ~/demo-workspace;
cl
cd ~/demo-workspace;

# Clone from GitHub (use your actual repo URL)
git clone https://github.com/YOUR_USERNAME/workspace-campaign-automation.git;

cd workspace-campaign-automation

# Quick look at structure
ls -la
```

**SAY WHILE CLONING:** "This pipeline automates creating ad variants for Instagram, Facebook, TikTok - each platform needs different aspect ratios and brand compliance."

**DO:**
```bash
# Create virtual environment
python3 -m venv venv;
source venv/bin/activate;

# Install dependencies
pip install -q -r requirements.txt;
```

**SAY:** "Quick setup - installing dependencies..."

---

### Part 2: Project Structure (30 seconds)

**SAY:** "Let me show you how campaigns are organized."

**DO:**
```bash
# Show brand directories
ls brand/
tree brand/ -L 1

# Show campaign inputs
tree inputs/ -L 2
```

**SAY:** "Each brand has its logo and assets. Campaign briefs are YAML configs - here's one..."

**DO:**
```bash
# Show brief
cat inputs/briefs/example_campaign.yaml | head -25
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
# Run the pipeline
python src/pipeline.py --brief inputs/briefs/example_campaign.yaml
```

**SAY WHILE RUNNING:**
- "Step 1: Parsing campaign brief..."
- "Step 2: Generating images with DALL-E..."
- "Creating variants for 1:1 Instagram, 9:16 Stories..."
- "Step 3: Validating brand compliance - checking colors, prohibited words..."
- "Generating compliance reports..."

---

### Part 4: Results (30 seconds)

**SAY:** "Here's what we generated..."

**DO:**
```bash
# Show output structure
tree outputs/campaign_*/products/ -L 2

# Or use ls
ls -la outputs/campaign_*/products/*/
```

**OPEN:** One or two generated images

**SAY:** "Multiple variants per product, each optimized for different platforms, all brand-compliant."

**DO:**
```bash
# Show reports
cat outputs/campaign_*/reports/generation_report.json | head -20
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
git clone https://github.com/YOUR_USERNAME/workspace-campaign-automation.git
cd workspace-campaign-automation
python3 -m venv venv && source venv/bin/activate
pip install -q -r requirements.txt

# 2. Structure (30s)
ls brand/
tree inputs/ -L 2
cat inputs/briefs/example_campaign.yaml | head -25

# 3. Run Campaign (60s)
python src/pipeline.py --brief inputs/briefs/example_campaign.yaml

# 4. Results (30s)
tree outputs/ -L 3
open outputs/campaign_*/products/product_1/1x1/*.png
cat outputs/campaign_*/reports/generation_report.json | head -20

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
2. **Test your git clone URL** beforehand
3. **Upgrade pip before demo** - already done in pre-demo setup
4. **Speed up install:** Use `pip install -q` for quiet mode
5. **Know your cuts:** If over time, skip the detailed tree commands
6. **Terminal font:** Make sure it's readable on recording

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


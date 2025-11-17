#!/bin/bash
# One-command setup script for Campaign Automation
# This script handles all setup steps including pre-commit hook installation

set -e

echo "🚀 Setting up Campaign Automation..."
echo ""

# Step 1: Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Step 2: Activate virtual environment
source venv/bin/activate

# Step 3: Set PYTHONPATH
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Step 4: Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet

# Step 5: Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Step 6: Install package in editable mode
echo ""
echo "📦 Installing package in editable mode..."
pip install -e . --quiet

# Step 7: Install pre-commit hook
echo ""
echo "🔒 Installing pre-commit hook..."
if [ -f "scripts/install_pre_commit_hook.sh" ]; then
    ./scripts/install_pre_commit_hook.sh
else
    echo "⚠️  Warning: install_pre_commit_hook.sh not found, skipping hook installation"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Configure your API key: echo 'OPENAI_API_KEY=sk-your-key-here' > .env"
echo "  3. Run a campaign: ./scripts/generate_campaign.sh"
echo ""


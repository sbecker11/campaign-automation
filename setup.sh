#!/bin/bash
# Setup script for Campaign Automation

set -e

# Detect operating system
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=macOS;;
    CYGWIN*)    MACHINE=Windows;;
    MINGW*)     MACHINE=Windows;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

# Check for Git
if ! command -v git &> /dev/null; then
    echo "Git is not installed."
    echo ""
    if [ "$MACHINE" = "macOS" ]; then
        echo "Install Git:"
        echo "  Run: xcode-select --install"
        echo "  Or visit: https://git-scm.com/download/mac"
    elif [ "$MACHINE" = "Windows" ]; then
        echo "Install Git:"
        echo "  Visit: https://git-scm.com/download/win"
    else
        echo "Install Git:"
        echo "  Visit: https://git-scm.com/downloads"
        echo "  Or run: sudo apt install git"
    fi
    echo ""
    echo "After installing Git, close and reopen your terminal, then run this script again."
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "This doesn't appear to be a git repository."
    echo ""
    echo "First, clone the repository:"
    echo "  1. Open a terminal window:"
    echo "     - macOS: Press Cmd+Space, type 'Terminal', press Enter"
    echo "     - Windows (Recommended): Open 'Git Bash' from Start menu"
    echo "       * Click Windows Start button, type 'Git Bash', click it"
    echo "     - Windows (Alternative): Press Win+R, type 'cmd', press Enter"
    echo ""
    echo "  2. Create a directory for your projects:"
    echo "     mkdir -p ~/my-github-projects"
    echo "     cd ~/my-github-projects"
    echo ""
    echo "  3. Clone the repository:"
    echo "     git clone https://github.com/sbecker11/campaign-automation.git"
    echo ""
    echo "  4. Enter the project directory and run setup:"
    echo "     cd campaign-automation"
    echo "     ./setup.sh"
    exit 1
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed."
    echo ""
    if [ "$MACHINE" = "macOS" ]; then
        echo "Install Python 3:"
        echo "  Visit: https://www.python.org/downloads/"
    elif [ "$MACHINE" = "Windows" ]; then
        echo "Install Python 3:"
        echo "  Visit: https://www.python.org/downloads/"
        echo "  Important: Check 'Add Python to PATH' during installation"
    else
        echo "Install Python 3:"
        echo "  Visit: https://www.python.org/downloads/"
        echo "  Or run: sudo apt install python3 python3-pip python3-venv"
    fi
echo ""
    echo "After installing Python 3, close and reopen your terminal, then run this script again."
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
pip install -e . --quiet

echo ""
echo "Setup complete!"
echo ""

# Prompt for API key if .env doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Configure API Key"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "To get your OpenAI API key:"
        echo "  1. Visit: https://platform.openai.com/api-keys"
        echo "  2. Sign in or create an account"
        echo "  3. Click 'Create new secret key'"
        echo "  4. Copy the key (you'll only see it once!)"
        echo ""
        read -p "Paste your OpenAI API key here (or press Enter to skip): " api_key
        if [ -n "$api_key" ]; then
            # Copy .env.example to .env and replace the placeholder
            cp .env.example .env
            # Use sed with backup extension for macOS compatibility
            if [ "$MACHINE" = "macOS" ]; then
                sed -i.bak "s/your_openai_api_key_here/$api_key/" .env
                rm -f .env.bak
            else
                sed -i "s/your_openai_api_key_here/$api_key/" .env
            fi
            echo "API key saved to .env file"
        else
            # Still create .env from example even if skipped
            cp .env.example .env
            echo ""
            echo "Skipped API key setup."
            echo "To add it later, edit the .env file and replace 'your_openai_api_key_here' with your API key."
        fi
        echo ""
    else
        # Fallback if .env.example doesn't exist
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Configure API Key"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "To get your OpenAI API key:"
        echo "  1. Visit: https://platform.openai.com/api-keys"
        echo "  2. Sign in or create an account"
        echo "  3. Click 'Create new secret key'"
        echo "  4. Copy the key (you'll only see it once!)"
        echo ""
        read -p "Paste your OpenAI API key here (or press Enter to skip): " api_key
        if [ -n "$api_key" ]; then
            echo "OPENAI_API_KEY=$api_key" > .env
            echo "API key saved to .env file"
        else
            echo ""
            echo "Skipped API key setup. Create a .env file later with:"
            echo "  echo 'OPENAI_API_KEY=sk-your-key' > .env"
fi
        echo ""
    fi
echo ""
else
    echo "API key file (.env) already exists. Skipping API key setup."
echo ""
fi

echo "Next steps:"
echo "  1. Activate: source venv/bin/activate"
echo "  2. Run: ./scripts/generate_campaign.sh"

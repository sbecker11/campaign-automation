# How to Render Mermaid Diagrams as PNG

## Option 1: Mermaid CLI (Recommended)

### Install Mermaid CLI
```bash
# Using npm (requires Node.js)
npm install -g @mermaid-js/mermaid-cli

# Or using Homebrew (macOS)
brew install mermaid-cli
```

### Render the diagram
```bash
# From the docs directory
cd docs
mmdc -i generate_campaign_flow.md -o generate_campaign_flow.png

# Or specify the mermaid code block explicitly
mmdc -i generate_campaign_flow.md -o generate_campaign_flow.png -t dark -b transparent
```

### Options:
- `-i`: Input file (markdown with mermaid code block)
- `-o`: Output file (PNG)
- `-t`: Theme (default, dark, forest, neutral)
- `-b`: Background color (transparent, white, etc.)
- `-w`: Width in pixels
- `-H`: Height in pixels

## Option 2: Online Tools

### Mermaid Live Editor
1. Go to https://mermaid.live/
2. Paste your mermaid code
3. Click "Actions" → "Download PNG"

### Mermaid.ink API
```bash
# Extract mermaid code from markdown and use API
curl "https://mermaid.ink/img/$(echo 'graph TD; A-->B' | base64)" -o diagram.png
```

## Option 3: VS Code Extension

1. Install "Markdown Preview Mermaid Support" extension
2. Open the markdown file
3. Right-click on the preview → "Export as PNG"

## Option 4: Python Script (Using mermaid.ink API)

Create a script to extract and render:

```python
#!/usr/bin/env python3
import re
import base64
import requests
from pathlib import Path

def extract_mermaid_code(markdown_file):
    """Extract mermaid code block from markdown."""
    content = Path(markdown_file).read_text()
    match = re.search(r'```mermaid\n(.*?)\n```', content, re.DOTALL)
    if match:
        return match.group(1)
    return None

def render_mermaid_to_png(mermaid_code, output_file):
    """Render mermaid diagram to PNG using mermaid.ink API."""
    # Encode mermaid code
    encoded = base64.urlsafe_b64encode(mermaid_code.encode()).decode()
    
    # Request PNG from API
    url = f"https://mermaid.ink/img/{encoded}"
    response = requests.get(url)
    
    if response.status_code == 200:
        Path(output_file).write_bytes(response.content)
        print(f"✅ Saved: {output_file}")
    else:
        print(f"❌ Error: {response.status_code}")

if __name__ == '__main__':
    mermaid_code = extract_mermaid_code('docs/generate_campaign_flow.md')
    if mermaid_code:
        render_mermaid_to_png(mermaid_code, 'docs/generate_campaign_flow.png')
    else:
        print("❌ No mermaid code found")
```

## Option 5: Quick Script (All-in-one)

Save this as `render_diagram.sh`:

```bash
#!/bin/bash
# Extract mermaid code and render to PNG

INPUT="$1"
OUTPUT="${INPUT%.md}.png"

if [ -z "$INPUT" ]; then
    echo "Usage: $0 <markdown_file>"
    exit 1
fi

# Check if mmdc is available
if command -v mmdc &> /dev/null; then
    echo "Using Mermaid CLI..."
    mmdc -i "$INPUT" -o "$OUTPUT" -t default -b white
elif command -v node &> /dev/null; then
    echo "Mermaid CLI not found. Install with: npm install -g @mermaid-js/mermaid-cli"
    exit 1
else
    echo "Node.js not found. Please install Node.js first."
    exit 1
fi
```

## Quick Start (If you have Node.js)

```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Render the diagram
cd docs
mmdc -i generate_campaign_flow.md -o generate_campaign_flow.png
```


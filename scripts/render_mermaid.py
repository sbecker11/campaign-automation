#!/usr/bin/env python3
"""
Render Mermaid diagram from markdown file to PNG.

Usage:
    python scripts/render_mermaid.py docs/generate_campaign_flow.md
    python scripts/render_mermaid.py docs/generate_campaign_flow.md -o output.png
"""

import re
import base64
import sys
import argparse
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ Error: requests library not found. Install with: pip install requests")
    sys.exit(1)


def extract_mermaid_code(markdown_file: Path) -> str:
    """Extract mermaid code block from markdown."""
    content = markdown_file.read_text()
    match = re.search(r'```mermaid\n(.*?)\n```', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def render_mermaid_to_png(mermaid_code: str, output_file: Path) -> bool:
    """Render mermaid diagram to PNG using mermaid.ink API."""
    # Encode mermaid code (URL-safe base64)
    encoded = base64.urlsafe_b64encode(mermaid_code.encode()).decode().rstrip('=')
    
    # Request PNG from API
    url = f"https://mermaid.ink/img/{encoded}"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            output_file.write_bytes(response.content)
            return True
        else:
            print(f"❌ Error: API returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching diagram: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Render Mermaid diagram from markdown to PNG')
    parser.add_argument('input', type=Path, help='Input markdown file with mermaid code block')
    parser.add_argument('-o', '--output', type=Path, help='Output PNG file (default: input filename with .png extension)')
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"❌ Error: Input file not found: {args.input}")
        sys.exit(1)
    
    # Extract mermaid code
    mermaid_code = extract_mermaid_code(args.input)
    if not mermaid_code:
        print(f"❌ Error: No mermaid code block found in {args.input}")
        sys.exit(1)
    
    # Determine output file
    if args.output:
        output_file = args.output
    else:
        output_file = args.input.with_suffix('.png')
    
    # Render to PNG
    print(f"📊 Rendering diagram from {args.input}...")
    if render_mermaid_to_png(mermaid_code, output_file):
        print(f"✅ Saved: {output_file}")
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()


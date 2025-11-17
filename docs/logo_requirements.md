# Logo Requirements

## Overview

Logos are optional in campaign images. If you want to use a logo, define `logo_path` in the `brand_guidelines` section of your campaign YAML. The logo will only be used if `logo_path` is defined AND the file exists.

## File Format Requirements

- **Format:** PNG (with transparency recommended for better integration)
- **Dimensions:** Minimum 512x512px
- **Aspect Ratio:** Square (1:1) recommended for best results
- **File Location:** Must match the `logo_path` specified in your campaign configuration

## Usage

1. Add your logo file to the project (e.g., `assets/spexture.com-logo.png`)
2. In your campaign YAML, add `logo_path` to the `brand_guidelines` section:
   ```yaml
   brand_guidelines:
     brand_colors:
       - "#FF6B35"
       - "#004E89"
     logo_path: "assets/spexture.com-logo.png"
   ```
3. The `generate_campaign.sh` script will automatically check if the logo file exists when `logo_path` is defined
4. If the file doesn't exist, you'll see a warning and the logo will be skipped

## Validation

The `generate_campaign.sh` script automatically validates:
- If `logo_path` is defined in the campaign YAML
- If the specified file exists
- Shows a warning if the file is missing
- Confirms if the file is found

No manual checking required - the script handles validation automatically.


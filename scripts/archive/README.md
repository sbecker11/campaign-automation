# Archive

This directory contains scripts that were used for one-time migrations or fixes and are no longer actively used.

## Archived Scripts

### `migrate_campaigns.py`
- **Purpose**: Migrated old campaign output structures to the new format
- **When**: Used during the transition from old structure (with `reports/` folder and separate JSON files) to the new consolidated `campaign_generated.json` format
- **Status**: No longer needed - all campaigns have been migrated

### `fix_campaign_json.py`
- **Purpose**: Fixed JSON structure issues in campaign output files
- **When**: Used to correct typos, standardize field names, and align structure with the generator's intended output
- **Status**: No longer needed - all campaigns have been fixed

### `download_sunglasses.sh`
- **Purpose**: Helper script for downloading sunglasses product images
- **When**: Used for testing and development with specific product assets
- **Status**: No longer needed - campaigns now use AI-generated images or existing assets from campaign YAML

### `report_campaign.sh`
- **Purpose**: Command-line script to display campaign_generated.json file
- **When**: Used to view campaign status and reports from the terminal
- **Status**: No longer needed - replaced by the refine UI (`refine_campaign.sh`) which provides better visualization, filtering, and interaction with campaign data

## Note

These scripts are kept for historical reference but should not be run on current campaigns. The current codebase generates campaigns in the correct format from the start.


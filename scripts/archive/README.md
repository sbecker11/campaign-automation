# Archive

This directory contains scripts that were used for one-time migrations or fixes and are no longer actively used.

## Archived Scripts

### `migrate_campaigns.py`
- **Purpose**: Migrated old campaign output structures to the new format
- **When**: Used during the transition from old structure (with `reports/` folder and separate JSON files) to the new consolidated `campaign_instance.json` format (previously `campaign_generated.json`)
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
- **Purpose**: Command-line script to display campaign_instance.json file (previously `campaign_generated.json`)
- **When**: Used to view campaign status and reports from the terminal
- **Status**: No longer needed - replaced by the refine UI (`refine_campaign.sh`) which provides better visualization, filtering, and interaction with campaign data

### `install_pre_commit_hook.sh`
- **Purpose**: Installs a Git pre-commit hook to prevent committing files in the `outputs/` directory
- **When**: Used during development setup to enforce repository structure
- **Status**: Not needed for production release - setup is handled by `setup.sh` or can be installed manually if needed

### `kill_refine_servers.sh`
- **Purpose**: Utility script to kill any running refine server processes
- **When**: Used during development to clean up stuck server processes
- **Status**: Development utility - not needed for production release

### `run_campaign_multiple.sh`
- **Purpose**: Runs the campaign pipeline multiple times with timestamps for testing/load testing
- **When**: Used for testing campaign generation at scale or generating multiple campaign instances
- **Status**: Testing/utility script - not needed for production release

### `render_mermaid.py`
- **Purpose**: Renders Mermaid diagrams from markdown files to PNG images
- **When**: Used for generating documentation diagrams
- **Status**: Development/documentation utility - not needed for production release

## Note

These scripts are kept for historical reference and development purposes. Production releases only require:
- `generate_campaign.sh` - Main campaign generation script
- `refine_campaign.sh` - Campaign refinement UI launcher
- `refine_server.py` - Refine UI server
- `refine_campaign.html` - Refine UI frontend


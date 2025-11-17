"""Campaign Campaign Parser"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any
import logging


class CampaignParser:
    """Parse and validate campaign campaigns."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.required_fields = [
            'campaign_id',
            'products',
            'target_market',
            'campaign_tagline'
        ]
    
    def parse(self, campaign_path: str) -> Dict[str, Any]:
        """Parse a campaign campaign from YAML or JSON file."""
        path = Path(campaign_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Campaign file not found: {campaign_path}")
        
        with open(path, 'r') as f:
            if path.suffix.lower() in ['.yaml', '.yml']:
                campaign = yaml.safe_load(f)
            elif path.suffix.lower() == '.json':
                campaign = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")
        
        self._validate(campaign)
        campaign = self._apply_defaults(campaign)
        
        self.logger.info(f"Successfully parsed campaign: {campaign.get('campaign_id')}")
        return campaign
    
    def _validate(self, campaign: Dict[str, Any]) -> None:
        """Validate required fields in campaign."""
        missing_fields = []
        
        for field in self.required_fields:
            if field not in campaign:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        if not isinstance(campaign['products'], list) or len(campaign['products']) == 0:
            raise ValueError("Campaign must contain at least one product")
        
        for idx, product in enumerate(campaign['products']):
            if 'product_id' not in product:
                raise ValueError(f"Product {idx} missing 'product_id'")
            if 'name' not in product:
                raise ValueError(f"Product {idx} missing 'name'")
    
    def _apply_defaults(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values for optional fields."""
        defaults = {
            'aspect_ratios': ['1:1', '9:16', '16:9'],
            'campaign_name': campaign.get('campaign_id', 'Campaign'),
            'localization': {'languages': ['en']},
            'brand_guidelines': {'brand_colors': [], 'logo_required': False},
            'content_safety': {'prohibited_words': []}
        }
        
        for key, value in defaults.items():
            if key not in campaign:
                campaign[key] = value
            elif isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if subkey not in campaign[key]:
                        campaign[key][subkey] = subvalue
        
        return campaign

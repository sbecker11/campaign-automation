"""Campaign Brief Parser"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any
import logging


class BriefParser:
    """Parse and validate campaign briefs."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.required_fields = [
            'campaign_id',
            'products',
            'target_market',
            'campaign_message'
        ]
    
    def parse(self, brief_path: str) -> Dict[str, Any]:
        """Parse a campaign brief from YAML or JSON file."""
        path = Path(brief_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Brief file not found: {brief_path}")
        
        with open(path, 'r') as f:
            if path.suffix.lower() in ['.yaml', '.yml']:
                brief = yaml.safe_load(f)
            elif path.suffix.lower() == '.json':
                brief = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")
        
        self._validate(brief)
        brief = self._apply_defaults(brief)
        
        self.logger.info(f"Successfully parsed brief: {brief.get('campaign_id')}")
        return brief
    
    def _validate(self, brief: Dict[str, Any]) -> None:
        """Validate required fields in brief."""
        missing_fields = []
        
        for field in self.required_fields:
            if field not in brief:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        if not isinstance(brief['products'], list) or len(brief['products']) == 0:
            raise ValueError("Brief must contain at least one product")
        
        for idx, product in enumerate(brief['products']):
            if 'product_id' not in product:
                raise ValueError(f"Product {idx} missing 'product_id'")
            if 'name' not in product:
                raise ValueError(f"Product {idx} missing 'name'")
    
    def _apply_defaults(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values for optional fields."""
        defaults = {
            'aspect_ratios': ['1:1', '9:16', '16:9'],
            'campaign_name': brief.get('campaign_id', 'Campaign'),
            'localization': {'languages': ['en']},
            'brand_guidelines': {'brand_colors': [], 'logo_required': False},
            'content_safety': {'prohibited_words': [], 'require_disclaimer': False}
        }
        
        for key, value in defaults.items():
            if key not in brief:
                brief[key] = value
            elif isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if subkey not in brief[key]:
                        brief[key][subkey] = subvalue
        
        return brief

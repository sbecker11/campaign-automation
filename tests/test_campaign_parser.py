"""
Tests for the Campaign Campaign Parser.
"""

import pytest
from pathlib import Path
import yaml
from src.campaign_parser import CampaignParser


def test_parse_sample_campaign(sample_campaign_yaml):
    """Test parsing a valid campaign campaign."""
    parser = CampaignParser()
    campaign = parser.parse(sample_campaign_yaml)
    
    assert campaign is not None
    assert campaign['campaign_id'] == 'test_campaign_001'
    assert len(campaign['products']) == 1
    assert campaign['products'][0]['product_id'] == 'test_sunscreen'


def test_campaign_parser_validates_required_fields(temp_dir):
    """Test that parser validates required fields."""
    # Create incomplete campaign
    incomplete_campaign = {
        'campaign_id': 'test_001'
        # Missing required fields
    }
    
    campaign_path = temp_dir / "incomplete_campaign.yaml"
    with open(campaign_path, 'w') as f:
        yaml.dump(incomplete_campaign, f)
    
    parser = CampaignParser()
    
    with pytest.raises((ValueError, KeyError)):
        parser.parse(campaign_path)


def test_campaign_parser_handles_invalid_yaml(temp_dir):
    """Test that parser handles invalid YAML gracefully."""
    # Create invalid YAML file
    invalid_yaml_path = temp_dir / "invalid.yaml"
    with open(invalid_yaml_path, 'w') as f:
        f.write("invalid: yaml: content:\n  - broken")
    
    parser = CampaignParser()
    
    with pytest.raises(yaml.YAMLError):
        parser.parse(invalid_yaml_path)

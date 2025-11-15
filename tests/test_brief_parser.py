"""
Tests for the Campaign Brief Parser.
"""

import pytest
from pathlib import Path
import yaml
from src.brief_parser import BriefParser


def test_parse_sample_brief(sample_brief_yaml):
    """Test parsing a valid campaign brief."""
    parser = BriefParser()
    brief = parser.parse(sample_brief_yaml)
    
    assert brief is not None
    assert brief['campaign_id'] == 'test_campaign_001'
    assert len(brief['products']) == 1
    assert brief['products'][0]['product_id'] == 'test_sunscreen'


def test_brief_parser_validates_required_fields(temp_dir):
    """Test that parser validates required fields."""
    # Create incomplete brief
    incomplete_brief = {
        'campaign_id': 'test_001'
        # Missing required fields
    }
    
    brief_path = temp_dir / "incomplete_brief.yaml"
    with open(brief_path, 'w') as f:
        yaml.dump(incomplete_brief, f)
    
    parser = BriefParser()
    
    with pytest.raises((ValueError, KeyError)):
        parser.parse(brief_path)


def test_brief_parser_handles_invalid_yaml(temp_dir):
    """Test that parser handles invalid YAML gracefully."""
    # Create invalid YAML file
    invalid_yaml_path = temp_dir / "invalid.yaml"
    with open(invalid_yaml_path, 'w') as f:
        f.write("invalid: yaml: content:\n  - broken")
    
    parser = BriefParser()
    
    with pytest.raises(yaml.YAMLError):
        parser.parse(invalid_yaml_path)

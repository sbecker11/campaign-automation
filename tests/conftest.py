"""
Shared test fixtures.
"""

import pytest
from pathlib import Path
import tempfile
from PIL import Image


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_campaign_dict():
    """Sample campaign dictionary for testing."""
    return {
        'campaign_id': 'test_campaign_001',
        'campaign_name': 'Test Summer Campaign',
        'products': [
            {
                'product_id': 'test_sunscreen',
                'name': 'Test Sunscreen SPF 50',
                'description': 'Premium sunscreen for testing',
                'generate_new': True
            }
        ],
        'target_market': 'US_California',
        'target_audience': 'test_audience_25-45',
        'campaign_tagline': 'Test campaign tagline',
        'campaign_hashtags': ['#TestCampaign', '#Testing'],
        'brand_guidelines': {
            'brand_colors': ['#FF6B35', '#004E89', '#FFFFFF'],
            'logo_required': False
        },
        'aspect_ratios': ['1:1', '9:16'],
        'content_safety': {
            'prohibited_words': ['guaranteed', 'miracle']
        }
    }


@pytest.fixture
def sample_campaign_yaml(temp_dir, sample_campaign_dict):
    """Create a sample campaign YAML file."""
    import yaml
    
    campaign_path = temp_dir / "test_campaign.yaml"
    with open(campaign_path, 'w') as f:
        yaml.dump(sample_campaign_dict, f)
    
    return campaign_path


@pytest.fixture
def brand_guidelines_dict():
    """Sample brand guidelines for testing."""
    return {
        'brand_colors': ['#FF6B35', '#004E89', '#FFFFFF'],
        'logo_required': False,
        'logo_path': None
    }


@pytest.fixture
def sample_image(temp_dir):
    """Create a sample image for testing."""
    img = Image.new('RGB', (500, 500), color='red')
    return img


@pytest.fixture
def sample_image_file(temp_dir):
    """Create a sample image file for testing."""
    img = Image.new('RGB', (500, 500), color='blue')
    img_path = temp_dir / "test_image.png"
    img.save(img_path)
    return img_path


# Keep old fixtures for backward compatibility
@pytest.fixture
def sample_brief_dict(sample_campaign_dict):
    """Deprecated: use sample_campaign_dict instead."""
    return sample_campaign_dict


@pytest.fixture
def sample_brief_yaml(sample_campaign_yaml):
    """Deprecated: use sample_campaign_yaml instead."""
    return sample_campaign_yaml

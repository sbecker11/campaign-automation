"""
Pytest configuration and shared fixtures for campaign automation tests.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from PIL import Image
import yaml


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_brief_dict():
    """Sample campaign brief dictionary."""
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
        'campaign_message': 'Test campaign message',
        'campaign_hashtags': ['#TestCampaign', '#Testing'],
        'brand_guidelines': {
            'brand_colors': ['#FF6B35', '#004E89', '#FFFFFF'],
            'logo_required': False
        },
        'aspect_ratios': ['1:1', '9:16'],
        'content_safety': {
            'prohibited_words': ['guaranteed', 'miracle'],
            'require_disclaimer': False
        }
    }


@pytest.fixture
def sample_brief_yaml(temp_dir, sample_brief_dict):
    """Create a temporary YAML campaign brief file."""
    brief_path = temp_dir / "test_brief.yaml"
    with open(brief_path, 'w') as f:
        yaml.dump(sample_brief_dict, f)
    return brief_path


@pytest.fixture
def sample_image():
    """Create a sample test image."""
    img = Image.new('RGB', (1024, 1024), color=(255, 100, 50))
    return img


@pytest.fixture
def sample_image_file(temp_dir, sample_image):
    """Create a sample test image file."""
    img_path = temp_dir / "test_image.png"
    sample_image.save(img_path)
    return img_path


@pytest.fixture
def brand_guidelines_dict():
    """Sample brand guidelines dictionary."""
    return {
        'brand_colors': [
            {'hex': '#FF6B35', 'name': 'Primary Orange'},
            {'hex': '#004E89', 'name': 'Primary Blue'},
            {'hex': '#FFFFFF', 'name': 'White'}
        ],
        'prohibited_colors': ['#FF0000'],
        'prohibited_words': ['guaranteed', 'miracle', 'cure'],
        'required_disclaimers': [],
        'logo_requirements': {
            'min_size_percent': 5,
            'max_size_percent': 20,
            'allowed_positions': ['top-left', 'top-right', 'bottom-left', 'bottom-right']
        }
    }

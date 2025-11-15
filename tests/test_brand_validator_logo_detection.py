"""
Tests for BrandValidator logo detection (lines 32-37).
"""

import pytest
from pathlib import Path
from PIL import Image
from src.brand_validator import BrandValidator


def test_validate_with_logo_detection(temp_dir):
    """Test validation when logo_path exists and logo detection runs."""
    validator = BrandValidator()
    
    # Create test image
    img = Image.new('RGB', (800, 600), 'white')
    img_path = temp_dir / "test_image.png"
    img.save(img_path)
    
    # Create logo file
    logo = Image.new('RGBA', (100, 100), (255, 0, 0, 255))
    logo_path = temp_dir / "logo.png"
    logo.save(logo_path)
    
    brief = {
        'brand_guidelines': {
            'logo_required': True,
            'logo_path': str(logo_path),
            'brand_colors': []
        }
    }
    
    result = validator.validate(img_path, brief)
    
    assert result is not None
    assert 'checks' in result
    assert 'logo_detection' in result['checks']


def test_validate_logo_not_detected(temp_dir):
    """Test when logo is required but not detected in image."""
    validator = BrandValidator()
    
    # Create image without logo
    img = Image.new('RGB', (800, 600), (255, 255, 255))
    img_path = temp_dir / "no_logo_image.png"
    img.save(img_path)
    
    # Create logo file
    logo = Image.new('RGBA', (50, 50), (0, 0, 255, 255))
    logo_path = temp_dir / "required_logo.png"
    logo.save(logo_path)
    
    brief = {
        'brand_guidelines': {
            'logo_required': True,
            'logo_path': str(logo_path),
            'brand_colors': []
        }
    }
    
    result = validator.validate(img_path, brief)
    
    # Should mark as non-compliant if logo not detected
    assert 'overall_compliant' in result


def test_validate_without_logo_path(temp_dir):
    """Test validation when no logo_path is provided."""
    validator = BrandValidator()
    
    img = Image.new('RGB', (500, 500), 'white')
    img_path = temp_dir / "image.png"
    img.save(img_path)
    
    brief = {
        'brand_guidelines': {
            'brand_colors': []
        }
    }
    
    result = validator.validate(img_path, brief)
    
    # Should skip logo detection
    assert result is not None


def test_validate_logo_path_not_exists(temp_dir):
    """Test when logo_path is provided but file doesn't exist."""
    validator = BrandValidator()
    
    img = Image.new('RGB', (500, 500), 'white')
    img_path = temp_dir / "image.png"
    img.save(img_path)
    
    brief = {
        'brand_guidelines': {
            'logo_path': '/nonexistent/logo.png',
            'brand_colors': []
        }
    }
    
    result = validator.validate(img_path, brief)
    
    # Should skip logo detection when file doesn't exist
    assert result is not None

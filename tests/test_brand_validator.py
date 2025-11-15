"""
Tests for the Brand Validator.
"""

import pytest
from PIL import Image
from src.brand_validator import BrandValidator


def test_validate_brand_colors(sample_image_file, sample_brief_dict):
    """Test validation of brand colors in an image."""
    validator = BrandValidator()
    
    result = validator.validate(sample_image_file, sample_brief_dict)
    assert 'overall_compliant' in result


def test_validate_comprehensive(sample_image_file, sample_brief_dict):
    """Test comprehensive validation."""
    validator = BrandValidator()
    
    result = validator.validate(sample_image_file, sample_brief_dict)
    
    assert 'overall_compliant' in result
    assert 'image_path' in result
    assert isinstance(result['overall_compliant'], bool)

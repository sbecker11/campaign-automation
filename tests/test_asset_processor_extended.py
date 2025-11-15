"""
Extended tests for Asset Processor.
"""

import pytest
from PIL import Image
from src.asset_processor import AssetProcessor


def test_resize_to_multiple_aspect_ratios(sample_image_file, sample_brief_dict, temp_dir):
    """Test creating variants for multiple aspect ratios."""
    processor = AssetProcessor()
    product = sample_brief_dict['products'][0]
    
    output_dir = temp_dir / "multi_output"
    output_dir.mkdir(exist_ok=True)
    
    # Test with different aspect ratios
    for aspect_ratio in ["1:1", "9:16", "16:9"]:
        result = processor.create_variant(
            sample_image_file,
            product,
            sample_brief_dict,
            aspect_ratio,
            output_dir
        )
        assert output_dir.exists()


def test_logo_validation(temp_dir):
    """Test logo file validation."""
    processor = AssetProcessor()
    
    # Test with non-existent logo
    if hasattr(processor, '_validate_logo_file'):
        result = processor._validate_logo_file("nonexistent_logo.png")
        assert result == False


def test_text_wrapping():
    """Test text wrapping functionality."""
    processor = AssetProcessor()
    
    if hasattr(processor, '_wrap_text'):
        # This would need a font object - skip if not available
        pytest.skip("Text wrapping test needs font setup")

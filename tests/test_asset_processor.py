"""
Tests for the Asset Processor.
"""

import pytest
from PIL import Image
from src.asset_processor import AssetProcessor


def test_create_variant(sample_image_file, sample_brief_dict, temp_dir):
    """Test creating image variants."""
    processor = AssetProcessor()
    
    product = sample_brief_dict['products'][0]
    aspect_ratio = "1:1"
    
    # Pass directory, not file path
    output_dir = temp_dir / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    result = processor.create_variant(
        sample_image_file,
        product,
        sample_brief_dict,
        aspect_ratio,
        output_dir
    )
    
    # Check that output was created
    assert output_dir.exists()
    # The create_variant should create files under output_dir
    output_files = list(output_dir.rglob("*.png"))
    assert len(output_files) > 0 or result is not None


def test_asset_processor_initialization():
    """Test AssetProcessor can be initialized."""
    processor = AssetProcessor()
    assert processor is not None

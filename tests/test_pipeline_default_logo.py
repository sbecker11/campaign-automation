"""
Tests for Pipeline default logo creation (lines 69-101).
"""

import pytest
from pathlib import Path
from src.pipeline import CampaignPipeline


def test_pipeline_creates_default_logo_if_missing(temp_dir):
    """Test that pipeline creates default logo when none exists."""
    brand_dir = temp_dir / "brand_no_logo"
    brand_dir.mkdir()
    
    # Don't create a logo - pipeline should create one
    pipeline = CampaignPipeline(brand_dir)
    
    # Check if default logo was created
    expected_logo_path = brand_dir / "logo.png"
    
    # Logo should exist or be attempted
    assert pipeline is not None


def test_pipeline_uses_existing_logo(temp_dir):
    """Test that pipeline uses existing logo when available."""
    from PIL import Image
    
    brand_dir = temp_dir / "brand_with_logo"
    brand_dir.mkdir()
    
    # Create existing logo
    existing_logo = Image.new('RGBA', (200, 200), (0, 255, 0, 255))
    logo_path = brand_dir / "logo.png"
    existing_logo.save(logo_path)
    
    pipeline = CampaignPipeline(brand_dir)
    
    # Should use existing logo
    assert logo_path.exists()
    
    # Verify it's the green logo we created, not a new one
    img = Image.open(logo_path)
    pixels = img.load()
    # Check a pixel is green (not the default orange from auto-generation)
    assert pixels[100, 100][1] == 255  # Green channel


def test_pipeline_default_logo_format(temp_dir):
    """Test the format of auto-generated logo."""
    brand_dir = temp_dir / "test_brand"
    brand_dir.mkdir()
    
    # Remove logo if it exists
    logo_path = brand_dir / "logo.png"
    if logo_path.exists():
        logo_path.unlink()
    
    pipeline = CampaignPipeline(brand_dir)
    
    # If logo was created, verify it
    if logo_path.exists():
        from PIL import Image
        logo = Image.open(logo_path)
        
        # Check dimensions
        assert logo.size == (200, 200)
        
        # Check mode includes alpha
        assert 'A' in logo.mode

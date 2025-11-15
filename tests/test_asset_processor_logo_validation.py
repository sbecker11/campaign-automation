"""
Tests for AssetProcessor logo validation (lines 47-75).
"""

import pytest
from pathlib import Path
from PIL import Image
from src.asset_processor import AssetProcessor


def test_validate_logo_file_valid_rgb(temp_dir):
    """Test logo validation with valid RGB image."""
    processor = AssetProcessor()
    
    logo = Image.new('RGB', (100, 100), (255, 0, 0))
    logo_path = temp_dir / "valid_rgb_logo.png"
    logo.save(logo_path)
    
    result = processor._validate_logo_file(str(logo_path))
    assert result == True


def test_validate_logo_file_valid_rgba(temp_dir):
    """Test logo validation with valid RGBA image."""
    processor = AssetProcessor()
    
    logo = Image.new('RGBA', (150, 150), (255, 0, 0, 255))
    logo_path = temp_dir / "valid_rgba_logo.png"
    logo.save(logo_path)
    
    result = processor._validate_logo_file(str(logo_path))
    assert result == True


def test_validate_logo_file_valid_grayscale(temp_dir):
    """Test logo validation with grayscale image (mode L)."""
    processor = AssetProcessor()
    
    logo = Image.new('L', (120, 120), 128)
    logo_path = temp_dir / "gray_logo.png"
    logo.save(logo_path)
    
    result = processor._validate_logo_file(str(logo_path))
    assert result == True


def test_validate_logo_file_too_small(temp_dir):
    """Test logo validation fails for images smaller than 10x10."""
    processor = AssetProcessor()
    
    logo = Image.new('RGB', (9, 9), (255, 0, 0))
    logo_path = temp_dir / "tiny_logo.png"
    logo.save(logo_path)
    
    result = processor._validate_logo_file(str(logo_path))
    assert result == False


def test_validate_logo_file_corrupted(temp_dir):
    """Test logo validation with corrupted file."""
    processor = AssetProcessor()
    
    corrupted_path = temp_dir / "corrupted.png"
    corrupted_path.write_bytes(b"This is not a valid image file")
    
    result = processor._validate_logo_file(str(corrupted_path))
    assert result == False


def test_validate_logo_file_nonexistent():
    """Test logo validation with non-existent file."""
    processor = AssetProcessor()
    
    result = processor._validate_logo_file("/path/to/nonexistent/logo.png")
    assert result == False


def test_validate_logo_file_caching(temp_dir):
    """Test that logo validation results are cached."""
    processor = AssetProcessor()
    
    logo = Image.new('RGB', (100, 100), (255, 0, 0))
    logo_path = temp_dir / "cached_logo.png"
    logo.save(logo_path)
    
    result1 = processor._validate_logo_file(str(logo_path))
    result2 = processor._validate_logo_file(str(logo_path))
    
    assert result1 == True
    assert result2 == True

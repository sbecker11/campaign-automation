"""
Comprehensive tests for utility functions.
"""

import pytest
from pathlib import Path
import shutil
from src.utils import ensure_dir, clean_temp_files, validate_image_path


def test_ensure_dir_creates_directory(temp_dir):
    """Test that ensure_dir creates directories."""
    new_dir = temp_dir / "new_directory"
    
    assert not new_dir.exists()
    
    result = ensure_dir(new_dir)
    
    assert new_dir.exists()
    assert result == new_dir


def test_ensure_dir_with_nested_paths(temp_dir):
    """Test ensure_dir with nested directory structure."""
    nested_dir = temp_dir / "level1" / "level2" / "level3"
    
    result = ensure_dir(nested_dir)
    
    assert nested_dir.exists()
    assert result == nested_dir


def test_ensure_dir_existing_directory(temp_dir):
    """Test ensure_dir with existing directory."""
    existing_dir = temp_dir / "existing"
    existing_dir.mkdir()
    
    result = ensure_dir(existing_dir)
    
    assert existing_dir.exists()
    assert result == existing_dir


def test_clean_temp_files_removes_directory(temp_dir):
    """Test that clean_temp_files removes temp directory."""
    test_temp = temp_dir / "temp_test"
    test_temp.mkdir()
    
    # Create some files in it
    (test_temp / "file1.txt").write_text("test")
    (test_temp / "file2.txt").write_text("test")
    
    assert test_temp.exists()
    
    clean_temp_files(test_temp)
    
    assert not test_temp.exists()


def test_clean_temp_files_nonexistent_directory(temp_dir):
    """Test clean_temp_files with non-existent directory."""
    nonexistent = temp_dir / "does_not_exist"
    
    # Should not raise error
    clean_temp_files(nonexistent)
    
    assert not nonexistent.exists()


def test_validate_image_path_valid_png(temp_dir):
    """Test validate_image_path with valid PNG file."""
    from PIL import Image
    
    img_path = temp_dir / "test.png"
    img = Image.new('RGB', (100, 100), color='red')
    img.save(img_path)
    
    assert validate_image_path(img_path) == True


def test_validate_image_path_valid_jpg(temp_dir):
    """Test validate_image_path with valid JPG file."""
    from PIL import Image
    
    img_path = temp_dir / "test.jpg"
    img = Image.new('RGB', (100, 100), color='blue')
    img.save(img_path)
    
    assert validate_image_path(img_path) == True


def test_validate_image_path_various_extensions(temp_dir):
    """Test validate_image_path with various valid extensions."""
    from PIL import Image
    
    valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    
    for ext in valid_extensions:
        img_path = temp_dir / f"test{ext}"
        
        # Create actual image file
        img = Image.new('RGB', (50, 50))
        img.save(img_path)
        
        assert validate_image_path(img_path) == True


def test_validate_image_path_invalid_extension(temp_dir):
    """Test validate_image_path with invalid extension."""
    txt_path = temp_dir / "test.txt"
    txt_path.write_text("not an image")
    
    assert validate_image_path(txt_path) == False


def test_validate_image_path_nonexistent_file(temp_dir):
    """Test validate_image_path with non-existent file."""
    nonexistent = temp_dir / "does_not_exist.png"
    
    assert validate_image_path(nonexistent) == False


def test_validate_image_path_case_insensitive(temp_dir):
    """Test that validate_image_path is case-insensitive."""
    from PIL import Image
    
    # Test uppercase extension
    img_path = temp_dir / "test.PNG"
    img = Image.new('RGB', (50, 50))
    img.save(img_path)
    
    assert validate_image_path(img_path) == True

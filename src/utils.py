"""Utility Functions"""

import logging
from pathlib import Path
import shutil


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists, create if it doesn't."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def clean_temp_files(temp_dir: Path = Path("temp")):
    """Clean up temporary files."""
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        logging.info(f"Cleaned temporary directory: {temp_dir}")


def validate_image_path(path: Path) -> bool:
    """Validate that path points to a valid image file."""
    if not path.exists():
        return False
    valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
    return path.suffix.lower() in valid_extensions

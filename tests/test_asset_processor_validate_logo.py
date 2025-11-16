from pathlib import Path
from unittest.mock import patch
from PIL import Image
import numpy as np
import pytest

from src.asset_processor import AssetProcessor


def test_validate_logo_unsupported_mode(tmp_path, caplog):
    ap = AssetProcessor()
    # Create palette image (mode 'P') to trigger unsupported mode branch
    p = tmp_path / "logo_p.png"
    img = Image.fromarray(np.full((20, 20, 3), 0, dtype=np.uint8), mode="RGB").convert("P")
    img.save(p)
    assert ap._validate_logo_file(str(p)) is False
    # Cached second call returns False without re-opening
    assert ap._validate_logo_file(str(p)) is False


def test_validate_logo_too_small(tmp_path):
    ap = AssetProcessor()
    p = tmp_path / "small.png"
    img = Image.new("RGB", (5, 5), (0, 0, 0))
    img.save(p)
    assert ap._validate_logo_file(str(p)) is False


def test_validate_logo_missing_file(tmp_path):
    ap = AssetProcessor()
    assert ap._validate_logo_file(str(tmp_path / "no.png")) is False



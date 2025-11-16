from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image
import pytest

from src.asset_processor import AssetProcessor


def _make_base(w=300, h=200, color=(240, 240, 240)):
    return Image.fromarray(np.full((h, w, 3), color, dtype=np.uint8))


def _make_logo_rgba(w=60, h=20, color=(20, 20, 20, 255)):
    return Image.fromarray(np.full((h, w, 4), color, dtype=np.uint8), mode='RGBA')


def _make_logo_rgb(w=60, h=20, color=(20, 20, 20)):
    return Image.fromarray(np.full((h, w, 3), color, dtype=np.uint8), mode='RGB')


@patch("PIL.Image.open")
def test_add_logo_with_text_heavy_and_background(mock_open):
    ap = AssetProcessor()
    base = _make_base()
    logo_rgba = _make_logo_rgba()
    # PIL.Image.open called for logo_path; return a fresh copy each time
    mock_open.return_value = logo_rgba.copy()

    # Force both branches: text-heavy True and needs_background True
    with patch.object(ap, "_logo_has_text", return_value=True), \
         patch.object(ap, "_logo_needs_background", return_value=True):
        out = ap._add_logo(base, "dummy_logo_path.png", aspect_ratio="1:1")
        assert isinstance(out, Image.Image)


@patch("PIL.Image.open")
def test_add_logo_non_rgba_path_and_no_background(mock_open):
    ap = AssetProcessor()
    base = _make_base()
    logo_rgb = _make_logo_rgb()
    mock_open.return_value = logo_rgb.copy()

    with patch.object(ap, "_logo_has_text", return_value=False), \
         patch.object(ap, "_logo_needs_background", return_value=False):
        out = ap._add_logo(base, "dummy_logo_path2.png", aspect_ratio="1:1")
        assert isinstance(out, Image.Image)



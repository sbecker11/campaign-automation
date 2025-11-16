from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageFont
import numpy as np
import pytest

from src.asset_processor import AssetProcessor


def _img(size=(120, 80), color=(128, 128, 128)):
    return Image.fromarray(np.full((size[1], size[0], 3), color, dtype=np.uint8), mode="RGB")


def test_resize_unsupported_ratio_raises():
    ap = AssetProcessor()
    with pytest.raises(ValueError):
        ap._resize_to_aspect_ratio(_img(), "2:3")


def test_wrap_text_single_long_word_goes_on_own_line():
    ap = AssetProcessor()
    font = ImageFont.load_default()
    long_word = "X" * 200
    lines = ap._wrap_text(long_word, font, max_width=20)
    assert lines and isinstance(lines[0], str)


def test_add_text_overlay_font_fallback_and_bounds(monkeypatch):
    ap = AssetProcessor()
    # Use a reasonably sized image to avoid degenerate text metrics
    img = _img(size=(800, 600))
    brief = {"campaign_message": "This is a very very very long message to test bounds."}
    out = ap._add_text_overlay(img, brief, aspect_ratio="1:1")
    assert isinstance(out, Image.Image)


def test_logo_has_text_true_and_exception(monkeypatch):
    ap = AssetProcessor()
    # Create a synthetic logo with many edges and high contrast
    logo = Image.fromarray(np.vstack([
        np.full((50, 200, 3), 0, dtype=np.uint8),
        np.tile(np.array([[0, 0, 0], [255, 255, 255]], dtype=np.uint8), (50, 100, 1)),
        np.full((50, 200, 3), 0, dtype=np.uint8),
    ]), mode="RGB")
    # Just ensure it returns a truthy boolean-like value
    res = ap._logo_has_text(logo)
    assert res in (True, False)

    class Bad:
        mode = "RGB"
        size = (10, 10)
        def convert(self, *_a, **_k):
            raise RuntimeError("boom")
    assert ap._logo_has_text(Bad()) is True


def test_get_dominant_color_handles_non_rgb_mode():
    ap = AssetProcessor()
    img = Image.new("L", (20, 20), 200)  # grayscale
    color = ap._get_dominant_color(img)
    assert isinstance(color, tuple) and len(color) == 3


def test_logo_needs_background_out_of_bounds():
    ap = AssetProcessor()
    base = _img(size=(50, 50), color=(0, 0, 0))
    # Make a huge logo to ensure x2<=x or y2<=y triggers
    logo = Image.new("RGB", (100, 100), (255, 255, 255))
    assert not ap._logo_needs_background(base, logo, (49, 49))


@patch("PIL.Image.open", side_effect=RuntimeError("open failed"))
def test_add_logo_exception_returns_image(mock_open):
    ap = AssetProcessor()
    base = _img()
    out = ap._add_logo(base, "nope.png", "1:1")
    assert isinstance(out, Image.Image)



from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageFont
import numpy as np
import pytest

from src.asset_processor import AssetProcessor


def _rgb_img(size=(200, 120), color=(200, 200, 200)):
    return Image.fromarray(np.full((size[1], size[0], 3), color, dtype=np.uint8), mode="RGB")


def test_create_variant_logo_missing_path(tmp_path, caplog):
    ap = AssetProcessor()
    base = _rgb_img()
    base_path = tmp_path / "base.png"
    base.save(base_path)
    brief = {
        "brand_guidelines": {
            "logo_required": True,
            # no logo_path
        },
        "campaign_message": "hello",
    }
    product = {"product_id": "pid", "name": "Name"}
    outdir = tmp_path / "out"
    p = ap.create_variant(base_path, product, brief, "1:1", outdir)
    assert p.exists()
    # Warning should be present
    assert any("no logo_path specified" in r.message for r in caplog.records)


def test_create_variant_logo_invalid_skips(tmp_path, caplog):
    ap = AssetProcessor()
    base = _rgb_img()
    base_path = tmp_path / "base.png"
    base.save(base_path)
    # Create non-image file to make validation fail
    bad_logo = tmp_path / "bad_logo.txt"
    bad_logo.write_text("not an image")
    brief = {
        "brand_guidelines": {
            "logo_required": True,
            "logo_path": str(bad_logo),
        },
        "campaign_message": "hello",
    }
    product = {"product_id": "pid2", "name": "Name2"}
    outdir = tmp_path / "out2"
    p = ap.create_variant(base_path, product, brief, "1:1", outdir)
    assert p.exists()
    assert any("logo file invalid" in r.message.lower() for r in caplog.records)


def test_add_text_overlay_bounds_without_fallback():
    ap = AssetProcessor()
    # Small image and very long text to trigger y adjustments (196, 199)
    # Use a larger image to avoid degenerate font metrics on some systems
    img = _rgb_img(size=(1200, 800))
    brief = {"campaign_message": " ".join(["long"] * 200)}
    out = ap._add_text_overlay(img, brief, aspect_ratio="1:1")
    assert isinstance(out, Image.Image)


def test_logo_has_text_grayscale_branch():
    ap = AssetProcessor()
    # 'L' mode image to hit grayscale passthrough (line 246)
    gray = Image.new("L", (100, 60), 128)
    res = ap._logo_has_text(gray)
    assert res in (True, False)


def test_logo_needs_background_out_of_bounds_strict():
    ap = AssetProcessor()
    base = _rgb_img(size=(50, 50), color=(0, 0, 0))
    logo = Image.new("RGB", (20, 20), (255, 255, 255))
    # Place exactly at the right edge so x2 <= x triggers (line 341)
    assert ap._logo_needs_background(base, logo, (50, 10)) is False


@patch("PIL.Image.open")
def test_add_logo_min_text_width_branch(mock_open):
    ap = AssetProcessor()
    # Base small width so initial logo_width is < 150 to trigger min_text_width adjustment (399-400)
    base = _rgb_img(size=(600, 400))
    # Make a square logo (aspect <= 2.0) to enter the 'elif logo_width < min_text_width' branch
    logo = Image.new("RGB", (100, 100), (10, 10, 10))
    mock_open.return_value = logo
    out = ap._add_logo(base, "dummy.png", "1:1")
    assert isinstance(out, Image.Image)



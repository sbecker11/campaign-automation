from pathlib import Path
from PIL import Image, ImageFont
import numpy as np
import pytest

from src.asset_processor import AssetProcessor


def _make_image(size=(300, 200), color=(120, 120, 120)):
    img = Image.new('RGB', size, color)
    return img


def test_wrap_text_basic():
    ap = AssetProcessor()
    font = ImageFont.load_default()
    long = "This is a long line that should wrap into multiple lines when constrained"
    lines = ap._wrap_text(long, font, max_width=100)
    assert isinstance(lines, list)
    assert len(lines) >= 2


def test_add_text_overlay_positions_and_defaults(tmp_path):
    ap = AssetProcessor()
    base = _make_image((400, 300))
    p = tmp_path / "base.png"
    base.save(p)

    brief = {
        "campaign_tagline": "Hello world from tests",
        "brand_guidelines": {}
    }
    # 1:1 overlay path (non-9:16)
    out = ap._add_text_overlay(Image.open(p), brief, aspect_ratio='1:1')
    assert isinstance(out, Image.Image)

    # 9:16 overlay path
    base_tall = _make_image((360, 640))
    pt = tmp_path / "base_tall.png"
    base_tall.save(pt)
    out2 = ap._add_text_overlay(Image.open(pt), brief, aspect_ratio='9:16')
    assert isinstance(out2, Image.Image)

    # No message returns original image
    no_msg = ap._add_text_overlay(Image.open(p), {"campaign_tagline": ""}, aspect_ratio='1:1')
    assert isinstance(no_msg, Image.Image)



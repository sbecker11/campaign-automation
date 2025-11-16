from pathlib import Path
import numpy as np
from PIL import Image
import pytest

from src.asset_processor import AssetProcessor


def _rgb_array(w, h, color):
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :] = color
    return arr


def test_logo_needs_background_true(tmp_path):
    ap = AssetProcessor()
    # Base image and logo with similar colors => high similarity -> True
    base = Image.fromarray(_rgb_array(200, 200, (200, 200, 200)))
    logo = Image.fromarray(_rgb_array(40, 20, (205, 205, 205)))
    pos = (150, 10)  # within bounds
    assert ap._logo_needs_background(base, logo, pos)


def test_logo_needs_background_false_out_of_bounds(tmp_path):
    ap = AssetProcessor()
    base = Image.fromarray(_rgb_array(100, 100, (0, 0, 0)))
    logo = Image.fromarray(_rgb_array(200, 200, (255, 255, 255)))  # larger than base
    pos = (90, 90)  # will go out of bounds -> early False
    assert not ap._logo_needs_background(base, logo, pos)


def test_logo_needs_background_error_defaults_true(monkeypatch):
    ap = AssetProcessor()
    base = Image.fromarray(_rgb_array(50, 50, (0, 0, 0)))
    # Force error by passing an object that doesn't have size attribute properly
    class BadImage:
        size = (10, 10)
        def convert(self, *args, **kwargs):
            raise RuntimeError("boom")
    assert ap._logo_needs_background(base, BadImage(), (0, 0)) is True



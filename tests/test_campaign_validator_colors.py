import numpy as np
import cv2
from src.campaign_validator import CampaignValidator


def test_validate_colors_finds_brand_color(tmp_path):
    validator = CampaignValidator()
    # Solid red image (BGR in OpenCV) -> red
    img = np.zeros((60, 60, 3), dtype=np.uint8)
    img[:] = (0, 0, 255)
    path = str(tmp_path / "red.png")
    cv2.imwrite(path, img)
    res = validator._validate_colors(path, ["#FF0000"])
    assert res["colors_present"] is True
    assert res["matches_found"] >= 1


def test_helpers_hex_similarity_dominant():
    validator = CampaignValidator()
    assert validator._hex_to_rgb("#AABBCC") == (170, 187, 204)
    sim = validator._color_similarity((255, 0, 0), (254, 1, 1))
    assert 0.99 <= sim <= 1.0
    pixels = np.array([[0, 0, 0], [0, 0, 0], [255, 0, 0], [255, 0, 0], [255, 0, 0]], dtype=np.uint8)
    dom = validator._extract_dominant_colors(pixels, n_colors=2)
    assert (0, 0, 0) in dom
    # Colors are quantized in _extract_dominant_colors to multiples of 32; 255 -> 224
    # Accept close-to-red dominant color
    assert any(np.linalg.norm(np.array(c) - np.array((255, 0, 0))) <= 32 for c in dom)



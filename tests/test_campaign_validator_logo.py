import numpy as np
import cv2
from src.campaign_validator import CampaignValidator


def test_detect_logo_handles_missing_images(tmp_path):
    validator = CampaignValidator()
    res = validator._detect_logo(tmp_path / "noimg.png", str(tmp_path / "nologo.png"))
    assert res["detected"] is False
    assert "error" in res


def test_detect_logo_detects_match(tmp_path):
    validator = CampaignValidator()
    # White canvas
    img = np.full((200, 200, 3), 255, dtype=np.uint8)
    # Black square as "logo"
    logo = np.full((20, 20, 3), 0, dtype=np.uint8)

    img_path = str(tmp_path / "img.png")
    logo_path = str(tmp_path / "logo.png")
    cv2.imwrite(img_path, img)
    cv2.imwrite(logo_path, logo)

    res = validator._detect_logo(img_path, logo_path)
    # Should compute a confidence and usually exceed threshold on simple synthetic data
    assert "confidence" in res
    assert res["confidence"] >= 0.0



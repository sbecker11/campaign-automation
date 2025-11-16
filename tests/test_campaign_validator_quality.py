import numpy as np
import cv2
from src.campaign_validator import CampaignValidator


def test_assess_quality_missing_file(tmp_path):
    validator = CampaignValidator()
    q = validator._assess_quality(tmp_path / "no.png")
    assert q["quality_score"] == 0.0


def test_assess_quality_low_res(tmp_path):
    validator = CampaignValidator()
    img = np.ones((100, 100, 3), dtype=np.uint8) * 127
    path = str(tmp_path / "small.png")
    cv2.imwrite(path, img)
    q = validator._assess_quality(path)
    assert 0.0 <= q["quality_score"] <= 0.5



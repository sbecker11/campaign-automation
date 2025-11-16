import json
from pathlib import Path
import pytest
from src.campaign_validator import CampaignValidator


def test_validate_logo_required_detected_false(tmp_path, monkeypatch):
    validator = CampaignValidator()
    image_path = tmp_path / "img.png"
    image_path.write_bytes(b"X")  # dummy file; methods will be monkeypatched

    brief = {
        "brand_guidelines": {
            "logo_required": True,
            "logo_path": str(image_path),
            "brand_colors": ["#FF0000"],
        }
    }

    monkeypatch.setattr(
        validator,
        "_detect_logo",
        lambda img, logo: {"detected": False, "confidence": 0.3, "threshold": 0.5},
    )
    monkeypatch.setattr(
        validator, "_validate_colors", lambda img, colors: {"colors_present": True, "matches_found": 1}
    )
    monkeypatch.setattr(validator, "_assess_quality", lambda img: {"quality_score": 0.9})

    result = validator.validate(image_path, brief)
    assert result["overall_compliant"] is False
    assert "logo_detection" in result["checks"]


def test_validate_logo_required_missing_path(tmp_path):
    validator = CampaignValidator()
    image_path = tmp_path / "img.png"
    image_path.write_bytes(b"X")

    brief = {
        "brand_guidelines": {
            "logo_required": True,
            "logo_path": str(tmp_path / "does_not_exist.png"),
        }
    }

    result = validator.validate(image_path, brief)
    # Should still include quality assessment even if logo missing
    assert "image_quality" in result["checks"]


def test_validate_brand_colors_not_present(tmp_path, monkeypatch):
    validator = CampaignValidator()
    image_path = tmp_path / "img.png"
    image_path.write_bytes(b"X")

    brief = {"brand_guidelines": {"brand_colors": ["#00FF00"]}}

    monkeypatch.setattr(
        validator, "_validate_colors", lambda img, colors: {"colors_present": False, "matches_found": 0}
    )
    monkeypatch.setattr(validator, "_assess_quality", lambda img: {"quality_score": 0.9})

    result = validator.validate(image_path, brief)
    assert result["checks"]["color_validation"]["colors_present"] is False



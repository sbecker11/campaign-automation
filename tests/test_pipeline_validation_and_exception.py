from pathlib import Path
from unittest.mock import patch, MagicMock
import shutil
import pytest

from src.pipeline import CampaignPipeline


def _campaign_min(tmp_path):
    return {
        "campaign_id": "cid2",
        "campaign_name": "C2",
        "brand_guidelines": {"logo_required": False, "brand_colors": ["#FF0000"]},
        "aspect_ratios": ["1:1"],
        "products": [{"product_id": "p1", "name": "Product 1", "generate_new": True}],
        "target_audience": "t",
    }


@patch("src.pipeline.ReportGenerator")
@patch("src.pipeline.ContentChecker")
@patch("src.pipeline.CampaignValidator")
@patch("src.pipeline.AssetProcessor")
@patch("src.pipeline.ImageGenerator")
@patch("src.pipeline.CampaignParser")
def test_process_product_emits_validation_warnings(mock_parser, mock_img, mock_asset, mock_validator, mock_checker, mock_report, tmp_path, caplog):
    assets_dir = tmp_path / "assets"; assets_dir.mkdir()
    # mock image generator to return a base image path
    base_img = tmp_path / "base.png"; base_img.write_bytes(b"\x89PNG\r\n\x1a\n")
    mock_img.return_value.generate_image.return_value = base_img
    # mock asset processor to return variant path (copy base)
    variant = tmp_path / "variant.png"; variant.write_bytes(b"\x89PNG\r\n\x1a\n")
    mock_asset.return_value.create_variant.return_value = variant
    # validator returns non-compliant with detailed checks
    mock_validator.return_value.validate.return_value = {
        "overall_compliant": False,
        "checks": {
            "logo_detection": {"detected": False, "confidence": 0.1, "threshold": 0.5},
            "color_validation": {"colors_present": False, "matches_found": 0},
            "image_quality": {"quality_score": 0.3},
        },
    }
    mock_checker.return_value.check.return_value = {"passed": True}
    campaign = _campaign_min(tmp_path)
    mock_parser.return_value.parse.return_value = campaign

    pipe = CampaignPipeline(assets_dir=assets_dir)
    res = pipe._process_product(campaign["products"][0], campaign, tmp_path / "outdir")
    assert res["status"] == "success"
    # Check that warnings were emitted
    messages = " ".join([r.message for r in caplog.records])
    assert "logo not detected" in messages
    assert "brand colors not detected" in messages
    assert "low image quality score" in messages


@patch("src.pipeline.ReportGenerator")
@patch("src.pipeline.ContentChecker")
@patch("src.pipeline.CampaignValidator")
@patch("src.pipeline.AssetProcessor")
@patch("src.pipeline.ImageGenerator")
@patch("src.pipeline.CampaignParser")
def test_process_product_exception_path(mock_parser, mock_img, mock_asset, mock_validator, mock_checker, mock_report, tmp_path):
    assets_dir = tmp_path / "assets"; assets_dir.mkdir()
    # Raise in image generator
    mock_img.return_value.generate_image.side_effect = RuntimeError("boom")
    mock_checker.return_value.check.return_value = {"passed": True}
    campaign = _campaign_min(tmp_path)
    mock_parser.return_value.parse.return_value = campaign
    pipe = CampaignPipeline(assets_dir=assets_dir)
    result = pipe._process_product(campaign["products"][0], campaign, tmp_path / "out")
    assert result["status"] == "error"
    assert "boom" in result["error"]



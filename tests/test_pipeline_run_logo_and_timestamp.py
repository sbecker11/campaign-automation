from pathlib import Path
from unittest.mock import patch, MagicMock
import re
import pytest

from src.pipeline import CampaignPipeline


def _minimal_campaign(tmp_path, logo_required=False):
    return {
        "campaign_id": "summer_2024",
        "campaign_name": "Summer",
        "brand_guidelines": {
            "logo_required": logo_required,
        },
        "aspect_ratios": ["1:1"],
        "products": [
            {"product_id": "p1", "name": "Product 1", "generate_new": False, "existing_assets": str(tmp_path)}
        ],
        "target_audience": "testers",
    }


@patch("src.pipeline.ReportGenerator")
@patch("src.pipeline.ContentChecker")
@patch("src.pipeline.CampaignValidator")
@patch("src.pipeline.AssetProcessor")
@patch("src.pipeline.ImageGenerator")
@patch("src.pipeline.CampaignParser")
def test_run_injects_logo_path_when_required(mock_parser, mock_img, mock_asset, mock_validator, mock_checker, mock_report, tmp_path):
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    # Provide a dummy image file so existing-assets path works
    img_file = tmp_path / "existing.png"
    img_file.write_bytes(b"\x89PNG\r\n\x1a\n")

    campaign = _minimal_campaign(tmp_path, logo_required=True)
    mock_parser.return_value.parse.return_value = campaign

    # validator returns pass
    mock_validator.return_value.validate.return_value = {"overall_compliant": True, "checks": {}}
    mock_checker.return_value.check.return_value = {"passed": True}
    # asset processor just returns the existing path unchanged
    mock_asset.return_value.create_variant.return_value = img_file

    pipe = CampaignPipeline(assets_dir=assets_dir)
    out_base = tmp_path / "out"
    pipe.run(campaign_path=Path("dummy.yaml"), output_base_dir=out_base, use_timestamp=False)

    # After run, logo_required campaign should have a logo_path injected if it was missing
    assert "logo_path" in campaign["brand_guidelines"]
    assert Path(campaign["brand_guidelines"]["logo_path"]).exists()


@patch("src.pipeline.ReportGenerator")
@patch("src.pipeline.ContentChecker")
@patch("src.pipeline.CampaignValidator")
@patch("src.pipeline.AssetProcessor")
@patch("src.pipeline.ImageGenerator")
@patch("src.pipeline.CampaignParser")
def test_run_uses_timestamped_output_dir(mock_parser, mock_img, mock_asset, mock_validator, mock_checker, mock_report, tmp_path):
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    img_file = tmp_path / "existing.png"
    img_file.write_bytes(b"\x89PNG\r\n\x1a\n")

    campaign = _minimal_campaign(tmp_path, logo_required=False)
    mock_parser.return_value.parse.return_value = campaign
    mock_validator.return_value.validate.return_value = {"overall_compliant": True, "checks": {}}
    mock_checker.return_value.check.return_value = {"passed": True}
    mock_asset.return_value.create_variant.return_value = img_file

    pipe = CampaignPipeline(assets_dir=assets_dir)
    out_base = tmp_path / "out"
    pipe.run(campaign_path=Path("dummy.yaml"), output_base_dir=out_base, use_timestamp=True)

    # The output directory should contain a folder beginning with campaign_id_
    subdirs = [p for p in (out_base).iterdir() if p.is_dir()]
    assert any(p.name.startswith("summer_2024_") for p in subdirs)



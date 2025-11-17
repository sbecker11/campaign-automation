from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from src.pipeline import CampaignPipeline


def _campaign_with_existing(existing_dir: Path | None):
    return {
        "campaign_id": "cid",
        "campaign_name": "C",
        "brand_guidelines": {},
        "aspect_ratios": ["1:1"],
        "products": [
            {
                "product_id": "p1",
                "name": "Product 1",
                "generate_new": False,
                **({"existing_assets": str(existing_dir)} if existing_dir is not None else {}),
            }
        ],
        "target_audience": "t",
    }


@patch("src.pipeline.InstanceGenerator")
@patch("src.pipeline.ContentChecker")
@patch("src.pipeline.CampaignValidator")
@patch("src.pipeline.AssetProcessor")
@patch("src.pipeline.ImageGenerator")
@patch("src.pipeline.CampaignParser")
def test_existing_assets_found(mock_parser, mock_img, mock_asset, mock_validator, mock_checker, mock_report, tmp_path):
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    img = tmp_path / "dir"
    img.mkdir()
    sample = img / "a.png"
    sample.write_bytes(b"\x89PNG\r\n\x1a\n")

    campaign = _campaign_with_existing(img)
    mock_parser.return_value.parse.return_value = campaign
    mock_checker.return_value.check.return_value = {"passed": True}
    mock_validator.return_value.validate.return_value = {"overall_compliant": True, "checks": {}}
    # asset processor should create the product output dir and return a variant path
    def _create_variant(base_image_path, product, brief, aspect_ratio, product_output_dir):
        product_output_dir.mkdir(parents=True, exist_ok=True)
        variant_path = product_output_dir / f"{product['product_id']}_{aspect_ratio.replace(':','x')}.png"
        variant_path.write_bytes(b"\x89PNG\r\n\x1a\n")
        return variant_path
    mock_asset.return_value.create_variant.side_effect = _create_variant

    pipe = CampaignPipeline(assets_dir=assets_dir)
    out_base = tmp_path / "out"
    pipe.run(Path("dummy.yaml"), output_base_dir=out_base)

    # Success path: a products folder should be created
    prod_dir = out_base / campaign["campaign_id"] / "products" / "p1"
    assert prod_dir.exists()


@patch("src.pipeline.InstanceGenerator")
@patch("src.pipeline.ContentChecker")
@patch("src.pipeline.CampaignValidator")
@patch("src.pipeline.AssetProcessor")
@patch("src.pipeline.ImageGenerator")
@patch("src.pipeline.CampaignParser")
def test_existing_assets_empty_dir_returns_error(mock_parser, mock_img, mock_asset, mock_validator, mock_checker, mock_report, tmp_path):
    assets_dir = tmp_path / "assets"; assets_dir.mkdir()
    empty = tmp_path / "empty"; empty.mkdir()
    campaign = _campaign_with_existing(empty)
    mock_parser.return_value.parse.return_value = campaign
    mock_checker.return_value.check.return_value = {"passed": True}

    pipe = CampaignPipeline(assets_dir=assets_dir)
    result = pipe._process_product(campaign["products"][0], campaign, tmp_path / "out")
    assert result["status"] == "error"
    assert "No images found" in result["error"]


@patch("src.pipeline.InstanceGenerator")
@patch("src.pipeline.ContentChecker")
@patch("src.pipeline.CampaignValidator")
@patch("src.pipeline.AssetProcessor")
@patch("src.pipeline.ImageGenerator")
@patch("src.pipeline.CampaignParser")
def test_existing_assets_not_specified_returns_error(mock_parser, mock_img, mock_asset, mock_validator, mock_checker, mock_report, tmp_path):
    assets_dir = tmp_path / "assets"; assets_dir.mkdir()
    campaign = _campaign_with_existing(None)
    mock_parser.return_value.parse.return_value = campaign
    mock_checker.return_value.check.return_value = {"passed": True}

    pipe = CampaignPipeline(assets_dir=assets_dir)
    result = pipe._process_product(campaign["products"][0], campaign, tmp_path / "out")
    assert result["status"] == "error"
    assert "No existing assets specified" in result["error"]



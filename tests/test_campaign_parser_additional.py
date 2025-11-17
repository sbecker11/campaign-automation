import json
from pathlib import Path
import yaml
import pytest

from src.campaign_parser import CampaignParser


def test_parse_file_not_found(tmp_path):
    parser = CampaignParser()
    missing = tmp_path / "no_such_file.yaml"
    with pytest.raises(FileNotFoundError):
        parser.parse(str(missing))


def test_parse_json_success_defaults(tmp_path):
    parser = CampaignParser()
    data = {
        "campaign_id": "cid-json",
        "products": [{"product_id": "p1", "name": "Product"}],
        "target_market": "US",
        "campaign_tagline": "Hello",
        # Provide partial brand_guidelines to test nested defaults filling
        "brand_guidelines": {"brand_colors": []},
    }
    p = tmp_path / "camp.json"
    p.write_text(json.dumps(data))
    campaign = parser.parse(str(p))
    assert campaign["campaign_id"] == "cid-json"
    # Defaults applied at top level
    assert "aspect_ratios" in campaign
    # Nested defaults merged
    assert "logo_required" in campaign["brand_guidelines"]
    assert campaign["brand_guidelines"]["logo_required"] is False


def test_parse_unsupported_extension(tmp_path):
    parser = CampaignParser()
    bad = tmp_path / "camp.txt"
    bad.write_text("x")
    with pytest.raises(ValueError, match="Unsupported file format"):
        parser.parse(str(bad))


def test_validate_products_empty(tmp_path):
    parser = CampaignParser()
    data = {
        "campaign_id": "cid",
        "products": [],
        "target_market": "US",
        "campaign_tagline": "Hi",
    }
    p = tmp_path / "empty.yaml"
    p.write_text(yaml.dump(data))
    with pytest.raises(ValueError, match="at least one product"):
        parser.parse(str(p))


def test_validate_product_missing_id(tmp_path):
    parser = CampaignParser()
    data = {
        "campaign_id": "cid",
        "products": [{"name": "Product"}],
        "target_market": "US",
        "campaign_tagline": "Hi",
    }
    p = tmp_path / "missing_id.yaml"
    p.write_text(yaml.dump(data))
    with pytest.raises(ValueError, match="missing 'product_id'"):
        parser.parse(str(p))


def test_validate_product_missing_name(tmp_path):
    parser = CampaignParser()
    data = {
        "campaign_id": "cid",
        "products": [{"product_id": "p1"}],
        "target_market": "US",
        "campaign_tagline": "Hi",
    }
    p = tmp_path / "missing_name.yaml"
    p.write_text(yaml.dump(data))
    with pytest.raises(ValueError, match="missing 'name'"):
        parser.parse(str(p))



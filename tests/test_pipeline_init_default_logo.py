from pathlib import Path
from unittest.mock import patch, MagicMock
import shutil
import pytest

from src.pipeline import CampaignPipeline


def test_pipeline_init_creates_default_logo(tmp_path):
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    logo_path = assets_dir / "generated_logo.png"
    assert not logo_path.exists()

    # Patch components that create heavy dependencies
    with patch("src.pipeline.CampaignParser"), \
         patch("src.pipeline.ImageGenerator"), \
         patch("src.pipeline.AssetProcessor"), \
         patch("src.pipeline.CampaignValidator"), \
         patch("src.pipeline.ContentChecker"), \
         patch("src.pipeline.ReportGenerator"):
        pipe = CampaignPipeline(assets_dir=assets_dir)
        # Default logo should be created during __init__
        assert logo_path.exists()



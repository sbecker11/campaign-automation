"""
Comprehensive tests for Campaign Pipeline.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.pipeline import CampaignPipeline
from PIL import Image


@pytest.fixture
def mock_components():
    """Mock all pipeline components."""
    with patch('src.pipeline.CampaignParser') as mock_parser, \
         patch('src.pipeline.ImageGenerator') as mock_img_gen, \
         patch('src.pipeline.AssetProcessor') as mock_processor, \
         patch('src.pipeline.BrandValidator') as mock_validator, \
         patch('src.pipeline.ContentChecker') as mock_checker, \
         patch('src.pipeline.ReportGenerator') as mock_reporter:
        
        # Setup CampaignParser mock
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        
        # Setup ImageGenerator mock
        mock_img_gen_instance = MagicMock()
        mock_img_gen.return_value = mock_img_gen_instance
        
        # Setup AssetProcessor mock
        mock_processor_instance = MagicMock()
        mock_processor.return_value = mock_processor_instance
        
        # Setup BrandValidator mock
        mock_validator_instance = MagicMock()
        mock_validator.return_value = mock_validator_instance
        
        # Setup ContentChecker mock
        mock_checker_instance = MagicMock()
        mock_checker_instance.check.return_value = {
            'passed': True,
            'issues': []
        }
        mock_checker.return_value = mock_checker_instance
        
        # Setup ReportGenerator mock
        mock_reporter_instance = MagicMock()
        mock_reporter.return_value = mock_reporter_instance
        
        yield {
            'parser': mock_parser_instance,
            'img_gen': mock_img_gen_instance,
            'processor': mock_processor_instance,
            'validator': mock_validator_instance,
            'checker': mock_checker_instance,
            'reporter': mock_reporter_instance
        }


def test_pipeline_run_completes(mock_components, sample_brief_dict, temp_dir):
    """Test that pipeline runs to completion."""
    brand_dir = temp_dir / "brand"
    brand_dir.mkdir(exist_ok=True)
    
    # Create brief file
    import yaml
    brief_path = temp_dir / "test_brief.yaml"
    with open(brief_path, 'w') as f:
        yaml.dump(sample_brief_dict, f)
    
    # Setup mocks
    mock_components['parser'].parse.return_value = sample_brief_dict
    
    # Mock image generation
    test_img_path = temp_dir / "generated.png"
    test_img = Image.new('RGB', (100, 100), 'red')
    test_img.save(test_img_path)
    
    mock_components['img_gen'].generate.return_value = str(test_img_path)
    mock_components['processor'].create_variant.return_value = temp_dir / "variant.png"
    mock_components['validator'].validate.return_value = {'overall_compliant': True}
    
    # Create pipeline and run
    pipeline = CampaignPipeline(brand_dir)
    output_dir = temp_dir / "output"
    
    result = pipeline.run(brief_path, output_dir)
    
    # Verify key components were called
    mock_components['parser'].parse.assert_called()
    mock_components['checker'].check.assert_called()  # Can be called multiple times


def test_pipeline_with_existing_assets(mock_components, temp_dir):
    """Test running pipeline with existing assets (no generation)."""
    brand_dir = temp_dir / "brand"
    brand_dir.mkdir(exist_ok=True)
    
    # Create brief with existing assets
    assets_dir = temp_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Create a test image
    test_img = Image.new('RGB', (100, 100), 'blue')
    test_img.save(assets_dir / "existing.png")
    
    brief = {
        'campaign_id': 'test_001',
        'campaign_name': 'Test Campaign',
        'campaign_message': 'Test message',
        'products': [
            {
                'product_id': 'prod1',
                'name': 'Product 1',
                'description': 'Test product',
                'existing_assets': str(assets_dir),
                'generate_new': False
            }
        ],
        'target_market': 'US',
        'aspect_ratios': ['1:1'],
        'brand_guidelines': {}
    }
    
    import yaml
    brief_path = temp_dir / "brief.yaml"
    with open(brief_path, 'w') as f:
        yaml.dump(brief, f)
    
    # Setup mocks
    mock_components['parser'].parse.return_value = brief
    mock_components['processor'].create_variant.return_value = temp_dir / "variant.png"
    mock_components['validator'].validate.return_value = {'overall_compliant': True}
    
    # Run pipeline
    pipeline = CampaignPipeline(brand_dir)
    output_dir = temp_dir / "output"
    
    result = pipeline.run(brief_path, output_dir)
    
    # Pipeline should complete
    assert result is None  # run() doesn't return a value


def test_pipeline_content_check(mock_components, sample_brief_dict, temp_dir):
    """Test that pipeline runs content check."""
    brand_dir = temp_dir / "brand"
    brand_dir.mkdir(exist_ok=True)
    
    import yaml
    brief_path = temp_dir / "brief.yaml"
    with open(brief_path, 'w') as f:
        yaml.dump(sample_brief_dict, f)
    
    # Setup mocks
    mock_components['parser'].parse.return_value = sample_brief_dict
    mock_components['checker'].check.return_value = {
        'passed': False,
        'issues': ['Prohibited word found'],
        'issues_count': 1
    }
    
    # Run pipeline
    pipeline = CampaignPipeline(brand_dir)
    output_dir = temp_dir / "output"
    
    result = pipeline.run(brief_path, output_dir)
    
    # Verify content check was called
    assert mock_components['checker'].check.called


def test_pipeline_multiple_products(mock_components, temp_dir):
    """Test pipeline with multiple products."""
    brand_dir = temp_dir / "brand"
    brand_dir.mkdir(exist_ok=True)
    
    # Brief with multiple products
    brief = {
        'campaign_id': 'multi_001',
        'campaign_name': 'Multi Product Campaign',
        'campaign_message': 'Multiple products',
        'products': [
            {
                'product_id': 'prod1',
                'name': 'Product 1',
                'description': 'First product',
                'generate_new': True
            },
            {
                'product_id': 'prod2',
                'name': 'Product 2',
                'description': 'Second product',
                'generate_new': True
            }
        ],
        'target_market': 'US',
        'aspect_ratios': ['1:1', '9:16'],
        'brand_guidelines': {}
    }
    
    import yaml
    brief_path = temp_dir / "brief.yaml"
    with open(brief_path, 'w') as f:
        yaml.dump(brief, f)
    
    # Setup mocks
    mock_components['parser'].parse.return_value = brief
    
    test_img_path = temp_dir / "gen.png"
    Image.new('RGB', (100, 100)).save(test_img_path)
    mock_components['img_gen'].generate.return_value = str(test_img_path)
    mock_components['processor'].create_variant.return_value = temp_dir / "var.png"
    mock_components['validator'].validate.return_value = {'overall_compliant': True}
    
    # Run pipeline
    pipeline = CampaignPipeline(brand_dir)
    output_dir = temp_dir / "output"
    
    result = pipeline.run(brief_path, output_dir)
    
    # Pipeline should complete
    assert result is None


def test_pipeline_multiple_aspect_ratios(mock_components, temp_dir):
    """Test pipeline creates variants for multiple aspect ratios."""
    brand_dir = temp_dir / "brand"
    brand_dir.mkdir(exist_ok=True)
    
    brief = {
        'campaign_id': 'ratio_test',
        'campaign_name': 'Ratio Test',
        'campaign_message': 'Test',
        'products': [
            {
                'product_id': 'prod1',
                'name': 'Product',
                'description': 'Test',
                'generate_new': True
            }
        ],
        'target_market': 'US',
        'aspect_ratios': ['1:1', '9:16', '16:9'],
        'brand_guidelines': {}
    }
    
    import yaml
    brief_path = temp_dir / "brief.yaml"
    with open(brief_path, 'w') as f:
        yaml.dump(brief, f)
    
    mock_components['parser'].parse.return_value = brief
    
    test_img_path = temp_dir / "gen.png"
    Image.new('RGB', (100, 100)).save(test_img_path)
    mock_components['img_gen'].generate.return_value = str(test_img_path)
    mock_components['processor'].create_variant.return_value = temp_dir / "var.png"
    mock_components['validator'].validate.return_value = {'overall_compliant': True}
    
    pipeline = CampaignPipeline(brand_dir)
    output_dir = temp_dir / "output"
    
    result = pipeline.run(brief_path, output_dir)
    
    # Should create variant for each aspect ratio
    assert mock_components['processor'].create_variant.call_count >= 3


def test_pipeline_generates_reports(mock_components, sample_brief_dict, temp_dir):
    """Test that pipeline generates reports at the end."""
    brand_dir = temp_dir / "brand"
    brand_dir.mkdir(exist_ok=True)
    
    import yaml
    brief_path = temp_dir / "brief.yaml"
    with open(brief_path, 'w') as f:
        yaml.dump(sample_brief_dict, f)
    
    mock_components['parser'].parse.return_value = sample_brief_dict
    
    test_img_path = temp_dir / "gen.png"
    Image.new('RGB', (100, 100)).save(test_img_path)
    mock_components['img_gen'].generate.return_value = str(test_img_path)
    mock_components['processor'].create_variant.return_value = temp_dir / "var.png"
    mock_components['validator'].validate.return_value = {'overall_compliant': True}
    
    pipeline = CampaignPipeline(brand_dir)
    output_dir = temp_dir / "output"
    
    result = pipeline.run(brief_path, output_dir)
    
    # Should generate reports
    mock_components['reporter'].generate_reports.assert_called()

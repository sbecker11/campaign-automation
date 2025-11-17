"""
Comprehensive tests for Instance Generator.
"""

import pytest
import json
from pathlib import Path
from src.instance_generator import InstanceGenerator


@pytest.fixture
def generator():
    """Create an InstanceGenerator instance."""
    return InstanceGenerator()


@pytest.fixture
def successful_results():
    """Sample successful processing results."""
    return [
        {
            'product_id': 'sunscreen_001',
            'product_name': 'Sunscreen SPF 50',
            'status': 'success',
            'base_image': '/path/to/sunscreen.png',
            'variants': [
                '/path/to/sunscreen_1x1.png',
                '/path/to/sunscreen_9x16.png'
            ],
            'validations': [
                {
                    'variant': '/path/to/sunscreen_1x1.png',
                    'ratio': '1:1',
                    'campaign_validation': {
                        'overall_compliant': True,
                        'checks': {}
                    },
                    'content_check': {
                        'passed': True
                    }
                },
                {
                    'variant': '/path/to/sunscreen_9x16.png',
                    'ratio': '9:16',
                    'campaign_validation': {
                        'overall_compliant': True,
                        'checks': {}
                    },
                    'content_check': {
                        'passed': True
                    }
                }
            ]
        }
    ]


def test_generate_reports_creates_status_json(generator, successful_results, sample_brief_dict, temp_dir):
    """Test that consolidated campaign_instance.json is created."""
    generator.generate_reports(successful_results, sample_brief_dict, temp_dir)
    
    status_file = temp_dir / 'campaign_instance.json'
    
    assert status_file.exists()


def test_status_json_structure(generator, successful_results, sample_brief_dict, temp_dir):
    """Test campaign_instance.json has correct structure with per-image records."""
    generator.generate_reports(successful_results, sample_brief_dict, temp_dir)
    
    status_path = temp_dir / 'campaign_instance.json'
    status = json.loads(status_path.read_text())
    
    assert 'campaign_id' in status
    assert 'summary' in status
    assert 'products' in status
    assert status['summary']['total_products'] == len(successful_results)
    # Check that products have image_variants array with per-image records
    assert len(status['products']) > 0
    product = status['products'][0]
    assert 'image_variants' in product
    assert len(product['image_variants']) > 0
    # Check that each image has all required fields
    image = product['image_variants'][0]
    assert 'path' in image
    assert 'ratio' in image
    assert 'campaign_validation' in image
    assert 'content_check' in image


def test_status_json_compliance_calculations(generator, successful_results, sample_brief_dict, temp_dir):
    """Test compliance rate calculations in campaign_instance.json."""
    generator.generate_reports(successful_results, sample_brief_dict, temp_dir)
    
    status_path = temp_dir / 'campaign_instance.json'
    status = json.loads(status_path.read_text())
    
    summary = status['summary']
    assert summary['total_variants_checked'] == 2
    assert summary['passed'] == 2
    assert summary['compliance_rate'] == '100.0%'


def test_create_generation_report_directly(generator, successful_results, sample_brief_dict):
    """Test _create_generation_report helper method."""
    report = generator._create_generation_report(successful_results, sample_brief_dict)
    
    assert isinstance(report, dict)
    assert 'summary' in report


def test_create_compliance_report_directly(generator, successful_results, sample_brief_dict):
    """Test _create_compliance_report helper method."""
    report = generator._create_compliance_report(successful_results, sample_brief_dict)
    
    assert isinstance(report, dict)
    assert 'summary' in report

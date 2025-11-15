"""
Comprehensive tests for Report Generator.
"""

import pytest
import json
from pathlib import Path
from src.report_generator import ReportGenerator


@pytest.fixture
def generator():
    """Create a ReportGenerator instance."""
    return ReportGenerator()


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
                    'brand_validation': {
                        'overall_compliant': True,
                        'checks': {}
                    }
                },
                {
                    'variant': '/path/to/sunscreen_9x16.png',
                    'ratio': '9:16',
                    'brand_validation': {
                        'overall_compliant': True,
                        'checks': {}
                    }
                }
            ]
        }
    ]


def test_generate_reports_creates_both_files(generator, successful_results, sample_brief_dict, temp_dir):
    """Test that both report files are created."""
    generator.generate_reports(successful_results, sample_brief_dict, temp_dir)
    
    generation_report = temp_dir / 'generation_report.json'
    compliance_report = temp_dir / 'compliance_report.json'
    
    assert generation_report.exists()
    assert compliance_report.exists()


def test_generation_report_structure(generator, successful_results, sample_brief_dict, temp_dir):
    """Test generation report has correct structure."""
    generator.generate_reports(successful_results, sample_brief_dict, temp_dir)
    
    report_path = temp_dir / 'generation_report.json'
    report = json.loads(report_path.read_text())
    
    assert 'campaign_id' in report
    assert 'summary' in report
    assert report['summary']['total_products'] == len(successful_results)


def test_compliance_report_calculations(generator, successful_results, sample_brief_dict, temp_dir):
    """Test compliance rate calculations."""
    generator.generate_reports(successful_results, sample_brief_dict, temp_dir)
    
    report_path = temp_dir / 'compliance_report.json'
    report = json.loads(report_path.read_text())
    
    summary = report['summary']
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

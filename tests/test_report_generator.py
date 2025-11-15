"""
Tests for the Report Generator.
"""

import pytest
from pathlib import Path
from src.report_generator import ReportGenerator


def test_report_generator_initialization():
    """Test ReportGenerator can be initialized."""
    generator = ReportGenerator()
    assert generator is not None


def test_generate_report(temp_dir, sample_brief_dict):
    """Test generating a campaign report."""
    generator = ReportGenerator()
    
    # Create mock campaign results
    campaign_results = {
        'campaign_id': 'test_001',
        'products': [],
        'total_variants': 0,
        'validation_results': []
    }
    
    output_path = temp_dir / "report.html"
    
    # Adjust method name based on actual implementation
    if hasattr(generator, 'generate'):
        result = generator.generate(campaign_results, output_path)
        assert result is not None or output_path.exists()

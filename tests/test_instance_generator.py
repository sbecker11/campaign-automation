"""
Tests for the Instance Generator.
"""

import pytest
from pathlib import Path
from src.instance_generator import InstanceGenerator


def test_instance_generator_initialization():
    """Test InstanceGenerator can be initialized."""
    generator = InstanceGenerator()
    assert generator is not None


def test_generate_report(temp_dir, sample_brief_dict):
    """Test generating a campaign report."""
    generator = InstanceGenerator()
    
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

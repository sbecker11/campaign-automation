"""
Tests for the GenAI Image Generator.
"""

import pytest
from unittest.mock import patch
from src.image_generator import ImageGenerator


def test_image_generator_initialization():
    """Test ImageGenerator initialization."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        generator = ImageGenerator()
        assert generator is not None


def test_generate_without_api_key():
    """Test that generator fails gracefully without API key."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises((ValueError, EnvironmentError, KeyError)):
            generator = ImageGenerator()
            generator.generate("test", "test")

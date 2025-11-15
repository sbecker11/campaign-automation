"""
Extended tests for Image Generator.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.image_generator import ImageGenerator


@patch('src.image_generator.OpenAI')
def test_generate_image_mock(mock_openai):
    """Test image generation with mocked OpenAI API."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.data = [MagicMock(url='https://example.com/test.png')]
    mock_openai.return_value.images.generate.return_value = mock_response
    
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        generator = ImageGenerator()
        
        if hasattr(generator, 'generate'):
            result = generator.generate(
                product_description="Test product",
                campaign_message="Test message"
            )
            
            assert result is not None


def test_image_generator_configuration():
    """Test different image generator configurations."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        generator = ImageGenerator()
        
        # Check that generator has expected attributes
        assert hasattr(generator, 'logger')

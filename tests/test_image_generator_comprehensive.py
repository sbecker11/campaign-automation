"""
Comprehensive tests for Image Generator.
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.image_generator import ImageGenerator


def test_image_generator_requires_api_key():
    """Test that ImageGenerator requires API key."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
            generator = ImageGenerator()


def test_image_generator_with_api_key():
    """Test ImageGenerator initialization with API key."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test-key-12345'}):
        generator = ImageGenerator()
        assert generator is not None
        assert hasattr(generator, 'client')
        assert hasattr(generator, 'temp_dir')


@patch('src.image_generator.requests.get')
@patch('src.image_generator.OpenAI')
def test_generate_image_success(mock_openai, mock_requests, temp_dir):
    """Test successful image generation."""
    # Setup OpenAI mock
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [MagicMock(url='https://example.com/image.png')]
    mock_client.images.generate.return_value = mock_response
    mock_openai.return_value = mock_client
    
    # Setup requests mock
    mock_img_response = MagicMock()
    mock_img_response.content = b'fake_image_data'
    mock_requests.return_value = mock_img_response
    
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test'}):
        generator = ImageGenerator()
        generator.temp_dir = temp_dir  # Use test temp dir
        
        product = {
            'product_id': 'test_001',
            'name': 'Test Sunscreen',
            'description': 'SPF 50 sunscreen'
        }
        
        brief = {
            'target_audience': 'outdoor enthusiasts',
            'campaign_tagline': 'Stay protected',
            'brand_guidelines': {
                'brand_colors': ['#FF6B35']
            }
        }
        
        result = generator.generate_image(product, brief)
        
        assert result is not None
        assert isinstance(result, Path)
        assert result.name == 'test_001_generated.png'


@patch('src.image_generator.OpenAI')
def test_build_prompt_includes_product_info(mock_openai):
    """Test that _build_prompt includes product information."""
    mock_openai.return_value = MagicMock()
    
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test'}):
        generator = ImageGenerator()
        
        product = {
            'product_id': 'prod1',
            'name': 'Premium Sunscreen',
            'description': 'Waterproof SPF 50+'
        }
        
        brief = {
            'target_audience': 'beach goers',
            'campaign_tagline': 'Ultimate protection',
            'brand_guidelines': {
                'brand_colors': ['#FF6B35', '#004E89']
            }
        }
        
        prompt = generator._build_prompt(product, brief)
        
        assert 'Premium Sunscreen' in prompt
        assert 'Waterproof SPF 50+' in prompt
        assert 'beach goers' in prompt


@patch('src.image_generator.OpenAI')
def test_build_prompt_includes_brand_colors(mock_openai):
    """Test that prompt includes brand colors."""
    mock_openai.return_value = MagicMock()
    
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test'}):
        generator = ImageGenerator()
        
        product = {'product_id': 'p1', 'name': 'Product'}
        brief = {
            'brand_guidelines': {
                'brand_colors': ['#FF6B35', '#004E89', '#FFFFFF']
            }
        }
        
        prompt = generator._build_prompt(product, brief)
        
        assert '#FF6B35' in prompt
        assert '#004E89' in prompt


@patch('src.image_generator.OpenAI')
def test_build_prompt_includes_campaign_tagline(mock_openai):
    """Test that prompt includes campaign tagline."""
    mock_openai.return_value = MagicMock()
    
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test'}):
        generator = ImageGenerator()
        
        product = {'product_id': 'p1', 'name': 'Product'}
        brief = {
            'campaign_tagline': 'Summer adventure awaits'
        }
        
        prompt = generator._build_prompt(product, brief)
        
        assert 'Summer adventure awaits' in prompt


@patch('src.image_generator.requests.get')
@patch('src.image_generator.OpenAI')
def test_generate_image_handles_api_error(mock_openai, mock_requests):
    """Test handling of API errors."""
    mock_client = MagicMock()
    mock_client.images.generate.side_effect = Exception("API Error")
    mock_openai.return_value = mock_client
    
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test'}):
        generator = ImageGenerator()
        
        product = {'product_id': 'p1', 'name': 'Product'}
        brief = {}
        
        with pytest.raises(Exception):
            generator.generate_image(product, brief)


@patch('src.image_generator.requests.get')
@patch('src.image_generator.OpenAI')
def test_generate_image_calls_dalle3(mock_openai, mock_requests, temp_dir):
    """Test that generate_image calls DALL-E 3 API."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [MagicMock(url='https://example.com/img.png')]
    mock_client.images.generate.return_value = mock_response
    mock_openai.return_value = mock_client
    
    mock_img_response = MagicMock()
    mock_img_response.content = b'image_data'
    mock_requests.return_value = mock_img_response
    
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test'}):
        generator = ImageGenerator()
        generator.temp_dir = temp_dir
        
        product = {'product_id': 'test', 'name': 'Product'}
        brief = {}
        
        result = generator.generate_image(product, brief)
        
        # Verify DALL-E 3 was called
        mock_client.images.generate.assert_called_once()
        call_args = mock_client.images.generate.call_args
        
        assert call_args[1]['model'] == 'dall-e-3'
        assert call_args[1]['n'] == 1
        assert call_args[1]['size'] == '1024x1024'


@patch('src.image_generator.requests.get')
@patch('src.image_generator.OpenAI')
def test_generate_image_downloads_and_saves(mock_openai, mock_requests, temp_dir):
    """Test that image is downloaded and saved."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [MagicMock(url='https://example.com/test.png')]
    mock_client.images.generate.return_value = mock_response
    mock_openai.return_value = mock_client
    
    fake_image_data = b'PNG_IMAGE_DATA_HERE'
    mock_img_response = MagicMock()
    mock_img_response.content = fake_image_data
    mock_requests.return_value = mock_img_response
    
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test'}):
        generator = ImageGenerator()
        generator.temp_dir = temp_dir
        
        product = {'product_id': 'download_test', 'name': 'Test'}
        brief = {}
        
        result = generator.generate_image(product, brief)
        
        # Check file was created
        assert result.exists()
        assert result.read_bytes() == fake_image_data
        
        # Check requests.get was called with image URL
        mock_requests.assert_called_once_with('https://example.com/test.png')

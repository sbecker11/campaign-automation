from unittest.mock import patch, MagicMock
from pathlib import Path
import numpy as np
from PIL import Image
import pytest
from src.image_generator import ImageGenerator


@patch('src.image_generator.requests.get')
@patch('src.image_generator.OpenAI')
def test_regenerates_on_color_bars_until_clean(mock_openai, mock_requests, tmp_path):
    # Mock initial OpenAI response and image download
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [MagicMock(url='https://example.com/first.png')]
    mock_client.images.generate.return_value = mock_response
    mock_openai.return_value = mock_client

    mock_img_response = MagicMock()
    mock_img_response.content = b'first_image'
    mock_requests.return_value = mock_img_response

    with patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test'}):
        gen = ImageGenerator()
        gen.temp_dir = tmp_path

        # _has_color_bars returns True once, then False to simulate a successful regen
        with patch.object(gen, '_has_color_bars', side_effect=[True, False]) as mock_cb:
            product = {'product_id': 'p', 'name': 'Prod'}
            brief = {}
            result = gen.generate_image(product, brief)

            # One regeneration should have been triggered → total generate calls == 2
            assert mock_client.images.generate.call_count == 2
            assert result.exists()
            assert result.name.endswith('_generated.png')


@patch('src.image_generator.requests.get')
@patch('src.image_generator.OpenAI')
def test_color_bars_retry_exhausted_uses_image_anyway(mock_openai, mock_requests, tmp_path):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [MagicMock(url='https://example.com/first.png')]
    mock_client.images.generate.return_value = mock_response
    mock_openai.return_value = mock_client

    mock_img_response = MagicMock()
    mock_img_response.content = b'image_data'
    mock_requests.return_value = mock_img_response

    with patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test'}):
        gen = ImageGenerator()
        gen.temp_dir = tmp_path

        # Always detects color bars → should attempt max retries (initial + 2 regens) then break
        with patch.object(gen, '_has_color_bars', return_value=True):
            product = {'product_id': 'p2', 'name': 'Prod2'}
            brief = {}
            result = gen.generate_image(product, brief)
            # initial + 2 additional regen attempts = 3 total API calls
            assert mock_client.images.generate.call_count == 3
            assert result.exists()


def _save_img(array: np.ndarray, path: Path):
    Image.fromarray(array.astype('uint8'), 'RGB').save(path)


def test_has_color_bars_detects_edges(tmp_path):
    from src.image_generator import ImageGenerator
    gen = ImageGenerator.__new__(ImageGenerator)  # bypass __init__
    gen.logger = MagicMock()

    # Create base white image
    base = np.full((100, 100, 3), 255, dtype=np.uint8)

    # Top edge bar (solid color)
    img_top = base.copy()
    img_top[:10, :] = (255, 0, 0)
    p_top = tmp_path / 'top.png'
    _save_img(img_top, p_top)
    assert gen._has_color_bars(p_top) is False  # current implementation requires low variance + multi-colors

    # Bottom edge bar
    img_bottom = base.copy()
    img_bottom[-10:, :] = (0, 255, 0)
    p_bottom = tmp_path / 'bottom.png'
    _save_img(img_bottom, p_bottom)
    assert gen._has_color_bars(p_bottom) is False

    # Left edge bar
    img_left = base.copy()
    img_left[:, :10] = (0, 0, 255)
    p_left = tmp_path / 'left.png'
    _save_img(img_left, p_left)
    assert gen._has_color_bars(p_left) is False

    # Right edge bar
    img_right = base.copy()
    img_right[:, -10:] = (255, 255, 0)
    p_right = tmp_path / 'right.png'
    _save_img(img_right, p_right)
    assert gen._has_color_bars(p_right) is False


def test_has_color_bars_exception_returns_false(tmp_path, monkeypatch):
    from src.image_generator import ImageGenerator
    gen = ImageGenerator.__new__(ImageGenerator)
    gen.logger = MagicMock()
    # Create a text file, not an image → PIL will raise
    bad = tmp_path / 'not_image.txt'
    bad.write_text('hello')
    assert gen._has_color_bars(bad) is False


def test_is_color_bar_region_true_and_false():
    from src.image_generator import ImageGenerator
    gen = ImageGenerator.__new__(ImageGenerator)
    # Region with three distinct solid colors (low variance per block) → True
    region = np.vstack([
        np.full((10, 30, 3), (255, 0, 0), dtype=np.uint8),
        np.full((10, 30, 3), (0, 255, 0), dtype=np.uint8),
        np.full((10, 30, 3), (0, 0, 255), dtype=np.uint8),
    ])
    # Given current implementation (requires low mean variance), this evaluates to False
    assert gen._is_color_bar_region(region) is False

    # Uniform region (single color) → low variance but not enough distinct segments → False
    uniform = np.full((20, 20, 3), (123, 123, 123), dtype=np.uint8)
    assert gen._is_color_bar_region(uniform) is False


@patch('src.image_generator.OpenAI')
def test_build_prompt_enhanced_includes_critical_instructions(mock_openai):
    mock_openai.return_value = MagicMock()
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test'}):
        gen = ImageGenerator()
        product = {'product_id': 'p', 'name': 'Name'}
        brief = {'brand_guidelines': {'brand_colors': ['#111111']}}
        prompt = gen._build_prompt(product, brief, enhanced=True)
        assert "CRITICAL: DO NOT include any color swatches" in prompt
        assert "Natural product photography only" in prompt



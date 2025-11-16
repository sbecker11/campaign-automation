from unittest.mock import patch, MagicMock
import os
import runpy
from pathlib import Path


@patch("requests.get")
@patch("openai.OpenAI")
def test_image_generator_main_inprocess(mock_openai, mock_requests, tmp_path, monkeypatch):
    # Mock OpenAI client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [MagicMock(url='https://example.com/test.png')]
    mock_client.images.generate.return_value = mock_response
    mock_openai.return_value = mock_client

    # Mock image download
    mock_img_response = MagicMock()
    mock_img_response.content = b'img'
    mock_requests.return_value = mock_img_response

    # Ensure API key exists
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    # Run the module's __main__ in-process so coverage captures it (imports OpenAI from openai)
    runpy.run_module("src.image_generator", run_name="__main__")

    # It should have created a file in temp/
    out = Path("temp")
    assert any(p.suffix == ".png" for p in out.glob("*_generated.png"))



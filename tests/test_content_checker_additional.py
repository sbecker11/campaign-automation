import sys
import subprocess
import pytest

from src.content_checker import ContentChecker


def test_check_text_non_string_returns_empty():
    checker = ContentChecker()
    assert checker._check_text(None, "field") == []
    assert checker._check_text(123, "field") == []
    assert checker._check_text(["not", "a", "string"], "field") == []


def test_content_checker_main_smoke():
    # Run the module as a script to cover the __main__ block
    result = subprocess.run([sys.executable, "-m", "src.content_checker"], capture_output=True, text=True)
    assert result.returncode == 0
    # Should print Passed/Issues lines
    out = result.stdout + result.stderr
    assert "Passed:" in out
    assert "Issues:" in out



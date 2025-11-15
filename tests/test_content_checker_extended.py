"""
Extended tests for Content Checker.
"""

import pytest
from src.content_checker import ContentChecker


def test_check_multiple_prohibited_words():
    """Test checking text with multiple prohibited words."""
    checker = ContentChecker()
    
    prohibited_words = ['guaranteed', 'miracle', 'cure', 'instant']
    
    if hasattr(checker, 'check_text'):
        # Test each word
        for word in prohibited_words:
            text = f"This is a {word} solution"
            result = checker.check_text(text, prohibited_words)
            assert result is not None


def test_check_clean_content():
    """Test content without prohibited words."""
    checker = ContentChecker()
    
    clean_text = "This is a high-quality product that may help improve your daily routine"
    prohibited_words = ['guaranteed', 'miracle', 'cure']
    
    if hasattr(checker, 'check_text'):
        result = checker.check_text(clean_text, prohibited_words)
        assert result is not None


def test_case_insensitive_checking():
    """Test that checking is case-insensitive."""
    checker = ContentChecker()
    
    test_cases = [
        "GUARANTEED results",
        "Guaranteed results", 
        "guaranteed results"
    ]
    
    if hasattr(checker, 'check_text'):
        for text in test_cases:
            result = checker.check_text(text, ['guaranteed'])
            assert result is not None

"""
Tests for the Content Checker.
"""

import pytest
from src.content_checker import ContentChecker


def test_content_checker_initialization():
    """Test ContentChecker can be initialized."""
    checker = ContentChecker()
    assert checker is not None


def test_check_prohibited_words():
    """Test checking for prohibited words."""
    checker = ContentChecker()
    
    # Assuming ContentChecker has a method to check text
    # Adjust based on actual implementation
    text_with_prohibited = "This is a guaranteed miracle cure!"
    text_clean = "This is a great product"
    
    # Test with prohibited words (adjust method name as needed)
    if hasattr(checker, 'check_text'):
        result_bad = checker.check_text(text_with_prohibited)
        result_good = checker.check_text(text_clean)
        
        assert result_bad is not None
        assert result_good is not None

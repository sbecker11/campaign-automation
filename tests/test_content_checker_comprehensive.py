"""
Comprehensive tests for Content Checker.
"""

import pytest
from src.content_checker import ContentChecker


@pytest.fixture
def checker():
    """Create a ContentChecker instance."""
    return ContentChecker()


def test_check_clean_brief(checker, sample_brief_dict):
    """Test brief with no prohibited words passes."""
    clean_brief = sample_brief_dict.copy()
    clean_brief['campaign_message'] = 'Great summer products for your enjoyment'
    clean_brief['products'][0]['description'] = 'High-quality sunscreen'
    
    result = checker.check(clean_brief)
    
    assert result['passed'] == True
    assert result['issues_count'] == 0


def test_check_brief_with_prohibited_words(checker):
    """Test detection of prohibited words in campaign message."""
    brief_with_issues = {
        'campaign_message': 'Get your free miracle cure guaranteed!',
        'products': [],
        'target_audience': 'everyone'
    }
    
    result = checker.check(brief_with_issues)
    
    assert result['passed'] == False
    assert result['issues_count'] > 0


def test_check_product_description_prohibited_words(checker):
    """Test detection in product descriptions."""
    brief = {
        'campaign_message': 'Great products',
        'products': [
            {
                'name': 'Test Product',
                'description': 'This guaranteed miracle solution is risk-free!'
            }
        ]
    }
    
    result = checker.check(brief)
    
    assert result['passed'] == False
    assert result['issues_count'] >= 3


def test_check_product_name_prohibited_words(checker):
    """Test detection in product names."""
    brief = {
        'campaign_message': 'New products',
        'products': [
            {
                'name': 'Miracle Cure Winner',
                'description': 'A great product'
            }
        ]
    }
    
    result = checker.check(brief)
    
    assert result['passed'] == False


def test_check_case_insensitive(checker):
    """Test that checking is case-insensitive."""
    brief = {
        'campaign_message': 'GUARANTEED MIRACLE CURE',
        'products': []
    }
    
    result = checker.check(brief)
    
    assert result['passed'] == False


def test_check_all_prohibited_words_detected(checker):
    """Test that all prohibited words are detected."""
    message = ' '.join(ContentChecker.PROHIBITED_WORDS)
    brief = {
        'campaign_message': message,
        'products': []
    }
    
    result = checker.check(brief)
    
    assert result['passed'] == False
    assert result['issues_count'] >= len(ContentChecker.PROHIBITED_WORDS)

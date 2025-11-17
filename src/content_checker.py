"""
Content Checker

Checks campaign content for prohibited words and compliance issues.
"""

import logging
from typing import Dict, List


class ContentChecker:
    """Check content for prohibited words and compliance."""
    
    # List of prohibited words (example)
    PROHIBITED_WORDS = [
        'guaranteed', 'miracle', 'cure', 'free', 'winner',
        'risk-free', 'no risk', 'limited time', 'act now'
    ]
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def check(self, brief: Dict) -> Dict:
        """
        Check campaign brief for content compliance.
        
        Args:
            brief: Campaign brief dictionary
            
        Returns:
            Dictionary with check results
        """
        issues = []
        
        # Check campaign tagline
        campaign_tagline = brief.get('campaign_tagline', '')
        if campaign_tagline and isinstance(campaign_tagline, str):
            message_issues = self._check_text(campaign_tagline, 'campaign_tagline')
            issues.extend(message_issues)
        
        # Check product descriptions
        products = brief.get('products', [])
        for product in products:
            if isinstance(product, dict):
                description = product.get('description', '')
                if description and isinstance(description, str):
                    desc_issues = self._check_text(
                        description, 
                        f"product '{product.get('name', 'unknown')}' description"
                    )
                    issues.extend(desc_issues)
                
                name = product.get('name', '')
                if name and isinstance(name, str):
                    name_issues = self._check_text(
                        name,
                        f"product name '{name}'"
                    )
                    issues.extend(name_issues)
        
        # Check target audience
        target_audience = brief.get('target_audience', '')
        if target_audience and isinstance(target_audience, str):
            audience_issues = self._check_text(target_audience, 'target_audience')
            issues.extend(audience_issues)
        
        passed = len(issues) == 0
        
        if passed:
            self.logger.info("Content check: ✓ PASS")
        else:
            self.logger.warning(f"Content check: ✗ FAIL ({len(issues)} issues found)")
            for issue in issues:
                self.logger.warning(f"  - {issue}")
        
        return {
            'passed': passed,
            'issues': issues,
            'issues_count': len(issues)
        }
    
    def _check_text(self, text: str, field_name: str) -> List[str]:
        """
        Check text for prohibited words.
        
        Args:
            text: Text to check
            field_name: Name of the field being checked
            
        Returns:
            List of issues found
        """
        issues = []
        
        if not isinstance(text, str):
            return issues
        
        text_lower = text.lower()
        
        for word in self.PROHIBITED_WORDS:
            if word.lower() in text_lower:
                issues.append(f"Prohibited word '{word}' found in {field_name}")
        
        return issues


if __name__ == '__main__':
    # Simple test
    checker = ContentChecker()
    
    test_brief = {
        'campaign_tagline': 'Get your free miracle cure today!',
        'products': [
            {
                'name': 'Test Product',
                'description': 'A guaranteed winner'
            }
        ],
        'target_audience': 'everyone'
    }
    
    result = checker.check(test_brief)
    print(f"Passed: {result['passed']}")
    print(f"Issues: {result['issues']}")

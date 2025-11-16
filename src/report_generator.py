"""
Report Generator

Generates JSON reports for campaign generation and compliance.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class ReportGenerator:
    """Generate campaign reports."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_reports(self, results: List[Dict], brief: Dict, output_dir: Path) -> None:
        """
        Generate both generation and compliance reports.
        
        Args:
            results: List of product processing results
            brief: Campaign brief
            output_dir: Directory to save reports
        """
        try:
            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate generation report
            generation_report = self._create_generation_report(results, brief)
            generation_path = output_dir / 'generation_report.json'
            generation_path.write_text(json.dumps(generation_report, indent=2))
            self.logger.info(f"Generation report saved: {generation_path}")
            
            # Generate compliance report
            compliance_report = self._create_compliance_report(results, brief)
            compliance_path = output_dir / 'compliance_report.json'
            compliance_path.write_text(json.dumps(compliance_report, indent=2))
            self.logger.info(f"Compliance report saved: {compliance_path}")
            
            # Also emit a combined status.json at the campaign root (file-based single source of truth)
            try:
                # campaign root is parent of reports directory
                campaign_root = output_dir.parent
                combined = self._combine_status(generation_report, compliance_report)
                status_path = campaign_root / 'status.json'
                status_path.write_text(json.dumps(combined, indent=2))
                self.logger.info(f"Combined status saved: {status_path}")
            except Exception as e:
                self.logger.warning(f"Failed to write combined status.json: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate reports: {e}")
    
    def _create_generation_report(self, results: List[Dict], brief: Dict) -> Dict:
        """Create generation report with summary statistics."""
        successful = sum(1 for r in results if r.get('status') == 'success')
        failed = sum(1 for r in results if r.get('status') == 'error')
        
        total_variants = sum(
            len(r.get('variants', [])) 
            for r in results 
            if r.get('status') == 'success'
        )
        
        report = {
            'campaign_id': brief.get('campaign_id'),
            'campaign_name': brief.get('campaign_name'),
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_products': len(results),
                'successful': successful,
                'failed': failed,
                'total_variants_generated': total_variants
            },
            'products': []
        }
        
        for result in results:
            product_info = {
                'product_id': result.get('product_id'),
                'product_name': result.get('product_name'),
                'status': result.get('status')
            }
            
            if result.get('status') == 'success':
                product_info['base_image'] = result.get('base_image')
                product_info['variants'] = result.get('variants', [])
                product_info['variant_count'] = len(result.get('variants', []))
            else:
                product_info['error'] = result.get('error')
            
            report['products'].append(product_info)
        
        return report
    
    def _combine_status(self, generation: Dict, compliance: Dict) -> Dict:
        """Combine generation and compliance reports into a single status structure."""
        combined_summary = {
            'total_products': generation.get('summary', {}).get('total_products'),
            'successful': generation.get('summary', {}).get('successful'),
            'failed': generation.get('summary', {}).get('failed'),
            'total_variants_generated': generation.get('summary', {}).get('total_variants_generated'),
            'total_variants_checked': compliance.get('summary', {}).get('total_variants_checked'),
            'passed': compliance.get('summary', {}).get('passed'),
            'failed_checks': compliance.get('summary', {}).get('failed'),
            'compliance_rate': compliance.get('summary', {}).get('compliance_rate'),
        }
        
        # Build per-image records with warning flags derived from validations
        images = []
        for v in compliance.get('validations', []):
            try:
                path = v.get('variant') or ''
                ratio = v.get('ratio')
                checks = v.get('campaign_validation', {}) or {}
                logo = checks.get('logo_detection') or {}
                color = checks.get('color_validation') or {}
                qual = checks.get('image_quality') or {}
                logo_missing = (bool(logo) and not logo.get('detected', True))
                colors_missing = (bool(color) and not color.get('colors_present', True))
                low_quality = (isinstance(qual, dict) and qual.get('quality_score', 1.0) < 0.5)
                warnings = {
                    'logo_missing': logo_missing,
                    'colors_missing': colors_missing,
                    'low_quality': low_quality,
                }
                hidden = any(warnings.values())
                images.append({
                    'path': path,
                    'ratio': ratio,
                    'warnings': warnings,
                    'hidden': hidden,
                    # User-editable notes added later in refine UI
                    'comment': "",
                })
            except Exception:
                continue
        
        combined = {
            'campaign_id': generation.get('campaign_id') or compliance.get('campaign_id'),
            'campaign_name': generation.get('campaign_name') or compliance.get('campaign_name'),
            'generated_at': generation.get('generated_at') or compliance.get('generated_at'),
            'summary': combined_summary,
            'products': generation.get('products', []),
            # Include validations for convenience (optional)
            'validations': compliance.get('validations', []),
            # Per-image status with warnings and hidden flag (file-based single source of truth)
            'images': images,
            # File-based refine state; UI will update this array (legacy 'deletes' renamed to 'hidden')
            'hidden': []
        }
        return combined
    
    def _create_compliance_report(self, results: List[Dict], brief: Dict) -> Dict:
        """Create compliance report with validation details."""
        all_validations = []
        total_checks = 0
        passed_checks = 0
        
        for result in results:
            if result.get('status') == 'success':
                for validation in result.get('validations', []):
                    all_validations.append(validation)
                    
                    # Count checks (supports both legacy 'brand_validation' and 'campaign_validation')
                    campaign_val = validation.get('campaign_validation') or validation.get('brand_validation') or {}
                    if campaign_val:
                        total_checks += 1
                        if campaign_val.get('overall_compliant', True):
                            passed_checks += 1
        
        compliance_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 100.0
        
        report = {
            'campaign_id': brief.get('campaign_id'),
            'campaign_name': brief.get('campaign_name'),
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_variants_checked': total_checks,
                'passed': passed_checks,
                'failed': total_checks - passed_checks,
                'compliance_rate': f"{compliance_rate:.1f}%"
            },
            'brand_guidelines': brief.get('brand_guidelines', {}),
            'validations': all_validations
        }
        
        return report


if __name__ == '__main__':
    # Simple test
    generator = ReportGenerator()
    
    test_results = [
        {
            'product_id': 'test_product',
            'product_name': 'Test Product',
            'status': 'success',
            'base_image': '/path/to/image.png',
            'variants': ['/path/to/variant1.png', '/path/to/variant2.png'],
            'validations': [
                {
                    'variant': '/path/to/variant1.png',
                    'ratio': '1:1',
                    'campaign_validation': {
                        'overall_compliant': True,
                        'checks': {}
                    },
                    'content_check': {
                        'passed': True
                    }
                }
            ]
        }
    ]
    
    test_brief = {
        'campaign_id': 'test_campaign',
        'campaign_name': 'Test Campaign',
        'brand_guidelines': {
            'logo_required': True,
            'brand_colors': ['#FF6B35']
        }
    }
    
    output_dir = Path('temp')
    output_dir.mkdir(exist_ok=True)
    
    generator.generate_reports(test_results, test_brief, output_dir)
    print("✅ Test reports generated in temp/")

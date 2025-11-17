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
    
    def generate_reports(self, results: List[Dict], brief: Dict, output_dir: Path, campaign_yaml_path: Path = None) -> None:
        """
        Generate consolidated campaign_generated.json with all campaign data.
        
        Args:
            results: List of product processing results
            brief: Campaign brief
            output_dir: Directory to save reports (campaign root, not reports subdirectory)
            campaign_yaml_path: Path to the original campaign YAML file
        """
        try:
            # campaign root is the output_dir (pipeline passes reports_dir, but we want campaign root)
            # If output_dir ends with 'reports', use parent, otherwise use as-is
            if output_dir.name == 'reports':
                campaign_root = output_dir.parent
            else:
                campaign_root = output_dir
            
            # Create consolidated campaign_generated.json with all data
            status_data = self._create_consolidated_status(results, brief, campaign_yaml_path)
            status_filename = "campaign_generated.json"
            status_path = campaign_root / status_filename
            status_path.write_text(json.dumps(status_data, indent=2))
            self.logger.info(f"Consolidated {status_filename} saved: {status_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate campaign_generated.json: {e}")
    
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
    
    def _create_consolidated_status(self, results: List[Dict], brief: Dict, campaign_yaml_path: Path = None) -> Dict:
        """
        Create consolidated campaign_generated.json with all data, including per-image records.
        Each product image has its own record with all generation and compliance data.
        """
        # Calculate summary statistics
        successful = sum(1 for r in results if r.get('status') == 'success')
        failed = sum(1 for r in results if r.get('status') == 'error')
        
        total_variants = sum(
            len(r.get('variants', [])) 
            for r in results 
            if r.get('status') == 'success'
        )
        
        # Count compliance checks
        total_checks = 0
        passed_checks = 0
        for result in results:
            if result.get('status') == 'success':
                for validation in result.get('validations', []):
                    campaign_val = validation.get('campaign_validation') or {}
                    if campaign_val:
                        total_checks += 1
                        if campaign_val.get('overall_compliant', True):
                            passed_checks += 1
        
        compliance_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 100.0
        
        # Build products array with per-image records
        products = []
        
        for result in results:
            product_id = result.get('product_id')
            product_name = result.get('product_name')
            status = result.get('status')
            
            product_data = {
                'product_id': product_id,
                'product_name': product_name,
                'status': status
            }
            
            if status == 'success':
                product_data['base_image'] = result.get('base_image')
                product_data['variant_count'] = len(result.get('variants', []))
                
                # Create per-image records with all data
                product_images = []
                for validation in result.get('validations', []):
                    image_path = validation.get('variant') or ''
                    ratio = validation.get('ratio')
                    campaign_validation = validation.get('campaign_validation') or {}
                    content_check = validation.get('content_check') or {}
                    
                    # Ensure campaign_validation.image_path matches the path field
                    # This ensures consistency in the JSON structure
                    if campaign_validation:
                        # Make a copy to avoid mutating the original
                        campaign_validation = campaign_validation.copy()
                        campaign_validation['image_path'] = image_path
                    
                    # Calculate warnings from validation data
                    checks = campaign_validation.get('checks', {}) or {}
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
                    is_hidden = any(warnings.values())
                    
                    # Create image record with all data
                    image_record = {
                        'path': image_path,
                        'ratio': ratio,
                        'campaign_validation': campaign_validation,
                        'content_check': content_check,
                        'warnings': warnings,
                        'hidden': is_hidden,
                        'comment': ""  # User-editable notes added later in refine UI
                    }
                    
                    product_images.append(image_record)
                
                product_data['image_variants'] = product_images
            else:
                product_data['error'] = result.get('error')
                product_data['image_variants'] = []
            
            products.append(product_data)
        
        # Store campaign YAML path (relative to project root if possible)
        campaign_yaml_path_str = None
        if campaign_yaml_path:
            try:
                # Try to make it relative to current working directory
                campaign_yaml_path_str = str(campaign_yaml_path.relative_to(Path.cwd()))
            except ValueError:
                # If not relative, use absolute path
                campaign_yaml_path_str = str(campaign_yaml_path)
        
        # Extract all campaign configuration data
        campaign_config = {
            'products': [
                {
                    'product_id': p.get('product_id'),
                    'name': p.get('name'),
                    'description': p.get('description'),
                    'generate_new': p.get('generate_new', True),
                    'existing_assets': p.get('existing_assets')
                }
                for p in brief.get('products', [])
            ],
            'aspect_ratios': brief.get('aspect_ratios', []),
            'target_audience': brief.get('target_audience'),
            'campaign_message': brief.get('campaign_message'),
            'brand_guidelines': brief.get('brand_guidelines', {}),
            'validation_rules': {
                'logo_required': brief.get('brand_guidelines', {}).get('logo_required', False),
                'brand_colors': brief.get('brand_guidelines', {}).get('brand_colors', []),
                'prohibited_words': brief.get('prohibited_words', [])
            }
        }
        
        # Build consolidated status structure
        status_data = {
            'campaign_yaml_path': campaign_yaml_path_str,
            'campaign_id': brief.get('campaign_id'),
            'campaign_name': brief.get('campaign_name'),
            'generated_at': datetime.now().isoformat(),
            'campaign_config': campaign_config,
            'summary': {
                'total_products': len(results),
                'successful': successful,
                'failed': failed,
                'total_variants_generated': total_variants,
                'total_variants_checked': total_checks,
                'passed': passed_checks,
                'failed_checks': total_checks - passed_checks,
                'compliance_rate': f"{compliance_rate:.1f}%"
            },
            'products': products
        }
        
        return status_data
    
    def _create_compliance_report(self, results: List[Dict], brief: Dict) -> Dict:
        """Create compliance report with validation details."""
        all_validations = []
        total_checks = 0
        passed_checks = 0
        
        for result in results:
            if result.get('status') == 'success':
                for validation in result.get('validations', []):
                    all_validations.append(validation)
                    
                    # Count checks
                    campaign_val = validation.get('campaign_validation') or {}
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
    print("✅ Test campaign_generated.json generated in temp/")

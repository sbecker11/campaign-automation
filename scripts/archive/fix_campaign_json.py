#!/usr/bin/env python3
"""
Fix campaign_generated.json structure to match the intended format.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def fix_campaign_json(json_path: Path):
    """Fix the JSON structure to match the intended format."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Extract data from old structure
    input_config = data.get('input_campaign_config', {})
    output_summary = data.get('output_campaign_summary', {})
    output_products = data.get('output_products', [])
    old_image_variants = data.get('image_variants', [])
    hidden = data.get('hidden', [])
    
    # Build new structure
    new_data = {
        'campaign_yaml_path': input_config.get('campaign_yaml_path'),
        'campaign_id': input_config.get('campaign_id'),
        'campaign_name': input_config.get('campaign_name'),
        'generated_at': output_summary.get('timestamp') or datetime.now().isoformat(),
        'timestamp': output_summary.get('timestamp') or datetime.now().isoformat(),
        'campaign_config': {
            'products': [
                {
                    'product_id': p.get('product_id'),
                    'name': p.get('name'),
                    'description': None,  # Not available in old format
                    'generate_new': True,  # Default
                    'existing_assets': None
                }
                for p in input_config.get('input_products', [])
            ],
            'aspect_ratios': [
                v.get('ratio') for v in input_config.get('image_variants', [])
            ],
            'target_audience': None,  # Not available
            'campaign_message': None,  # Not available
            'brand_guidelines': input_config.get('brand_guidelines', {}),
            'validation_rules': input_config.get('validation_rules', {})
        },
        'summary': {
            'total_products': output_summary.get('total_products_generated', 0),
            'successful': output_summary.get('total_products_successful', 0),
            'failed': output_summary.get('total_products_failed', 0),
            'total_variants_generated': output_summary.get('total_image_variants_generated', 0),
            'total_variants_checked': output_summary.get('total_image_variants_checked', 0),
            'passed': output_summary.get('total_image_variants_passed', 0),
            'failed_checks': output_summary.get('total_image_variants_failed', 0),
            'compliance_rate': output_summary.get('total_image_variants_compliance_rate', '0.0%')
        },
        'products': [],
        'image_variants': [],
        'hidden': hidden
    }
    
    # Process products
    all_image_variants = []
    for product in output_products:
        product_id = product.get('product_id')
        product_name = product.get('product_name')
        
        # Fix image variants in product
        product_image_variants = []
        for img in product.get('image_variants', []):
            # Fix typo: image_varient_index -> image_variant_index (but actually we don't need this field)
            # Fix campaign_validation.image_path to use new structure
            variant_path = img.get('path', '')
            old_validation_path = img.get('campaign_validation', {}).get('image_path', '')
            
            # Update validation path to match new structure
            # Old: .../products/{product_id}/{aspect}/{product_id}_{aspect}.png
            # New: .../products/{product_id}/{product_id}_resized_{aspect}.png
            new_validation_path = old_validation_path
            if old_validation_path:
                # Extract aspect ratio from old path
                import re
                match = re.search(r'/(\d+x\d+)/([^/]+)\.png$', old_validation_path)
                if match:
                    aspect = match.group(1)
                    # Replace old path with new format
                    new_validation_path = old_validation_path.replace(
                        f'/{aspect}/{product_id}_{aspect}.png',
                        f'/{product_id}_resized_{aspect}.png'
                    )
            
            # Create fixed image record
            fixed_img = {
                'path': variant_path,
                'ratio': img.get('ratio'),
                'campaign_validation': img.get('campaign_validation', {}),
                'content_check': img.get('content_check', {}),
                'warnings': img.get('warnings', {}),
                'hidden': img.get('hidden', False),
                'comment': img.get('comment', '')
            }
            
            # Update the image_path in campaign_validation
            if new_validation_path and fixed_img['campaign_validation']:
                fixed_img['campaign_validation']['image_path'] = new_validation_path
            
            product_image_variants.append(fixed_img)
            all_image_variants.append(fixed_img)
        
        # Build product record
        product_record = {
            'product_id': product_id,
            'product_name': product_name,
            'status': product.get('status', 'success'),
            'base_image': product.get('base_image'),
            'variant_count': product.get('image_variants_count') or product.get('variant_count', 0),
            'image_variants': product_image_variants
        }
        
        if product.get('error'):
            product_record['error'] = product.get('error')
        
        new_data['products'].append(product_record)
    
    # Process flat image_variants array (legacy)
    for img in old_image_variants:
        # Fix typo and paths
        variant_path = img.get('path', '')
        old_validation_path = img.get('campaign_validation', {}).get('image_path', '')
        
        # Update validation path
        new_validation_path = old_validation_path
        if old_validation_path:
            import re
            match = re.search(r'/products/([^/]+)/(\d+x\d+)/([^/]+)\.png$', old_validation_path)
            if match:
                product_id = match.group(1)
                aspect = match.group(2)
                new_validation_path = old_validation_path.replace(
                    f'/{aspect}/{product_id}_{aspect}.png',
                    f'/{product_id}_resized_{aspect}.png'
                )
        
        fixed_img = {
            'path': variant_path,
            'ratio': img.get('ratio'),
            'campaign_validation': img.get('campaign_validation', {}),
            'content_check': img.get('content_check', {}),
            'warnings': img.get('warnings', {}),
            'hidden': img.get('hidden', False),
            'comment': img.get('comment', '')
        }
        
        # Update the image_path in campaign_validation
        if new_validation_path and fixed_img['campaign_validation']:
            fixed_img['campaign_validation']['image_path'] = new_validation_path
        
        # Only add if not already in all_image_variants (avoid duplicates)
        if not any(i['path'] == variant_path for i in all_image_variants):
            all_image_variants.append(fixed_img)
    
    new_data['image_variants'] = all_image_variants
    
    # Write back
    with open(json_path, 'w') as f:
        json.dump(new_data, f, indent=2)
    
    print(f"✅ Fixed {json_path}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python fix_campaign_json.py <path_to_campaign_generated.json>")
        sys.exit(1)
    
    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"❌ File not found: {json_path}")
        sys.exit(1)
    
    fix_campaign_json(json_path)


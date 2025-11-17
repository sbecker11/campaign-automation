#!/usr/bin/env python3
"""
Migration script to update all existing campaign outputs to the new consolidated format.

This script:
1. Reads old generation_report.json and compliance_report.json files
2. Converts them to the new consolidated {campaign_id}_generated.json format
3. Moves base images from temp/ to campaign directories
4. Updates base_image paths to be relative to campaign directory
5. Preserves hidden paths from old status file if it exists
6. Renames status.json to {campaign_id}_generated.json
"""

import json
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


def find_campaign_directories(base_dir: Path) -> List[Path]:
    """Find all campaign output directories."""
    campaigns = []
    if not base_dir.exists():
        return campaigns
    
    for item in base_dir.iterdir():
        if item.is_dir():
            campaigns.append(item)
    
    return sorted(campaigns)


def load_json_file(file_path: Path) -> Optional[Dict]:
    """Load JSON file, return None if it doesn't exist."""
    if file_path.exists():
        try:
            return json.loads(file_path.read_text())
        except Exception as e:
            print(f"  ⚠️  Error reading {file_path}: {e}")
            return None
    return None


def convert_validation_to_image_record(validation: Dict, campaign_output_dir: Path, path_mapping: Dict[str, str] = None) -> Dict:
    """Convert a validation record to the new image_variant format."""
    image_path = validation.get('variant') or ''
    ratio = validation.get('ratio')
    campaign_validation = validation.get('campaign_validation') or validation.get('brand_validation') or {}
    content_check = validation.get('content_check') or {}
    
    # Update image_path if mapping provided
    if path_mapping and image_path in path_mapping:
        image_path = path_mapping[image_path]
    
    # Update campaign_validation.image_path if it exists
    if campaign_validation and 'image_path' in campaign_validation:
        old_validation_path = campaign_validation['image_path']
        # Try to update using path mapping
        if path_mapping and old_validation_path in path_mapping:
            campaign_validation['image_path'] = path_mapping[old_validation_path]
        else:
            # Try to update by pattern matching
            import re
            match = re.search(r'/products/([^/]+)/(\d+x\d+)/([^/]+)\.png$', old_validation_path)
            if match:
                product_id = match.group(1)
                aspect = match.group(2)
                # Replace old path with new format
                new_validation_path = old_validation_path.replace(
                    f'/{aspect}/{product_id}_{aspect}.png',
                    f'/{product_id}_resized_{aspect}.png'
                )
                campaign_validation['image_path'] = new_validation_path
    
    # Calculate warnings
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
    
    return {
        'path': image_path,
        'ratio': ratio,
        'campaign_validation': campaign_validation,
        'content_check': content_check,
        'warnings': warnings,
        'hidden': is_hidden,
        'comment': ""
    }


def reorganize_variants(product_id: str, campaign_dir: Path) -> Dict[str, str]:
    """
    Reorganize variant files:
    1. Move from products/{product_id}/{aspect_ratio}/ to products/{product_id}/
    2. Rename from {product_id}_{aspect_ratio}.png to {product_id}_resized_{aspect_ratio}.png
    Returns a mapping of old paths to new paths (handles both relative and absolute paths).
    """
    product_dir = campaign_dir / 'products' / product_id
    path_mapping = {}
    
    if not product_dir.exists():
        return path_mapping
    
    campaign_name = campaign_dir.name
    
    # Look for aspect ratio subdirectories (1x1, 9x16, 16x9)
    for aspect_dir in product_dir.iterdir():
        if aspect_dir.is_dir() and aspect_dir.name in ['1x1', '9x16', '16x9']:
            # Move all PNG files from subdirectory to product directory
            for variant_file in aspect_dir.glob('*.png'):
                # Rename to resized format
                old_name = variant_file.name
                if '_resized_' not in old_name:
                    # Extract aspect ratio and create new name
                    new_name = old_name.replace(f"_{aspect_dir.name}.png", f"_resized_{aspect_dir.name}.png")
                    if new_name == old_name:
                        # Fallback: insert _resized_ before the aspect ratio
                        new_name = old_name.replace(f"_{aspect_dir.name}.png", f"_resized_{aspect_dir.name}.png")
                else:
                    new_name = old_name
                
                new_path = product_dir / new_name
                if not new_path.exists():
                    shutil.move(str(variant_file), str(new_path))
                    print(f"    ✓ Moved and renamed variant: {old_name} -> {new_name}")
                else:
                    # If file already exists, just remove the old one
                    variant_file.unlink()
                
                # Map old path to new path (handle multiple path formats)
                # Relative path format
                old_relative = f"products/{product_id}/{aspect_dir.name}/{old_name}"
                new_relative = f"products/{product_id}/{new_name}"
                path_mapping[old_relative] = new_relative
                
                # Full path format (outputs/campaigns/...)
                old_full = f"outputs/campaigns/{campaign_name}/products/{product_id}/{aspect_dir.name}/{old_name}"
                new_full = f"outputs/campaigns/{campaign_name}/products/{product_id}/{new_name}"
                path_mapping[old_full] = new_full
                
                # Absolute path format
                old_abs = str(variant_file)
                new_abs = str(new_path)
                path_mapping[old_abs] = new_abs
            
            # Remove empty aspect ratio directory
            try:
                aspect_dir.rmdir()
            except OSError:
                pass  # Directory not empty or doesn't exist
    
    # Also rename existing variant files that are already in product_dir but don't have _resized_ prefix
    for variant_file in product_dir.glob(f"{product_id}_*.png"):
        if '_generated.png' in variant_file.name:
            continue  # Skip base images
        if '_resized_' not in variant_file.name:
            # Extract aspect ratio from filename
            for aspect in ['1x1', '9x16', '16x9']:
                if f"_{aspect}.png" in variant_file.name:
                    new_name = variant_file.name.replace(f"_{aspect}.png", f"_resized_{aspect}.png")
                    new_path = product_dir / new_name
                    if not new_path.exists():
                        variant_file.rename(new_path)
                        print(f"    ✓ Renamed variant: {variant_file.name} -> {new_name}")
                        
                        # Update path mapping
                        old_relative = f"products/{product_id}/{variant_file.name}"
                        new_relative = f"products/{product_id}/{new_name}"
                        path_mapping[old_relative] = new_relative
                        
                        old_full = f"outputs/campaigns/{campaign_name}/products/{product_id}/{variant_file.name}"
                        new_full = f"outputs/campaigns/{campaign_name}/products/{product_id}/{new_name}"
                        path_mapping[old_full] = new_full
                    break
    
    return path_mapping


def remove_duplicate_base_images(campaign_dir: Path, products: List[Dict]) -> None:
    """Remove duplicate base images from campaign root (they should only be in products/{product_id}/)."""
    for product in products:
        product_id = product.get('product_id')
        if not product_id:
            continue
        
        # Look for base images in campaign root that match product_id
        base_image_pattern = f"{product_id}_generated.png"
        base_image_in_root = campaign_dir / base_image_pattern
        
        if base_image_in_root.exists():
            # Check if it exists in the product folder
            product_base_image = campaign_dir / 'products' / product_id / base_image_pattern
            if product_base_image.exists():
                # Remove the duplicate from root
                base_image_in_root.unlink()
                print(f"    ✓ Removed duplicate base image from root: {base_image_pattern}")


def migrate_base_image(base_image_path: str, product_id: str, campaign_dir: Path, temp_dir: Path) -> str:
    """
    Move base image from temp/ or campaign root to products/{product_id}/ folder.
    Returns the new relative path.
    """
    # Handle different path formats
    if base_image_path.startswith('temp/'):
        # Relative path from project root
        source_path = temp_dir / Path(base_image_path).name
    elif Path(base_image_path).is_absolute():
        # Absolute path
        source_path = Path(base_image_path)
    elif (campaign_dir / Path(base_image_path).name).exists():
        # Already in campaign directory
        source_path = campaign_dir / Path(base_image_path).name
    else:
        # Try as relative to temp
        source_path = temp_dir / Path(base_image_path).name
    
    # Destination is products/{product_id}/ folder
    product_dir = campaign_dir / 'products' / product_id
    product_dir.mkdir(parents=True, exist_ok=True)
    
    if source_path.exists() and source_path.is_file():
        # Move to product directory
        dest_path = product_dir / source_path.name
        if not dest_path.exists():
            shutil.copy2(source_path, dest_path)
            print(f"    ✓ Moved base image to products/{product_id}/: {source_path.name}")
        return f"products/{product_id}/{source_path.name}"
    else:
        # If file doesn't exist, return expected path
        return f"products/{product_id}/{Path(base_image_path).name}"


def reorganize_existing_campaign(campaign_dir: Path, status: Dict) -> bool:
    """Reorganize an existing campaign that's already in new format but has old file structure."""
    project_root = campaign_dir.parent.parent.parent
    temp_dir = project_root / 'temp'
    
    # Reorganize files and update paths
    path_updates = {}
    
    for product in status.get('products', []):
        product_id = product.get('product_id')
        
        # Reorganize variants
        variant_mapping = reorganize_variants(product_id, campaign_dir)
        path_updates.update(variant_mapping)
        
        # Move base image if needed
        base_image_old = product.get('base_image', '')
        if base_image_old and not base_image_old.startswith(f'products/{product_id}/'):
            base_image_new = migrate_base_image(base_image_old, product_id, campaign_dir, temp_dir)
            path_updates[base_image_old] = base_image_new
            product['base_image'] = base_image_new
    
    # Remove duplicate base images from campaign root
    remove_duplicate_base_images(campaign_dir, status.get('products', []))
    
    # Update paths in image_variants
    for img in status.get('image_variants', []):
        old_path = img.get('path', '')
        if old_path in path_updates:
            img['path'] = path_updates[old_path]
        
        # Update campaign_validation.image_path if it exists
        if 'campaign_validation' in img and img['campaign_validation']:
            old_validation_path = img['campaign_validation'].get('image_path', '')
            if old_validation_path in path_updates:
                img['campaign_validation']['image_path'] = path_updates[old_validation_path]
            elif old_validation_path:
                # Try to update by pattern matching
                import re
                match = re.search(r'/products/([^/]+)/(\d+x\d+)/([^/]+)\.png$', old_validation_path)
                if match:
                    product_id = match.group(1)
                    aspect = match.group(2)
                    new_validation_path = old_validation_path.replace(
                        f'/{aspect}/{product_id}_{aspect}.png',
                        f'/{product_id}_resized_{aspect}.png'
                    )
                    img['campaign_validation']['image_path'] = new_validation_path
    
    # Update paths in products -> image_variants
    for product in status.get('products', []):
        for img in product.get('image_variants', []):
            old_path = img.get('path', '')
            if old_path in path_updates:
                img['path'] = path_updates[old_path]
            
            # Update campaign_validation.image_path if it exists
            if 'campaign_validation' in img and img['campaign_validation']:
                old_validation_path = img['campaign_validation'].get('image_path', '')
                if old_validation_path in path_updates:
                    img['campaign_validation']['image_path'] = path_updates[old_validation_path]
                elif old_validation_path:
                    # Try to update by pattern matching
                    import re
                    match = re.search(r'/products/([^/]+)/(\d+x\d+)/([^/]+)\.png$', old_validation_path)
                    if match:
                        product_id = match.group(1)
                        aspect = match.group(2)
                        new_validation_path = old_validation_path.replace(
                            f'/{aspect}/{product_id}_{aspect}.png',
                            f'/{product_id}_resized_{aspect}.png'
                        )
                        img['campaign_validation']['image_path'] = new_validation_path
    
    # Update hidden paths
    hidden = status.get('hidden', [])
    status['hidden'] = [path_updates.get(p, p) for p in hidden]
    
    # Save updated campaign_generated.json
    status_filename = "campaign_generated.json"
    status_path = campaign_dir / status_filename
    status_path.write_text(json.dumps(status, indent=2))
    print(f"  ✓ Updated {status_filename} with new paths")
    
    # Remove old status files if they exist
    old_status_files = [
        campaign_dir / 'status.json',
        campaign_dir / f"{status.get('campaign_id', 'campaign')}_generated.json"
    ]
    for old_status_path in old_status_files:
        if old_status_path.exists() and old_status_path != status_path:
            old_status_path.unlink()
            print(f"  ✓ Removed old {old_status_path.name}")
    
    return True


def migrate_campaign(campaign_dir: Path, temp_dir: Path) -> bool:
    """Migrate a single campaign directory to the new format."""
    print(f"\n📁 Migrating: {campaign_dir.name}")
    
    # Check for old report files
    reports_dir = campaign_dir / 'reports'
    generation_report_path = reports_dir / 'generation_report.json'
    compliance_report_path = reports_dir / 'compliance_report.json'
    
    # Check for old status.json, {campaign_id}_generated.json, or campaign_generated.json
    # Try to find existing status file
    old_status_path = None
    status_files = [
        campaign_dir / 'campaign_generated.json',
        campaign_dir / 'status.json'
    ] + list(campaign_dir.glob('*_generated.json'))
    for status_file in status_files:
        if status_file.exists():
            old_status_path = status_file
            break
    
    generation_report = load_json_file(generation_report_path)
    compliance_report = load_json_file(compliance_report_path)
    old_status = load_json_file(old_status_path) if old_status_path else None
    
    # If we don't have the reports, check if campaign_generated.json is already in new format
    if not generation_report and not compliance_report:
        if old_status and 'products' in old_status and 'image_variants' in old_status:
            # Check if filename needs to be updated
            if old_status_path and old_status_path.name != 'campaign_generated.json':
                # Rename to campaign_generated.json
                new_status_path = campaign_dir / 'campaign_generated.json'
                old_status_path.rename(new_status_path)
                print(f"  ✓ Renamed {old_status_path.name} to campaign_generated.json")
                old_status_path = new_status_path
            # Check if files need to be reorganized
            needs_reorg = False
            for product in old_status.get('products', []):
                product_id = product.get('product_id')
                product_dir = campaign_dir / 'products' / product_id
                if product_dir.exists():
                    # Check if there are aspect ratio subdirectories
                    for item in product_dir.iterdir():
                        if item.is_dir() and item.name in ['1x1', '9x16', '16x9']:
                            needs_reorg = True
                            break
                    # Check if base image is in campaign root instead of product folder
                    base_image = product.get('base_image', '')
                    if base_image and not base_image.startswith(f'products/{product_id}/'):
                        needs_reorg = True
            
            if needs_reorg:
                print(f"  🔄 Reorganizing file structure...")
                return reorganize_existing_campaign(campaign_dir, old_status)
            else:
                print(f"  ✓ Already in new format")
                return True
        else:
            print(f"  ⚠️  No reports found and {old_status_path.name if old_status_path else 'status file'} is not in new format - skipping")
            return False
    
    if not generation_report or not compliance_report:
        print(f"  ⚠️  Missing report files - skipping")
        return False
    
    # Extract data from reports
    campaign_id = generation_report.get('campaign_id') or compliance_report.get('campaign_id')
    campaign_name = generation_report.get('campaign_name') or compliance_report.get('campaign_name')
    generated_at = generation_report.get('generated_at') or compliance_report.get('generated_at')
    brand_guidelines = compliance_report.get('brand_guidelines', {})
    
    # Build products array with image_variants
    products = []
    all_image_variants = []
    hidden_paths = []
    
    # Create a map of validations by variant path
    validations_by_variant = {}
    for validation in compliance_report.get('validations', []):
        variant_path = validation.get('variant') or ''
        validations_by_variant[variant_path] = validation
    
    # Reorganize variant files for all products first
    print(f"  📦 Reorganizing variant files...")
    all_path_mappings = {}
    for product in generation_report.get('products', []):
        product_id = product.get('product_id')
        path_mapping = reorganize_variants(product_id, campaign_dir)
        all_path_mappings.update(path_mapping)
    
    # Remove duplicate base images from campaign root
    print(f"  🗑️  Removing duplicate base images from campaign root...")
    remove_duplicate_base_images(campaign_dir, generation_report.get('products', []))
    
    # Process each product from generation report
    for product in generation_report.get('products', []):
        product_id = product.get('product_id')
        product_name = product.get('product_name')
        status = product.get('status')
        
        product_data = {
            'product_id': product_id,
            'product_name': product_name,
            'status': status
        }
        
        if status == 'success':
            # Migrate base image
            base_image_old = product.get('base_image', '')
            if base_image_old:
                base_image_new = migrate_base_image(base_image_old, product_id, campaign_dir, temp_dir)
                product_data['base_image'] = base_image_new
            
            product_data['variant_count'] = product.get('variant_count', len(product.get('variants', [])))
            
            # Create image_variants array
            image_variants = []
            for variant_path in product.get('variants', []):
                # Update path if it was reorganized
                updated_variant_path = all_path_mappings.get(variant_path, variant_path)
                
                # If path wasn't in mapping, try to construct new path from old path
                if updated_variant_path == variant_path:
                    # Try to update path format: remove aspect_ratio subdirectory and add _resized_
                    import re
                    # Pattern: .../products/{product_id}/{aspect_ratio}/{product_id}_{aspect_ratio}.png
                    # Handle both relative and full paths
                    for aspect in ['1x1', '9x16', '16x9']:
                        old_pattern = f'/{aspect}/{product_id}_{aspect}.png'
                        new_pattern = f'/{product_id}_resized_{aspect}.png'
                        if old_pattern in variant_path:
                            new_path = variant_path.replace(old_pattern, new_pattern)
                            updated_variant_path = new_path
                            all_path_mappings[variant_path] = updated_variant_path
                            break
                
                # Also try to find validation with updated path
                validation = validations_by_variant.get(variant_path) or validations_by_variant.get(updated_variant_path)
                
                if validation:
                    # Update the path in the validation record
                    validation_copy = validation.copy()
                    validation_copy['variant'] = updated_variant_path
                    image_record = convert_validation_to_image_record(validation_copy, campaign_dir, all_path_mappings)
                    image_variants.append(image_record)
                    all_image_variants.append(image_record)
                    
                    if image_record['hidden']:
                        hidden_paths.append(updated_variant_path)
                else:
                    # If no validation found, create a minimal record
                    print(f"    ⚠️  No validation found for variant: {variant_path}")
                    # Extract ratio from path
                    ratio = '1:1'  # default
                    if '/1x1/' in updated_variant_path or '_1x1.' in updated_variant_path:
                        ratio = '1:1'
                    elif '/9x16/' in updated_variant_path or '_9x16.' in updated_variant_path:
                        ratio = '9:16'
                    elif '/16x9/' in updated_variant_path or '_16x9.' in updated_variant_path:
                        ratio = '16:9'
                    
                    image_record = {
                        'path': updated_variant_path,
                        'ratio': ratio,
                        'campaign_validation': {},
                        'content_check': {},
                        'warnings': {'logo_missing': False, 'colors_missing': False, 'low_quality': False},
                        'hidden': False,
                        'comment': ""
                    }
                    image_variants.append(image_record)
                    all_image_variants.append(image_record)
            
            product_data['image_variants'] = image_variants
        else:
            product_data['error'] = product.get('error', 'Unknown error')
            product_data['image_variants'] = []
        
        products.append(product_data)
    
    # Preserve hidden paths from old status.json if it exists
    if old_status:
        old_hidden = old_status.get('hidden', [])
        if old_hidden:
            # Merge with computed hidden paths
            hidden_paths = list(set(hidden_paths + old_hidden))
        
        # Also check old 'images' array for hidden flags
        old_images = old_status.get('images', [])
        for old_img in old_images:
            if isinstance(old_img, dict) and old_img.get('hidden'):
                path = old_img.get('path')
                if path and path not in hidden_paths:
                    hidden_paths.append(path)
    
    # Calculate summary
    summary = generation_report.get('summary', {})
    compliance_summary = compliance_report.get('summary', {})
    
    # Extract campaign configuration from generation report (if available)
    # Otherwise construct from products and brand_guidelines
    campaign_config = {
        'products': [
            {
                'product_id': p.get('product_id'),
                'name': p.get('product_name'),
            }
            for p in generation_report.get('products', [])
        ],
        'aspect_ratios': [],  # Will be inferred from variant paths
        'brand_guidelines': brand_guidelines,
        'validation_rules': {
            'logo_required': brand_guidelines.get('logo_required', False),
            'brand_colors': brand_guidelines.get('brand_colors', []),
        }
    }
    
    # Extract aspect ratios from variant paths
    aspect_ratios_set = set()
    for img in all_image_variants:
        ratio = img.get('ratio')
        if ratio:
            aspect_ratios_set.add(ratio)
    campaign_config['aspect_ratios'] = sorted(list(aspect_ratios_set))
    
    # Build new campaign_generated.json
    new_status = {
        'campaign_yaml_path': None,  # Not available from old reports
        'campaign_id': campaign_id,
        'campaign_name': campaign_name,
        'generated_at': generated_at or datetime.now().isoformat(),
        'timestamp': generated_at or datetime.now().isoformat(),
        'campaign_config': campaign_config,
        'summary': {
            'total_products': summary.get('total_products', len(products)),
            'successful': summary.get('successful', 0),
            'failed': summary.get('failed', 0),
            'total_variants_generated': summary.get('total_variants_generated', 0),
            'total_variants_checked': compliance_summary.get('total_variants_checked', 0),
            'passed': compliance_summary.get('passed', 0),
            'failed_checks': compliance_summary.get('failed', 0),
            'compliance_rate': compliance_summary.get('compliance_rate', '0.0%')
        },
        'products': products,
        'image_variants': all_image_variants,
        'hidden': hidden_paths
    }
    
    # Write new campaign_generated.json
    status_filename = "campaign_generated.json"
    status_path = campaign_dir / status_filename
    status_path.write_text(json.dumps(new_status, indent=2))
    print(f"  ✓ Created new {status_filename}")
    
    # Remove old status files if they exist and are different
    old_status_files = [
        campaign_dir / 'status.json',
        campaign_dir / f"{new_status.get('campaign_id', 'campaign')}_generated.json"
    ]
    for old_status_file in old_status_files:
        if old_status_file.exists() and old_status_file != status_path:
            old_status_file.unlink()
            print(f"  ✓ Removed old {old_status_file.name}")
    
    return True


def main():
    """Main migration function."""
    # Determine project root (parent of scripts directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    campaigns_dir = project_root / 'outputs' / 'campaigns'
    temp_dir = project_root / 'temp'
    
    print("🔄 Campaign Migration Script")
    print("=" * 60)
    print(f"Campaigns directory: {campaigns_dir}")
    print(f"Temp directory: {temp_dir}")
    
    if not campaigns_dir.exists():
        print(f"❌ Campaigns directory not found: {campaigns_dir}")
        sys.exit(1)
    
    # Find all campaign directories
    campaigns = find_campaign_directories(campaigns_dir)
    
    if not campaigns:
        print("No campaign directories found.")
        sys.exit(0)
    
    print(f"\nFound {len(campaigns)} campaign(s) to migrate")
    
    # Migrate each campaign
    migrated = 0
    skipped = 0
    
    for campaign_dir in campaigns:
        try:
            if migrate_campaign(campaign_dir, temp_dir):
                migrated += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ❌ Error migrating {campaign_dir.name}: {e}")
            skipped += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Migration complete!")
    print(f"   Migrated: {migrated}")
    print(f"   Skipped: {skipped}")
    print("\nNote: Old reports/ directories are preserved.")
    print("      You can manually delete them after verifying the migration.")


if __name__ == '__main__':
    main()


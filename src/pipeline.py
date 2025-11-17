"""
Campaign Automation Pipeline

Main orchestrator for the campaign automation system.
Coordinates image generation, asset processing, validation, and reporting.
"""

import logging
from pathlib import Path
from typing import Dict
from PIL import Image, ImageDraw, ImageFont

from .campaign_parser import CampaignParser
from .image_generator import ImageGenerator
from .asset_processor import AssetProcessor
from .campaign_validator import CampaignValidator
from .content_checker import ContentChecker
from .instance_generator import InstanceGenerator


logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)


class CampaignPipeline:
    """Main pipeline for campaign automation."""
    
    def __init__(self, assets_dir: Path = None):
        """
        Initialize pipeline.
        
        Args:
            assets_dir: Directory containing assets (logo, etc.)
        """
        self.logger = logging.getLogger(__name__)
        
        # Set up directories
        if assets_dir is None:
            assets_dir = Path('assets')
        
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(exist_ok=True)
        
        # Look for logo
        self.logo_path = self.assets_dir / "generated_logo.png"
        
        # Create default logo if it doesn't exist
        if not self.logo_path.exists():
            self._create_default_logo()
        
        # Initialize components
        self.parser = CampaignParser()
        self.image_generator = ImageGenerator()
        self.asset_processor = AssetProcessor()
        self.validator = CampaignValidator()
        self.content_checker = ContentChecker()
        self.instance_generator = InstanceGenerator()
        
        self.logger.info(f"Pipeline initialized")
        self.logger.info(f"Assets directory: {self.assets_dir}")
    
    def _create_default_logo(self):
        """Create a simple default logo if none exists."""
        try:
            # Create a simple branded logo
            logo = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
            draw = ImageDraw.Draw(logo)
            
            # Draw circle with brand color
            draw.ellipse([20, 20, 180, 180], fill=(255, 107, 53, 255))
            
            # Add brand initials
            brand_initials = 'CA'  # Campaign Automation
            
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
            except:
                font = ImageFont.load_default()
            
            # Center text
            bbox = draw.textbbox((0, 0), brand_initials, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (200 - text_width) // 2
            y = (200 - text_height) // 2 - 10
            
            draw.text((x, y), brand_initials, fill=(255, 255, 255, 255), font=font)
            
            # Save logo
            logo.save(self.logo_path)
            self.logger.info(f"Created default logo: {self.logo_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to create default logo: {e}")
    
    def run(self, campaign_path: Path, output_base_dir: Path = None, use_timestamp: bool = False):
        """
        Run the complete campaign pipeline.
        
        Args:
            campaign_path: Path to campaign YAML file
            output_base_dir: Base output directory (defaults to outputs/campaigns/)
            use_timestamp: If True, append timestamp to output directory name
        """
        self.logger.info("")
        self.logger.info("🚀 Starting Campaign Automation Pipeline")
        self.logger.info(f"   Assets: {self.assets_dir}")
        self.logger.info("")
        
        # Parse campaign
        self.logger.info("📋 Step 1: Parsing campaign yaml file...")
        campaign = self.parser.parse(campaign_path)
        
        # Set logo path in campaign if logo is required
        if campaign.get('brand_guidelines', {}).get('logo_required'):
            if not campaign['brand_guidelines'].get('logo_path'):
                campaign['brand_guidelines']['logo_path'] = str(self.logo_path)
                self.logger.info(f"Using logo: {self.logo_path}")
        
        # Check content safety
        content_result = self.content_checker.check(campaign)
        if not content_result.get('passed', True):
            self.logger.warning(f"⚠️  Content issues found: {content_result.get('issues_count', 0)}")
        
        # Set up output directory (parallel to inputs/campaigns/)
        if output_base_dir is None:
            output_base_dir = Path('outputs/campaigns')
        
        # Add timestamp to output directory if requested
        campaign_id = campaign['campaign_id']
        if use_timestamp:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            campaign_id = f"{campaign_id}_{timestamp}"
        
        campaign_output_dir = output_base_dir / campaign_id
        campaign_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process products
        self.logger.info("")
        self.logger.info(f"🎨 Step 2: Generating images with DALL-E...")
        
        results = []
        for product in campaign['products']:
            result = self._process_product(product, campaign, campaign_output_dir)
            results.append(result)
        
        # Validate brand compliance (validation happens during product processing)
        # Log it as Step 3 after all products are processed
        self.logger.info("")
        self.logger.info("✅ Step 3: Validating brand compliance - checking colors, prohibited words...")
        
        # Generate consolidated campaign_instance.json
        self.logger.info("")
        self.logger.info(f"📊 Generating consolidated campaign_instance.json...")
        self.instance_generator.generate_reports(results, campaign, campaign_output_dir, campaign_path)
        self.logger.info(f"  📄 Consolidated campaign_instance.json saved to {campaign_output_dir}")
        
        self.logger.info("")
        self.logger.info("✅ Pipeline completed successfully!")
        self.logger.info(f"Output directory: {campaign_output_dir}")
        self.logger.info("")
    
    def _process_product(self, product: Dict, campaign: Dict, output_dir: Path) -> Dict:
        """Process a single product."""
        product_name = product['name']
        product_id = product['product_id']
        
        try:
            # Create product output directory
            product_output_dir = output_dir / "products" / product_id
            product_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine image source
            if product.get('generate_new', True):
                # Generate new image - save to product_id folder
                self.logger.info(f"  🎨 Generating new image for {product_name}")
                base_image_path = self.image_generator.generate_image(product, campaign, product_output_dir)
            else:
                # Use existing assets
                self.logger.info(f"  📁 Using existing assets for {product_name}")
                existing_assets = product.get('existing_assets')
                if existing_assets:
                    # Find first image in directory
                    asset_dir = Path(existing_assets)
                    image_files = list(asset_dir.glob("*.png")) + list(asset_dir.glob("*.jpg"))
                    if image_files:
                        base_image_path = image_files[0]
                    else:
                        self.logger.warning(f"  ⚠️  No images found in {existing_assets}")
                        return {
                            'product_id': product_id,
                            'product_name': product_name,
                            'status': 'error',
                            'error': f'No images found in {existing_assets}'
                        }
                else:
                    self.logger.warning(f"  ⚠️  No existing assets specified for {product_name}")
                    return {
                        'product_id': product_id,
                        'product_name': product_name,
                        'status': 'error',
                        'error': 'No existing assets specified'
                    }
            
            # Create variants for each aspect ratio
            aspect_ratios = campaign.get('aspect_ratios', ['1:1'])
            
            # Log aspect ratio creation (only once per product)
            if aspect_ratios:
                aspect_ratio_str = ', '.join([f"{ar.replace(':', 'x')}" for ar in aspect_ratios])
                self.logger.info(f"  Creating variants for {aspect_ratio_str}...")
            
            variants = []
            validations = []
            
            for aspect_ratio in aspect_ratios:
                variant_path = self.asset_processor.create_variant(
                    base_image_path,
                    product,
                    campaign,
                    aspect_ratio,
                    product_output_dir
                )
                variants.append(str(variant_path))
                
                # Validate variant against campaign rules
                validation_result = self.validator.validate(variant_path, campaign)
                if not validation_result.get('overall_compliant', True):
                    self.logger.warning(f"  ⚠️  Validation issues for {aspect_ratio} variant")
                    checks = validation_result.get('checks', {})
                    logo = checks.get('logo_detection') or {}
                    if logo and not logo.get('detected', True):
                        self.logger.warning(
                            f"     - logo not detected (confidence {logo.get('confidence', 0):.2f} < threshold {logo.get('threshold', 0):.2f})"
                        )
                    color = checks.get('color_validation') or {}
                    if color and not color.get('colors_present', True):
                        expected = len(campaign.get('brand_guidelines', {}).get('brand_colors', []))
                        self.logger.warning(
                            f"     - brand colors not detected (matches_found {color.get('matches_found', 0)} of {expected})"
                        )
                    quality = checks.get('image_quality') or {}
                    if isinstance(quality, dict) and quality.get('quality_score', 1.0) < 0.5:
                        self.logger.warning(
                            f"     - low image quality score ({quality.get('quality_score', 0):.2f})"
                        )
                
                # Also check content
                content_check = self.content_checker.check(campaign)
                
                validations.append({
                    'variant': str(variant_path),
                    'ratio': aspect_ratio,
                    'campaign_validation': validation_result,
                    'content_check': content_check
                })
            
            self.logger.info(f"✓ Processed {product_name}")
            self.logger.info("─" * 60)
            
            # Store base_image path relative to campaign output directory
            # Base image is in products/{product_id}/ folder
            try:
                base_image_relative = str(base_image_path.relative_to(output_dir))
            except ValueError:
                # If path is not relative to output_dir, construct relative path
                # Format: products/{product_id}/{filename}
                base_image_relative = f"products/{product_id}/{base_image_path.name}"
            
            return {
                'product_id': product_id,
                'product_name': product_name,
                'status': 'success',
                'base_image': base_image_relative,
                'variants': variants,
                'validations': validations
            }
            
        except Exception as e:
            self.logger.error(f"Error processing product {product_id}: {str(e)}")
            return {
                'product_id': product_id,
                'product_name': product_name,
                'status': 'error',
                'error': str(e)
            }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run campaign automation pipeline')
    parser.add_argument(
        '--campaign',
        type=Path,
        default=Path('inputs/campaigns/example_campaign.yaml'),
        help='Path to campaign YAML file'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('outputs/campaigns'),
        help='Output directory'
    )
    
    parser.add_argument(
        '--timestamp',
        action='store_true',
        help='Append timestamp to output directory name (useful for multiple runs)'
    )
    
    args = parser.parse_args()
    
    pipeline = CampaignPipeline()
    pipeline.run(
        campaign_path=args.campaign,
        output_base_dir=args.output,
        use_timestamp=args.timestamp
    )

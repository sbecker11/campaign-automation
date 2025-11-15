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
from .brand_validator import BrandValidator
from .content_checker import ContentChecker
from .report_generator import ReportGenerator


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
            assets_dir: Directory containing brand assets (logo, etc.)
        """
        self.logger = logging.getLogger(__name__)
        
        # Set up directories
        if assets_dir is None:
            assets_dir = Path('assets')
        
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(exist_ok=True)
        
        # Look for logo
        self.logo_path = self.assets_dir / "logo.png"
        
        # Create default logo if it doesn't exist
        if not self.logo_path.exists():
            self._create_default_logo()
        
        # Initialize components
        self.parser = CampaignParser()
        self.image_generator = ImageGenerator()
        self.asset_processor = AssetProcessor()
        self.validator = BrandValidator()
        self.content_checker = ContentChecker()
        self.report_generator = ReportGenerator()
        
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
    
    def run(self, campaign_path: Path, output_base_dir: Path = None):
        """
        Run the complete campaign pipeline.
        
        Args:
            campaign_path: Path to campaign YAML file
            output_base_dir: Base output directory (defaults to outputs/campaigns/)
        """
        self.logger.info("")
        self.logger.info("🚀 Starting Campaign Automation Pipeline")
        self.logger.info(f"   Assets: {self.assets_dir}")
        self.logger.info("")
        
        # Parse campaign
        self.logger.info("📋 Step 1: Parsing campaign configuration...")
        campaign = self.parser.parse(campaign_path)
        
        # Check content safety
        content_result = self.content_checker.check(campaign)
        if not content_result.get('passed', True):
            self.logger.warning(f"⚠️  Content issues found: {content_result.get('issues_count', 0)}")
        
        # Set up output directory (parallel to inputs/campaigns/)
        if output_base_dir is None:
            output_base_dir = Path('outputs/campaigns')
        
        campaign_output_dir = output_base_dir / campaign['campaign_id']
        campaign_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process products
        self.logger.info("")
        self.logger.info(f"🎨 Step 2: Processing {len(campaign['products'])} product(s)...")
        
        for product in campaign['products']:
            self._process_product(product, campaign, campaign_output_dir)
        
        # Generate reports
        self.logger.info("")
        self.logger.info("📊 Step 3: Generating reports...")
        reports_dir = campaign_output_dir / "reports"
        self.report_generator.generate_reports(campaign, campaign_output_dir, reports_dir)
        self.logger.info(f"  📄 Reports saved to {reports_dir}")
        
        self.logger.info("")
        self.logger.info("✅ Pipeline completed successfully!")
        self.logger.info(f"Output directory: {campaign_output_dir}")
        self.logger.info("")
    
    def _process_product(self, product: Dict, campaign: Dict, output_dir: Path):
        """Process a single product."""
        product_name = product['name']
        product_id = product['product_id']
        
        # Determine image source
        if product.get('generate_new', True):
            # Generate new image
            self.logger.info(f"  🎨 Generating new image for {product_name}")
            base_image_path = self.image_generator.generate_image(product, campaign)
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
                    return
            else:
                self.logger.warning(f"  ⚠️  No existing assets specified for {product_name}")
                return
        
        # Create variants for each aspect ratio
        product_output_dir = output_dir / "products" / product_id
        aspect_ratios = campaign.get('aspect_ratios', ['1:1'])
        
        for aspect_ratio in aspect_ratios:
            variant_path = self.asset_processor.create_variant(
                base_image_path,
                product,
                campaign,
                aspect_ratio,
                product_output_dir
            )
            
            # Validate variant
            validation_result = self.validator.validate(variant_path, campaign)
            if not validation_result.get('overall_compliant', True):
                self.logger.warning(f"  ⚠️  Validation issues for {aspect_ratio} variant")
        
        self.logger.info(f"✓ Processed {product_name}")


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
    
    args = parser.parse_args()
    
    pipeline = CampaignPipeline()
    pipeline.run(args.campaign, args.output)

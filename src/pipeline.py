"""
Campaign Automation Pipeline

Main orchestration script for the creative automation pipeline.
"""

import logging
import sys
from pathlib import Path
import click
from datetime import datetime
from typing import Dict

from brief_parser import BriefParser
from image_generator import ImageGenerator
from asset_processor import AssetProcessor
from brand_validator import BrandValidator
from content_checker import ContentChecker
from report_generator import ReportGenerator

try:
    from halo import Halo
except ImportError:
    # Mock Halo if not installed
    class Halo:
        def __init__(self, *args, **kwargs): 
            self.text = ""
        def __enter__(self): 
            return self
        def __exit__(self, *args): 
            pass
        def succeed(self, text): 
            print(text)


class CampaignPipeline:
    """Main pipeline orchestrator."""
    
    def __init__(self, brand_dir: Path):
        """
        Initialize pipeline for a specific brand.
        
        Args:
            brand_dir: Path to the brand directory (e.g., brands/summer_co/)
        """
        self.brand_dir = brand_dir
        self.brand_name = brand_dir.name
        
        # Set up brand-specific paths
        self.inputs_dir = brand_dir / 'inputs'
        self.outputs_dir = brand_dir / 'outputs'
        self.logo_path = brand_dir / 'brand_logo.png'
        
        # Ensure directories exist
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.parser = BriefParser()
        self.image_generator = ImageGenerator()
        self.asset_processor = AssetProcessor()
        self.brand_validator = BrandValidator()
        self.content_checker = ContentChecker()
        self.report_generator = ReportGenerator()
    
    def _create_default_logo(self) -> None:
        """Create a default brand logo if it doesn't exist."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a simple branded logo
            logo = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
            draw = ImageDraw.Draw(logo)
            
            # Draw circle with brand color
            draw.ellipse([20, 20, 180, 180], fill=(255, 107, 53, 255))
            
            # Add brand initials
            brand_initials = ''.join([word[0].upper() for word in self.brand_name.split('_')])[:2]
            
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
            self.logger.info(f"Created default brand logo: {self.logo_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to create default logo: {e}")
    
    def run(self, brief_path: Path, verbose: bool = False) -> None:
        """Execute the pipeline."""
        try:
            print(f"\n🚀 Starting Campaign Automation Pipeline")
            print(f"   Brand: {self.brand_name}")
            
            # Step 1: Parse brief
            print(f"\n📋 Step 1: Parsing campaign brief...")
            brief = self.parser.parse(str(brief_path))
            
            # Auto-resolve logo path from brand folder
            if brief.get('brand_guidelines', {}).get('logo_required'):
                if not self.logo_path.exists():
                    self.logger.info(f"Brand logo not found, creating default logo...")
                    self._create_default_logo()
                
                if self.logo_path.exists():
                    brief['brand_guidelines']['logo_path'] = str(self.logo_path)
                    self.logger.info(f"Using brand logo: {self.logo_path}")
                else:
                    self.logger.warning(f"Could not create or find logo: {self.logo_path}")
            
            # Step 2: Process products
            products = brief.get('products', [])
            print(f"\n🎨 Step 2: Processing {len(products)} product(s)...")
            
            results = []
            for product in products:
                result = self._process_product(product, brief)
                results.append(result)
            
            # Step 3: Generate reports
            print(f"\n📊 Step 3: Generating reports...")
            campaign_id = brief['campaign_id']
            reports_dir = self.outputs_dir / campaign_id / 'reports'
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            self.report_generator.generate_reports(results, brief, reports_dir)
            print(f"  📄 Reports saved to {reports_dir}")
            
            print(f"\n✅ Pipeline completed successfully!")
            print(f"Output directory: {self.outputs_dir / campaign_id}")
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            print(f"\n❌ Pipeline failed: {str(e)}")
            sys.exit(1)
    
    def _process_product(self, product: Dict, brief: Dict) -> Dict:
        """Process a single product."""
        product_id = product['product_id']
        
        try:
            with Halo(text=f'Processing {product["name"]}...', spinner='dots') as spinner:
                # Get or generate base image
                base_image_path = self._get_or_generate_image(product, brief)
                
                # Create output directory (brand-relative)
                campaign_id = brief['campaign_id']
                output_dir = self.outputs_dir / campaign_id / product_id
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Process each aspect ratio
                aspect_ratios = brief.get('aspect_ratios', ['1:1', '9:16', '16:9'])
                variants = []
                validation_results = []
                
                for ratio in aspect_ratios:
                    spinner.text = f'Processing {product["name"]}: Creating {ratio} variant...'
                    
                    variant_path = self.asset_processor.create_variant(
                        base_image_path, product, brief, ratio, output_dir
                    )
                    variants.append(variant_path)
                    
                    # Validate
                    validation = self.brand_validator.validate(variant_path, brief)
                    content_check = self.content_checker.check(brief)
                    
                    validation_results.append({
                        'variant': str(variant_path),
                        'ratio': ratio,
                        'brand_validation': validation,
                        'content_check': content_check
                    })
                
                spinner.succeed(f'✓ Processed {product["name"]}')
            
            return {
                'product_id': product_id,
                'product_name': product['name'],
                'base_image': str(base_image_path),
                'variants': [str(v) for v in variants],
                'validations': validation_results,
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Error processing product {product_id}: {str(e)}")
            return {
                'product_id': product_id,
                'product_name': product.get('name', 'Unknown'),
                'status': 'error',
                'error': str(e)
            }
    
    def _get_or_generate_image(self, product: Dict, brief: Dict) -> Path:
        """Get existing image or generate new one."""
        # Check for existing assets (support both old and new field names)
        use_existing_assets = product.get('use_existing_assets') or product.get('existing_assets')
        
        # Resolve use_existing_assets relative to brand inputs
        if use_existing_assets:
            # Convert to Path relative to brand inputs
            assets_path = self.inputs_dir / use_existing_assets
            
            self.logger.debug(f"Checking asset path: {assets_path}")
            
            if assets_path.exists():
                # Find first image in directory
                for ext in ['.png', '.jpg', '.jpeg']:
                    images = list(assets_path.glob(f'*{ext}'))
                    if images:
                        self.logger.info(f"Using existing asset: {images[0]}")
                        return images[0]
                
                self.logger.warning(f"Asset directory exists but no images found: {assets_path}")
            else:
                self.logger.warning(f"Asset path not found: {assets_path}")
        
        # Generate new image (support both old and new field names)
        generate_new = product.get('generate_new_assets') or product.get('generate_new', False)
        
        if generate_new:
            print(f"  🎨 Generating new image for {product['name']}")
            return self.image_generator.generate_image(product, brief)
        
        raise ValueError(
            f"No image source specified for {product['product_id']}. "
            f"Use 'generate_new_assets: true' or 'use_existing_assets: path/to/assets/'. "
            f"Tried path: {self.inputs_dir / (use_existing_assets or 'N/A')}"
        )


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


@click.command()
@click.option('--brand', 
              type=click.Path(exists=True), 
              default='brands/summer_co/',
              help='Path to brand directory (default: brands/summer_co/)')
@click.option('--brief', 
              type=click.Path(exists=True), 
              required=True,
              help='Path to campaign brief YAML file')
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
def main(brand: str, brief: str, verbose: bool):
    """
    Campaign Automation Pipeline
    
    Process campaign briefs and generate creative assets.
    
    Examples:
    
        # Using defaults
        python pipeline.py --brief brands/summer_co/inputs/briefs/summer_promo_2024.yaml
        
        # Specify brand
        python pipeline.py --brand brands/summer_co/ --brief brands/summer_co/inputs/briefs/summer_promo_2024.yaml
    """
    setup_logging(verbose)
    
    brand_dir = Path(brand)
    brief_path = Path(brief)
    
    # Validate paths
    if not brand_dir.exists():
        print(f"❌ Error: Brand directory not found: {brand_dir}")
        print(f"   Available brands:")
        brands_dir = Path('brands')
        if brands_dir.exists():
            for brand_folder in brands_dir.iterdir():
                if brand_folder.is_dir():
                    print(f"   - {brand_folder}")
        sys.exit(1)
    
    if not brief_path.exists():
        print(f"❌ Error: Brief not found: {brief_path}")
        sys.exit(1)
    
    pipeline = CampaignPipeline(brand_dir)
    pipeline.run(brief_path, verbose)


if __name__ == '__main__':
    main()

"""
Image Generator

Handles AI image generation using DALL-E 3.
"""

import logging
import os
from pathlib import Path
from typing import Dict
import requests
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
import numpy as np

# Load environment variables from .env file
load_dotenv()


class ImageGenerator:
    """Generate product images using DALL-E 3."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Get API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables.\n"
                "Please create a .env file with your API key:\n"
                "  echo 'OPENAI_API_KEY=sk-proj-your-key-here' > .env"
            )
        
        self.client = OpenAI(api_key=api_key)
        self.temp_dir = Path('temp')
        self.temp_dir.mkdir(exist_ok=True)
    
    def generate_image(self, product: Dict, brief: Dict, output_dir: Path = None) -> Path:
        """
        Generate product image using DALL-E 3.
        
        Args:
            product: Product information
            brief: Campaign brief
            output_dir: Optional directory to save the image. If None, saves to temp/
            
        Returns:
            Path to generated image
        """
        product_id = product['product_id']
        
        self.logger.info(f"Generating image for {product['name']}")
        
        # Build prompt
        prompt = self._build_prompt(product, brief)
        self.logger.debug(f"Prompt: {prompt}")
        
        try:
            # Call DALL-E 3
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                quality="standard",
                size="1024x1024"
            )
            
            # Download image
            image_url = response.data[0].url
            image_data = requests.get(image_url).content
            
            # Determine output directory
            if output_dir is None:
                save_dir = self.temp_dir
            else:
                save_dir = Path(output_dir)
                save_dir.mkdir(parents=True, exist_ok=True)
            
            # Save to output directory
            output_path = save_dir / f"{product_id}_generated.png"
            output_path.write_bytes(image_data)
            
            # Validate image - check for color bars and regenerate if found
            max_retries = 3
            retry_count = 0  # number of additional regenerations due to color bars
            while retry_count < max_retries:
                if self._has_color_bars(output_path):
                    self.logger.warning(f"Color bars detected in generated image (attempt {retry_count + 1}/{max_retries})")
                    if retry_count < max_retries - 1:
                        # Regenerate with stronger prompt
                        self.logger.info("Regenerating image with enhanced prompt to avoid color bars...")
                        response = self.client.images.generate(
                            model="dall-e-3",
                            prompt=self._build_prompt(product, brief, enhanced=True),
                            n=1,
                            quality="standard",
                            size="1024x1024"
                        )
                        image_url = response.data[0].url
                        image_data = requests.get(image_url).content
                        output_path.write_bytes(image_data)
                        retry_count += 1
                    else:
                        self.logger.error("Color bars still present after retries - using image anyway")
                        break
                else:
                    break
            
            total_generations = 1 + retry_count
            if total_generations > 1:
                self.logger.info(
                    f"Image generated successfully after {total_generations} calls to DALL-E for product {product_id}"
                )
            else:
                self.logger.info(
                    f"Image generated successfully on first DALL-E call for product {product_id}"
                )
            self.logger.info(f"Final image path: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Image generation failed: {str(e)}")
            raise
    
    def _has_color_bars(self, image_path: Path) -> bool:
        """
        Detect color bars in generated images.
        
        Color bars typically appear as:
        - Horizontal or vertical strips of solid colors
        - Usually at edges (top, bottom, sides)
        - High color uniformity in rectangular regions
        
        Returns True if color bars are detected.
        """
        try:
            img = Image.open(image_path)
            img_array = np.array(img.convert('RGB'))
            height, width = img_array.shape[:2]
            
            # Check edges for color bars (top, bottom, left, right)
            edge_thickness = min(50, height // 10, width // 10)  # Check 10% of image or 50px, whichever is smaller
            
            # Check top edge
            top_region = img_array[:edge_thickness, :]
            if self._is_color_bar_region(top_region):
                self.logger.debug("Color bar detected at top edge")
                return True
            
            # Check bottom edge
            bottom_region = img_array[-edge_thickness:, :]
            if self._is_color_bar_region(bottom_region):
                self.logger.debug("Color bar detected at bottom edge")
                return True
            
            # Check left edge
            left_region = img_array[:, :edge_thickness]
            if self._is_color_bar_region(left_region):
                self.logger.debug("Color bar detected at left edge")
                return True
            
            # Check right edge
            right_region = img_array[:, -edge_thickness:]
            if self._is_color_bar_region(right_region):
                self.logger.debug("Color bar detected at right edge")
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Error detecting color bars: {e}")
            # If we can't detect, assume no color bars (better to use image than reject)
            return False
    
    def _is_color_bar_region(self, region: np.ndarray) -> bool:
        """
        Check if a region is a color bar (high color uniformity).
        
        Color bars have:
        - Low color variance (solid colors)
        - Distinct color segments (multiple solid color blocks)
        """
        if region.size == 0:
            return False
        
        # Reshape to 2D array of pixels
        pixels = region.reshape(-1, 3)
        
        # Calculate color variance - color bars have low variance (solid colors)
        color_variance = np.var(pixels, axis=0).mean()
        
        # Color bars typically have very low variance (< 100)
        # But we also need to check for multiple distinct color segments
        if color_variance < 100:
            # Check for multiple distinct color segments (typical of color bars)
            # Sample pixels at regular intervals
            step = max(1, len(pixels) // 20)  # Sample ~20 pixels
            sampled = pixels[::step]
            
            # Count distinct colors (colors that differ significantly)
            distinct_colors = []
            for pixel in sampled:
                is_distinct = True
                for existing in distinct_colors:
                    # If colors are similar (within 30 RGB units), they're the same
                    if np.linalg.norm(pixel - existing) < 30:
                        is_distinct = False
                        break
                if is_distinct:
                    distinct_colors.append(pixel)
                    if len(distinct_colors) >= 3:  # Color bars typically have 3+ distinct colors
                        return True
        
        return False
    
    def _build_prompt(self, product: Dict, brief: Dict, enhanced: bool = False) -> str:
        """Build DALL-E prompt from product and campaign brief."""
        prompt_parts = [
            f"Professional product photography of {product['name']}.",
            f"{product.get('description', '')}.",
            f"Shot in a lifestyle context that appeals to {brief.get('target_audience', 'general audience')}.",
        ]
        
        # Add brand colors
        brand_colors = brief.get('brand_guidelines', {}).get('brand_colors', [])
        if brand_colors:
            colors_str = ', '.join(brand_colors)
            prompt_parts.append(f"Use these brand colors as accents: {colors_str}.")
        
        # Add style guidelines
        prompt_parts.extend([
            "Clean, modern aesthetic with excellent lighting.",
            "High-quality commercial photography style.",
            "Product should be the hero of the image, clearly visible and appealing.",
        ])
        
        # Add campaign tagline context
        campaign_tagline = brief.get('campaign_tagline', '')
        if campaign_tagline:
            prompt_parts.append(
                f"Suitable for social media advertising with emotional appeal that conveys: {campaign_tagline}."
            )
        
        # CRITICAL: Avoid color bars and overlays
        if enhanced:
            prompt_parts.extend([
                "Photography should be clean, professional, and suitable for a global consumer brand.",
                "No text or watermarks in the image.",
                "CRITICAL: DO NOT include any color swatches, color bars, color strips, or color palettes in the image.",
                "CRITICAL: DO NOT add any colored rectangles, strips, or bars at the edges or anywhere in the image.",
                "Natural product photography only - absolutely no graphic design elements, overlays, or color calibration bars.",
                "The image must be pure product photography with no decorative elements, color samples, or design overlays.",
            ])
        else:
            prompt_parts.extend([
                "Photography should be clean, professional, and suitable for a global consumer brand.",
                "No text or watermarks in the image.",
                "DO NOT include color swatches, color bars, or brand color strips in the image.",
                "Natural product photography only - no graphic design elements or overlays.",
            ])
        
        return '\n'.join(prompt_parts)


if __name__ == '__main__':
    # Simple test
    generator = ImageGenerator()
    
    test_product = {
        'product_id': 'test_product',
        'name': 'Test Product',
        'description': 'A beautiful test product'
    }
    
    test_brief = {
        'target_audience': 'test users',
        'campaign_tagline': 'Test tagline',
        'brand_guidelines': {
            'brand_colors': ['#FF6B35', '#004E89']
        }
    }
    
    print("Testing image generation...")
    result = generator.generate_image(test_product, test_brief)
    print(f"✅ Image generated: {result}")

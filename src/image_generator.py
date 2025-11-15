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
    
    def generate_image(self, product: Dict, brief: Dict) -> Path:
        """
        Generate product image using DALL-E 3.
        
        Args:
            product: Product information
            brief: Campaign brief
            
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
            
            # Save to temp directory
            output_path = self.temp_dir / f"{product_id}_generated.png"
            output_path.write_bytes(image_data)
            
            self.logger.info(f"Image generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Image generation failed: {str(e)}")
            raise
    
    def _build_prompt(self, product: Dict, brief: Dict) -> str:
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
        
        # Add campaign message context
        campaign_message = brief.get('campaign_message', '')
        if campaign_message:
            prompt_parts.append(
                f"Suitable for social media advertising with emotional appeal that conveys: {campaign_message}."
            )
        
        # CRITICAL: Avoid color bars and overlays
        prompt_parts.extend([
            "Photography should be clean, professional, and suitable for a global consumer brand.",
            "No text or watermarks in the image.",
            "DO NOT include color swatches, color bars, or brand color strips in the image.",
            "Natural product photography only - no graphic design elements or overlays."
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
        'campaign_message': 'Test message',
        'brand_guidelines': {
            'brand_colors': ['#FF6B35', '#004E89']
        }
    }
    
    print("Testing image generation...")
    result = generator.generate_image(test_product, test_brief)
    print(f"✅ Image generated: {result}")

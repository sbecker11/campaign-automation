"""
Asset Processor

Handles image processing including aspect ratio conversion and text overlay.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Tuple, List, Optional
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from dotenv import load_dotenv


load_dotenv()

# Minimum logo width (as a fraction of image width) for tall 9:16 assets.
# Configurable via .env: LOGO_WIDTH_RATIO_9_16=0.33
try:
    LOGO_WIDTH_RATIO_9_16 = float(os.getenv("LOGO_WIDTH_RATIO_9_16", "0.33"))
except ValueError:
    LOGO_WIDTH_RATIO_9_16 = 0.33


class AssetProcessor:
    """Process and transform campaign assets."""
    
    ASPECT_RATIOS = {
        '1:1': (1080, 1080),
        '9:16': (1080, 1920),
        '16:9': (1920, 1080),
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._logo_cache = {}  # Cache logo validation results
    
    def _validate_logo_file(self, logo_path: str) -> bool:
        """
        Validate that logo file exists and is usable.
        
        Returns True if logo is valid, False otherwise.
        Caches result to avoid repeated validation.
        """
        # Check cache first
        if logo_path in self._logo_cache:
            return self._logo_cache[logo_path]
        
        path = Path(logo_path)
        
        # Check if file exists
        if not path.exists():
            self.logger.warning(f"Logo file not found: {logo_path}")
            self._logo_cache[logo_path] = False
            return False
        
        # Try to open and validate the image
        try:
            logo = Image.open(path)
            logo.verify()  # Verify it's not corrupted
            
            # Re-open after verify (verify closes the file)
            logo = Image.open(path)
            
            # Check mode is supported
            if logo.mode not in ['RGB', 'RGBA', 'L']:
                self.logger.warning(f"Logo has unsupported mode: {logo.mode}")
                self._logo_cache[logo_path] = False
                return False
            
            # Check dimensions are reasonable
            width, height = logo.size
            if width < 10 or height < 10:
                self.logger.warning(f"Logo too small: {width}×{height}px")
                self._logo_cache[logo_path] = False
                return False
            
            # Logo is valid
            self.logger.info(f"Logo validated: {width}×{height}px, mode: {logo.mode}")
            self._logo_cache[logo_path] = True
            return True
            
        except Exception as e:
            self.logger.warning(f"Logo file is invalid or corrupted: {e}")
            self._logo_cache[logo_path] = False
            return False
    
    def create_variant(self, base_image_path: Path, product: Dict, 
                      brief: Dict, aspect_ratio: str, output_dir: Path) -> Path:
        """Create a variant of the image for specified aspect ratio with text overlay."""
        image = Image.open(base_image_path)
        image = self._resize_to_aspect_ratio(image, aspect_ratio)
        image = self._add_text_overlay(image, brief, aspect_ratio)
        
        # Add logo only if required AND valid
        if brief.get('brand_guidelines', {}).get('logo_required'):
            logo_path = brief['brand_guidelines'].get('logo_path')
            
            if logo_path:
                # Validate logo before attempting to add it
                if self._validate_logo_file(logo_path):
                    self.logger.info(f"Adding logo from {logo_path} to {aspect_ratio} variant")
                    image = self._add_logo(image, logo_path, aspect_ratio)
                    self.logger.info(f"Logo added successfully to {aspect_ratio} variant")
                else:
                    self.logger.warning(f"Skipping logo for {product['product_id']} - logo file invalid")
            else:
                self.logger.warning(f"logo_required=True but no logo_path specified")
        
        ratio_dir = output_dir / aspect_ratio.replace(':', 'x')
        ratio_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = ratio_dir / f"{product['product_id']}_{aspect_ratio.replace(':', 'x')}.png"
        image.save(output_path, quality=95, optimize=True)
        
        self.logger.info(f"Created variant: {output_path}")
        return output_path
    
    def _resize_to_aspect_ratio(self, image: Image.Image, aspect_ratio: str) -> Image.Image:
        """Resize and crop image to target aspect ratio."""
        if aspect_ratio not in self.ASPECT_RATIOS:
            raise ValueError(f"Unsupported aspect ratio: {aspect_ratio}")
        
        target_size = self.ASPECT_RATIOS[aspect_ratio]
        target_width, target_height = target_size
        target_aspect = target_width / target_height
        
        current_width, current_height = image.size
        current_aspect = current_width / current_height
        
        if current_aspect > target_aspect:
            new_width = int(current_height * target_aspect)
            left = (current_width - new_width) // 2
            image = image.crop((left, 0, left + new_width, current_height))
        elif current_aspect < target_aspect:
            new_height = int(current_width / target_aspect)
            top = (current_height - new_height) // 2
            image = image.crop((0, top, current_width, top + new_height))
        
        image = image.resize(target_size, Image.Resampling.LANCZOS)
        return image
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []
        
        temp_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = temp_draw.textbbox((0, 0), test_line, font=font)
            test_width = bbox[2] - bbox[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _add_text_overlay(self, image: Image.Image, brief: Dict, aspect_ratio: str) -> Image.Image:
        """Add campaign message as text overlay with proper text wrapping."""
        message = brief.get('campaign_message', '')
        
        if not message:
            return image
        
        width, height = image.size
        
        try:
            font_size = int(height * 0.05)
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            font = ImageFont.load_default()
        
        margin = 40
        max_text_width = width - (2 * margin)
        
        lines = self._wrap_text(message, font, max_text_width)
        
        temp_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        line_height = temp_draw.textbbox((0, 0), "Ay", font=font)[3] - temp_draw.textbbox((0, 0), "Ay", font=font)[1]
        line_spacing = int(line_height * 0.3)
        total_text_height = len(lines) * line_height + (len(lines) - 1) * line_spacing
        
        max_line_width = 0
        for line in lines:
            bbox = temp_draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            max_line_width = max(max_line_width, line_width)
        
        if aspect_ratio == '9:16':
            text_y = int(height * 0.78)
        else:
            text_y = int(height * 0.75)
        
        if text_y + total_text_height + margin > height:
            text_y = height - total_text_height - margin - 20
        
        if text_y < margin:
            text_y = margin
        
        padding = 25
        bg_left = max(margin, (width - max_line_width) // 2 - padding)
        bg_top = max(margin, text_y - padding)
        bg_right = min(width - margin, (width + max_line_width) // 2 + padding)
        bg_bottom = min(height - margin, text_y + total_text_height + padding)
        
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        overlay_draw.rectangle(
            [bg_left, bg_top, bg_right, bg_bottom],
            fill=(0, 0, 0, 180)
        )
        
        image = image.convert('RGBA')
        image = Image.alpha_composite(image, overlay)
        
        draw = ImageDraw.Draw(image)
        current_y = text_y
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            text_x = (width - line_width) // 2
            text_x = max(margin, min(text_x, width - line_width - margin))
            
            draw.text((text_x, current_y), line, font=font, fill=(255, 255, 255, 255))
            current_y += line_height + line_spacing
        
        image = image.convert('RGB')
        
        return image
    
    def _logo_has_text(self, logo: Image.Image) -> bool:
        """
        Detect if logo contains text by checking for high contrast edges.
        
        Text-heavy logos typically have many sharp edges and high contrast.
        Returns True if logo appears to contain text.
        """
        try:
            # Convert to grayscale for edge detection
            if logo.mode != 'L':
                gray = logo.convert('L')
            else:
                gray = logo
            
            # Resize to reasonable size for analysis (faster processing)
            analysis_size = (200, 200)
            if gray.size != analysis_size:
                gray = gray.resize(analysis_size, Image.Resampling.LANCZOS)
            
            # Convert to numpy array
            img_array = np.array(gray)
            
            # Calculate edge density using simple gradient
            # Text has many horizontal and vertical edges
            horizontal_edges = np.abs(np.diff(img_array, axis=1))
            vertical_edges = np.abs(np.diff(img_array, axis=0))
            
            # High edge density indicates text
            edge_density = (np.mean(horizontal_edges) + np.mean(vertical_edges)) / 2
            
            # Calculate contrast (text has high contrast)
            contrast = np.std(img_array)
            
            # Text logos typically have:
            # - Edge density > 15 (many edges)
            # - Contrast > 40 (high contrast between text and background)
            has_text = edge_density > 15 and contrast > 40
            
            if has_text:
                self.logger.debug(f"Logo appears to contain text (edge_density={edge_density:.1f}, contrast={contrast:.1f})")
            
            return has_text
            
        except Exception as e:
            self.logger.warning(f"Error detecting text in logo: {e}")
            # Default to True to be safe (assume text might be present)
            return True
    
    def _get_dominant_color(self, image: Image.Image) -> Tuple[int, int, int]:
        """Extract the dominant color from an image region."""
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to small size for faster processing
        image = image.resize((50, 50), Image.Resampling.LANCZOS)
        
        # Get pixel data
        pixels = np.array(image)
        pixels = pixels.reshape(-1, 3)
        
        # Calculate mean color (simple but effective)
        mean_color = np.mean(pixels, axis=0)
        
        return tuple(map(int, mean_color))
    
    def _color_similarity(self, color1: Tuple[int, int, int], 
                         color2: Tuple[int, int, int]) -> float:
        """
        Calculate color similarity between two RGB colors.
        
        Returns a value between 0 and 1, where 1 is identical.
        """
        # Euclidean distance in RGB space
        distance = np.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(color1, color2)))
        
        # Maximum possible distance in RGB space
        max_distance = np.sqrt(3 * 255 ** 2)
        
        # Convert to similarity (1 = identical, 0 = maximally different)
        similarity = 1 - (distance / max_distance)
        
        return similarity
    
    def _logo_needs_background(self, image: Image.Image, logo: Image.Image,
                               position: Tuple[int, int]) -> bool:
        """
        Determine if logo needs a background by checking color similarity.
        
        Args:
            image: The base image
            logo: The logo to place
            position: (x, y) position where logo will be placed
            
        Returns:
            True if logo needs background, False otherwise
        """
        try:
            # Get the region where logo will be placed
            x, y = position
            logo_width, logo_height = logo.size
            
            # Ensure we don't go out of bounds
            x2 = min(x + logo_width, image.size[0])
            y2 = min(y + logo_height, image.size[1])
            
            if x2 <= x or y2 <= y:
                return False
            
            # Crop the background region
            background_region = image.crop((x, y, x2, y2))
            
            # Get dominant color of background region
            bg_color = self._get_dominant_color(background_region)
            
            # Get dominant color of logo (ignoring transparency)
            logo_rgb = logo.convert('RGB')
            logo_color = self._get_dominant_color(logo_rgb)
            
            # Calculate similarity
            similarity = self._color_similarity(bg_color, logo_color)
            
            # If colors are very similar (>70% similar), add background
            # This ensures logo is visible when it blends into the background
            needs_background = similarity > 0.70
            
            if needs_background:
                self.logger.info(
                    f"Logo color matches background (similarity={similarity:.2f}) - adding semi-transparent black background"
                )
            
            return needs_background
            
        except Exception as e:
            self.logger.warning(f"Error checking logo background need: {e}")
            # Default to adding background if we can't determine
            return True
    
    def _add_logo(self, image: Image.Image, logo_path: str, aspect_ratio: str) -> Image.Image:
        """
        Add brand logo to image corner with optional background.
        
        Automatically adds a semi-transparent background if the logo colors
        are similar to the background image colors.
        
        Note: This method assumes logo has already been validated by _validate_logo_file().
        """
        try:
            logo = Image.open(logo_path)
            width, height = image.size
            max_logo_width = int(width * 0.12)
            
            logo_aspect = logo.width / logo.height
            logo_width = max_logo_width
            
            # For tall 9:16 assets, ensure logo is not shrunk below a minimum
            # so that it remains visually prominent (e.g., social stories).
            if aspect_ratio == '9:16':
                min_logo_width = int(width * LOGO_WIDTH_RATIO_9_16)  # configured fraction of width
                if logo_width < min_logo_width:
                    logo_width = min_logo_width
                    self.logger.info(
                        f"Increased logo base width for 9:16 from {max_logo_width}px to {logo_width}px "
                        f"to keep it visible on tall assets"
                    )
            logo_height = int(logo_width / logo_aspect)
            
            # Check if logo contains text that would be too small
            # If logo is text-heavy and would be resized too small, increase size
            if self._logo_has_text(logo):
                # For text logos, ensure minimum readable size
                min_text_width = 150  # Minimum width for readable text
                
                # For wide logos (aspect ratio > 2), they might need even more width
                if logo_aspect > 2.0:
                    min_text_width = max(200, int(width * 0.20))  # Up to 20% for wide text logos
                elif logo_width < min_text_width:
                    min_text_width = max(150, int(width * 0.18))  # Up to 18% for normal text logos
                
                if logo_width < min_text_width:
                    logo_width = min_text_width
                    logo_height = int(logo_width / logo_aspect)
                    self.logger.info(f"Increased logo size to {logo_width}x{logo_height} to maintain text readability (aspect: {logo_aspect:.2f})")
            
            logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
            
            padding = 20
            position = (width - logo_width - padding, padding)
            
            # Check if logo needs background (if logo color matches background color)
            if self._logo_needs_background(image, logo, position):
                # Add semi-transparent black rectangle behind logo for better visibility
                image = image.convert('RGBA')
                
                # Create overlay for background
                overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                
                # Add some padding around logo
                bg_padding = 10
                bg_left = position[0] - bg_padding
                bg_top = position[1] - bg_padding
                bg_right = position[0] + logo_width + bg_padding
                bg_bottom = position[1] + logo_height + bg_padding
                
                # Draw semi-transparent black rectangle
                overlay_draw.rectangle(
                    [bg_left, bg_top, bg_right, bg_bottom],
                    fill=(0, 0, 0, 160)  # Semi-transparent black (alpha=160/255)
                )
                
                # Composite the background
                image = Image.alpha_composite(image, overlay)
                
                self.logger.info("Added semi-transparent black background behind logo (logo color matches background)")
            
            # Convert to RGBA for pasting logo
            image = image.convert('RGBA')
            
            # Paste logo
            if logo.mode == 'RGBA':
                image.paste(logo, position, logo)
            else:
                logo_rgba = logo.convert('RGBA')
                image.paste(logo_rgba, position, logo_rgba)
            
            # Convert back to RGB
            image = image.convert('RGB')
            
            self.logger.info(f"Logo pasted at position {position}, size: {logo_width}x{logo_height}")
            
        except Exception as e:
            self.logger.error(f"Failed to add logo: {e}", exc_info=True)
        
        return image

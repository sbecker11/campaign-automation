"""
Brand Validator

Computer vision-based brand compliance checking.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple
import cv2
import numpy as np
from PIL import Image


class BrandValidator:
    """Validate brand compliance using computer vision."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate(self, image_path: Path, brief: Dict) -> Dict:
        """Perform comprehensive brand validation."""
        results = {
            'image_path': str(image_path),
            'overall_compliant': True,
            'checks': {}
        }
        
        brand_guidelines = brief.get('brand_guidelines', {})
        
        if brand_guidelines.get('logo_required'):
            logo_path = brand_guidelines.get('logo_path')
            if logo_path and Path(logo_path).exists():
                logo_result = self._detect_logo(image_path, logo_path)
                results['checks']['logo_detection'] = logo_result
                if not logo_result['detected']:
                    results['overall_compliant'] = False
        
        brand_colors = brand_guidelines.get('brand_colors', [])
        if brand_colors:
            color_result = self._validate_colors(image_path, brand_colors)
            results['checks']['color_validation'] = color_result
        
        quality_result = self._assess_quality(image_path)
        results['checks']['image_quality'] = quality_result
        
        status = '✓ PASS' if results['overall_compliant'] else '✗ FAIL'
        self.logger.info(f"Validation complete: {status}")
        
        return results
    
    def _detect_logo(self, image_path: Path, logo_path: str) -> Dict:
        """Detect logo using template matching."""
        image = cv2.imread(str(image_path))
        logo = cv2.imread(logo_path)
        
        if image is None or logo is None:
            return {'detected': False, 'confidence': 0.0, 'error': 'Failed to load images'}
        
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_logo = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)
        
        scales = [0.5, 0.75, 1.0, 1.25, 1.5]
        best_match = 0.0
        
        for scale in scales:
            width = int(gray_logo.shape[1] * scale)
            height = int(gray_logo.shape[0] * scale)
            
            if width > gray_image.shape[1] or height > gray_image.shape[0]:
                continue
            
            resized_logo = cv2.resize(gray_logo, (width, height))
            result = cv2.matchTemplate(gray_image, resized_logo, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            if max_val > best_match:
                best_match = max_val
        
        threshold = 0.6
        detected = best_match >= threshold
        
        return {
            'detected': detected,
            'confidence': float(best_match),
            'threshold': threshold
        }
    
    def _validate_colors(self, image_path: Path, brand_colors: List[str]) -> Dict:
        """Validate presence of brand colors."""
        image = Image.open(image_path).convert('RGB')
        image.thumbnail((300, 300))
        
        pixels = np.array(image).reshape(-1, 3)
        dominant_colors = self._extract_dominant_colors(pixels, n_colors=5)
        brand_rgb = [self._hex_to_rgb(c) for c in brand_colors]
        
        matches = []
        for brand_color in brand_rgb:
            for dom_color in dominant_colors:
                similarity = self._color_similarity(brand_color, dom_color)
                if similarity > 0.85:
                    matches.append({'brand_color': brand_color, 'similarity': similarity})
                    break
        
        return {
            'colors_present': len(matches) > 0,
            'matches_found': len(matches)
        }
    
    def _assess_quality(self, image_path: Path) -> Dict:
        """Assess image quality."""
        image = cv2.imread(str(image_path))
        if image is None:
            return {'quality_score': 0.0}
        
        height, width = image.shape[:2]
        resolution_score = min(1.0, (width * height) / (1920 * 1080))
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(1.0, laplacian_var / 500)
        
        quality_score = (resolution_score * 0.5 + sharpness_score * 0.5)
        
        return {'quality_score': float(quality_score)}
    
    def _extract_dominant_colors(self, pixels: np.ndarray, n_colors: int = 5) -> List[Tuple]:
        """Extract dominant colors."""
        reduced = (pixels // 32) * 32
        unique, counts = np.unique(reduced, axis=0, return_counts=True)
        sorted_indices = np.argsort(counts)[::-1]
        dominant = unique[sorted_indices[:n_colors]]
        return [tuple(map(int, color)) for color in dominant]
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex to RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _color_similarity(self, color1: Tuple, color2: Tuple) -> float:
        """Calculate color similarity."""
        distance = np.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(color1, color2)))
        max_distance = np.sqrt(3 * 255 ** 2)
        return 1 - (distance / max_distance)

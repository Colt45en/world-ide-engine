"""Aesthetic Pathway: The Soul of form. Golden Ratio color harmonies and mood detection."""
import numpy as np
from dataclasses import dataclass
from typing import Tuple

@dataclass
class PaletteResult:
    primary_color: Tuple[float, float, float]
    secondary_color: Tuple[float, float, float]
    accent_color: Tuple[float, float, float]
    mood: str
    score: float
    lighting_profile: str

@dataclass
class AestheticEvaluation:
    beauty_score: float
    mood: str
    palette: PaletteResult
    harmonies: dict

class AestheticPathway:
    """AI Art Director: analyzes geometry and generates optimal aesthetics."""
    
    PHI = 1.61803398875  # Golden Ratio
    GOLDEN_ANGLE = 137.5  # degrees
    
    def __init__(self):
        self.color_space = 'hsl'
    
    def evaluate(self, geometry_stats) -> AestheticEvaluation:
        """Main evaluation: form → mood → color → score."""
        # 1. Determine mood from geometry entropy
        mood = 'energetic' if geometry_stats.entropy > 0.5 else 'calm'
        
        # 2. Generate color palette from mood
        palette = self.generate_harmonic_palette(mood)
        
        # 3. Calculate aesthetic score from aspect ratios
        score = self._calculate_aesthetic_score(geometry_stats.aspect_ratio)
        
        # 4. Generate color harmonies (triadic, complementary, etc)
        harmonies = self._generate_harmonies(palette.primary_color)
        
        return AestheticEvaluation(
            beauty_score=score,
            mood=mood,
            palette=palette,
            harmonies=harmonies
        )
    
    def generate_harmonic_palette(self, mood: str) -> PaletteResult:
        """Use Golden Angle to space colors harmonically."""
        # Base hue depends on mood
        if mood == 'energetic':
            base_hue = np.random.random() * 0.15  # Warm: red/orange range
            saturation = 0.8
            lightness = 0.5
        else:
            base_hue = 0.5 + (np.random.random() * 0.2)  # Cool: blue/teal range
            saturation = 0.6
            lightness = 0.7
        
        # Primary color
        primary_hue = base_hue
        primary = self._hsl_to_rgb(primary_hue, saturation, lightness)
        
        # Secondary via Golden Ratio (phi = 0.618...)
        secondary_hue = (base_hue + self.PHI) % 1.0
        secondary = self._hsl_to_rgb(secondary_hue, saturation * 0.8, lightness + 0.1)
        
        # Accent: complementary
        accent_hue = (base_hue + 0.5) % 1.0
        accent = self._hsl_to_rgb(accent_hue, saturation, lightness - 0.1)
        
        lighting = 'high_contrast' if mood == 'energetic' else 'soft_box'
        
        return PaletteResult(
            primary_color=primary,
            secondary_color=secondary,
            accent_color=accent,
            mood=mood,
            score=0.0,
            lighting_profile=lighting
        )
    
    def _calculate_aesthetic_score(self, aspect_ratio: Tuple[float, float, float]) -> float:
        """Score geometry based on proximity to Golden Ratio proportions."""
        ratio = aspect_ratio[1] / (aspect_ratio[0] + 1e-8)  # height/width
        target_ratio = self.PHI
        
        # Perfect score at Golden Ratio, degrades as distance increases
        distance = abs(ratio - target_ratio)
        score = 1.0 - min(distance / target_ratio, 1.0)
        return float(np.clip(score, 0.0, 1.0))
    
    def _hsl_to_rgb(self, h: float, s: float, l: float) -> Tuple[float, float, float]:
        """Convert HSL to RGB."""
        a = s * min(l, 1 - l)
        def f(n):
            k = (n + h * 12) % 12
            return l - a * max(min(k - 3, 9 - k, 1), -1)
        return (f(0), f(8), f(4))
    
    def _generate_harmonies(self, primary: Tuple[float, float, float]) -> dict:
        """Generate color harmony schemes."""
        h, s, l = self._rgb_to_hsl(primary)
        
        complementary = self._hsl_to_rgb((h + 0.5) % 1.0, s, l)
        triadic_1 = self._hsl_to_rgb((h + 1/3) % 1.0, s, l)
        triadic_2 = self._hsl_to_rgb((h + 2/3) % 1.0, s, l)
        analogous_1 = self._hsl_to_rgb((h + 0.083) % 1.0, s, l)
        analogous_2 = self._hsl_to_rgb((h - 0.083) % 1.0, s, l)
        
        return {
            'complementary': complementary,
            'triadic': [primary, triadic_1, triadic_2],
            'analogous': [analogous_2, primary, analogous_1],
            'monochromatic': [
                self._hsl_to_rgb(h, s, l * 0.5),
                primary,
                self._hsl_to_rgb(h, s, l * 1.5)
            ]
        }
    
    def _rgb_to_hsl(self, rgb: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Convert RGB to HSL."""
        r, g, b = rgb
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        l = (max_c + min_c) / 2
        
        if max_c == min_c:
            h = s = 0
        else:
            d = max_c - min_c
            s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
            if max_c == r:
                h = ((g - b) / d + (6 if g < b else 0)) / 6
            elif max_c == g:
                h = ((b - r) / d + 2) / 6
            else:
                h = ((r - g) / d + 4) / 6
        
        return (h % 1.0, s, l)

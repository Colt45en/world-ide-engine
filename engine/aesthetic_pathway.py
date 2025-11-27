# engine/aesthetic_pathway.py
import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass
class AestheticEvaluation:
    """Result of mesh aesthetic analysis."""
    score: float  # 0.0-1.0, higher = more aesthetically pleasing
    mood: str  # 'energetic' or 'calm'
    optimalColor: int  # hex color (0xRRGGBB)
    secondaryColor: int
    lightingProfile: str  # 'high_contrast' or 'soft_box'
    geometry_stats: Dict

class AestheticPathway:
    """The Soul: Analyzes geometry and generates harmonic color schemes.
    
    Uses Golden Ratio (PHI ≈ 1.618) to create mathematically pleasing palettes.
    Geometry entropy determines mood (jagged → energetic, smooth → calm).
    """
    
    def __init__(self):
        self.PHI = 1.61803398875
    
    def evaluate(self, mesh: Dict) -> AestheticEvaluation:
        """Analyze mesh and return optimal aesthetics."""
        # 1. Analyze form
        geom_stats = self._analyzeGeometry(mesh)
        
        # 2. Determine mood from entropy
        mood = 'energetic' if geom_stats['entropy'] > 0.5 else 'calm'
        
        # 3. Generate harmonic palette
        palette = self._generateHarmonicPalette(mood)
        
        # 4. Calculate aesthetic score (0.0-1.0)
        # Prefer meshes with dimensions close to PHI ratio
        ratio = geom_stats['height'] / (geom_stats['width'] + 1e-8)
        score = 1.0 - min(abs(ratio - self.PHI), 1.0)
        
        return AestheticEvaluation(
            score=score,
            mood=mood,
            optimalColor=palette['primary'],
            secondaryColor=palette['secondary'],
            lightingProfile='high_contrast' if mood == 'energetic' else 'soft_box',
            geometry_stats=geom_stats
        )
    
    def _analyzeGeometry(self, mesh: Dict) -> Dict:
        """Compute form statistics: bounds, entropy (jaggedness)."""
        positions = mesh['geometry']['attributes']['position']['array']
        
        minX = minY = minZ = np.inf
        maxX = maxY = maxZ = -np.inf
        totalVariance = 0.0
        
        # Scan for bounds and variance
        for i in range(0, len(positions), 3):
            x = positions[i]
            y = positions[i + 1] if i + 1 < len(positions) else 0
            z = positions[i + 2] if i + 2 < len(positions) else 0
            
            minX = min(minX, x)
            maxX = max(maxX, x)
            minY = min(minY, y)
            maxY = max(maxY, y)
            minZ = min(minZ, z)
            maxZ = max(maxZ, z)
            
            # Variance: difference from previous vertex
            if i > 2:
                prevY = positions[i - 2]
                totalVariance += abs(y - prevY)
        
        height = maxY - minY
        width = maxX - minX
        depth = maxZ - minZ
        
        # Normalized entropy score
        entropy = min(totalVariance / (len(positions) + 1e-8), 1.0)
        
        return {
            'width': width,
            'height': height,
            'depth': depth,
            'entropy': entropy,
            'volume': width * height * depth
        }
    
    def _generateHarmonicPalette(self, mood: str) -> Dict[str, int]:
        """Golden Angle algorithm: space colors harmonically via PHI.
        
        The golden angle is ~137.5 degrees, ensuring distinct but harmonious colors.
        """
        # Base hue depends on mood
        if mood == 'energetic':
            baseHue = np.random.rand() * 0.15  # Warm: red/orange zone
        else:
            baseHue = 0.5 + np.random.rand() * 0.2  # Cool: blue/teal zone
        
        # Complementary hues via PHI shift
        primaryHue = baseHue
        secondaryHue = (baseHue + 0.61803398875) % 1.0  # Shift by golden ratio
        
        return {
            'primary': self._HSLtoHex(primaryHue, 0.8, 0.5),
            'secondary': self._HSLtoHex(secondaryHue, 0.6, 0.7)
        }
    
    def _HSLtoHex(self, h: float, s: float, l: float) -> int:
        """Convert HSL to hex color (0xRRGGBB)."""
        a = s * min(l, 1 - l)
        
        def f(n):
            k = (n + h * 12) % 12
            color = l - a * max(min(k - 3, 9 - k, 1), -1)
            return max(0, min(255, round(255 * color)))
        
        r = f(0)
        g = f(8)
        b = f(4)
        
        return (r << 16) | (g << 8) | b
    
    def hexToRGB(self, hexColor: int) -> Tuple[int, int, int]:
        """Reverse: hex to RGB tuple."""
        r = (hexColor >> 16) & 0xFF
        g = (hexColor >> 8) & 0xFF
        b = hexColor & 0xFF
        return (r, g, b)
    
    def hexToCSS(self, hexColor: int) -> str:
        """Format hex as CSS string #RRGGBB."""
        return f"#{hexColor:06X}"

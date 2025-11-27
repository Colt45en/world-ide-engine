"""
morphing/materials/material_model.py

Material science models for isotropic swelling and UV-driven morphing.

Core model: realized metric = g²(x,y) * I
  where g(x,y) ∈ [g_min, g_max] is the programmable growth field.

Calibration: UV dose (0-255) maps to growth g via experimental curve.
"""

import numpy as np
from typing import Callable, Tuple, Optional
from dataclasses import dataclass
import json


@dataclass
class CalibrationCurve:
    """UV dose to growth field mapping."""
    uv_levels: np.ndarray  # (0, 1, ..., 255) dose values
    growth_values: np.ndarray  # corresponding g values
    
    def dose_to_growth(self, dose: np.ndarray) -> np.ndarray:
        """Interpolate growth from UV dose."""
        return np.interp(dose, self.uv_levels, self.growth_values)
    
    def growth_to_dose(self, growth: np.ndarray) -> np.ndarray:
        """Inverse: growth to dose (for fabrication)."""
        return np.interp(growth, self.growth_values, self.uv_levels)


class IsotropicMaterial:
    """Isotropic swelling material with uniform growth."""
    
    def __init__(self, g_min: float = 0.7, g_max: float = 2.5):
        """
        Args:
            g_min: minimum isotropic growth (no UV)
            g_max: maximum isotropic growth (saturated UV)
        """
        self.g_min = g_min
        self.g_max = g_max
        self.calibration = None
    
    def calibrate_from_experiments(self, doses: np.ndarray, measured_growths: np.ndarray):
        """Fit calibration curve from experimental UV dose → measured growth data.
        
        Args:
            doses: (M,) UV dose levels (0-255 grayscale)
            measured_growths: (M,) corresponding isotropic growth factors g
        """
        # Clip to valid range
        growth_clip = np.clip(measured_growths, self.g_min, self.g_max)
        self.calibration = CalibrationCurve(doses.astype(float), growth_clip)
    
    def default_calibration(self):
        """Simple sigmoidal calibration for demos."""
        doses = np.linspace(0, 255, 256)
        # Sigmoid: g(dose) = g_min + (g_max - g_min) / (1 + exp(-k*(dose - 127)))
        k = 0.025
        growths = self.g_min + (self.g_max - self.g_min) / (1 + np.exp(-k * (doses - 127)))
        self.calibration = CalibrationCurve(doses, growths)
        return self.calibration
    
    def growth_to_grayscale(self, growth_field: np.ndarray) -> np.ndarray:
        """Convert growth field to 8-bit grayscale pattern for UV fabrication.
        
        Returns:
            (N,) uint8 array suitable for printing on transparency or lithography
        """
        if self.calibration is None:
            self.default_calibration()
        
        doses = self.calibration.growth_to_dose(growth_field)
        return np.clip(doses, 0, 255).astype(np.uint8)
    
    def grayscale_to_growth(self, grayscale: np.ndarray) -> np.ndarray:
        """Inverse: grayscale pattern to growth field."""
        if self.calibration is None:
            self.default_calibration()
        
        return self.calibration.dose_to_growth(grayscale.astype(float))


class PatternFabricator:
    """Convert growth field to fabrication formats (PNG, SVG)."""
    
    @staticmethod
    def to_png(growth_field: np.ndarray, nx: int, ny: int, filename: str):
        """Save grayscale growth pattern as PNG for fabrication.
        
        Args:
            growth_field: (N,) or (nx, ny) array of growth values
            nx, ny: dimensions if 1D input
            filename: output PNG path
        """
        if growth_field.ndim == 1:
            pattern = growth_field.reshape(nx, ny)
        else:
            pattern = growth_field
        
        # Normalize to 0-255
        pattern_norm = ((pattern - pattern.min()) / (pattern.max() - pattern.min() + 1e-8) * 255).astype(np.uint8)
        
        # Use PIL if available
        try:
            from PIL import Image
            img = Image.fromarray(pattern_norm, mode='L')
            img.save(filename)
            return True
        except ImportError:
            # Fallback: raw binary
            with open(filename + '.raw', 'wb') as f:
                f.write(pattern_norm.tobytes())
            return False
    
    @staticmethod
    def to_svg(growth_field: np.ndarray, nx: int, ny: int, filename: str, cell_size: float = 1.0):
        """Export as SVG with opacity encoding growth.
        
        Args:
            growth_field: (N,) or (nx, ny) array
            nx, ny: grid dimensions
            filename: output SVG path
            cell_size: size of each cell in SVG units
        """
        if growth_field.ndim == 1:
            pattern = growth_field.reshape(nx, ny)
        else:
            pattern = growth_field
        
        # Normalize to 0-1 for opacity
        opacity = (pattern - pattern.min()) / (pattern.max() - pattern.min() + 1e-8)
        
        svg_header = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{nx * cell_size}" height="{ny * cell_size}" xmlns="http://www.w3.org/2000/svg">
<style>
  .growth-cell {{ fill: black; }}
</style>
'''
        
        svg_content = svg_header
        for i in range(nx):
            for j in range(ny):
                x, y = i * cell_size, j * cell_size
                op = opacity[i, j]
                svg_content += f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" class="growth-cell" opacity="{op}"/>\n'
        
        svg_content += '</svg>'
        
        with open(filename, 'w') as f:
            f.write(svg_content)


class ConstraintProjector:
    """Project growth fields to satisfy material/fabrication constraints."""
    
    @staticmethod
    def clip_bounds(growth_field: np.ndarray, g_min: float, g_max: float) -> np.ndarray:
        """Hard bounds: g_min ≤ g ≤ g_max."""
        return np.clip(growth_field, g_min, g_max)
    
    @staticmethod
    def discrete_quantize(growth_field: np.ndarray, bits: int = 8) -> np.ndarray:
        """Quantize to discrete UV dose levels (e.g., 8-bit: 256 levels)."""
        levels = 2**bits
        quantized = np.round(growth_field * (levels - 1)) / (levels - 1)
        return quantized
    
    @staticmethod
    def smooth_project(growth_field: np.ndarray, radius: int = 2, iterations: int = 3) -> np.ndarray:
        """Smooth growth field via repeated averaging (preserves avg, reduces high-freq)."""
        g = growth_field.copy()
        for _ in range(iterations):
            g_smooth = g.copy()
            for i in range(len(g)):
                neighbors = [j for j in range(max(0, i-radius), min(len(g), i+radius+1))]
                g_smooth[i] = np.mean(g[neighbors])
            g = g_smooth
        return g

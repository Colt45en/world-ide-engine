"""Morphing Geometry Module

Target surface representations for morphing workflows:
- AnalyticSurface: Parametric 3D surfaces
- MeshTarget: Triangle mesh targets
- SurfaceMetric: First fundamental form computation
"""

from morphing.geometry.target import (
    AnalyticSurface,
    MeshTarget,
    SurfaceMetric,
    sample_surface_on_grid
)

__all__ = [
    "AnalyticSurface",
    "MeshTarget", 
    "SurfaceMetric",
    "sample_surface_on_grid"
]

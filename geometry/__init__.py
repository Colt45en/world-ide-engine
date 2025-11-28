"""Geometry Package

Provides geometry processing and mesh generation:
- IntelligentSurfaceNets: Adaptive mesh generation from voxels
- MeshData: Mesh data structure
- GeometryStats: Geometry analysis statistics
"""

from geometry.surface_nets import IntelligentSurfaceNets, MeshData, GeometryStats

__all__ = [
    "IntelligentSurfaceNets",
    "MeshData",
    "GeometryStats"
]

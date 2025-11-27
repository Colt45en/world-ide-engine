"""
morphing/geometry/target.py

Core representations for 3D target surfaces and 2D→3D metric mapping.

This module handles:
  - Analytic surfaces (parametric forms like spheres, saddles)
  - Mesh-based targets (imported STL/OBJ)
  - First fundamental form (metric) computation
  - Parameterization and flattening to 2D domains
"""

import numpy as np
from typing import Callable, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SurfaceMetric:
    """Represents the first fundamental form (metric tensor) at each cell."""
    metric: np.ndarray  # (N, 2, 2) array of metric matrices per cell
    positions: np.ndarray  # (N, 2) array of cell centers in 2D domain
    neighbors: list  # adjacency list for smoothness


class AnalyticSurface:
    """Parametric 3D surface defined by an explicit formula."""
    
    def __init__(self, X_func: Callable[[float, float], Tuple[float, float, float]],
                 domain: Tuple[Tuple[float, float], Tuple[float, float]]):
        """
        Args:
            X_func: X(u, v) -> (x, y, z) parameterization
            domain: ((u_min, u_max), (v_min, v_max))
        """
        self.X = X_func
        self.domain = domain

    def evaluate(self, u: np.ndarray, v: np.ndarray) -> np.ndarray:
        """Evaluate surface at (u, v) points. Returns (N, 3) array."""
        return np.array([self.X(ui, vi) for ui, vi in zip(u.flat, v.flat)]).reshape(*u.shape, 3)

    def metric_at_points(self, u: np.ndarray, v: np.ndarray, eps: float = 1e-5) -> np.ndarray:
        """Compute first fundamental form g_ij = ∂_i X · ∂_j X at (u,v) points.
        
        Returns:
            (N, 2, 2) array of metric matrices
        """
        # Partial derivatives via finite differences
        X_u = (np.array([self.X(ui + eps, vi) for ui, vi in zip(u.flat, v.flat)]) -
               np.array([self.X(ui - eps, vi) for ui, vi in zip(u.flat, v.flat)])) / (2 * eps)
        
        X_v = (np.array([self.X(ui, vi + eps) for ui, vi in zip(u.flat, v.flat)]) -
               np.array([self.X(ui, vi - eps) for ui, vi in zip(u.flat, v.flat)])) / (2 * eps)

        # Metric g_ij = ∂_i X · ∂_j X
        g = np.zeros((len(u.flat), 2, 2))
        g[:, 0, 0] = np.sum(X_u * X_u, axis=1)  # g_uu
        g[:, 0, 1] = np.sum(X_u * X_v, axis=1)  # g_uv
        g[:, 1, 0] = g[:, 0, 1]  # g_vu = g_uv
        g[:, 1, 1] = np.sum(X_v * X_v, axis=1)  # g_vv

        return g

    def spherical_cap(R: float, h: float):
        """Convenience: spherical cap of radius R and height h."""
        def X(u, v):
            x, y = u, v
            r_sq = x**2 + y**2
            if r_sq > R**2 - (R - h)**2:
                return (x, y, 0)  # flat outside cap
            z = np.sqrt(R**2 - r_sq) - (R - h)
            return (x, y, z)
        
        domain = ((-np.sqrt(R**2 - (R - h)**2), np.sqrt(R**2 - (R - h)**2)),
                  (-np.sqrt(R**2 - (R - h)**2), np.sqrt(R**2 - (R - h)**2)))
        return AnalyticSurface(X, domain)


class MeshTarget:
    """3D target surface as a triangle mesh (STL/OBJ)."""
    
    def __init__(self, vertices: np.ndarray, faces: np.ndarray, uv_map: Optional[np.ndarray] = None):
        """
        Args:
            vertices: (V, 3) vertex positions
            faces: (F, 3) triangle face indices
            uv_map: (V, 2) optional UV parameterization (if not provided, computed via simple projection)
        """
        self.vertices = vertices
        self.faces = faces
        self.uv_map = uv_map if uv_map is not None else self._default_uv()

    def _default_uv(self) -> np.ndarray:
        """Simple orthographic projection to 2D (X-Y plane)."""
        uv = self.vertices[:, :2].copy()
        uv -= uv.min(axis=0)
        uv /= (uv.max(axis=0) + 1e-8)
        return uv

    def face_metric(self) -> SurfaceMetric:
        """Compute metric tensor for each face (triangle)."""
        nfaces = len(self.faces)
        metrics = np.zeros((nfaces, 2, 2))
        
        for i, (i0, i1, i2) in enumerate(self.faces):
            # Vertices of triangle
            v0, v1, v2 = self.vertices[[i0, i1, i2]]
            u0, u1, u2 = self.uv_map[[i0, i1, i2]]
            
            # Partial derivatives in UV space (linear on triangle)
            du1, du2 = u1 - u0, u2 - u0
            dv1, dv2 = v1 - v0, v2 - v0
            
            # Jacobian: 3x2 matrix mapping (du, dv) → 3D
            J = np.column_stack([dv1, dv2])
            
            # Metric g = J^T J (pullback of Euclidean metric)
            metrics[i] = J.T @ J
        
        positions = np.mean(self.vertices[self.faces], axis=1)[:, :2]  # face centers in 3D projected to 2D
        
        return SurfaceMetric(metric=metrics, positions=positions, neighbors=self._adjacency())

    def _adjacency(self) -> list:
        """Build face adjacency list."""
        adj = [[] for _ in range(len(self.faces))]
        edges = {}
        for face_idx, (i0, i1, i2) in enumerate(self.faces):
            for e0, e1 in [(i0, i1), (i1, i2), (i2, i0)]:
                edge = tuple(sorted([e0, e1]))
                if edge in edges:
                    other_face = edges[edge]
                    adj[face_idx].append(other_face)
                    adj[other_face].append(face_idx)
                else:
                    edges[edge] = face_idx
        return adj


def sample_surface_on_grid(surface: AnalyticSurface, nx: int, ny: int) -> Tuple[np.ndarray, np.ndarray]:
    """Sample an analytic surface on a regular grid and return metric field."""
    (u_min, u_max), (v_min, v_max) = surface.domain
    u = np.linspace(u_min, u_max, nx)
    v = np.linspace(v_min, v_max, ny)
    uu, vv = np.meshgrid(u, v, indexing='ij')
    
    metrics = surface.metric_at_points(uu, vv)
    positions = np.column_stack([uu.flat, vv.flat])
    
    return metrics.reshape(nx * ny, 2, 2), positions

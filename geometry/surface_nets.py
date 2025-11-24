"""Intelligent Surface Nets: adaptive mesh generation from voxels with intelligent vertex placement."""
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict, Optional

@dataclass
class MeshData:
    vertices: np.ndarray
    indices: np.ndarray
    normals: Optional[np.ndarray] = None

@dataclass
class GeometryStats:
    bounds_min: np.ndarray
    bounds_max: np.ndarray
    entropy: float
    surface_area: float
    volume_enclosed: float
    aspect_ratio: Tuple[float, float, float]

class IntelligentSurfaceNets:
    """Generate meshes from voxel volumes with intelligent vertex placement and fractal DNA."""
    
    def __init__(self, volume_data: np.ndarray, resolution: Tuple[int, int, int]):
        self.volume = volume_data
        self.dims = np.array(resolution)
        self.smoothing_factor = 0.0
        self.detail_multiplier = 1.0
        self.fractal_seed = np.random.randint(0, 2**31)

    def enable_smoothing(self, level: float):
        """Configure Laplacian smoothing intensity."""
        self.smoothing_factor = np.clip(level * 0.1, 0.0, 1.0)

    def enhance_detail(self, level: float):
        """Modulate fractal detail (turbulence in vertex placement)."""
        self.detail_multiplier = max(1.0, level)

    def generate_mesh(self) -> MeshData:
        """Generate triangle mesh from voxel volume."""
        vertices, vertex_map = [], {}
        width, height, depth = self.dims
        
        for x in range(width - 1):
            for y in range(height - 1):
                for z in range(depth - 1):
                    cube_mask = self._calculate_cube_mask(x, y, z)
                    if 0 < cube_mask < 255:
                        vertex = self._calculate_intelligent_vertex(x, y, z, cube_mask)
                        vertex_map[(x, y, z)] = len(vertices)
                        vertices.append(vertex)
        
        vertices = np.array(vertices, dtype=np.float32).reshape(-1, 3) if vertices else np.zeros((0, 3), dtype=np.float32)
        indices = self._generate_topology(vertex_map)
        indices = np.array(indices, dtype=np.uint32) if indices else np.array([], dtype=np.uint32)
        normals = self._compute_vertex_normals(vertices, indices)
        
        if self.smoothing_factor > 0.0 and len(vertices) > 0:
            vertices = self._apply_laplacian_smoothing(vertices, indices)
        
        return MeshData(vertices=vertices, indices=indices, normals=normals)

    def _calculate_cube_mask(self, x: int, y: int, z: int) -> int:
        """Check which of 8 cube corners are solid."""
        mask = 0
        corners = [(0,0,0), (1,0,0), (1,1,0), (0,1,0), (0,0,1), (1,0,1), (1,1,1), (0,1,1)]
        for i, (dx, dy, dz) in enumerate(corners):
            nx, ny, nz = x + dx, y + dy, z + dz
            if 0 <= nx < self.dims[0] and 0 <= ny < self.dims[1] and 0 <= nz < self.dims[2]:
                if self.volume[nx, ny, nz] > 0.5:
                    mask |= (1 << i)
        return mask

    def _calculate_intelligent_vertex(self, x: int, y: int, z: int, mask: int) -> np.ndarray:
        """Place vertex at center of mass of density, then apply fractal noise."""
        vertex = np.array([x + 0.5, y + 0.5, z + 0.5], dtype=np.float32)
        total_density = 0.0
        com = np.zeros(3)
        
        corners = [(0,0,0), (1,0,0), (1,1,0), (0,1,0), (0,0,1), (1,0,1), (1,1,1), (0,1,1)]
        for dx, dy, dz in corners:
            nx, ny, nz = x + dx, y + dy, z + dz
            if 0 <= nx < self.dims[0] and 0 <= ny < self.dims[1] and 0 <= nz < self.dims[2]:
                density = self.volume[nx, ny, nz]
                total_density += density
                com += density * np.array([nx + dx*0.5, ny + dy*0.5, nz + dz*0.5])
        
        if total_density > 0:
            vertex = (com / total_density).astype(np.float32)
        
        # Apply fractal DNA
        if self.detail_multiplier > 1.0:
            hash_val = np.sin(x * 12.9898 + y * 78.233 + z * 31.415 + self.fractal_seed) * 43758.5453
            noise = hash_val - np.floor(hash_val)
            offset = (noise - 0.5) * 0.2 * (self.detail_multiplier - 1.0)
            vertex += offset * 0.3
        
        return vertex

    def _generate_topology(self, vertex_map: Dict) -> np.ndarray:
        """Connect adjacent vertices into triangles."""
        indices = []
        for (x, y, z), v0 in vertex_map.items():
            if (x+1, y, z) in vertex_map and (x, y+1, z) in vertex_map:
                v1 = vertex_map[(x+1, y, z)]
                v2 = vertex_map[(x, y+1, z)]
                indices.extend([v0, v1, v2])
        return np.array(indices, dtype=np.uint32) if indices else np.array([], dtype=np.uint32)

    def _apply_laplacian_smoothing(self, vertices: np.ndarray, indices: np.ndarray, iterations: int = 3) -> np.ndarray:
        """Relax vertices toward neighbors for organic look."""
        verts = vertices.copy()
        for _ in range(iterations):
            neighbor_sums = np.zeros_like(verts)
            neighbor_counts = np.zeros(len(verts))
            for i in range(0, len(indices), 3):
                pairs = [(indices[i], [indices[i+1], indices[i+2]]), 
                         (indices[i+1], [indices[i], indices[i+2]]),
                         (indices[i+2], [indices[i], indices[i+1]])]
                for src, targets in pairs:
                    for tgt in targets:
                        neighbor_sums[src] += verts[tgt]
                        neighbor_counts[src] += 1
            for i in range(len(verts)):
                if neighbor_counts[i] > 0:
                    avg = neighbor_sums[i] / neighbor_counts[i]
                    verts[i] += (avg - verts[i]) * self.smoothing_factor
        return verts

    def _compute_vertex_normals(self, vertices: np.ndarray, indices: np.ndarray) -> np.ndarray:
        """Calculate per-vertex normals from face normals."""
        normals = np.zeros_like(vertices)
        if len(indices) > 0:
            for i in range(0, len(indices), 3):
                i0, i1, i2 = indices[i], indices[i+1], indices[i+2]
                edge1 = vertices[i1] - vertices[i0]
                edge2 = vertices[i2] - vertices[i0]
                face_normal = np.cross(edge1, edge2)
                for idx in [i0, i1, i2]:
                    normals[idx] += face_normal
        lengths = np.linalg.norm(normals, axis=1, keepdims=True)
        normals = np.divide(normals, lengths + 1e-8)
        return normals.astype(np.float32)

    def analyze_geometry(self) -> GeometryStats:
        """Analyze mesh for aesthetic feedback (entropy, bounds, etc)."""
        mesh = self.generate_mesh()
        vertices = mesh.vertices
        
        bounds_min = vertices.min(axis=0) if len(vertices) > 0 else np.zeros(3)
        bounds_max = vertices.max(axis=0) if len(vertices) > 0 else np.ones(3)
        extents = bounds_max - bounds_min
        max_extent = np.max(extents)
        aspect_ratio = tuple((extents / (max_extent + 1e-8)).tolist())
        
        if len(vertices) > 1:
            centroid = vertices.mean(axis=0)
            distances = np.linalg.norm(vertices - centroid, axis=1)
            entropy = float(np.std(distances) / (np.mean(distances) + 1e-8))
        else:
            entropy = 0.5
        entropy = np.clip(entropy, 0.0, 1.0)
        
        surface_area = 0.0
        if len(mesh.indices) > 0:
            for i in range(0, len(mesh.indices), 3):
                i0, i1, i2 = mesh.indices[i:i+3]
                edge1 = vertices[i1] - vertices[i0]
                edge2 = vertices[i2] - vertices[i0]
                surface_area += 0.5 * np.linalg.norm(np.cross(edge1, edge2))
        
        return GeometryStats(bounds_min, bounds_max, entropy, float(surface_area), 0.0, aspect_ratio)

"""
OrchestratorProceduralBridge - Procedural mesh generation from orchestrator state.

Generates fractal-seeded meshes based on:
- Token embeddings (seed the fractal algorithm)
- Decision type (select fractal pattern)
- Physics parameters (modulate detail level)
"""

from __future__ import annotations
import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple


@dataclass
class ProceduralDNA:
    """DNA that defines procedural generation parameters."""
    seed: int
    fractal_type: str  # 'sierpinski', 'menger', 'mandelbulb', 'terrain'
    detail_level: int  # 1-10
    scale: float
    noise_amplitude: float
    color_seed: int
    timestamp: float = field(default_factory=time.time)


@dataclass
class ProceduralMesh:
    """Generated procedural mesh data."""
    mesh_id: str
    dna: ProceduralDNA
    vertices: List[Tuple[float, float, float]]
    indices: List[int]
    normals: List[Tuple[float, float, float]]
    uvs: List[Tuple[float, float]]
    bounds: Dict[str, Tuple[float, float, float]]


class FractalGenerator:
    """Core fractal generation algorithms."""
    
    @staticmethod
    def generate_sierpinski(depth: int, scale: float = 1.0) -> Tuple[List, List]:
        """Generate Sierpinski pyramid vertices and indices."""
        vertices = []
        indices = []
        
        # Base tetrahedron vertices
        base = [
            (0, scale, 0),
            (-scale * 0.866, -scale * 0.5, -scale * 0.5),
            (scale * 0.866, -scale * 0.5, -scale * 0.5),
            (0, -scale * 0.5, scale)
        ]
        
        def subdivide(v1, v2, v3, v4, d):
            if d == 0:
                idx = len(vertices)
                vertices.extend([v1, v2, v3, v4])
                # 4 faces of tetrahedron
                indices.extend([idx, idx+1, idx+2])
                indices.extend([idx, idx+2, idx+3])
                indices.extend([idx, idx+3, idx+1])
                indices.extend([idx+1, idx+3, idx+2])
                return
            
            # Midpoints
            m01 = tuple((a + b) / 2 for a, b in zip(v1, v2))
            m02 = tuple((a + b) / 2 for a, b in zip(v1, v3))
            m03 = tuple((a + b) / 2 for a, b in zip(v1, v4))
            m12 = tuple((a + b) / 2 for a, b in zip(v2, v3))
            m13 = tuple((a + b) / 2 for a, b in zip(v2, v4))
            m23 = tuple((a + b) / 2 for a, b in zip(v3, v4))
            
            # 4 sub-tetrahedra (not the center one)
            subdivide(v1, m01, m02, m03, d - 1)
            subdivide(m01, v2, m12, m13, d - 1)
            subdivide(m02, m12, v3, m23, d - 1)
            subdivide(m03, m13, m23, v4, d - 1)
        
        subdivide(base[0], base[1], base[2], base[3], min(depth, 5))
        return vertices, indices
    
    @staticmethod
    def generate_terrain(size: int, amplitude: float, seed: int) -> Tuple[List, List]:
        """Generate simple terrain mesh using diamond-square algorithm."""
        import random
        random.seed(seed)
        
        # Create height map
        n = size + 1
        heights = [[0.0] * n for _ in range(n)]
        
        # Diamond-square algorithm (simplified)
        step = size
        while step > 1:
            half = step // 2
            
            # Diamond step
            for y in range(half, n - 1, step):
                for x in range(half, n - 1, step):
                    avg = (heights[y - half][x - half] +
                           heights[y - half][x + half] +
                           heights[y + half][x - half] +
                           heights[y + half][x + half]) / 4
                    heights[y][x] = avg + random.uniform(-amplitude, amplitude)
            
            # Square step
            for y in range(0, n, half):
                offset = half if (y // half) % 2 == 0 else 0
                for x in range(offset, n, step):
                    count = 0
                    total = 0.0
                    for dy, dx in [(-half, 0), (half, 0), (0, -half), (0, half)]:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < n and 0 <= nx < n:
                            total += heights[ny][nx]
                            count += 1
                    if count > 0:
                        heights[y][x] = total / count + random.uniform(-amplitude, amplitude)
            
            amplitude *= 0.5
            step = half
        
        # Generate vertices and indices
        vertices = []
        indices = []
        scale = 1.0 / size
        
        for y in range(n):
            for x in range(n):
                vertices.append((x * scale - 0.5, heights[y][x], y * scale - 0.5))
        
        for y in range(size):
            for x in range(size):
                i = y * n + x
                indices.extend([i, i + n, i + 1])
                indices.extend([i + 1, i + n, i + n + 1])
        
        return vertices, indices
    
    @staticmethod
    def generate_menger_sponge(depth: int, scale: float = 1.0) -> Tuple[List, List]:
        """Generate Menger sponge vertices and indices."""
        vertices = []
        indices = []
        
        def add_cube(x, y, z, s):
            idx = len(vertices)
            # 8 vertices of cube
            for dz in [0, 1]:
                for dy in [0, 1]:
                    for dx in [0, 1]:
                        vertices.append((x + dx * s, y + dy * s, z + dz * s))
            
            # 12 triangles (6 faces, 2 triangles each)
            faces = [
                [0, 1, 3, 2],  # bottom
                [4, 6, 7, 5],  # top
                [0, 4, 5, 1],  # front
                [2, 3, 7, 6],  # back
                [0, 2, 6, 4],  # left
                [1, 5, 7, 3]   # right
            ]
            for f in faces:
                indices.extend([idx + f[0], idx + f[1], idx + f[2]])
                indices.extend([idx + f[0], idx + f[2], idx + f[3]])
        
        def menger(x, y, z, s, d):
            if d == 0:
                add_cube(x, y, z, s)
                return
            
            ns = s / 3
            for dz in range(3):
                for dy in range(3):
                    for dx in range(3):
                        # Skip center cubes (cross pattern)
                        center = (dx == 1) + (dy == 1) + (dz == 1)
                        if center >= 2:
                            continue
                        menger(x + dx * ns, y + dy * ns, z + dz * ns, ns, d - 1)
        
        menger(-scale / 2, -scale / 2, -scale / 2, scale, min(depth, 3))
        return vertices, indices


class OrchestratorProceduralBridge:
    """Bridge between MetaOrchestrator and procedural generation."""
    
    def __init__(self):
        self.generators: Dict[str, ProceduralMesh] = {}
        self.generator = FractalGenerator()
        self.generation_count = 0
    
    def generate_from_orchestrator(self, gen_id: str, orchestrator_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate procedural mesh from orchestrator state.
        
        Args:
            gen_id: Unique generator ID
            orchestrator_state: State from MetaOrchestrator.orchestrate()
        
        Returns:
            Generated mesh data
        """
        self.generation_count += 1
        
        # Extract parameters from orchestrator state
        embeddings = orchestrator_state.get('embeddings', [0.5])
        decision = orchestrator_state.get('decision', 'balanced')
        physics_params = orchestrator_state.get('physics_params', {})
        
        # Derive procedural DNA
        avg_embedding = sum(embeddings) / len(embeddings) if embeddings else 0.5
        
        # Map decision to fractal type
        if decision == 'aggressive':
            fractal_type = 'menger'
            detail_level = 3
        elif decision == 'balanced':
            fractal_type = 'terrain'
            detail_level = 5
        else:
            fractal_type = 'sierpinski'
            detail_level = 4
        
        # Create DNA
        seed = int(avg_embedding * 10000)
        dna = ProceduralDNA(
            seed=seed,
            fractal_type=fractal_type,
            detail_level=detail_level,
            scale=physics_params.get('mass', 1.0),
            noise_amplitude=avg_embedding * 0.5,
            color_seed=seed ^ 0xDEAD
        )
        
        # Generate mesh
        if fractal_type == 'sierpinski':
            vertices, indices = self.generator.generate_sierpinski(detail_level, dna.scale)
        elif fractal_type == 'menger':
            vertices, indices = self.generator.generate_menger_sponge(detail_level, dna.scale)
        else:  # terrain
            vertices, indices = self.generator.generate_terrain(
                2 ** detail_level, dna.noise_amplitude, seed
            )
        
        # Calculate bounds
        if vertices:
            min_x = min(v[0] for v in vertices)
            max_x = max(v[0] for v in vertices)
            min_y = min(v[1] for v in vertices)
            max_y = max(v[1] for v in vertices)
            min_z = min(v[2] for v in vertices)
            max_z = max(v[2] for v in vertices)
            bounds = {
                'min': (min_x, min_y, min_z),
                'max': (max_x, max_y, max_z)
            }
        else:
            bounds = {'min': (0, 0, 0), 'max': (0, 0, 0)}
        
        # Create mesh
        mesh = ProceduralMesh(
            mesh_id=gen_id,
            dna=dna,
            vertices=vertices,
            indices=indices,
            normals=[],  # Would compute normals in production
            uvs=[],      # Would compute UVs in production
            bounds=bounds
        )
        
        self.generators[gen_id] = mesh
        
        return {
            'mesh_id': gen_id,
            'dna': {
                'seed': dna.seed,
                'fractal_type': dna.fractal_type,
                'detail_level': dna.detail_level,
                'scale': dna.scale
            },
            'vertex_count': len(vertices),
            'index_count': len(indices),
            'bounds': bounds
        }
    
    def get_mesh_statistics(self, gen_id: str) -> Dict[str, Any]:
        """Get statistics for a generated mesh."""
        mesh = self.generators.get(gen_id)
        if not mesh:
            return {'error': 'mesh not found'}
        
        return {
            'vertex_count': len(mesh.vertices),
            'face_count': len(mesh.indices) // 3,
            'bounds': mesh.bounds,
            'fractal_type': mesh.dna.fractal_type,
            'detail_level': mesh.dna.detail_level
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get procedural system status."""
        return {
            'total_generators': len(self.generators),
            'total_generations': self.generation_count,
            'cached_meshes': len(self.generators),
            'mesh_ids': list(self.generators.keys())
        }


__all__ = ['OrchestratorProceduralBridge', 'ProceduralDNA', 'ProceduralMesh', 'FractalGenerator']

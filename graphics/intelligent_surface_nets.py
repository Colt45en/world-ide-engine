# graphics/intelligent_surface_nets.py
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class MeshGeometry:
    """Output mesh with attributes and indices."""
    vertices: np.ndarray  # (N, 3) positions
    indices: np.ndarray   # (M,) flattened indices for triangles
    
    def to_dict(self) -> Dict:
        return {
            'geometry': {
                'attributes': {
                    'position': {
                        'array': self.vertices.astype(np.float32),
                        'itemSize': 3
                    }
                },
                'index': self.indices.astype(np.uint32)
            }
        }

class IntelligentSurfaceNets:
    """2D voxel grid → 3D mesh with fractal DNA mutation.
    
    The "intelligence" injects deterministic noise into vertex placement,
    allowing the mesh to mutate based on detail level while maintaining smoothness.
    """
    
    def __init__(self, volumeData: Dict[str, np.ndarray]):
        """
        Args:
            volumeData: dict with 'volume' (3D binary array) and 'resolution' (dict with x,y,z)
        """
        self.volume = volumeData['volume']
        self.dims = volumeData['resolution']  # {x, y, z}
        self.smoothingFactor = 0.0
        self.detailMultiplier = 1.0
    
    def enableSmoothing(self, level: float) -> None:
        """Enable Laplacian smoothing. level in [0, 10] → factor in [0, 1]."""
        self.smoothingFactor = max(0, min(1, level * 0.1))
    
    def enhanceDetail(self, level: float) -> None:
        """Enhance fractal detail via noise multiplication."""
        self.detailMultiplier = float(level)
    
    def generateMesh(self) -> MeshGeometry:
        """Core generation: surface extraction → topology → smoothing."""
        vertices = []
        indices = []
        width = int(self.dims['x'])
        height = int(self.dims['y'])
        depth = int(self.dims['z'])
        
        # 1. Extract surface crossings via cube marching
        gridBuffer = {}  # Maps "x,y,z" → vertex index
        
        for x in range(width - 1):
            for y in range(height - 1):
                for z in range(depth - 1):
                    # Check 8 corners of cube for surface
                    mask = self._calculateCubeMask(x, y, z)
                    
                    # If surface exists (mixed solid/empty)
                    if 0 < mask < 255:
                        vertex = self._calculateIntelligentVertex(x, y, z)
                        key = f"{x},{y},{z}"
                        gridBuffer[key] = len(vertices) // 3
                        vertices.extend([vertex['x'], vertex['y'], vertex['z']])
        
        # 2. Generate topology (simplified quad connectivity)
        self._generateTopology(gridBuffer, indices, width, height, depth)
        
        # 3. Laplacian smoothing
        if self.smoothingFactor > 0:
            vertices = self._applyLaplacianSmoothing(
                vertices, indices, int(min(5, self.smoothingFactor * 10))
            )
        
        return MeshGeometry(
            vertices=np.array(vertices, dtype=np.float32).reshape(-1, 3),
            indices=np.array(indices, dtype=np.uint32)
        )
    
    def _calculateIntelligentVertex(self, x: int, y: int, z: int) -> Dict[str, float]:
        """Place vertex inside voxel with fractal DNA mutation."""
        vx = float(x) + 0.5
        vy = float(y) + 0.5
        vz = float(z) + 0.5
        
        # Fractal noise: deterministic hash-based noise
        if self.detailMultiplier > 1.0:
            noise = np.sin(x * 12.9898 + y * 78.233 + z * 31.415) * 43758.5453
            offset = (noise % 1.0) * 0.2 * (self.detailMultiplier - 1.0)
            
            vx += offset
            vy += offset
            vz += offset
        
        return {'x': vx, 'y': vy, 'z': vz}
    
    def _calculateCubeMask(self, x: int, y: int, z: int) -> int:
        """Bitmask for 8 corners: 0=empty, 1=solid."""
        mask = 0
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    xi, yi, zi = x + i, y + j, z + k
                    if 0 <= xi < self.dims['x'] and 0 <= yi < self.dims['y'] and 0 <= zi < self.dims['z']:
                        if self.volume[xi, yi, zi] > 0:
                            mask |= (1 << (i * 4 + j * 2 + k))
        return mask
    
    def _generateTopology(self, gridBuffer: Dict, indices: List, width: int, height: int, depth: int) -> None:
        """Connect vertices into faces (simplified: grid-based quads → triangles)."""
        for x in range(width - 1):
            for y in range(height - 1):
                for z in range(depth - 1):
                    # Check 4 edges of this cube face
                    corners = [
                        f"{x},{y},{z}",
                        f"{x+1},{y},{z}",
                        f"{x+1},{y+1},{z}",
                        f"{x},{y+1},{z}"
                    ]
                    
                    valid_corners = [gridBuffer.get(c) for c in corners if c in gridBuffer]
                    
                    # Create triangles from valid corners
                    if len(valid_corners) >= 3:
                        for i in range(1, len(valid_corners) - 1):
                            indices.extend([valid_corners[0], valid_corners[i], valid_corners[i+1]])
    
    def _applyLaplacianSmoothing(self, vertices: List[float], indices: List[int], iterations: int) -> List[float]:
        """Relax vertices toward neighbor average (skin-like smoothness)."""
        vert_array = np.array(vertices, dtype=np.float32).reshape(-1, 3)
        vcount = len(vert_array)
        
        for _ in range(iterations):
            offsets = np.zeros_like(vert_array)
            counts = np.zeros(vcount)
            
            # Accumulate neighbor positions
            for i in range(0, len(indices), 3):
                for j in range(3):
                    src = indices[(i + j) % len(indices)]
                    tgt = indices[(i + (j + 1) % 3) % len(indices)]
                    if src < vcount and tgt < vcount:
                        offsets[src] += vert_array[tgt]
                        counts[src] += 1
            
            # Apply smoothing
            for i in range(vcount):
                if counts[i] > 0:
                    target = offsets[i] / counts[i]
                    vert_array[i] += (target - vert_array[i]) * self.smoothingFactor
        
        return vert_array.flatten().tolist()

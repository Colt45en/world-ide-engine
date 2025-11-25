# graphics/cad_renderer.py
import numpy as np
from typing import Dict, List, Tuple, NamedTuple
from dataclasses import dataclass

class Vec3(NamedTuple):
    x: float
    y: float
    z: float
    
    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def normalize(self):
        length = (self.x**2 + self.y**2 + self.z**2)**0.5
        if length < 1e-8:
            return Vec3(0, 0, 1)
        return Vec3(self.x/length, self.y/length, self.z/length)
    
    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

@dataclass
class Mat4:
    """4x4 column-major matrix."""
    m: List[float]  # 16 elements
    
    @staticmethod
    def identity():
        return Mat4([1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1])
    
    @staticmethod
    def translate(v: Vec3):
        m = Mat4.identity()
        m.m[12] = v.x
        m.m[13] = v.y
        m.m[14] = v.z
        return m
    
    @staticmethod
    def scale(v: Vec3):
        m = Mat4.identity()
        m.m[0] = v.x
        m.m[5] = v.y
        m.m[10] = v.z
        return m
    
    @staticmethod
    def ortho(left: float, right: float, bottom: float, top: float, near: float, far: float):
        """Orthographic projection (parallel lines, no perspective)."""
        m = Mat4.identity()
        m.m[0] = 2.0 / (right - left)
        m.m[5] = 2.0 / (top - bottom)
        m.m[10] = -2.0 / (far - near)
        m.m[12] = -(right + left) / (right - left)
        m.m[13] = -(top + bottom) / (top - bottom)
        m.m[14] = -(far + near) / (far - near)
        return m
    
    @staticmethod
    def perspective(fov: float, aspect: float, near: float, far: float):
        """Perspective projection (converging lines)."""
        f = 1.0 / np.tan(fov / 2.0)
        m = Mat4.identity()
        m.m[0] = f / aspect
        m.m[5] = f
        m.m[10] = (far + near) / (near - far)
        m.m[11] = -1.0
        m.m[14] = (2.0 * far * near) / (near - far)
        m.m[15] = 0.0
        return m
    
    @staticmethod
    def lookAt(eye: Vec3, target: Vec3, up: Vec3):
        """View matrix: position camera at eye looking toward target."""
        forward = (target - eye).normalize()
        right = forward.cross(up).normalize()
        up_actual = right.cross(forward).normalize()
        
        m = Mat4.identity()
        m.m[0] = right.x
        m.m[4] = right.y
        m.m[8] = right.z
        m.m[1] = up_actual.x
        m.m[5] = up_actual.y
        m.m[9] = up_actual.z
        m.m[2] = -forward.x
        m.m[6] = -forward.y
        m.m[10] = -forward.z
        m.m[12] = -right.dot(eye)
        m.m[13] = -up_actual.dot(eye)
        m.m[14] = forward.dot(eye)
        
        return m
    
    def multiply(self, other: 'Mat4') -> 'Mat4':
        """Matrix multiplication (column-major)."""
        result = [0] * 16
        for col in range(4):
            for row in range(4):
                for k in range(4):
                    result[col * 4 + row] += self.m[k * 4 + row] * other.m[col * 4 + k]
        return Mat4(result)

@dataclass
class ViewportProjection:
    visible: bool
    screenX: float
    screenY: float
    depth: float

class CADRenderer:
    """4-View CAD System: TOP, ISO, FRONT, CAMERA in quad-layout."""
    
    def __init__(self, screenWidth: float, screenHeight: float):
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.viewportWidth = screenWidth / 2.0
        self.viewportHeight = screenHeight / 2.0
    
    def projectPoint(self, worldPos: Vec3, mvp: Mat4, 
                     viewportX: float, viewportY: float, 
                     vpWidth: float, vpHeight: float) -> ViewportProjection:
        """Project 3D point through MVP matrix to 2D screen in viewport."""
        # Transform to clip space
        x = mvp.m[0]*worldPos.x + mvp.m[4]*worldPos.y + mvp.m[8]*worldPos.z + mvp.m[12]
        y = mvp.m[1]*worldPos.x + mvp.m[5]*worldPos.y + mvp.m[9]*worldPos.z + mvp.m[13]
        z = mvp.m[2]*worldPos.x + mvp.m[6]*worldPos.y + mvp.m[10]*worldPos.z + mvp.m[14]
        w = mvp.m[3]*worldPos.x + mvp.m[7]*worldPos.y + mvp.m[11]*worldPos.z + mvp.m[15]
        
        # Clip culling
        if w < 0.001 or z < -1.0 or z > 1.0:
            return ViewportProjection(visible=False, screenX=0, screenY=0, depth=0)
        
        # Perspective divide → NDC
        ndc_x = x / w
        ndc_y = y / w
        ndc_z = z / w
        
        # Viewport transform
        screenX = (ndc_x + 1.0) * 0.5 * vpWidth + viewportX
        screenY = (1.0 - ndc_y) * 0.5 * vpHeight + viewportY
        
        return ViewportProjection(
            visible=True,
            screenX=screenX,
            screenY=screenY,
            depth=ndc_z
        )
    
    def renderCAD(self, cubeVertices: List[Vec3], cubeIndices: List[int]) -> Dict:
        """Render cube in 4-view quad layout.
        
        Returns: dict with viewport results:
          'TOP': ortho view looking down from above
          'ISO': isometric view
          'FRONT': front ortho view
          'CAMERA': perspective game camera view
        """
        results = {}
        
        # Identity model matrix (cube at origin)
        M = Mat4.identity()
        
        # --- View 1: TOP (Ortho, looking down -Y) ---
        V_top = Mat4.lookAt(Vec3(0, 10, 0), Vec3(0, 0, 0), Vec3(0, 0, -1))
        P_ortho = Mat4.ortho(-5, 5, -5, 5, 0.1, 100)
        MVP_top = P_ortho.multiply(V_top).multiply(M)
        
        # --- View 2: ISO (Ortho, isometric angle ~45°) ---
        V_iso = Mat4.lookAt(Vec3(10, 10, 10), Vec3(0, 0, 0), Vec3(0, 1, 0))
        MVP_iso = P_ortho.multiply(V_iso).multiply(M)
        
        # --- View 3: FRONT (Ortho, looking down -Z) ---
        V_front = Mat4.lookAt(Vec3(0, 0, 10), Vec3(0, 0, 0), Vec3(0, 1, 0))
        MVP_front = P_ortho.multiply(V_front).multiply(M)
        
        # --- View 4: CAMERA (Perspective, game view) ---
        V_persp = Mat4.lookAt(Vec3(0, 5, 15), Vec3(0, 0, 0), Vec3(0, 1, 0))
        P_persp = Mat4.perspective(1.04, self.viewportWidth / self.viewportHeight, 0.1, 100.0)
        MVP_camera = P_persp.multiply(V_persp).multiply(M)
        
        # Project all vertices in each view
        views = [
            ('TOP', MVP_top, 0, 0),
            ('ISO', MVP_iso, self.viewportWidth, 0),
            ('FRONT', MVP_front, 0, self.viewportHeight),
            ('CAMERA', MVP_camera, self.viewportWidth, self.viewportHeight)
        ]
        
        for viewName, mvp, vpX, vpY in views:
            projections = []
            for vertex in cubeVertices:
                proj = self.projectPoint(vertex, mvp, vpX, vpY, 
                                        self.viewportWidth, self.viewportHeight)
                projections.append(proj)
            
            results[viewName] = {
                'name': viewName,
                'projections': projections,
                'indices': cubeIndices,
                'viewportX': vpX,
                'viewportY': vpY,
                'viewportWidth': self.viewportWidth,
                'viewportHeight': self.viewportHeight
            }
        
        return results

def createCube(size: float = 2.0) -> Tuple[List[Vec3], List[int]]:
    """Create a simple cube centered at origin."""
    s = size / 2.0
    vertices = [
        Vec3(-s, -s, -s), Vec3(s, -s, -s), Vec3(s, s, -s), Vec3(-s, s, -s),  # front
        Vec3(-s, -s, s), Vec3(s, -s, s), Vec3(s, s, s), Vec3(-s, s, s),      # back
    ]
    
    indices = [
        0, 1, 2, 0, 2, 3,  # front
        5, 4, 7, 5, 7, 6,  # back
        4, 5, 1, 4, 1, 0,  # bottom
        3, 2, 6, 3, 6, 7,  # top
        4, 0, 3, 4, 3, 7,  # left
        1, 5, 6, 1, 6, 2,  # right
    ]
    
    return vertices, indices

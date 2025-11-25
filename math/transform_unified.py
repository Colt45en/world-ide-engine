# math/transform_unified.py
"""
Transform Unification: Embed 2D as special case of 3D.

A 2D affine transform (scale, rotate, translate) is a 3×3 matrix.
A 3D transform is a 4×4 matrix.

We unify both using 4×4 matrices where the 2D version has z=0 and ignores z-scale.
Both Transform3D and RectTransform output identical Mat4 format.
"""

import numpy as np
from typing import NamedTuple
from dataclasses import dataclass
from math import cos, sin, sqrt

class Quat(NamedTuple):
    """Quaternion: (w, x, y, z) for 3D rotation."""
    w: float
    x: float
    y: float
    z: float
    
    @staticmethod
    def identity():
        return Quat(1, 0, 0, 0)
    
    def normalize(self):
        length = sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)
        if length < 1e-8:
            return Quat.identity()
        return Quat(self.w/length, self.x/length, self.y/length, self.z/length)
    
    def toMat3(self):
        """Convert quaternion to 3x3 rotation matrix (row-major list)."""
        w, x, y, z = self.w, self.x, self.y, self.z
        xx, yy, zz = x*x, y*y, z*z
        xy, xz, yz = x*y, x*z, y*z
        wx, wy, wz = w*x, w*y, w*z
        
        return [
            1 - 2*(yy + zz),     2*(xy - wz),     2*(xz + wy),
                2*(xy + wz), 1 - 2*(xx + zz),     2*(yz - wx),
                2*(xz - wy),     2*(yz + wx), 1 - 2*(xx + yy)
        ]

@dataclass
class Mat4:
    """4x4 column-major matrix (16 elements)."""
    m: list  # [m00, m10, m20, m30, m01, m11, m21, m31, ...]
    
    @staticmethod
    def identity():
        return Mat4([1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1])
    
    @staticmethod
    def translate(v: 'Vec3'):
        m = Mat4.identity()
        m.m[12] = v.x
        m.m[13] = v.y
        m.m[14] = v.z
        return m
    
    @staticmethod
    def scale(v: 'Vec3'):
        m = Mat4.identity()
        m.m[0] = v.x
        m.m[5] = v.y
        m.m[10] = v.z
        return m
    
    def multiply(self, other: 'Mat4') -> 'Mat4':
        """Matrix multiplication: self * other."""
        result = [0] * 16
        for col in range(4):
            for row in range(4):
                for k in range(4):
                    result[col*4 + row] += self.m[k*4 + row] * other.m[col*4 + k]
        return Mat4(result)
    
    def __repr__(self):
        return f"Mat4({self.m})"

class Vec3(NamedTuple):
    """3D vector."""
    x: float
    y: float
    z: float
    
    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

class Vec2(NamedTuple):
    """2D vector."""
    x: float
    y: float

class Transform3D:
    """Heavy 3D transform: position, rotation (quaternion), scale."""
    
    def __init__(self, 
                 position: Vec3 = None,
                 rotation: Quat = None,
                 scale: Vec3 = None):
        self.position = position or Vec3(0, 0, 0)
        self.rotation = (rotation or Quat.identity()).normalize()
        self.scale = scale or Vec3(1, 1, 1)
    
    def toMatrix(self) -> Mat4:
        """Convert to 4x4 matrix: T * R * S."""
        # Scale
        S = Mat4.scale(self.scale)
        
        # Rotation (from quaternion to 3x3, embed in 4x4)
        rot3x3 = self.rotation.toMat3()
        R = Mat4.identity()
        R.m[0], R.m[4], R.m[8] = rot3x3[0], rot3x3[1], rot3x3[2]
        R.m[1], R.m[5], R.m[9] = rot3x3[3], rot3x3[4], rot3x3[5]
        R.m[2], R.m[6], R.m[10] = rot3x3[6], rot3x3[7], rot3x3[8]
        
        # Translation
        T = Mat4.translate(self.position)
        
        return T.multiply(R.multiply(S))
    
    def inverse(self) -> 'Transform3D':
        """Compute inverse transform."""
        rot_inv = Quat(self.rotation.w, -self.rotation.x, -self.rotation.y, -self.rotation.z)
        scale_inv = Vec3(1/self.scale.x if self.scale.x != 0 else 0,
                         1/self.scale.y if self.scale.y != 0 else 0,
                         1/self.scale.z if self.scale.z != 0 else 0)
        
        # pos_inv = -rot_inv * (scale_inv * position)
        pos_scaled = Vec3(self.position.x * scale_inv.x,
                         self.position.y * scale_inv.y,
                         self.position.z * scale_inv.z)
        pos_inv = rot_inv.toMat3()  # Placeholder: proper quaternion rotation needed
        
        return Transform3D(position=Vec3(-self.position.x, -self.position.y, -self.position.z),
                          rotation=rot_inv,
                          scale=scale_inv)

class RectTransform:
    """Light 2D transform: pixel-based (x, y, width, height, rotation, depth)."""
    
    def __init__(self,
                 x: float = 0,
                 y: float = 0,
                 w: float = 100,
                 h: float = 100,
                 rotation: float = 0,  # radians
                 depth: float = 0):    # z-index for layering
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rotation = rotation
        self.depth = depth
    
    def toMatrix(self) -> Mat4:
        """Promote 2D transform to 4x4 matrix.
        
        Maps pixel space: x,y to world, rotation around Z only, depth for sorting.
        Order: T(x,y,depth) * Rz(rotation) * S(w, h, 1)
        """
        # Translation to pixel position
        T = Mat4.translate(Vec3(self.x, self.y, self.depth))
        
        # Rotation: 2D rotation around Z axis
        c, s = cos(self.rotation), sin(self.rotation)
        R = Mat4.identity()
        R.m[0] = c
        R.m[4] = -s
        R.m[1] = s
        R.m[5] = c
        
        # Scale: width, height, z-scale is 1 (flat in Z)
        S = Mat4.scale(Vec3(self.w, self.h, 1.0))
        
        return T.multiply(R.multiply(S))
    
    def inverse(self) -> 'RectTransform':
        """Inverse 2D transform."""
        return RectTransform(
            x=-self.x,
            y=-self.y,
            w=1/self.w if self.w != 0 else 0,
            h=1/self.h if self.h != 0 else 0,
            rotation=-self.rotation,
            depth=-self.depth
        )
    
    def toPixelBounds(self) -> tuple:
        """Return axis-aligned bounding box if rotation == 0, else None."""
        if abs(self.rotation) < 1e-6:
            return (self.x, self.y, self.x + self.w, self.y + self.h)
        return None

class Camera:
    """Unified camera: switch between 3D (perspective) and 2D (orthographic) modes."""
    
    def __init__(self, screenWidth: float, screenHeight: float):
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.view = Mat4.identity()
        self.proj = Mat4.identity()
        self.viewProj = Mat4.identity()
    
    def update(self):
        """Recompute combined view-projection matrix."""
        self.viewProj = self.proj.multiply(self.view)
    
    def setPerspective3D(self, eye: Vec3, target: Vec3, up: Vec3 = None,
                        fov: float = 1.04, near: float = 0.1, far: float = 1000.0):
        """Mode: 3D First-Person Camera."""
        if up is None:
            up = Vec3(0, 1, 0)
        
        # Simplified lookAt (uses position as view)
        self.view = Mat4.translate(eye * -1.0)  # Placeholder
        
        aspect = self.screenWidth / self.screenHeight
        f = 1.0 / np.tan(fov / 2.0)
        self.proj = Mat4.identity()
        self.proj.m[0] = f / aspect
        self.proj.m[5] = f
        self.proj.m[10] = (far + near) / (near - far)
        self.proj.m[11] = -1.0
        self.proj.m[14] = (2.0 * far * near) / (near - far)
        self.proj.m[15] = 0.0
        
        self.update()
    
    def setOrthographic2D(self, screenWidth: float, screenHeight: float,
                         near: float = -100, far: float = 100):
        """Mode: 2D UI Overlay (Orthographic)."""
        # View: identity (camera at origin)
        self.view = Mat4.identity()
        
        # Projection: map [0, W] x [H, 0] to NDC [-1, 1]
        # (Screen Y is inverted: 0 at top)
        self.proj = Mat4.identity()
        self.proj.m[0] = 2.0 / screenWidth
        self.proj.m[5] = -2.0 / screenHeight  # Flip Y
        self.proj.m[10] = -2.0 / (far - near)
        self.proj.m[12] = -1.0
        self.proj.m[13] = 1.0
        self.proj.m[14] = -(far + near) / (far - near)
        
        self.update()

def unprojectMouse(mouseX: float, mouseY: float, 
                   screenWidth: float, screenHeight: float,
                   invViewProj: Mat4, 
                   nearPlane: float = 0.1, 
                   farPlane: float = 1000.0) -> tuple:
    """Unproject 2D mouse coord to 3D ray (for picking/raycasting).
    
    Returns: (origin, direction) of ray in world space.
    """
    # NDC coordinates
    ndc_x = 2.0 * mouseX / screenWidth - 1.0
    ndc_y = 1.0 - 2.0 * mouseY / screenHeight
    
    # Near and far points in clip space
    near_clip = [ndc_x, ndc_y, -1.0, 1.0]
    far_clip = [ndc_x, ndc_y, 1.0, 1.0]
    
    # Transform back to world space (apply inverse VP)
    # Placeholder: proper matrix-vector multiplication needed
    
    return (Vec3(0, 0, 0), Vec3(0, 0, 1))

def projectMouse(worldPos: Vec3, viewProj: Mat4, 
                 screenWidth: float, screenHeight: float) -> tuple:
    """Project 3D world position to 2D screen (inverse of unproject)."""
    # Transform to clip space (MVP)
    x = viewProj.m[0]*worldPos.x + viewProj.m[4]*worldPos.y + viewProj.m[8]*worldPos.z + viewProj.m[12]
    y = viewProj.m[1]*worldPos.x + viewProj.m[5]*worldPos.y + viewProj.m[9]*worldPos.z + viewProj.m[13]
    z = viewProj.m[2]*worldPos.x + viewProj.m[6]*worldPos.y + viewProj.m[10]*worldPos.z + viewProj.m[14]
    w = viewProj.m[3]*worldPos.x + viewProj.m[7]*worldPos.y + viewProj.m[11]*worldPos.z + viewProj.m[15]
    
    if w < 1e-8:
        return None
    
    # Perspective divide → NDC
    ndc_x = x / w
    ndc_y = y / w
    
    # Viewport transform
    screen_x = (ndc_x + 1.0) * 0.5 * screenWidth
    screen_y = (1.0 - ndc_y) * 0.5 * screenHeight
    
    return (screen_x, screen_y)

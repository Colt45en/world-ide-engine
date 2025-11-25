import math
from dataclasses import dataclass, field


@dataclass
class Vec3:
    x: float
    y: float
    z: float

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, s):
        return Vec3(self.x * s, self.y * s, self.z * s)
    
    def __rmul__(self, s):
        return self * s
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def length(self):
        return math.sqrt(self.dot(self))
    
    def normalized(self):
        l = self.length()
        if l > 1e-10:
            return self * (1.0 / l)
        return Vec3(0, 0, 0)
    
    def tuple(self):
        return (self.x, self.y, self.z)

@dataclass
class Quat:
    w: float
    x: float
    y: float
    z: float

    @staticmethod
    def identity():
        return Quat(1, 0, 0, 0)
    
    @staticmethod
    def fromAxisAngle(axis: Vec3, angle: float):
        axis = axis.normalized()
        half_angle = angle * 0.5
        s = math.sin(half_angle)
        return Quat(
            math.cos(half_angle),
            axis.x * s,
            axis.y * s,
            axis.z * s
        )
    
    def __mul__(self, other):
        if isinstance(other, Quat):
            return Quat(
                self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z,
                self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y,
                self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x,
                self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w
            )
        elif isinstance(other, Vec3):
            qv = Quat(0, other.x, other.y, other.z)
            q_conj = Quat(self.w, -self.x, -self.y, -self.z)
            result = (self * qv) * q_conj
            return Vec3(result.x, result.y, result.z)
    
    def conjugate(self):
        return Quat(self.w, -self.x, -self.y, -self.z)
    
    def normalize(self):
        l = math.sqrt(self.w * self.w + self.x * self.x + self.y * self.y + self.z * self.z)
        if l > 1e-10:
            return Quat(self.w / l, self.x / l, self.y / l, self.z / l)
        return Quat.identity()
    
    def toMat3(self):
        n = self.normalize()
        xx = n.x * n.x
        yy = n.y * n.y
        zz = n.z * n.z
        xy = n.x * n.y
        xz = n.x * n.z
        yz = n.y * n.z
        wx = n.w * n.x
        wy = n.w * n.y
        wz = n.w * n.z
        
        return [
            [1 - 2*(yy + zz), 2*(xy - wz), 2*(xz + wy)],
            [2*(xy + wz), 1 - 2*(xx + zz), 2*(yz - wx)],
            [2*(xz - wy), 2*(yz + wx), 1 - 2*(xx + yy)]
        ]

@dataclass
class Mat3:
    def __init__(self, m=None):
        if m is None:
            self.m = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        else:
            self.m = m
    
    def __mul__(self, other):
        if isinstance(other, Vec3):
            return Vec3(
                self.m[0][0] * other.x + self.m[0][1] * other.y + self.m[0][2] * other.z,
                self.m[1][0] * other.x + self.m[1][1] * other.y + self.m[1][2] * other.z,
                self.m[2][0] * other.x + self.m[2][1] * other.y + self.m[2][2] * other.z
            )
        elif isinstance(other, Mat3):
            result = [[0]*3 for _ in range(3)]
            for i in range(3):
                for j in range(3):
                    for k in range(3):
                        result[i][j] += self.m[i][k] * other.m[k][j]
            return Mat3(result)
    
    def transpose(self):
        return Mat3([[self.m[j][i] for j in range(3)] for i in range(3)])

class RigidBody:
    def __init__(self, position: Vec3, mass: float, collider=None):
        self.position = position
        self.velocity = Vec3(0, 0, 0)
        self.force = Vec3(0, 0, 0)
        
        self.orientation = Quat.identity()
        self.angular_velocity = Vec3(0, 0, 0)
        self.torque = Vec3(0, 0, 0)
        
        self.mass = mass
        self.inv_mass = 1.0 / mass if mass > 0 else 0
        
        self.collider = collider
        
        self.inv_inertia_local = Mat3([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.inv_inertia_world = Mat3()
        self.updateInertiaWorld()
        
        self.gravity = Vec3(0, -9.81, 0)

    def setBoxInertia(self, width: float, height: float, depth: float):
        if self.mass <= 0:
            self.inv_inertia_local = Mat3()
            return
        
        Ix = (self.mass / 12.0) * (height * height + depth * depth)
        Iy = (self.mass / 12.0) * (width * width + depth * depth)
        Iz = (self.mass / 12.0) * (width * width + height * height)
        
        inv_Ix = 1.0 / Ix if Ix > 0 else 0
        inv_Iy = 1.0 / Iy if Iy > 0 else 0
        inv_Iz = 1.0 / Iz if Iz > 0 else 0
        
        self.inv_inertia_local = Mat3([
            [inv_Ix, 0, 0],
            [0, inv_Iy, 0],
            [0, 0, inv_Iz]
        ])
        self.updateInertiaWorld()

    def setSphereInertia(self, radius: float):
        if self.mass <= 0:
            self.inv_inertia_local = Mat3()
            return
        
        I = (self.mass * radius * radius) * (2.0 / 5.0)
        inv_I = 1.0 / I if I > 0 else 0
        
        self.inv_inertia_local = Mat3([
            [inv_I, 0, 0],
            [0, inv_I, 0],
            [0, 0, inv_I]
        ])
        self.updateInertiaWorld()

    def updateInertiaWorld(self):
        R = Mat3(self.orientation.toMat3())
        R_T = R.transpose()
        self.inv_inertia_world = R * self.inv_inertia_local * R_T

    def applyImpulse(self, impulse: Vec3, contact_point: Vec3):
        self.velocity = self.velocity + impulse * self.inv_mass
        
        r = contact_point - self.position
        angular_impulse = r.cross(impulse)
        angular_change = self.inv_inertia_world * angular_impulse
        self.angular_velocity = self.angular_velocity + angular_change

    def integrate(self, dt: float):
        if self.inv_mass == 0:
            return
        
        self.force = self.force + self.gravity * self.mass
        
        acceleration = self.force * self.inv_mass
        self.velocity = self.velocity + acceleration * dt
        self.position = self.position + self.velocity * dt
        
        self.force = Vec3(0, 0, 0)
        
        omega_mag = self.angular_velocity.length()
        if omega_mag > 1e-6:
            omega_norm = self.angular_velocity.normalized()
            angle_change = omega_mag * dt
            dq = Quat.fromAxisAngle(omega_norm, angle_change)
            self.orientation = (dq * self.orientation).normalize()
        
        self.updateInertiaWorld()

    def setWorldCollider(self):
        if self.collider:
            self.collider.position = self.position.tuple()

    def getWorldCollider(self):
        return self.collider





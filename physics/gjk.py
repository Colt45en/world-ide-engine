import math
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class SupportPoint:
    p: Tuple[float, float, float]
    a: Tuple[float, float, float]
    b: Tuple[float, float, float]

def vec_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

def vec_add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])

def vec_scale(v, s):
    return (v[0] * s, v[1] * s, v[2] * s)

def vec_dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

def vec_cross(a, b):
    return (a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0])

def vec_len(v):
    return math.sqrt(vec_dot(v, v))

def vec_norm(v):
    l = vec_len(v)
    return vec_scale(v, 1.0 / l) if l > 1e-10 else (0, 0, 0)

def vec_neg(v):
    return (-v[0], -v[1], -v[2])

class Collider:
    def getSupport(self, direction: Tuple[float, float, float]) -> Tuple[float, float, float]:
        raise NotImplementedError

class BoxCollider(Collider):
    def __init__(self, position, half_extents):
        self.position = position
        self.half_extents = half_extents

    def getSupport(self, direction):
        support = (
            self.position[0] + (self.half_extents[0] if direction[0] > 0 else -self.half_extents[0]),
            self.position[1] + (self.half_extents[1] if direction[1] > 0 else -self.half_extents[1]),
            self.position[2] + (self.half_extents[2] if direction[2] > 0 else -self.half_extents[2])
        )
        return support

class SphereCollider(Collider):
    def __init__(self, position, radius):
        self.position = position
        self.radius = radius

    def getSupport(self, direction):
        d_norm = vec_norm(direction)
        return vec_add(self.position, vec_scale(d_norm, self.radius))

class GJK:
    MAX_ITERATIONS = 100
    EPSILON = 1e-6

    def __init__(self):
        self.simplex: List[SupportPoint] = []

    def _getSupportPoint(self, collider_a: Collider, collider_b: Collider, direction: Tuple) -> SupportPoint:
        point_a = collider_a.getSupport(direction)
        point_b = collider_b.getSupport(vec_neg(direction))
        world_point = vec_sub(point_a, point_b)
        return SupportPoint(p=world_point, a=point_a, b=point_b)

    def _sameDirection(self, a: Tuple, b: Tuple) -> bool:
        return vec_dot(a, b) > 0

    def _perpendicular(self, a: Tuple, b: Tuple) -> Tuple:
        ac = vec_cross(a, b)
        return vec_cross(ac, a)

    def _handleSimplex2(self) -> tuple:
        a = self.simplex[1].p
        b = self.simplex[0].p
        ao = vec_neg(a)
        ab = vec_sub(b, a)
        direction = self._perpendicular(ab, ao)
        if vec_len(direction) < self.EPSILON:
            direction = vec_cross(ab, (0, 1, 0))
            if vec_len(direction) < self.EPSILON:
                direction = vec_cross(ab, (0, 0, 1))
        return False, vec_norm(direction)

    def _handleSimplex3(self) -> tuple:
        a = self.simplex[2].p
        b = self.simplex[1].p
        c = self.simplex[0].p
        ao = vec_neg(a)
        ab = vec_sub(b, a)
        ac = vec_sub(c, a)
        abc = vec_cross(ab, ac)
        acb = vec_cross(ac, abc)
        if self._sameDirection(acb, ao):
            self.simplex.pop(1)
            return False, vec_norm(acb)
        abo = vec_cross(abc, ab)
        if self._sameDirection(abo, ao):
            self.simplex.pop(0)
            return False, vec_norm(abo)
        return False, vec_norm(abc)

    def _handleSimplex4(self) -> tuple:
        a = self.simplex[3].p
        b = self.simplex[2].p
        c = self.simplex[1].p
        d = self.simplex[0].p
        ao = vec_neg(a)
        abc = vec_cross(vec_sub(b, a), vec_sub(c, a))
        if self._sameDirection(abc, ao):
            self.simplex.pop(0)
            return False, vec_norm(abc)
        acd = vec_cross(vec_sub(c, a), vec_sub(d, a))
        if self._sameDirection(acd, ao):
            self.simplex.pop(1)
            return False, vec_norm(acd)
        adb = vec_cross(vec_sub(d, a), vec_sub(b, a))
        if self._sameDirection(adb, ao):
            self.simplex.pop(2)
            return False, vec_norm(adb)
        return True, (0, 0, 0)

    def _handleSimplex(self) -> tuple:
        if len(self.simplex) == 2:
            return self._handleSimplex2()
        elif len(self.simplex) == 3:
            return self._handleSimplex3()
        elif len(self.simplex) == 4:
            return self._handleSimplex4()
        return False, (1, 0, 0)

    def colliding(self, collider_a: Collider, collider_b: Collider) -> bool:
        self.simplex = []
        direction = (1, 0, 0)
        for _ in range(self.MAX_ITERATIONS):
            support = self._getSupportPoint(collider_a, collider_b, direction)
            if vec_dot(support.p, direction) < 0:
                return False
            self.simplex.append(support)
            colliding, direction = self._handleSimplex()
            if colliding:
                return True
            if vec_len(direction) < self.EPSILON:
                return True
        return False

    def getSimplex(self) -> List[SupportPoint]:
        return self.simplex

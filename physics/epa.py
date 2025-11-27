import math
from dataclasses import dataclass

from physics.gjk import SupportPoint, vec_sub, vec_add, vec_scale, vec_dot, vec_cross, vec_len, vec_norm

@dataclass
class ContactInfo:
    normal: tuple[float, float, float]
    depth: float
    world_point_a: tuple[float, float, float]
    world_point_b: tuple[float, float, float]
    contact_count: int

@dataclass
class EPAFace:
    a: int
    b: int
    c: int
    normal: tuple[float, float, float]

class EPA:
    MAX_ITERATIONS = 50
    EPSILON = 1e-6

    def __init__(self):
        self.vertices: list[SupportPoint] = []
        self.faces: list[EPAFace] = []
        self.edges: list[tuple] = []

    def _makeFace(self, a: int, b: int, c: int) -> EPAFace | None:
        edge1 = vec_sub(self.vertices[b].p, self.vertices[a].p)
        edge2 = vec_sub(self.vertices[c].p, self.vertices[a].p)
        normal = vec_cross(edge1, edge2)
        
        if vec_len(normal) < self.EPSILON:
            return None
        
        normal = vec_norm(normal)
        
        to_origin = vec_neg(self.vertices[a].p)
        if vec_dot(normal, to_origin) < 0:
            normal = vec_neg(normal)
        
        return EPAFace(a=a, b=b, c=c, normal=normal)

    def _getClosestFace(self) -> tuple:
        min_dist = float('inf')
        closest_face = None
        closest_idx = -1
        
        for i, face in enumerate(self.faces):
            if face is None:
                continue
            
            dist = vec_dot(face.normal, self.vertices[face.a].p)
            
            if dist < min_dist:
                min_dist = dist
                closest_face = face
                closest_idx = i
        
        return closest_face, closest_idx, min_dist

    def _isObservedByVertex(self, face: EPAFace, vertex: SupportPoint) -> bool:
        plane_dist = vec_dot(face.normal, vec_sub(vertex.p, self.vertices[face.a].p))
        return plane_dist > self.EPSILON

    def _findHorizon(self, start_idx: int, vertex: SupportPoint) -> list[tuple]:
        horizon = []
        processed = set()
        
        stack = [start_idx]
        
        while stack:
            face_idx = stack.pop()
            if face_idx in processed:
                continue
            processed.add(face_idx)
            
            face = self.faces[face_idx]
            if face is None:
                continue
            
            if self._isObservedByVertex(face, vertex):
                edges = [(face.a, face.b), (face.b, face.c), (face.c, face.a)]
                for edge in edges:
                    horizon.append(edge)
                    
                    for i, other_face in enumerate(self.faces):
                        if other_face is None or i == face_idx or i in processed:
                            continue
                        if (other_face.a == edge[1] and other_face.b == edge[0]) or \
                           (other_face.b == edge[1] and other_face.c == edge[0]) or \
                           (other_face.c == edge[1] and other_face.a == edge[0]):
                            stack.append(i)
            else:
                for i, other_face in enumerate(self.faces):
                    if other_face is None or i == face_idx or i in processed:
                        continue
                    if any((other_face.a == (face.a, face.b)[j % 2] and 
                           other_face.b == (face.a, face.b)[(j + 1) % 2]) for j in range(3)):
                        stack.append(i)
        
        horizon_edges = []
        edge_count = {}
        for edge in horizon:
            key = tuple(sorted(edge))
            edge_count[key] = edge_count.get(key, 0) + 1
        
        for edge, count in edge_count.items():
            if count == 1:
                horizon_edges.append(edge)
        
        return horizon_edges

    def _barycentric(self, p: tuple, a: tuple, b: tuple, c: tuple) -> tuple[float, float, float]:
        v0 = vec_sub(c, a)
        v1 = vec_sub(b, a)
        v2 = vec_sub(p, a)
        
        dot00 = vec_dot(v0, v0)
        dot01 = vec_dot(v0, v1)
        dot02 = vec_dot(v0, v2)
        dot11 = vec_dot(v1, v1)
        dot12 = vec_dot(v1, v2)
        
        denom = dot00 * dot11 - dot01 * dot01
        if abs(denom) < self.EPSILON:
            return (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)
        
        v = (dot11 * dot02 - dot01 * dot12) / denom
        w = (dot00 * dot12 - dot01 * dot02) / denom
        u = 1.0 - v - w
        
        return (u, v, w)

    def _getContactPoint(self, face: EPAFace) -> tuple:
        a_pt = self.vertices[face.a]
        b_pt = self.vertices[face.b]
        c_pt = self.vertices[face.c]
        
        contact_world = face.normal
        u, v, w = self._barycentric(contact_world, a_pt.p, b_pt.p, c_pt.p)
        
        contact_a = vec_add(vec_scale(a_pt.a, u), vec_add(vec_scale(b_pt.a, v), vec_scale(c_pt.a, w)))
        contact_b = vec_add(vec_scale(a_pt.b, u), vec_add(vec_scale(b_pt.b, v), vec_scale(c_pt.b, w)))
        
        return contact_a, contact_b

    def expand(self, simplex: list[SupportPoint], collider_a, collider_b) -> ContactInfo | None:
        if len(simplex) < 4:
            return None
        
        self.vertices = simplex[:]
        self.faces = []
        
        self.faces.append(self._makeFace(0, 1, 2))
        self.faces.append(self._makeFace(0, 3, 1))
        self.faces.append(self._makeFace(0, 2, 3))
        self.faces.append(self._makeFace(1, 3, 2))
        
        for iteration in range(self.MAX_ITERATIONS):
            closest_face, closest_idx, closest_dist = self._getClosestFace()
            
            if closest_face is None:
                break
            
            search_dir = closest_face.normal
            support = SupportPoint(
                p=vec_sub(
                    collider_a.getSupport(search_dir),
                    collider_b.getSupport(vec_scale(search_dir, -1))
                ),
                a=collider_a.getSupport(search_dir),
                b=collider_b.getSupport(vec_scale(search_dir, -1))
            )
            
            new_dist = vec_dot(support.p, search_dir)
            
            if new_dist - closest_dist < self.EPSILON:
                contact_a, contact_b = self._getContactPoint(closest_face)
                
                return ContactInfo(
                    normal=closest_face.normal,
                    depth=closest_dist,
                    world_point_a=contact_a,
                    world_point_b=contact_b,
                    contact_count=1
                )
            
            self.vertices.append(support)
            vertex_idx = len(self.vertices) - 1
            
            self.faces[closest_idx] = None
            
            horizon_edges = self._findHorizon(closest_idx, support)
            
            for edge in horizon_edges:
                new_face = self._makeFace(edge[0], edge[1], vertex_idx)
                if new_face is not None:
                    self.faces.append(new_face)
        
        closest_face, _, _ = self._getClosestFace()
        if closest_face:
            contact_a, contact_b = self._getContactPoint(closest_face)
            return ContactInfo(
                normal=closest_face.normal,
                depth=vec_dot(closest_face.normal, self.vertices[closest_face.a].p),
                world_point_a=contact_a,
                world_point_b=contact_b,
                contact_count=1
            )
        
        return None





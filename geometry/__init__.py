"""
Geometry Engine - 3D Mathematics and Spatial Operations

Provides fundamental 3D geometry classes and operations for physics simulation,
rendering, and spatial reasoning.
"""

import math


class Vector3:
    """
    3D Vector class with comprehensive mathematical operations

    Supports all standard vector operations needed for physics simulation:
    - Arithmetic: +, -, *, /, +=, -=, *=, /=
    - Vector operations: dot, cross, magnitude, normalize
    - Distance and projection operations
    - Component access: x, y, z
    """

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __repr__(self):
        return f"Vector3({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"

    def __str__(self):
        return f"({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"

    def __eq__(self, other):
        if not isinstance(other, Vector3):
            return False
        return (abs(self.x - other.x) < 1e-10 and
                abs(self.y - other.y) < 1e-10 and
                abs(self.z - other.z) < 1e-10)

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide vector by zero")
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __imul__(self, scalar):
        self.x *= scalar
        self.y *= scalar
        self.z *= scalar
        return self

    def __itruediv__(self, scalar):
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide vector by zero")
        self.x /= scalar
        self.y /= scalar
        self.z /= scalar
        return self

    def magnitude(self):
        """Return the magnitude (length) of the vector"""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def magnitude_squared(self):
        """Return the squared magnitude (faster than magnitude for comparisons)"""
        return self.x**2 + self.y**2 + self.z**2

    def normalize(self):
        """Return a normalized (unit length) version of this vector"""
        mag = self.magnitude()
        if mag == 0:
            return Vector3(0, 0, 0)
        return self / mag

    def normalized(self):
        """Return a normalized (unit length) version of this vector"""
        return self.normalize()

    def dot(self, other):
        """Return the dot product with another vector"""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        """Return the cross product with another vector"""
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def distance_to(self, other):
        """Return the Euclidean distance to another vector"""
        return (other - self).magnitude()

    def distance_squared_to(self, other):
        """Return the squared Euclidean distance to another vector"""
        return (other - self).magnitude_squared()

    def angle_to(self, other):
        """Return the angle in radians between this vector and another"""
        cos_theta = self.dot(other) / (self.magnitude() * other.magnitude())
        cos_theta = max(-1.0, min(1.0, cos_theta))  # Clamp for numerical stability
        return math.acos(cos_theta)

    def project_onto(self, other):
        """Return the projection of this vector onto another vector"""
        if other.magnitude_squared() == 0:
            return Vector3(0, 0, 0)
        return other * (self.dot(other) / other.magnitude_squared())

    def reflect(self, normal):
        """Return the reflection of this vector off a surface with given normal"""
        normal = normal.normalize()
        return self - normal * (2 * self.dot(normal))

    def lerp(self, other, t):
        """Linear interpolation between this vector and another"""
        t = max(0.0, min(1.0, t))
        return self + (other - self) * t

    def clamp_magnitude(self, max_magnitude):
        """Return a vector with magnitude clamped to max_magnitude"""
        mag = self.magnitude()
        if mag > max_magnitude:
            return self.normalize() * max_magnitude
        return Vector3(self.x, self.y, self.z)

    def is_zero(self, tolerance=1e-10):
        """Check if this vector is approximately zero"""
        return self.magnitude_squared() < tolerance * tolerance

    def copy(self):
        """Return a copy of this vector"""
        return Vector3(self.x, self.y, self.z)

    @staticmethod
    def zero():
        """Return a zero vector"""
        return Vector3(0, 0, 0)

    @staticmethod
    def one():
        """Return a vector with all components set to 1"""
        return Vector3(1, 1, 1)

    @staticmethod
    def up():
        """Return the up vector (0, 1, 0)"""
        return Vector3(0, 1, 0)

    @staticmethod
    def down():
        """Return the down vector (0, -1, 0)"""
        return Vector3(0, -1, 0)

    @staticmethod
    def left():
        """Return the left vector (-1, 0, 0)"""
        return Vector3(-1, 0, 0)

    @staticmethod
    def right():
        """Return the right vector (1, 0, 0)"""
        return Vector3(1, 0, 0)

    @staticmethod
    def forward():
        """Return the forward vector (0, 0, 1)"""
        return Vector3(0, 0, 1)

    @staticmethod
    def back():
        """Return the back vector (0, 0, -1)"""
        return Vector3(0, 0, -1)


class Ray:
    """
    3D Ray class for ray casting and intersection tests

    A ray is defined by an origin point and a direction vector.
    The direction should typically be normalized for most operations.
    """

    def __init__(self, origin, direction):
        self.origin = origin.copy()
        self.direction = direction.copy()

    def __repr__(self):
        return f"Ray(origin={self.origin}, direction={self.direction})"

    def point_at_distance(self, distance):
        """Return the point along the ray at the given distance from origin"""
        return self.origin + self.direction * distance

    def normalize_direction(self):
        """Normalize the direction vector in-place"""
        self.direction = self.direction.normalize()

    def is_normalized(self, tolerance=1e-6):
        """Check if the direction vector is normalized"""
        return abs(self.direction.magnitude() - 1.0) < tolerance


class GeometryEngine:
    """
    Geometry engine for spatial operations and collision detection

    Provides ray casting, collision detection, and spatial queries.
    """

    def __init__(self):
        self.debug_mode = False

    def ray_sphere_intersection(self, ray, sphere_center, sphere_radius):
        """
        Compute intersection of ray with sphere

        Returns the distance along the ray to the first intersection point,
        or None if no intersection occurs.

        Uses the quadratic formula for ray-sphere intersection.
        """
        # Vector from ray origin to sphere center
        oc = sphere_center - ray.origin

        # Project oc onto ray direction
        proj = oc.dot(ray.direction)

        # Distance from sphere center to ray line
        distance_squared = oc.magnitude_squared() - proj * proj

        # Check if ray intersects sphere
        radius_squared = sphere_radius * sphere_radius
        if distance_squared > radius_squared:
            return None

        # Distance from projection point to intersection points
        offset = math.sqrt(radius_squared - distance_squared)

        # Two possible intersection distances
        t1 = proj - offset
        t2 = proj + offset

        # Return the smallest positive distance
        if t1 > 0:
            return t1
        elif t2 > 0:
            return t2
        else:
            return None

    def ray_plane_intersection(self, ray, plane_point, plane_normal):
        """
        Compute intersection of ray with plane

        Returns the distance along the ray to the intersection point,
        or None if no intersection occurs (ray parallel to plane).
        """
        denom = ray.direction.dot(plane_normal)

        if abs(denom) < 1e-6:  # Ray parallel to plane
            return None

        # Vector from ray origin to plane point
        to_plane = plane_point - ray.origin

        # Distance along ray to intersection
        t = to_plane.dot(plane_normal) / denom

        if t < 0:  # Intersection behind ray origin
            return None

        return t

    def point_in_sphere(self, point, sphere_center, sphere_radius):
        """Check if a point is inside a sphere"""
        distance_squared = point.distance_squared_to(sphere_center)
        return distance_squared <= sphere_radius * sphere_radius

    def sphere_sphere_intersection(self, center1, radius1, center2, radius2):
        """Check if two spheres intersect"""
        distance = center1.distance_to(center2)
        return distance <= (radius1 + radius2)

    def closest_point_on_line(self, point, line_start, line_end):
        """
        Find the closest point on a line segment to a given point

        Returns the point on the line segment closest to the input point.
        """
        line_vec = line_end - line_start
        point_vec = point - line_start

        line_length_squared = line_vec.magnitude_squared()

        if line_length_squared == 0:
            return line_start.copy()

        # Projection parameter
        t = max(0.0, min(1.0, point_vec.dot(line_vec) / line_length_squared))

        return line_start + line_vec * t

    def point_line_distance(self, point, line_start, line_end):
        """Compute the distance from a point to a line segment"""
        closest = self.closest_point_on_line(point, line_start, line_end)
        return point.distance_to(closest)

    def triangle_area(self, v1, v2, v3):
        """Compute the area of a triangle defined by three points"""
        # Use cross product magnitude / 2
        cross = (v2 - v1).cross(v3 - v1)
        return cross.magnitude() / 2.0

    def barycentric_coordinates(self, point, v1, v2, v3):
        """
        Compute barycentric coordinates of a point relative to a triangle

        Returns (u, v, w) where u + v + w = 1, or None if point is outside triangle.
        """
        # Compute vectors
        v1v2 = v2 - v1
        v1v3 = v3 - v1
        v1p = point - v1

        # Compute dot products
        dot11 = v1v2.dot(v1v2)
        dot12 = v1v2.dot(v1v3)
        dot1p = v1v2.dot(v1p)
        dot22 = v1v3.dot(v1v3)
        dot2p = v1v3.dot(v1p)

        # Compute barycentric coordinates
        denom = dot11 * dot22 - dot12 * dot12
        if abs(denom) < 1e-10:
            return None  # Degenerate triangle

        v = (dot22 * dot1p - dot12 * dot2p) / denom
        w = (dot11 * dot2p - dot12 * dot1p) / denom
        u = 1.0 - v - w

        # Check if point is inside triangle
        if u >= 0 and v >= 0 and w >= 0:
            return (u, v, w)
        else:
            return None

    def enable_debug(self):
        """Enable debug mode for geometry operations"""
        self.debug_mode = True

    def disable_debug(self):
        """Disable debug mode"""
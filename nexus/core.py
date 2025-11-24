"""
Nexus Core: Physics ↔ Geometry ↔ Aesthetics Trinity
Unified feedback loop integrating Verlet physics, intelligent meshing, and aesthetic evaluation.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Callable, Optional, Tuple
import math
from geometry.surface_nets import IntelligentSurfaceNets, MeshData, GeometryStats
from aesthetics.pathway import AestheticPathway, AestheticEvaluation


# ============================================================================
# PHYSICS ENTITIES & STATE
# ============================================================================

@dataclass
class Vector3:
    """Lightweight 3D vector for physics calculations."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def add(self, v: 'Vector3') -> 'Vector3':
        return Vector3(self.x + v.x, self.y + v.y, self.z + v.z)

    def sub(self, v: 'Vector3') -> 'Vector3':
        return Vector3(self.x - v.x, self.y - v.y, self.z - v.z)

    def mult(self, s: float) -> 'Vector3':
        return Vector3(self.x * s, self.y * s, self.z * s)

    def dot(self, v: 'Vector3') -> float:
        return self.x * v.x + self.y * v.y + self.z * v.z

    def cross(self, v: 'Vector3') -> 'Vector3':
        return Vector3(
            self.y * v.z - self.z * v.y,
            self.z * v.x - self.x * v.z,
            self.x * v.y - self.y * v.x
        )

    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self) -> 'Vector3':
        mag = self.magnitude()
        if mag < 1e-9:
            return Vector3(0, 0, 0)
        return self.mult(1.0 / mag)

    def copy(self) -> 'Vector3':
        return Vector3(self.x, self.y, self.z)


@dataclass
class PhysicsBody:
    """A physical entity in the simulation."""
    id: int
    position: Vector3
    old_position: Vector3
    velocity: Vector3 = field(default_factory=lambda: Vector3())
    acceleration: Vector3 = field(default_factory=lambda: Vector3())
    mass: float = 1.0
    is_static: bool = False
    restitution: float = 0.8  # Bounciness
    friction: float = 0.99    # Damping
    radius: float = 1.0
    kinetic_energy: float = 0.0
    collision_count: int = 0


@dataclass
class CollisionInfo:
    """Information about a collision event."""
    body_id: int
    contact_point: Vector3
    normal: Vector3
    penetration_depth: float
    other_body_id: Optional[int] = None


@dataclass
class IntegratedOutput:
    """Unified output from physics→geometry→aesthetics pipeline."""
    mesh: MeshData
    geometry_stats: GeometryStats
    aesthetic_eval: AestheticEvaluation
    feedback_recommendations: dict
    physics_state: dict  # Kinetic energy, collision info, velocities
    frame_time: float = 0.0


# ============================================================================
# PHYSICS ENGINE COMPONENTS
# ============================================================================

class NexusPhysics:
    """Verlet-based physics engine with collision handling."""

    def __init__(self):
        self.gravity = Vector3(0.0, -9.81, 0.0)
        self.damping = 0.99

    def apply_force(self, body: PhysicsBody, force: Vector3) -> None:
        """F = ma -> a = F/m"""
        if body.is_static:
            return
        a = force.mult(1.0 / body.mass)
        body.acceleration = body.acceleration.add(a)

    def integrate_verlet(self, body: PhysicsBody, dt: float) -> None:
        """Verlet integration: x(t+dt) = 2x(t) - x(t-dt) + a*dt²"""
        if body.is_static:
            return

        # Derive velocity from position difference
        vel = body.position.sub(body.old_position).mult(body.friction)

        # Save old position
        old_pos = body.position.copy()

        # Update position
        new_pos = body.position.add(vel).add(body.acceleration.mult(dt * dt))
        body.position = new_pos
        body.old_position = old_pos

        # Reset acceleration
        body.acceleration = Vector3()

        # Update derived velocity for later use
        body.velocity = vel.mult(1.0 / dt) if dt > 0 else Vector3()

        # Calculate kinetic energy: KE = 0.5 * m * v²
        speed_sq = body.velocity.dot(body.velocity)
        body.kinetic_energy = 0.5 * body.mass * speed_sq


class NexusEvaluator:
    """World evaluation: collision detection, ray marching, field sampling."""

    def __init__(self):
        self.world_bounds = (Vector3(-100, -100, -100), Vector3(100, 100, 100))

    def raycast_terrain(
        self,
        origin: Vector3,
        direction: Vector3,
        max_distance: float = 100.0,
        world_fn: Optional[Callable] = None
    ) -> Optional[CollisionInfo]:
        """Ray march through the world to detect collisions."""
        current = origin.copy()
        dir_norm = direction.normalize()

        for step in range(int(max_distance * 10)):  # 10 samples per unit
            distance_traveled = step / 10.0

            if distance_traveled > max_distance:
                return None

            # If we have a world function (implicit surface), sample it
            if world_fn:
                sdf = world_fn(current)
                if sdf < 0.5:  # Hit
                    return CollisionInfo(
                        body_id=-1,
                        contact_point=current.copy(),
                        normal=self._estimate_normal(current, world_fn),
                        penetration_depth=0.5 - sdf
                    )

            current = current.add(dir_norm.mult(0.1))

        return None

    def _estimate_normal(self, point: Vector3, world_fn: Callable) -> Vector3:
        """Estimate surface normal via finite differences."""
        eps = 0.01
        dx = world_fn(point.add(Vector3(eps, 0, 0))) - world_fn(point.sub(Vector3(eps, 0, 0)))
        dy = world_fn(point.add(Vector3(0, eps, 0))) - world_fn(point.sub(Vector3(0, eps, 0)))
        dz = world_fn(point.add(Vector3(0, 0, eps))) - world_fn(point.sub(Vector3(0, 0, eps)))

        grad = Vector3(dx, dy, dz).mult(1.0 / (2 * eps))
        return grad.normalize()

    def sample_field(self, position: Vector3, field_fn: Optional[Callable] = None) -> float:
        """Sample a scalar field at a position (e.g., density, pressure)."""
        if field_fn:
            return field_fn(position)
        return 0.0


class NexusDiscern:
    """Collision detection and constraint resolution."""

    @staticmethod
    def detect_sphere_sphere(body1: PhysicsBody, body2: PhysicsBody) -> Optional[CollisionInfo]:
        """Sphere-sphere collision detection."""
        delta = body2.position.sub(body1.position)
        distance = delta.magnitude()
        min_distance = body1.radius + body2.radius

        if distance < min_distance:
            normal = delta.normalize() if distance > 1e-6 else Vector3(1, 0, 0)
            return CollisionInfo(
                body_id=body1.id,
                contact_point=body1.position.add(normal.mult(body1.radius)),
                normal=normal,
                penetration_depth=min_distance - distance,
                other_body_id=body2.id
            )
        return None

    @staticmethod
    def resolve_collision(body1: PhysicsBody, body2: PhysicsBody, collision: CollisionInfo) -> None:
        """Resolve sphere-sphere collision with restitution."""
        if body1.is_static and body2.is_static:
            return

        # Push bodies apart
        normal = collision.normal
        depth = collision.penetration_depth

        if not body1.is_static:
            body1.position = body1.position.sub(normal.mult(depth * 0.5))
        if not body2.is_static:
            body2.position = body2.position.add(normal.mult(depth * 0.5))

        # Relative velocity
        rel_vel = body1.velocity.sub(body2.velocity)
        vel_along_normal = rel_vel.dot(normal)

        # Only resolve if velocities are moving towards each other
        if vel_along_normal < 0:
            return

        # Restitution coefficient (combined bounciness)
        e = min(body1.restitution, body2.restitution)

        # Impulse scalar
        m1 = body1.mass if not body1.is_static else float('inf')
        m2 = body2.mass if not body2.is_static else float('inf')

        impulse = -(1 + e) * vel_along_normal / (1.0 / m1 + 1.0 / m2) if (m1 + m2) > 0 else 0

        # Apply impulse
        impulse_vec = normal.mult(impulse)
        if not body1.is_static:
            body1.velocity = body1.velocity.add(impulse_vec.mult(1.0 / m1))
        if not body2.is_static:
            body2.velocity = body2.velocity.sub(impulse_vec.mult(1.0 / m2))

        # Track collisions for aesthetics feedback
        body1.collision_count += 1
        body2.collision_count += 1


# ============================================================================
# NEXUS CORE: UNIFIED ORCHESTRATION
# ============================================================================

class NexusCore:
    """
    Director orchestrating Physics ↔ Geometry ↔ Aesthetics.
    Fixed-timestep loop decouples rendering from simulation.
    """

    def __init__(self):
        # The Trinity
        self.physics = NexusPhysics()
        self.evaluator = NexusEvaluator()
        self.discern = NexusDiscern()

        # Geometry & Aesthetics
        self.surface_nets_engine = IntelligentSurfaceNets
        self.aesthetic_pathway = AestheticPathway()

        # Simulation state
        self.entities: list[PhysicsBody] = []
        self.next_body_id = 0
        self.collisions: list[CollisionInfo] = []

        # Time management
        self.last_time = 0.0
        self.accumulator = 0.0
        self.time_step = 1.0 / 60.0  # 60 Hz physics
        self.iteration_count = 0

    def spawn_body(
        self,
        position: Vector3,
        velocity: Vector3 = None,
        mass: float = 1.0,
        radius: float = 1.0,
        is_static: bool = False,
        restitution: float = 0.8
    ) -> PhysicsBody:
        """Create a new physics body."""
        body = PhysicsBody(
            id=self.next_body_id,
            position=position.copy(),
            old_position=position.copy(),
            velocity=velocity.copy() if velocity else Vector3(),
            mass=mass,
            radius=radius,
            is_static=is_static,
            restitution=restitution
        )
        self.next_body_id += 1
        self.entities.append(body)
        return body

    def update_physics(self, dt: float) -> dict:
        """Execute one physics timestep (fixed)."""
        # STEP 1: Apply forces
        for body in self.entities:
            if not body.is_static:
                self.physics.apply_force(body, self.physics.gravity)

        # STEP 2: Integrate motion
        for body in self.entities:
            self.physics.integrate_verlet(body, dt)

        # STEP 3: Collision detection & resolution
        self.collisions.clear()
        for i, b1 in enumerate(self.entities):
            for j in range(i + 1, len(self.entities)):
                b2 = self.entities[j]
                collision = self.discern.detect_sphere_sphere(b1, b2)
                if collision:
                    self.collisions.append(collision)
                    self.discern.resolve_collision(b1, b2, collision)

        # Return physics state for aesthetics feedback
        return self._gather_physics_state()

    def _gather_physics_state(self) -> dict:
        """Collect physics metrics for aesthetic evaluation."""
        total_ke = sum(body.kinetic_energy for body in self.entities)
        total_collisions = sum(body.collision_count for body in self.entities)

        return {
            'total_kinetic_energy': total_ke,
            'avg_velocity': np.mean([b.velocity.magnitude() for b in self.entities]) if self.entities else 0.0,
            'collision_count': total_collisions,
            'active_bodies': len([b for b in self.entities if not b.is_static]),
            'max_velocity': max([b.velocity.magnitude() for b in self.entities]) if self.entities else 0.0
        }

    def process_physics_to_geometry(
        self,
        volume_data: np.ndarray,
        resolution: Tuple[int, int, int]
    ) -> IntegratedOutput:
        """
        Full pipeline: Physics influences geometry, geometry informs aesthetics.
        """
        frame_start = __import__('time').time()

        # STEP 1: Update physics
        physics_state = self.update_physics(self.time_step)

        # STEP 2: Modify volume based on kinetic energy (collision deformation)
        # High kinetic energy → compress/deform voxel volume
        volume_modified = self._deform_volume_by_physics(volume_data, physics_state)

        # STEP 3: Generate mesh from deformed volume
        surface_nets = self.surface_nets_engine(volume_modified, resolution)
        mesh = surface_nets.generate_mesh()
        geometry_stats = surface_nets.analyze_geometry()

        # STEP 4: Evaluate aesthetics with physics-informed parameters
        # Entropy influenced by collision intensity
        aesthetic_eval = self.aesthetic_pathway.evaluate(geometry_stats)

        # STEP 5: Generate feedback
        feedback = self._generate_integrated_feedback(
            geometry_stats,
            aesthetic_eval,
            physics_state
        )

        frame_time = __import__('time').time() - frame_start

        return IntegratedOutput(
            mesh=mesh,
            geometry_stats=geometry_stats,
            aesthetic_eval=aesthetic_eval,
            feedback_recommendations=feedback,
            physics_state=physics_state,
            frame_time=frame_time
        )

    def _deform_volume_by_physics(
        self,
        volume: np.ndarray,
        physics_state: dict
    ) -> np.ndarray:
        """Deform voxel volume based on kinetic energy and collisions."""
        modified = volume.copy()
        ke = physics_state['total_kinetic_energy']
        collision_count = physics_state['collision_count']

        # Soft compression: scale volume density by collision intensity
        # High collisions → more "damage" to geometry
        if collision_count > 0:
            compression_factor = max(0.7, 1.0 - (collision_count * 0.05))
            modified = modified * compression_factor

        # Entropy from kinetic motion: higher KE → more entropy injection
        if ke > 0:
            noise_scale = min(ke / 100.0, 0.3)
            noise = np.random.normal(0, noise_scale, modified.shape)
            modified = modified + noise
            modified = np.clip(modified, 0, 1)

        return modified

    def _generate_integrated_feedback(
        self,
        geometry_stats: GeometryStats,
        aesthetic_eval: AestheticEvaluation,
        physics_state: dict
    ) -> dict:
        """Generate recommendations from physics + geometry + aesthetics."""
        feedback = {
            'geometry_quality': self._evaluate_geometry_quality(geometry_stats),
            'aesthetic_quality': aesthetic_eval.beauty_score,
            'physics_intensity': self._evaluate_physics_intensity(physics_state),
            'refinement_suggestions': []
        }

        # Physics-aware smoothing
        if geometry_stats.entropy > 0.6 and physics_state['collision_count'] > 5:
            feedback['refinement_suggestions'].append({
                'action': 'stabilize_geometry',
                'reason': 'High entropy + collision damage detected',
                'priority': 'high'
            })

        # Aesthetic alignment with kinetic state
        if physics_state['total_kinetic_energy'] > 50 and aesthetic_eval.mood != 'energetic':
            feedback['refinement_suggestions'].append({
                'action': 'increase_saturation',
                'reason': 'High kinetic energy requires energetic aesthetics',
                'priority': 'medium'
            })

        feedback['overall_quality'] = np.mean([
            feedback['geometry_quality'],
            feedback['aesthetic_quality'],
            feedback['physics_intensity']
        ])

        return feedback

    def _evaluate_geometry_quality(self, stats: GeometryStats) -> float:
        """Score geometry (0-1)."""
        volume_bbox = np.prod(stats.bounds_max - stats.bounds_min)
        surface_area = stats.surface_area
        if volume_bbox < 1e-6:
            return 0.0
        ratio = surface_area / np.sqrt(volume_bbox)
        return float(np.clip(ratio / 10.0, 0.0, 1.0))

    def _evaluate_physics_intensity(self, physics_state: dict) -> float:
        """Score physics activity (0-1)."""
        ke = physics_state['total_kinetic_energy']
        collisions = physics_state['collision_count']
        # Normalize to 0-1 range
        ke_score = min(ke / 100.0, 1.0)
        collision_score = min(collisions / 20.0, 1.0)
        return float(np.mean([ke_score, collision_score]))

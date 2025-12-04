"""
PhysicsOrchestratorBridge - Bridge between MetaOrchestrator and physics engine.

Converts orchestrator semantic outputs to physics parameters:
- Token embeddings -> mass, velocity
- Decision type -> force profiles
- Render transforms -> body positioning
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple

# Note: physics.body module may provide RigidBody and Vector3 in the future
# for integration with a more advanced physics engine


@dataclass
class Vector3:
    """Simple 3D vector for physics calculations."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __mul__(self, scalar: float):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)


@dataclass
class PhysicsBody:
    """A physics body created from orchestrator state."""
    body_id: str
    mass: float
    position: Vector3
    velocity: Vector3
    restitution: float = 0.8
    gravity: float = 9.81
    is_static: bool = False
    
    # Integration state
    old_position: Vector3 = field(default_factory=lambda: Vector3())
    acceleration: Vector3 = field(default_factory=lambda: Vector3())
    kinetic_energy: float = 0.0


class PhysicsOrchestratorBridge:
    """Bridge between MetaOrchestrator and physics simulation."""
    
    def __init__(self):
        self.bodies: Dict[str, PhysicsBody] = {}
        self.integration_steps = 0
        self.time_step = 1.0 / 60.0
    
    def create_body_from_orchestrator(
        self, 
        body_id: str, 
        orchestrator_state: Dict[str, Any]
    ) -> PhysicsBody:
        """
        Create a physics body from orchestrator output.
        
        Args:
            body_id: Unique body identifier
            orchestrator_state: State from MetaOrchestrator.orchestrate()
        
        Returns:
            Created PhysicsBody
        """
        # Extract physics parameters
        physics_params = orchestrator_state.get('physics_params', {})
        render_transforms = orchestrator_state.get('render_transforms', {})
        
        # Get mass from physics params
        mass = physics_params.get('mass', 1.0)
        
        # Get velocity
        velocity_tuple = physics_params.get('velocity', (0, 0, 0))
        velocity = Vector3(velocity_tuple[0], velocity_tuple[1], velocity_tuple[2])
        
        # Get position from render transforms
        position_tuple = render_transforms.get('position', (0, 0, 0))
        position = Vector3(position_tuple[0], position_tuple[1], position_tuple[2])
        
        # Get restitution
        restitution = physics_params.get('restitution', 0.8)
        
        # Create body
        body = PhysicsBody(
            body_id=body_id,
            mass=mass,
            position=position,
            velocity=velocity,
            restitution=restitution,
            old_position=Vector3(position.x, position.y, position.z)
        )
        
        self.bodies[body_id] = body
        return body
    
    def apply_orchestrator_to_body(
        self,
        body_id: str,
        orchestrator_state: Dict[str, Any]
    ) -> Optional[PhysicsBody]:
        """Apply new orchestrator state to existing body."""
        body = self.bodies.get(body_id)
        if not body:
            return self.create_body_from_orchestrator(body_id, orchestrator_state)
        
        physics_params = orchestrator_state.get('physics_params', {})
        
        # Update velocity (as impulse)
        if 'velocity' in physics_params:
            v = physics_params['velocity']
            body.velocity = Vector3(v[0], v[1], v[2])
        
        # Update mass if changed
        if 'mass' in physics_params:
            body.mass = physics_params['mass']
        
        return body
    
    def step_simulation(self, dt: Optional[float] = None) -> Dict[str, Any]:
        """
        Step physics simulation forward.
        
        Args:
            dt: Time step (defaults to 1/60)
        
        Returns:
            Simulation state after step
        """
        dt = dt or self.time_step
        self.integration_steps += 1
        
        # Verlet integration for all bodies
        for body in self.bodies.values():
            if body.is_static:
                continue
            
            # Apply gravity
            body.acceleration = Vector3(0, -body.gravity, 0)
            
            # Verlet integration: x(t+dt) = 2*x(t) - x(t-dt) + a*dt^2
            vel = Vector3(
                body.position.x - body.old_position.x,
                body.position.y - body.old_position.y,
                body.position.z - body.old_position.z
            )
            
            new_pos = Vector3(
                body.position.x + vel.x + body.acceleration.x * dt * dt,
                body.position.y + vel.y + body.acceleration.y * dt * dt,
                body.position.z + vel.z + body.acceleration.z * dt * dt
            )
            
            body.old_position = body.position
            body.position = new_pos
            
            # Update velocity
            body.velocity = Vector3(vel.x / dt, vel.y / dt, vel.z / dt)
            
            # Calculate kinetic energy
            speed_sq = body.velocity.x**2 + body.velocity.y**2 + body.velocity.z**2
            body.kinetic_energy = 0.5 * body.mass * speed_sq
            
            # Ground collision (simple plane at y=0)
            if body.position.y < 0:
                body.position = Vector3(body.position.x, 0, body.position.z)
                # Bounce: reflect velocity and apply restitution
                # In Verlet, velocity is implicit from position difference
                # To bounce, we set old_position such that the next position difference
                # gives upward velocity
                current_vel_y = body.velocity.y
                bounced_vel_y = -current_vel_y * body.restitution
                # old_position.y should be: position.y - bounced_vel_y * dt
                body.old_position = Vector3(
                    body.old_position.x,
                    body.position.y - bounced_vel_y * dt,
                    body.old_position.z
                )
        
        return self._gather_state()
    
    def _gather_state(self) -> Dict[str, Any]:
        """Gather current simulation state."""
        total_ke = sum(b.kinetic_energy for b in self.bodies.values())
        
        return {
            'step': self.integration_steps,
            'total_kinetic_energy': total_ke,
            'body_count': len(self.bodies),
            'bodies': {
                bid: {
                    'position': b.position.to_tuple(),
                    'velocity': b.velocity.to_tuple(),
                    'kinetic_energy': b.kinetic_energy
                }
                for bid, b in self.bodies.items()
            }
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get physics system status."""
        return {
            'active_bodies': len(self.bodies),
            'total_integration_steps': self.integration_steps,
            'body_ids': list(self.bodies.keys())
        }


__all__ = ['PhysicsOrchestratorBridge', 'PhysicsBody', 'Vector3']

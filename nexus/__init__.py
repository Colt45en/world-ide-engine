"""
Nexus module - Core AI orchestration and physics engine.

Components:
- NexusCore: Physics engine with Verlet integration, collision detection
- NexusAgent: AI agent with perception-reasoning-action-learning loop
- QTP Bridge: Quantum Thought Pipeline for frame packet generation
- Bus Server: WebSocket server for real-time streaming
"""

from .core import (
    NexusCore,
    NexusPhysics,
    NexusEvaluator,
    NexusDiscern,
    Vector3,
    PhysicsBody,
    CollisionInfo,
    IntegratedOutput
)

__all__ = [
    'NexusCore',
    'NexusPhysics',
    'NexusEvaluator',
    'NexusDiscern',
    'Vector3',
    'PhysicsBody',
    'CollisionInfo',
    'IntegratedOutput'
]

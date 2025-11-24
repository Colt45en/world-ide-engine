"""
Nexus Physics API - FastAPI wrapper for NexusCore physics engine
Bridges the Keeper Nexus orchestration with physics→geometry→aesthetics pipeline
Connects to World Engine Studio React frontend
"""

import json
import time
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

# Try to import the physics engine, gracefully degrade if unavailable
PHYSICS_AVAILABLE = False
try:
    from nexus.core import NexusCore, Vector3, PhysicsBody
    PHYSICS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Physics engine not available: {e}")
    print("   Running in simulation mode (mock physics)")

# --- CONFIGURATION ---
app = FastAPI(title="Nexus Physics API", version="1.0")

# Allow React frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATA MODELS ---
class SpawnBodyRequest(BaseModel):
    """Request to spawn a physics body"""
    position: Dict[str, float]  # {x, y, z}
    velocity: Optional[Dict[str, float]] = None
    mass: float = 1.0
    radius: float = 1.0
    is_static: bool = False
    restitution: float = 0.8
    label: Optional[str] = None

class PhysicsStepRequest(BaseModel):
    """Request to step physics simulation"""
    dt: Optional[float] = None  # If None, uses fixed timestep

class PhysicsState(BaseModel):
    """Current physics simulation state"""
    frame: int
    total_kinetic_energy: float
    avg_velocity: float
    collision_count: int
    active_bodies: int
    max_velocity: float
    entities_count: int
    timestamp: float

# --- SIMULATION MANAGER ---
class SimulationManager:
    """Manages physics simulation state"""
    
    def __init__(self):
        self.nexus = NexusCore() if PHYSICS_AVAILABLE else None
        self.frame_count = 0
        self.start_time = time.time()
        self.entity_labels = {}  # id -> label mapping
        
    def is_healthy(self) -> bool:
        """Check if simulation is running"""
        return self.nexus is not None
    
    def spawn_body(self, request: SpawnBodyRequest) -> Dict[str, Any]:
        """Spawn a new physics body"""
        if not self.nexus:
            return self._mock_spawn(request)
        
        pos = Vector3(request.position.get('x', 0), 
                     request.position.get('y', 0), 
                     request.position.get('z', 0))
        vel = None
        if request.velocity:
            vel = Vector3(request.velocity.get('x', 0),
                         request.velocity.get('y', 0),
                         request.velocity.get('z', 0))
        
        body = self.nexus.spawn_body(
            position=pos,
            velocity=vel,
            mass=request.mass,
            radius=request.radius,
            is_static=request.is_static,
            restitution=request.restitution
        )
        
        # Track label
        self.entity_labels[body.id] = request.label or f"Body_{body.id}"
        
        return {
            "id": body.id,
            "label": self.entity_labels[body.id],
            "position": {"x": body.position.x, "y": body.position.y, "z": body.position.z},
            "mass": body.mass,
            "radius": body.radius,
            "is_static": body.is_static
        }
    
    def _mock_spawn(self, request: SpawnBodyRequest) -> Dict[str, Any]:
        """Mock body spawn when physics unavailable"""
        body_id = self.frame_count
        self.frame_count += 1
        label = request.label or f"Body_{body_id}"
        self.entity_labels[body_id] = label
        
        return {
            "id": body_id,
            "label": label,
            "position": request.position,
            "mass": request.mass,
            "radius": request.radius,
            "is_static": request.is_static,
            "mock": True
        }
    
    def step_physics(self, dt: Optional[float] = None) -> PhysicsState:
        """Step the physics simulation"""
        if self.nexus:
            physics_state = self.nexus.update_physics(dt or self.nexus.time_step)
        else:
            # Mock state
            physics_state = {
                'total_kinetic_energy': 5.0 + (self.frame_count % 10) * 0.5,
                'avg_velocity': 0.5,
                'collision_count': self.frame_count % 5,
                'active_bodies': 5,
                'max_velocity': 2.5
            }
        
        self.frame_count += 1
        
        return PhysicsState(
            frame=self.frame_count,
            total_kinetic_energy=physics_state['total_kinetic_energy'],
            avg_velocity=physics_state['avg_velocity'],
            collision_count=physics_state['collision_count'],
            active_bodies=physics_state['active_bodies'],
            max_velocity=physics_state['max_velocity'],
            entities_count=len(self.nexus.entities) if self.nexus else len(self.entity_labels),
            timestamp=time.time() - self.start_time
        )
    
    def get_state(self) -> PhysicsState:
        """Get current physics state without stepping"""
        if self.nexus:
            physics_state = self.nexus._gather_physics_state()
        else:
            physics_state = {
                'total_kinetic_energy': 5.0,
                'avg_velocity': 0.5,
                'collision_count': 0,
                'active_bodies': len(self.entity_labels),
                'max_velocity': 2.5
            }
        
        return PhysicsState(
            frame=self.frame_count,
            total_kinetic_energy=physics_state['total_kinetic_energy'],
            avg_velocity=physics_state['avg_velocity'],
            collision_count=physics_state['collision_count'],
            active_bodies=physics_state['active_bodies'],
            max_velocity=physics_state['max_velocity'],
            entities_count=len(self.nexus.entities) if self.nexus else len(self.entity_labels),
            timestamp=time.time() - self.start_time
        )
    
    def get_entities(self) -> List[Dict[str, Any]]:
        """Get all entities"""
        if not self.nexus:
            return []
        
        entities = []
        for body in self.nexus.entities:
            entities.append({
                "id": body.id,
                "label": self.entity_labels.get(body.id, f"Body_{body.id}"),
                "position": {
                    "x": body.position.x,
                    "y": body.position.y,
                    "z": body.position.z
                },
                "velocity": {
                    "x": body.velocity.x,
                    "y": body.velocity.y,
                    "z": body.velocity.z
                },
                "mass": body.mass,
                "radius": body.radius,
                "kinetic_energy": body.kinetic_energy,
                "collision_count": body.collision_count,
                "is_static": body.is_static
            })
        
        return entities

# Global simulation instance
simulation = SimulationManager()

# --- API ENDPOINTS ---

@app.get("/")
def read_root():
    """Health check"""
    return {
        "status": "Nexus Physics API Online",
        "physics_available": PHYSICS_AVAILABLE,
        "simulation_mode": "real" if PHYSICS_AVAILABLE else "mock"
    }

@app.get("/health")
def health():
    """Health status"""
    return {
        "physics_enabled": simulation.is_healthy(),
        "frame_count": simulation.frame_count,
        "entities": len(simulation.entity_labels)
    }

@app.post("/physics/spawn")
def spawn_body(request: SpawnBodyRequest):
    """Spawn a new physics body"""
    try:
        result = simulation.spawn_body(request)
        return {"success": True, "body": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/physics/step")
def step_physics(request: PhysicsStepRequest):
    """Step the physics simulation"""
    try:
        state = simulation.step_physics(request.dt)
        return {"success": True, "state": state}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/physics/state")
def get_physics_state():
    """Get current physics state"""
    try:
        state = simulation.get_state()
        return {"success": True, "state": state}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/physics/entities")
def get_entities():
    """Get all entities in simulation"""
    try:
        entities = simulation.get_entities()
        return {"success": True, "entities": entities}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/physics/reset")
def reset_simulation():
    """Reset the simulation"""
    global simulation
    simulation = SimulationManager()
    return {"success": True, "message": "Simulation reset"}

# --- KEEPER NEXUS INTEGRATION ---

@app.post("/prophecy/apply_physics")
def apply_physics_prophecy(prophecy: str = Body(..., embed=True)):
    """
    Apply a prophecy as a physics force or parameter change.
    Example: 'apply_force_y:10' -> apply 10N upward force
    """
    try:
        # Parse prophecy directives
        if prophecy.startswith("apply_force_"):
            # Format: apply_force_x:5 or apply_force_y:10
            parts = prophecy.split(":")
            if len(parts) == 2:
                axis = parts[0].split("_")[2]  # x, y, or z
                magnitude = float(parts[1])
                
                # For demo: just update gravity in active bodies
                if simulation.nexus:
                    for body in simulation.nexus.entities:
                        if not body.is_static:
                            if axis == 'x':
                                force = Vector3(magnitude, 0, 0)
                            elif axis == 'y':
                                force = Vector3(0, magnitude, 0)
                            else:
                                force = Vector3(0, 0, magnitude)
                            simulation.nexus.physics.apply_force(body, force)
                
                return {
                    "success": True,
                    "prophecy": prophecy,
                    "action": f"Applied force {magnitude}N on axis {axis}"
                }
        
        return {"success": False, "message": "Unknown prophecy format"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🌀 NEXUS PHYSICS API INITIATED...")
    print(f"📊 Physics Available: {PHYSICS_AVAILABLE}")
    print("🚀 Starting on http://0.0.0.0:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)

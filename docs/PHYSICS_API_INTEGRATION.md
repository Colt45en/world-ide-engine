# Physics API Integration Guide

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Studio (Frontend)                  │
│  - Node graph visualization                                 │
│  - Performance monitoring                                   │
│  - Terminal commands                                        │
│  - Integrated with usePhysicsAPI hooks                      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           Nexus Physics API (FastAPI on :8001)              │
│  - /physics/spawn    - Create new physics body              │
│  - /physics/step     - Advance simulation                   │
│  - /physics/state    - Get current metrics                  │
│  - /physics/entities - List all bodies                      │
│  - /prophecy/apply_physics - Keeper Nexus integration       │
└────────────────────────┬────────────────────────────────────┘
                         │ Python API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           NexusCore Physics Engine (nexus/core.py)          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ NexusPhysics │  │ NexusEvaluator│  │NexusDiscern  │      │
│  │  - Verlet    │  │ - Raycast     │  │ - Collision  │      │
│  │  - Forces    │  │ - Sampling    │  │ - Resolution │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
           │
           ├──────────────► geometry.surface_nets (IntelligentSurfaceNets)
           └──────────────► aesthetics.pathway (AestheticPathway)
```

## Quick Start

### 1. Start the Physics API

```bash
cd c:\fresh-world-engine
python api/nexus_physics_api.py
# Server running on http://0.0.0.0:8001
```

### 2. Update .env for React Studio

```bash
# .env or .env.local in React app
REACT_APP_PHYSICS_API=http://localhost:8001
```

### 3. Use Physics in Studio Components

```jsx
import { usePhysicsSimulation } from './usePhysicsAPI';

function PhysicsPanel() {
  const {
    isConnected,
    physicsState,
    entities,
    spawnBody,
    stepSimulation,
  } = usePhysicsSimulation();

  return (
    <div>
      <h2>Physics Status: {isConnected ? '🟢 Connected' : '🔴 Offline'}</h2>
      
      {physicsState && (
        <div>
          <p>Frame: {physicsState.frame}</p>
          <p>Kinetic Energy: {physicsState.total_kinetic_energy.toFixed(2)}</p>
          <p>Collisions: {physicsState.collision_count}</p>
          <p>Bodies: {physicsState.entities_count}</p>
        </div>
      )}
      
      <button onClick={() => spawnBody({x: 0, y: 5, z: 0}, 'Sphere')}>
        Spawn Body
      </button>
      
      <button onClick={stepSimulation}>
        Step Physics
      </button>
    </div>
  );
}
```

## API Endpoints Reference

### POST /physics/spawn
**Spawn a new physics body**

Request:
```json
{
  "position": {"x": 0, "y": 5, "z": 0},
  "velocity": {"x": 1, "y": 0, "z": 0},
  "mass": 1.0,
  "radius": 1.0,
  "is_static": false,
  "restitution": 0.8,
  "label": "MyBody"
}
```

Response:
```json
{
  "success": true,
  "body": {
    "id": 0,
    "label": "MyBody",
    "position": {"x": 0, "y": 5, "z": 0},
    "mass": 1.0,
    "radius": 1.0,
    "is_static": false
  }
}
```

### POST /physics/step
**Advance physics simulation by one timestep (1/60 second)**

Request:
```json
{
  "dt": null
}
```

Response:
```json
{
  "success": true,
  "state": {
    "frame": 42,
    "total_kinetic_energy": 12.5,
    "avg_velocity": 0.75,
    "collision_count": 2,
    "active_bodies": 5,
    "max_velocity": 2.5,
    "entities_count": 5,
    "timestamp": 0.7
  }
}
```

### GET /physics/state
**Get current simulation state without stepping**

Response:
```json
{
  "success": true,
  "state": {
    "frame": 42,
    "total_kinetic_energy": 12.5,
    "avg_velocity": 0.75,
    "collision_count": 2,
    "active_bodies": 5,
    "max_velocity": 2.5,
    "entities_count": 5,
    "timestamp": 0.7
  }
}
```

### GET /physics/entities
**Get all physics bodies in simulation**

Response:
```json
{
  "success": true,
  "entities": [
    {
      "id": 0,
      "label": "MyBody",
      "position": {"x": 0.1, "y": 4.95, "z": 0},
      "velocity": {"x": 1.0, "y": -0.05, "z": 0},
      "mass": 1.0,
      "radius": 1.0,
      "kinetic_energy": 0.5,
      "collision_count": 0,
      "is_static": false
    }
  ]
}
```

### POST /physics/reset
**Clear all entities and reset simulation**

Response:
```json
{
  "success": true,
  "message": "Simulation reset"
}
```

### POST /prophecy/apply_physics
**Apply a prophecy directive (Keeper Nexus integration)**

Request:
```json
{
  "prophecy": "apply_force_y:10"
}
```

Supported prophecies:
- `apply_force_x:MAGNITUDE` - Apply force on X axis
- `apply_force_y:MAGNITUDE` - Apply force on Y axis (e.g., `apply_force_y:5`)
- `apply_force_z:MAGNITUDE` - Apply force on Z axis

Response:
```json
{
  "success": true,
  "prophecy": "apply_force_y:10",
  "action": "Applied force 10N on axis y"
}
```

## Integration with Studio Node Graph

Map physics entities to visual nodes:

```jsx
// In your NodeGraph component
useEffect(() => {
  const pollPhysics = async () => {
    const { entities } = usePhysicsSimulation();
    
    // Convert physics entities to node graph nodes
    const visualNodes = entities.map(entity => ({
      id: entity.id,
      label: entity.label,
      x: (entity.position.x + 10) * 40,  // Scale to canvas
      y: (entity.position.y + 10) * 40,
      vx: entity.velocity.x * 0.1,
      vy: entity.velocity.y * 0.1,
      radius: entity.radius * 5,
      type: entity.kinetic_energy > 5 ? 'active' : 'idle',
      collisions: entity.collision_count,
    }));
    
    setNodes(visualNodes);
  };
  
  const interval = setInterval(pollPhysics, 16); // ~60 FPS
  return () => clearInterval(interval);
}, [entities]);
```

## Environment Notes

### Python 3.12 Compatibility
- Python 3.12.7 has a typing.py regression that prevents numpy/scipy from importing
- The API gracefully degrades to **mock physics mode** when imports fail
- Both real and mock modes expose identical REST interfaces
- To use real physics: Install Python 3.12 or earlier, or wait for numpy Python 3.12 fix

### Running in Mock Mode
When physics engine unavailable, the API:
- Still responds to all endpoints with realistic data
- Allows React Studio to develop UI without physics
- Returns simulated physics state (kinetic energy, collisions, etc.)
- Tracks spawned bodies and maintains state

## Terminal Commands Integration

```jsx
// In Studio executeCommand()
case 'physics':
  executeCommand('physics spawn 0 5 0');  // x y z
  break;

case 'physics':
  const [, cmd, ...args] = cmdStr.split(' ');
  
  if (cmd === 'spawn') {
    const [x, y, z] = args.map(Number);
    await spawnBody({x, y, z}, `Spawned_${Date.now()}`);
    addLog(`Spawned physics body at (${x}, ${y}, ${z})`, 'success');
  }
  
  if (cmd === 'step') {
    await stepSimulation();
    addLog(`Physics frame: ${physicsState.frame}`, 'info');
  }
  break;
```

## Performance Monitoring Integration

Wire physics metrics into Studio performance panel:

```jsx
// Use physics state in PerformancePanel
const PhysicsMetrics = ({ physicsState }) => {
  if (!physicsState) return null;
  
  return (
    <div>
      <h3>Physics Engine</h3>
      <div>KE: {physicsState.total_kinetic_energy.toFixed(1)} J</div>
      <div>Vel Avg: {physicsState.avg_velocity.toFixed(2)} m/s</div>
      <div>Collisions: {physicsState.collision_count}</div>
      <div>Frame: {physicsState.frame} @ {physicsState.timestamp.toFixed(2)}s</div>
    </div>
  );
};
```


# 🏗️ Fresh World Engine Architecture

This document describes the overall architecture of the Fresh World Engine.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FRESH WORLD ENGINE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   STUDIO LAYER  │    │   GAME LAYER    │    │  PREFAB LAYER   │          │
│  │  (Dashboards)   │    │   (Playables)   │    │  (Construction) │          │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘          │
│           │                      │                      │                    │
│           └──────────────────────┼──────────────────────┘                    │
│                                  │                                           │
│                         ┌────────▼────────┐                                  │
│                         │    BUS LAYER    │                                  │
│                         │ (Event System)  │                                  │
│                         └────────┬────────┘                                  │
│                                  │                                           │
│           ┌──────────────────────┼──────────────────────┐                    │
│           │                      │                      │                    │
│  ┌────────▼────────┐    ┌────────▼────────┐    ┌────────▼────────┐          │
│  │   NEXUS CORE    │    │  WORLD ENGINE   │    │   META LAYER    │          │
│  │  (Simulation)   │    │   (Physics)     │    │  (AI/Thought)   │          │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘          │
│           │                      │                      │                    │
│           └──────────────────────┼──────────────────────┘                    │
│                                  │                                           │
│                         ┌────────▼────────┐                                  │
│                         │  BACKEND LAYER  │                                  │
│                         │ (WebSocket/API) │                                  │
│                         └─────────────────┘                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Layer Descriptions

### 1. Studio Layer (`studio/`)
The development environment and tools.

| Component | File | Purpose |
|-----------|------|---------|
| World Engine Studio | `world-engine-studio.html` | Master control center |
| Game Hub | `game-hub.html` | Game launcher & catalog |
| World Layer | `nexus-world-layer.html` | 3D viewport with WebSocket |
| Game Environment | `game-environment.html` | Development playground |
| Map Bus | `map-orchestrator-bus.html` | Tile/chunk management |
| Settings Hub | `nexus-settings-hub.html` | System configuration |
| Story IDE | `story-ide.html` | Narrative writing tool |
| Math Center | `nexus-forge-mathematical-control-center.html` | Mathematical visualization |

### 2. Game Layer (`game/`)
Playable games and interactive sandboxes.

| Component | File | Purpose |
|-----------|------|---------|
| Tool Sandbox | `toolsandbox.html` | 3D mesh builder |
| Cosmic Tunnel | `cosmic-tunnel.html` | Space visualization |
| Cultivation Combat | `cultivation_combat_game.html` | Combat game |
| VFX Test | `vfx-test.html` | Visual effects testing |

### 3. Prefab Layer (`prefab/`)
Avatar and model construction tools.

| Component | File | Purpose |
|-----------|------|---------|
| CAD Core | `nexus_cad_core.html` | CAD-style body editor |
| Creature Rig | `creature-rig-sandbox.html` | Rigging tools |
| Anatomy Assembler | `anatomy_assembler.html` | Body assembly |
| GLB Exporter | `glb_exporter.html` | Model export |

### 4. Bus Layer (`src/buses/`)
Event-driven communication system.

```
┌─────────────────────────────────────────────────────────┐
│                     BUS ARCHITECTURE                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  MapBus  │  │GraphicsBus│ │ EventBus │  │EntityBus │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
│       │             │             │             │        │
│       └─────────────┴─────────────┴─────────────┘        │
│                          │                               │
│                    ┌─────▼─────┐                         │
│                    │ Bus Core  │                         │
│                    │(Pub/Sub)  │                         │
│                    └───────────┘                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**MapBus** - Tile and chunk operations
- `tile:create`, `tile:update`, `tile:delete`
- `chunk:load`, `chunk:unload`
- `zone:define`, `zone:enter`, `zone:exit`

**GraphicsBus** - Rendering pipeline
- `render:frame`, `render:resize`
- `shader:compile`, `shader:apply`
- `texture:load`, `texture:bind`

**EventBus** - Game events
- `game:start`, `game:pause`, `game:end`
- `entity:spawn`, `entity:destroy`
- `input:keydown`, `input:keyup`

**EntityBus** - Entity lifecycle
- `entity:create`, `entity:update`, `entity:delete`
- `component:add`, `component:remove`
- `system:tick`

### 5. Nexus Core (`nexus/`, `src/nexus.ts`)
World simulation and sacred geometry.

```typescript
// Core Classes in src/nexus.ts
class GoldenGlyph {
    // Sacred geometry symbols
    // Position, rotation, frequency
}

class GoldString {
    // Resonance pathways between glyphs
    // Energy flow, connections
}

class TerrainNode {
    // World terrain data
    // Height, biome, resources
}

class GridEntity {
    // Entity in the world grid
    // Position, components, state
}

class Nexus {
    // Main world container
    // Glyphs, strings, entities
}
```

### 6. World Engine (`backend/`, `physics/`)
Physics simulation and world state.

**API Endpoints:**
```
GET  /api/entities      - List all entities
POST /api/entities      - Create entity
GET  /api/physics/step  - Advance simulation
POST /api/world/load    - Load world state
```

### 7. Meta Layer (`meta/`)
AI reasoning and orchestration.

| Component | Purpose |
|-----------|---------|
| Thought Engine | AI reasoning system |
| Tensor Room | Tensor operations |
| Token Lab | NLP embeddings |
| Orchestrator | System coordination |

---

## Communication Protocols

### WebSocket (Real-time)
```
ws://localhost:8765 - Nexus WebSocket Server

Messages:
→ { type: 'entity:spawn', data: {...} }
← { type: 'entity:spawned', id: '...', data: {...} }
→ { type: 'world:sync' }
← { type: 'world:state', entities: [...], glyphs: [...] }
```

### HTTP API (Request/Response)
```
http://localhost:8001 - World Engine API (FastAPI)

POST /api/physics/step
{
    "deltaTime": 0.016,
    "entities": [...]
}
```

### iframe postMessage (Cross-window)
```javascript
// Parent → Child
iframe.contentWindow.postMessage({
    type: 'entity:update',
    entity: {...}
}, '*');

// Child → Parent
parent.postMessage({
    type: 'event:triggered',
    event: 'player:death'
}, '*');
```

---

## Data Flow Example

```
User Action → Bus Event → System Handler → State Update → Render
     │            │              │              │           │
     │            │              │              │           │
     ▼            ▼              ▼              ▼           ▼
[Click tile]  [MapBus]     [TileSystem]   [WorldState]  [Canvas]
              emit()        process()       update()     draw()
```

---

## File Organization

```
fresh-world-engine/
├── studio/           # Development dashboards
├── game/             # Playable games
├── prefab/           # Model construction
├── nexus/            # Nexus ecosystem
├── meta/             # AI & meta-systems
├── src/              # TypeScript source
│   ├── buses/        # Event buses
│   ├── engine/       # Game engine
│   ├── components/   # React components
│   └── nexus.ts      # Core module
├── backend/          # Python API
├── apps/             # Standalone demos
├── docs/             # Documentation
├── config/           # Configuration
├── assets/           # Static assets
└── archive/          # Historical docs
```

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML5, TypeScript, React, Three.js |
| Styling | Tailwind CSS |
| Build | Vite |
| Backend | Python, FastAPI |
| Real-time | WebSocket |
| Database | SQLite (Keeper) |
| Testing | Jest, Vitest, Pytest |

---

## Extension Points

### Adding a New Bus
```javascript
class CustomBus extends EventEmitter {
    constructor() {
        super();
        this.name = 'CustomBus';
    }
    
    emit(event, data) {
        super.emit(event, { ...data, timestamp: Date.now() });
    }
}
```

### Adding a New Dashboard
1. Create `studio/my-dashboard.html`
2. Include navigation bar with shortcuts
3. Register in navigation maps
4. Add to `game-hub.html` if applicable

### Adding a New Entity Type
```typescript
class MyEntity extends GridEntity {
    customProperty: string;
    
    update(deltaTime: number) {
        // Custom logic
    }
}
```

---

## Performance Considerations

- **Rendering**: Use requestAnimationFrame, batch draw calls
- **Physics**: Fixed timestep simulation (16ms)
- **WebSocket**: Debounce rapid updates
- **State**: Immutable updates, selective re-renders
- **Memory**: Pool objects, avoid allocations in hot paths

---

## Related Documentation

- [README.md](./README.md) - Project overview
- [GETTING_STARTED.md](./GETTING_STARTED.md) - Quick start guide
- [docs/API.md](./docs/API.md) - API reference
- [docs/BUS_SPECIFICATION.md](./docs/BUS_SPECIFICATION.md) - Bus details

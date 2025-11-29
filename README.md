# 🌍 Fresh World Engine

A comprehensive game development and world simulation platform featuring recursive agent systems, mathematical visualization, physics integration, and modular architecture.

---

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open browser to http://localhost:5173
```

**Alternative - Static Server:**
```bash
python -m http.server 8080
# Open http://localhost:8080/studio/world-engine-studio.html
```

---

## 📁 Project Structure

```
fresh-world-engine/
├── 📂 studio/              # Main development dashboards (START HERE)
│   ├── world-engine-studio.html    # Master control center
│   ├── game-hub.html               # Game launcher & catalog
│   ├── nexus-world-layer.html      # 3D world viewport
│   ├── game-environment.html       # Game dev environment
│   ├── map-orchestrator-bus.html   # Map & tile system
│   ├── nexus-settings-hub.html     # Central settings
│   ├── story-ide.html              # Story writing IDE
│   └── ...more tools
│
├── 📂 game/                # Playable games & sandboxes
│   ├── toolsandbox.html           # 3D mesh builder
│   ├── cosmic-tunnel.html         # Space visualization
│   ├── cultivation_combat_game.html
│   └── ...more games
│
├── 📂 prefab/              # Avatar & body construction
│   ├── nexus_cad_core.html        # CAD-style body editor
│   ├── creature-rig-sandbox.html  # Rigging tools
│   ├── anatomy_assembler.html     # Body assembly
│   └── glb_exporter.html          # Model export
│
├── 📂 nexus/               # Nexus ecosystem
│   ├── audio_sacred_geometry.html # Audio-reactive visuals
│   ├── tensor.html                # Tensor operations
│   ├── keeper_control_plane.html  # System control
│   └── api/                       # Backend API
│
├── 📂 meta/                # Meta-systems & AI
│   ├── tensor_room.html           # Tensor lab
│   ├── token_embedding_lab.html   # NLP tools
│   ├── thought-engine/            # AI reasoning
│   └── orchestrator.py            # System orchestrator
│
├── 📂 apps/                # Standalone demos & tools
│   ├── demos/                     # Visual demonstrations
│   └── tools/                     # Utility applications
│
├── 📂 src/                 # TypeScript/React source
│   ├── nexus.ts                   # Core Nexus module
│   ├── components/                # React components
│   ├── engine/                    # Game engine
│   └── buses/                     # Event bus system
│
├── 📂 docs/                # Documentation
│   ├── ARCHITECTURE.md            # System architecture
│   ├── API.md                     # API reference
│   └── architecture/              # Detailed specs
│
├── 📂 archive/             # Historical documents (not needed for dev)
│   ├── phase-reports/             # Development phases
│   ├── integration-docs/          # Integration history
│   └── completion-reports/        # Milestone reports
│
├── 📂 config/              # Configuration files
├── 📂 assets/              # Static assets (images, sounds)
└── 📂 backend/             # Python backend services
```

---

## 🎮 Main Entry Points

| Entry Point | Description | URL |
|------------|-------------|-----|
| **World Engine Studio** | Master dashboard & control center | `/studio/world-engine-studio.html` |
| **Game Hub** | Play & launch all games | `/studio/game-hub.html` |
| **World Layer** | 3D world viewport with WebSocket | `/studio/nexus-world-layer.html` |
| **Settings Hub** | Configure all systems | `/studio/nexus-settings-hub.html` |
| **Story IDE** | Write narratives & stories | `/studio/story-ide.html` |

---

## ⌨️ Keyboard Shortcuts

Navigate anywhere with these shortcuts:

| Shortcut | Destination |
|----------|-------------|
| `Esc` | World Engine Studio (Home) |
| `Ctrl+1` | Math Center |
| `Ctrl+2` | Orchestrator |
| `Ctrl+3` | Map Bus |
| `Ctrl+4` | Game Environment |
| `Ctrl+5` | Keeper IDE |
| `Ctrl+6` | Simulator |
| `Ctrl+7` | World Layer |
| `Ctrl+8` | Game Hub |
| `Ctrl+9` | Settings Hub |
| `Ctrl+0` | Story IDE |

---

## 🔧 Core Systems

### Bus Architecture
The engine uses an event-driven bus system for communication:

- **MapBus** - Tile/chunk/zone management
- **GraphicsBus** - Rendering pipeline
- **EventBus** - Game events & triggers
- **EntityBus** - Entity lifecycle management

### WebSocket Integration
Real-time communication via WebSocket:
```
ws://localhost:8765  - Nexus WebSocket server
http://localhost:8001 - World Engine API (FastAPI)
```

### Nexus Module (TypeScript)
Core world simulation classes in `src/nexus.ts`:
- `GoldenGlyph` - Sacred geometry symbols
- `GoldString` - Resonance pathways
- `TerrainNode` - World terrain data
- `GridEntity` - Entity management
- `Nexus` - Main world container

---

## 🎨 Module Categories

### Sound & Frequency
- `apps/demos/vibe_engine_nexus_demo.html` - Audio engine
- `nexus/audio_sacred_geometry.html` - Sacred geometry audio
- `apps/demos/letter_note_demo.html` - Musical notation

### Graphics & Rendering
- `apps/demos/lighting_time_demo.html` - Lighting system
- `graphics/` - Graphics subsystems
- `vfx/` - Visual effects

### Memory & AI
- `meta/thought-engine/` - AI reasoning system
- `meta/tensor_room.html` - Tensor operations
- `knowledge/` - Knowledge graph

### World Building
- `studio/terrain-world-builder.html` - Terrain editor
- `game/toolsandbox.html` - 3D mesh builder
- `prefab/` - Prefab construction tools

---

## 🛠️ Development

### Prerequisites
- Node.js 18+
- Python 3.10+ (for backend)
- npm or pnpm

### Backend Services
```bash
# Start Nexus WebSocket server
python nexus/bus_server.py

# Start World Engine API
cd backend && uvicorn main:app --reload --port 8001
```

### Frontend Development
```bash
npm run dev        # Vite dev server
npm run build      # Production build
npm run test       # Run tests
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System architecture overview |
| [docs/API.md](./docs/API.md) | API reference |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Contribution guidelines |
| [docs/QUICK_START.md](./docs/QUICK_START.md) | Getting started guide |

---

## 🗄️ Archive

Historical documents are in `archive/` for reference:
- `archive/phase-reports/` - Development phase documentation
- `archive/integration-docs/` - Integration history
- `archive/completion-reports/` - Milestone completions

---

## 📜 License

See [LICENSE](./LICENSE) for details.

---

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

*Built with Three.js, React, TypeScript, FastAPI, and WebSockets*

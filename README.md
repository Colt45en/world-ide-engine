# 🌍 Fresh World Engine

> **A Biomimetic AI Platform for Autonomous World-Building**

[![Version](https://img.shields.io/badge/version-3.1.0-blue.svg)]()
[![Python](https://img.shields.io/badge/python-3.12-yellow.svg)]()
[![C++](https://img.shields.io/badge/C++-17-orange.svg)]()

---

## 📚 Core Documentation

| Document | Purpose |
|----------|---------|
| **[NEXUS_AI_BLUEPRINT.md](docs/core/NEXUS_AI_BLUEPRINT.md)** | Complete technical specification |
| **[STARTUP_GUIDE.md](docs/core/STARTUP_GUIDE.md)** | Get running in 2 minutes |
| **[ARCHITECTURE.md](docs/core/ARCHITECTURE.md)** | Deep-dive into components |

---

## ⚡ Quick Start (2 Minutes)

```powershell
# Terminal 1: Start the Brain (launches everything)
py -3.12 nexus_swarm/nexus_trainer_loop.py

# Terminal 2: Start HTTP Server
py -3.12 -m http.server 8888

# Open browser
start http://localhost:8888/nexus_analytics_dashboard.html
```

**That's it!** See [STARTUP_GUIDE.md](docs/core/STARTUP_GUIDE.md) for details.

---

## 🧬 System Overview

| Component | Language | Port | Purpose |
|-----------|----------|------|---------|
| 🧠 **Nucleus Eye** | Python | 8765 | Central nervous system |
| 👁️ **NovaOmega** | C++ | - | Context management |
| 🐝 **SwarmMind** | Python | - | 9 autonomous agents |
| 🎵 **Holy Beat** | C++ | - | Audio→Tensor pipeline |
| 🧮 **Tensor Core** | C++ | 8085 | Mathematical resonance |

---

## 🐝 The 9 Agents

| Agent | Role | Agent | Role |
|-------|------|-------|------|
| 🔮 Oracle | Strategy | 🎓 Trainer | ML Training |
| 🎯 Strategist | Planning | 🔍 Auditor | Code Review |
| 🏗️ Architect | Design | 🧪 Tester | QA |
| 💻 Coder | Implementation | 🎨 Designer | UI/Assets |
| 🧹 Janitor | Maintenance | | |

---

## 📁 Key Files

```
fresh-world-engine/
├── nexus_swarm/
│   └── nexus_trainer_loop.py   ← MAIN ENTRY POINT
├── nucleus/
│   ├── nova_omega.cpp          ← C++ cognitive core
│   └── NexusHolyBeatSystem.hpp ← Audio pipeline
├── docs/core/
│   ├── NEXUS_AI_BLUEPRINT.md   ← Full specification
│   ├── STARTUP_GUIDE.md        ← Quick start
│   └── ARCHITECTURE.md         ← Technical deep-dive
└── config/
    └── nexus_config.json       ← System configuration
```

---

## 🔌 Service Ports

| Port | Service | Protocol |
|------|---------|----------|
| **8765** | Python Brain | WebSocket |
| **8085** | C++ Tensor | WebSocket |
| **8888** | HTTP Server | HTTP |
| **8002** | ChromaDB | HTTP |

---

## 🌐 Dashboards

| Dashboard | URL |
|-----------|-----|
| Analytics | http://localhost:8888/nexus_analytics_dashboard.html |
| Resonance | http://localhost:8888/nexus_resonance_interface.html |
| Scheduler | http://localhost:8888/nexus_scheduler.html |

---

## 📖 Additional Documentation

### Access Dashboards

| Dashboard | URL | Purpose |
|-----------|-----|---------|
| Analytics | http://localhost:8888/nexus_analytics_dashboard.html | Real-time metrics |
| Resonance | http://localhost:8888/nexus_resonance_interface.html | Tensor visualization |
| Viz | http://localhost:8888/nexus_viz_dashboard.html | System overview |
| Studio | http://localhost:8888/studio/world-engine-studio.html | World editor |

### Service Ports

| Port | Service | Protocol |
|------|---------|----------|
| 8085 | Nexus WebSocket Server (C++) | WebSocket |
| 8765 | Python Bridge | WebSocket |
| 8888 | HTTP File Server | HTTP |
| 8001 | Docker Sandbox | HTTP |
| 8002 | ChromaDB (Vector Memory) | HTTP |
| 3001 | Nucleus API | HTTP |

---

## 🧠 Nucleus Nexus AI

The core C++ reasoning engine with real-time WebSocket communication.

### Architecture
```
┌─────────────────────────────────────────────────────┐
│              nexus_server.exe (Port 8085)           │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ Holy Beat   │  │ Tensor Core │  │  WebSocket  │ │
│  │   System    │  │   Memory    │  │   Handler   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Build & Run

```powershell
# Compile with MSVC
cl /EHsc /std:c++17 /I"nucleus" /Fe:bin\nexus_server.exe nucleus\nexus_server.cpp

# Run server
.\bin\nexus_server.exe
# Output: [NEXUS] Server initialized on port 8085
```

### WebSocket Messages

```json
// Request metrics
{"type": "get_metrics"}

// Response
{
  "type": "metrics",
  "holy_beat": {"tempo": 120, "energy": 0.75, "pattern": "fibonacci"},
  "tensor_core": {"dimensions": 4, "resonance": 0.92}
}
```

---

## 🐝 Genesis Swarm Mind

A 9-agent autonomous AI swarm system for intelligent code generation and maintenance.

### Agent Roster

| Agent | Role | Specialty |
|-------|------|-----------|
| 🧹 **Janitor** | Code cleanup | Dead code removal, formatting |
| 📚 **Archivist** | Documentation | Auto-generate docs, comments |
| 📬 **Courier** | File operations | Create, move, sync files |
| 🧬 **Evolutionist** | Code evolution | Refactoring, optimization |
| 🔮 **Oracle** | Predictions | Bug detection, suggestions |
| 🔍 **Inquisitor** | Analysis | Code review, quality checks |
| 🎯 **Strategist** | Planning | Architecture decisions |
| 🏗️ **Architect** | Structure | Component design, patterns |
| 🎓 **Trainer** | Learning | Skill acquisition via TDD |

### CLI Commands

```powershell
cd nexus_swarm

# Start interactive swarm
node nexus_swarm.js

# Direct commands
node nexus_swarm.js --review "path/to/file.js"
node nexus_swarm.js --evolve "path/to/module/"
node nexus_swarm.js --document "src/"
node nexus_swarm.js --train "React hooks"
node nexus_swarm.js --query "How does the tensor core work?"
```

### Trainer Agent (New!)

The Trainer agent implements skill acquisition through TDD cycles:

```javascript
// Train a new skill
await swarm.train("WebSocket authentication");

// Output:
// [TRAINER] Generating hypothesis for: WebSocket authentication
// [TRAINER] Writing failing test...
// [TRAINER] Implementing solution...
// [TRAINER] Test passed! Skill acquired.
// [TRAINER] Stored skill in ChromaDB vector memory
```

---

## ⚡ Tensor Core Memory

Mathematical resonance system using the Resonance Alphabet for symbolic computation.

### Resonance Alphabet

| Glyph | Symbol | Meaning | Frequency |
|-------|--------|---------|-----------|
| Α | Nexus | Connection point | 432 Hz |
| Β | Flow | Energy pathway | 528 Hz |
| Γ | Gate | Transition node | 639 Hz |
| Δ | Delta | Change vector | 741 Hz |
| Ω | Omega | Completion | 852 Hz |

### Tensor Operations

```cpp
// In nucleus/NexusTensorCore.hpp
TensorField field(4); // 4-dimensional tensor
field.setResonance(0.92);
field.applyGlyph(Glyph::NEXUS);
auto result = field.collapse(); // Returns eigenvalue
```

### Memory Integration

The Tensor Core connects to ChromaDB for persistent vector memory:

```python
# Query tensor memories
import chromadb
client = chromadb.HttpClient(host="localhost", port=8002)
collection = client.get_collection("tensor_memories")
results = collection.query(query_texts=["resonance pattern"], n_results=5)
```

---

## 🎵 Holy Beat Sound System

Audio-reactive synthesis engine with sacred geometry patterns.

### Audio States

| State | Description | BPM Range |
|-------|-------------|-----------|
| `calm` | Ambient, meditative | 60-80 |
| `focused` | Work rhythm | 80-120 |
| `energized` | High activity | 120-160 |
| `transcendent` | Peak flow | 160+ |

### Integration

```javascript
// Connect to Holy Beat via WebSocket
const ws = new WebSocket('ws://localhost:8085');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'audio_state') {
    console.log(`Tempo: ${data.tempo}, Energy: ${data.energy}`);
  }
};

// Request audio state
ws.send(JSON.stringify({ type: 'get_audio_state' }));
```

### Demos

- `bin/holy_beat_demo.exe` - Standalone audio demo
- `nexus_sator_resonance.html` - Visual audio interface
- `apps/demos/vibe_engine_nexus_demo.html` - Full vibe engine

---

## 📊 Analytics Dashboard

Real-time monitoring dashboard with process tracking.

### Features

- **Process Monitoring**: CPU/Memory for all Nexus processes
- **Holy Beat Metrics**: Live tempo, energy, pattern display
- **Tensor Core Data**: Resonance levels, field dimensions
- **Swarm Activity**: Agent status and task progress
- **Docker Health**: Container status monitoring

### Process Display

```
┌────────────────────────────────────────┐
│ PROCESS MONITOR                        │
├────────────────────────────────────────┤
│ nexus_server.exe    CPU: 2.3%  MEM: 45MB
│ python (bridge)     CPU: 1.1%  MEM: 82MB
│ node (swarm)        CPU: 3.2%  MEM: 156MB
│ chromadb            CPU: 0.8%  MEM: 234MB
└────────────────────────────────────────┘
```

### Access

```
http://localhost:8888/nexus_analytics_dashboard.html
```

---

## 🐳 Docker Deployment

### Container Architecture

```yaml
services:
  nexus_sandbox:       # Port 8001 - FastAPI sandbox
  nexus_memory:        # Port 8002 - ChromaDB vector DB
  nucleus-core:        # Core processing
  nucleus-api:         # REST API gateway
  nucleus-gateway:     # Load balancer
```

### Quick Deploy

```powershell
cd sandbox
docker-compose up -d

# Check status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# View logs
docker logs nexus_sandbox -f
```

### Health Check

```powershell
# Test ChromaDB
curl http://localhost:8002/api/v1/heartbeat

# Test Sandbox
curl http://localhost:8001/health
```

---
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
- `nexus_sator_resonance.html` - Holy Beat integration
- `bin/holy_beat_demo.exe` - C++ audio demo

### Graphics & Rendering
- `apps/demos/lighting_time_demo.html` - Lighting system
- `graphics/` - Graphics subsystems
- `vfx/` - Visual effects

### Memory & AI
- `nexus_swarm/` - 9-agent AI swarm
- `nucleus/` - C++ core engine
- `meta/thought-engine/` - AI reasoning system
- `meta/tensor_room.html` - Tensor operations
- `knowledge/` - Knowledge graph

### World Building
- `studio/terrain-world-builder.html` - Terrain editor
- `game/toolsandbox.html` - 3D mesh builder
- `prefab/` - Prefab construction tools

---

## 🗂️ Key Files

### C++ Nucleus Core
```
nucleus/
├── nexus_server.cpp           # Main WebSocket server
├── NexusWebSocketServer.hpp   # WebSocket implementation
├── NexusHolyBeatSystem.hpp    # Audio synthesis
├── NexusTensorCore.hpp        # Tensor mathematics
├── NexusResonanceAlphabet.hpp # Symbolic glyphs
└── nucleus.cpp                # Core processing
```

### Node.js Swarm
```
nexus_swarm/
├── nexus_swarm.js    # 9-agent swarm (2662 lines)
├── nexus_bridge.py   # Process monitoring bridge
├── swarm.config.js   # Agent configuration
└── skills/           # Acquired skill modules
```

### Dashboards
```
├── nexus_analytics_dashboard.html  # Real-time metrics
├── nexus_viz_dashboard.html        # System visualization
├── nexus_resonance_interface.html  # Tensor UI
└── studio/                         # Development tools
```

---

## 🛠️ Development

### Prerequisites
- **C++ Compiler**: MSVC 19.50+ (Visual Studio 2025+)
- **Node.js**: 18+
- **Python**: 3.10+ with psutil
- **Docker**: For ChromaDB and sandbox

### Build C++ Components

```powershell
# Compile nexus server
cl /EHsc /std:c++17 /I"nucleus" /Fe:bin\nexus_server.exe nucleus\nexus_server.cpp

# Compile Holy Beat demo
cl /EHsc /std:c++17 /I"nucleus" /Fe:bin\holy_beat_demo.exe nucleus\holy_beat_demo.cpp

# Compile Tensor demo
cl /EHsc /std:c++17 /I"nucleus" /Fe:bin\tensor_demo.exe nucleus\tensor_demo.cpp
```

### Install Python Dependencies

```powershell
pip install psutil chromadb websockets
```

### Start All Services

```powershell
# 1. Docker services
cd sandbox && docker-compose up -d

# 2. C++ WebSocket server (new terminal)
.\bin\nexus_server.exe

# 3. Python bridge (new terminal)
cd nexus_swarm && python nexus_bridge.py

# 4. HTTP server (new terminal)
python -m http.server 8888

# 5. Swarm (optional, new terminal)
cd nexus_swarm && node nexus_swarm.js
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System architecture overview |
| [ENGINE_BUILD_GUIDE.md](./ENGINE_BUILD_GUIDE.md) | C++ build instructions |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Contribution guidelines |
| [docs/API.md](./docs/API.md) | API reference |

---

## 🔧 Troubleshooting

### Port Conflicts
```powershell
# Check what's using a port
netstat -ano | findstr :8085

# Kill process by PID
taskkill /F /PID <pid>
```

### Docker Issues
```powershell
# Restart containers
docker-compose down && docker-compose up -d

# Check container logs
docker logs nexus_sandbox -f
```

### WebSocket Connection Failed
1. Verify `nexus_server.exe` is running
2. Check port 8085 is not blocked by firewall
3. Confirm browser allows WebSocket connections

---

## 📜 License

See [LICENSE](./LICENSE) for details.

---

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

**Tech Stack:**
- **C++17** - Core engine (MSVC)
- **Node.js** - Swarm agents
- **Python** - Bridge & backend
- **Three.js** - 3D graphics
- **React/TypeScript** - UI components
- **WebSocket** - Real-time communication
- **ChromaDB** - Vector memory
- **Docker** - Container deployment

---

*Nexus AI Platform - Where mathematics meets consciousness*

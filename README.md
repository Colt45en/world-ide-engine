# World Engine IDE

A comprehensive, fully connected development environment that integrates mathematics, graphics, prefab pipelines, AI intelligence, metadata management, and web development into a cohesive, scalable system.

## 🌟 Features

### Core Systems

1. **Math Engine** - Pure mathematical computation
   - Vector and matrix operations
   - 3D transformations
   - Geometric calculations
   - Distance and spatial computations

2. **Graphics Engine** - Visual rendering and processing
   - Material system (PBR support)
   - Shader management
   - Render queue
   - Default geometries (cube, sphere, etc.)

3. **Prefab Pipeline** - Template-based asset creation
   - Prefab registration and instantiation
   - Component-based architecture
   - Default prefabs (cube, sphere, light)
   - Override system for customization

4. **AI Intelligence** - Smart analysis and suggestions
   - Pattern recognition
   - Performance optimization insights
   - Quality improvements
   - Workflow predictions

5. **MetaBase** - Comprehensive data management
   - Schema-based storage
   - Query system with filtering
   - Import/export functionality
   - Indexed search

6. **Web Framework** - Web development tools
   - Route management
   - Component system
   - Template rendering
   - UI generation

### System Integration

**DataBus** - The central nervous system that connects all components:
- Event-based communication
- Subscribe/publish pattern
- Message history tracking
- Wildcard subscriptions
- Real-time data sharing across all subsystems

## 🚀 Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/Colt45en/world-ide-engine.git
cd world-ide-engine

# Install dependencies (if any added)
npm install
```

### Running the Engine

```bash
# Start the engine
npm start

# Development mode with auto-reload
npm run dev

# Run tests
npm test

# Build the project
npm run build
```

## 📖 Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    World Engine IDE                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐          DataBus           ┌─────────┐│
│  │ Math Engine  │◄──────────┬──────────────►│Graphics ││
│  └──────────────┘           │                │Engine   ││
│         ▲                   │                └─────────┘│
│         │                   │                     ▲      │
│         │                   │                     │      │
│  ┌──────┴──────┐           │           ┌────────┴────┐ │
│  │   Prefab    │◄──────────┼──────────►│     AI      │ │
│  │  Pipeline   │           │           │Intelligence │ │
│  └─────────────┘           │           └─────────────┘ │
│         ▲                   │                     ▲      │
│         │                   │                     │      │
│  ┌──────┴──────┐           │           ┌────────┴────┐ │
│  │  MetaBase   │◄──────────┴──────────►│    Web      │ │
│  │  (Storage)  │                       │ Framework   │ │
│  └─────────────┘                       └─────────────┘ │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Math to Graphics**: Mathematical calculations feed into visual rendering
2. **Prefab Integration**: Prefabs utilize both math and graphics systems
3. **AI Monitoring**: AI analyzes all system activities for optimization
4. **MetaBase Storage**: All data is persisted and queryable
5. **Web Interface**: Web framework provides UI for all systems

## 💡 Usage Examples

### Creating and Instantiating a Prefab

```javascript
import { WorldEngine } from './src/index.js';

const engine = new WorldEngine();
await engine.initialize();

// Create a custom prefab
engine.prefabPipeline.registerPrefab('custom-box', {
  name: 'Custom Box',
  components: {
    geometry: { type: 'cube', size: [2, 2, 2] },
    material: 'pbr',
    transform: { position: [0, 1, 0] }
  }
});

// Instantiate the prefab
const instance = engine.prefabPipeline.instantiate({
  prefabId: 'custom-box',
  overrides: {
    transform: { position: [5, 0, 0] }
  }
});
```

### Using the Math Engine

```javascript
// Perform calculations
engine.dataBus.publish('math:compute', {
  operation: 'distance',
  params: {
    p1: [0, 0, 0],
    p2: [3, 4, 0]
  }
});

// Subscribe to results
engine.dataBus.subscribe('math:calculation', (data) => {
  console.log('Result:', data.result);
});
```

### Querying the MetaBase

```javascript
// Store data
engine.dataBus.publish('meta:store', {
  collection: 'assets',
  id: 'asset_1',
  value: {
    name: 'My Texture',
    type: 'texture',
    path: '/assets/textures/wood.png'
  }
});

// Query data
const assets = engine.metaBase.query({
  collection: 'assets',
  filter: { type: 'texture' }
});
```

### Creating Web Routes

```javascript
// Add a custom route
engine.webFramework.addRoute('/custom', {
  name: 'Custom Page',
  handler: (params) => ({
    title: 'Custom Page',
    content: 'Your custom content here'
  })
});

// Navigate to route
engine.dataBus.publish('web:route', {
  path: '/custom',
  params: {}
});
```

## 🔧 Configuration

The system is designed to be modular and extensible. Each subsystem can be configured independently through the DataBus communication layer.

### DataBus Channels

- `math:*` - Math engine operations
- `graphics:*` - Graphics rendering
- `prefab:*` - Prefab management
- `ai:*` - AI analysis and suggestions
- `meta:*` - Data storage and retrieval
- `web:*` - Web interface operations

## 🧪 Testing

The system includes built-in testing capabilities:

```bash
npm test
```

## 🔐 Security

- No hardcoded credentials
- Secure data storage patterns
- Input validation on all subsystems
- Safe event handling with error boundaries

## 🤝 Contributing

This is a foundational system designed to scale. Contributions are welcome to:
- Add new subsystems
- Enhance existing features
- Improve performance
- Expand AI capabilities
- Add more prefabs and templates

## 📝 License

MIT License - See LICENSE file for details

## 🎯 Roadmap

- [ ] Advanced physics integration
- [ ] Real-time collaboration
- [ ] Plugin system
- [ ] Visual scripting
- [ ] Asset marketplace integration
- [ ] Cloud synchronization
- [ ] Advanced AI code generation
- [ ] VR/AR support

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**World Engine IDE** - Building the future of integrated development environments. 

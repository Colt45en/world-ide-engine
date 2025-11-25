# Meta-Orchestrator V2 Architecture

## Overview

The Meta-Orchestrator is a unified coordination layer that integrates five core meta-systems into a single, cohesive pipeline. It enables text input to flow through morpheme decomposition, semantic reasoning, zone-based orchestration, and finally physics/rendering automation.

## Core Systems

### 1. TokenLab (Figure-8 Morpheme System)
**Location**: `meta/orchestrator_v2.py::TokenLab`

Implements bidirectional morpheme processing:
- **Breakdown (Downward)**: Atomizes words into constituent morphemes
  - "rebuild" → ["re", "build"]
  - "multibuild" → ["multi", "build"]
  - Caches results for repeated lookups

- **Reconstruction (Upward)**: Rebuilds state vectors from morphemes
  - Each morpheme has a 3×3 transformation matrix M and bias vector b
  - Applies M*x + b at each step
  - Tracks consistency factor κ (attenuation per morpheme)
  - Returns StationaryUnit with latent state vector

**Morpheme Registry** (6 base morphemes):
- `re`: Restoration (M scales to 0.95-1.05)
- `build`: Construction (M scales to 1.15)
- `multi`: Scaling (M scales to 1.4)
- `-ize`: Causative (coupled transformations)
- `-ness`: Quality/state (M scales down)
- `<id>`: Identity fallback

**Example**:
```python
lab = TokenLab()
bd = lab.breakdown("rebuild")      # ["re", "build"]
su = lab.reconstruct(bd)            # [1.02, 1.05, 0.99]
```

### 2. LexicalLogicEngine (Word Button System)
**Location**: `meta/orchestrator_v2.py::LexicalLogicEngine`

Semantic reasoning through word button activation:
- **10 Word Buttons**: ALIGN, PROJ, REFINE, POLY, IRONY, INTENSITY, GRAPH, DIRECTION, NOISE, MANUAL
- Each button has:
  - Activation value (0.0 to 1.0)
  - Semantic connections (graph edges)
  - Transform scale metadata
  - Category classification

- **Activation Semantics**:
  - Pressing a button increases its activation by 0.3
  - Propagates 0.1 activation to connected buttons
  - Returns updated SemanticState with active button list

**Button Graph** (selected connections):
```
ALIGN ←→ PROJ ←→ REFINE ←→ POLY
IRONY ←→ INTENSITY ←→ GRAPH ←→ POLY
DIRECTION ←→ ALIGN
MANUAL ←→ DIRECTION
```

### 3. PipelineCanvas (8-Zone Orchestration)
**Location**: `meta/orchestrator_v2.py::PipelineCanvas`

Routes execution through semantic stages:

```
HEAD
  ↓ [tokenize]
ROOT_EXTRACTION
  ↓ [breakdown]
CONTEXT_STRIPPING
  ↓ [strip_metadata]
AXIOMATIC_MAPPING
  ↓ [map_semantics]
RELATIONSHIP_WEAVING
  ↓ [weave_connections]
PATTERN_RECOGNITION
  ↓ [recognize_patterns]
SYNTHETIC_REBUILD
  ↓ [reconstruct]
ACTIONABLE_OUTPUT
  ↓ [generate_output]
```

Each zone:
- Increments cycle counter
- Executes zone-specific handler
- Records PipelineRecord with state snapshot
- Triggers associated automations

### 4. KnowledgeVault (Central Data Hub)
**Location**: `meta/orchestrator_v2.py::KnowledgeVault`

Central repository for all system state:
- **System Registry**: Tracks 7 subsystems (TokenLab, LexicalLogic, PipelineCanvas, Physics, KnowledgeVault, UpflowAutomation, CLIParser)
- **Compliance Tracking**: Each system has status and compliance level
- **Metrics**: Counters for tokens_processed, morphemes_decomposed, logic_decisions, zone_transitions, automations_triggered
- **Manifest Export**: JSON-serializable unified state record

**API**:
```python
vault = KnowledgeVault()
vault.register_system("token_lab", SystemRole.TOKEN_LAB)
vault.increment_metric("tokens_processed", 3)
manifest = vault.create_manifest()  # Full system state
```

### 5. UpflowAutomation (Decision Routing)
**Location**: `meta/orchestrator_v2.py::UpflowAutomation`

Routes meta-system decisions to physics/rendering:

**Three Automation Rules**:

1. **token_to_physics**: Tokens + Embeddings → Physics Parameters
   - avg_embedding determines mass (0.5 to 1.5 range)
   - Computes velocity and restitution from embeddings
   - Rule priority: standard

2. **decision_to_transform**: Decision + Physics → Render Transforms
   - Position: (mass × 2.0, mass × 1.5, 0)
   - Rotation: (0, mass × π, 0)
   - Scale: (1/mass, 1/mass, 1/mass)

3. **embedding_to_color**: Embeddings → HSL Palette
   - Hue from embedding[0] (0-360°)
   - Saturation from embedding[1] (0-100%)
   - Lightness from embedding[2] (0-100%)
   - Computes secondary color at ±120° hue offset

**Rule Execution**:
- Sorted by priority (highest first)
- Triggered only if condition is met
- Results merged into execution state
- Action log maintained for audit trail

## Main Orchestrator

**Location**: `meta/orchestrator_v2.py::MetaOrchestrator`

Coordinates all subsystems through single entry point:

```python
orch = MetaOrchestrator()
result = orch.orchestrate("rebuild resilience")
status = orch.get_status()
```

**Orchestration Pipeline**:
1. Tokenize input text
2. Breakdown each token into morphemes (TokenLab)
3. Reconstruct to state vectors
4. Generate embeddings (sum of reconstructed vector / dimension)
5. Apply semantic logic (threshold-based: aggressive/balanced/gentle)
6. Apply UpflowAutomation rules (tokens→physics, decision→transforms, embeddings→colors)
7. Increment metrics and log execution
8. Return complete execution state

**Result Structure**:
```python
{
  "input": "rebuild",
  "tokens": ["rebuild"],
  "breakdowns": [["re", "build"]],
  "reconstructions": [[1.02, 1.05, 0.99]],
  "embeddings": [1.02],
  "decision": "aggressive",
  "physics_params": {
    "mass": 1.52,
    "velocity": (3.04, 2.03, 0),
    "restitution": 1.01,
    "gravity": 9.81
  },
  "render_transforms": {
    "position": (3.04, 2.28, 0),
    "rotation": (0, 4.77, 0),
    "scale": (0.66, 0.66, 0.66)
  },
  "colors": {
    "primary": "hsl(102, 53%, 102%)",
    "secondary": "hsl(222, 53%, 102%)"
  }
}
```

## Data Flow Diagram

```
Text Input
    ↓
[TokenLab.breakdown] → Morphemes → [Reconstruct] → State Vectors
    ↓
[LexicalLogic] → Semantic State (button activations)
    ↓
[Embeddings] (average of state vector values)
    ↓
[Logic Decision] (threshold-based on average embedding)
    ↓
[UpflowAutomation Rules]
  ├→ tokens + embeddings → physics_params
  ├→ decision + physics → render_transforms
  └→ embeddings → colors
    ↓
[Physics Engine] (receives mass, velocity, restitution)
[Graphics Engine] (receives position, rotation, scale)
[Procedural System] (receives color palette)
    ↓
Execution State + Manifest Log
```

## Integration Points

### With Physics Engine
- `physics_params` includes mass, velocity, restitution, gravity
- Can be directly applied to `physics.body.RigidBody`
- Supports impulse-based collision response (see physics/solver.py)

### With Graphics/Rendering
- `render_transforms` provides position, rotation, scale for scene graph
- `colors` provides HSL palette for material/shader properties
- Directly compatible with rendering backends

### With Procedural Generation
- `embeddings` can seed noise/fractal parameters
- `decision` can drive procedural algorithm selection
- `tokens` can feed into content generation systems

## Performance Characteristics

**Time Complexity**:
- TokenLab breakdown: O(word_length) amortized (cached)
- TokenLab reconstruct: O(morphemes × matrix_size) = O(n × 9)
- UpflowAutomation: O(rules) = O(3)
- Overall: O(tokens × morphemes) + O(rules)

**Space Complexity**:
- TokenLab caches: O(unique_words × morpheme_count)
- LexicalLogic state: O(buttons × connections) = O(100)
- KnowledgeVault: O(systems + executions)

## Testing

Run `python test_orchestrator.py` to verify:
- Morpheme decomposition accuracy
- State vector reconstruction
- Physics parameter generation
- Color palette generation
- Manifest creation and metrics tracking

## Future Enhancements

1. **Recursive Feedback**: System outputs → inputs (5+ cycles)
2. **Advanced Logic**: Replace threshold-based with neural decision
3. **Morpheme Learning**: Train transformation matrices from corpus
4. **Button Learning**: Discover optimal button sequences via reinforcement learning
5. **Zone Customization**: User-defined zone handlers and automations
6. **Audio Integration**: Map morpheme/button states to synthesis parameters

## References

- Figure-8 breakdown/reconstruction: `figure_8_breakdown_reconstruction.js`
- Advanced CLI: `advanced-argument-parser.js`
- Lexical Logic: `nexus-sase-trainer.html`
- Knowledge Vault: `knowledge-vault-dashboard.html`
- Meta Learning: `meta learning.txt`

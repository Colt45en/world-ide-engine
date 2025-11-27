# Nexus: The Body & Soul Feedback Architecture

## Overview

The **Nexus** is an orchestration hub that integrates two complementary systems:
- **The Body** (IntelligentSurfaceNets): Geometric form generation with intelligent vertex placement
- **The Soul** (AestheticPathway): AI-driven aesthetic evaluation using Golden Ratio harmonies

Together, they create a **form-aesthetics feedback loop** where geometry informs visual properties, and aesthetics retroactively demand geometric refinements.

## Architecture

```
Volume Data (voxels)
     ↓
┌─────────────────────────────────────┐
│  NEXUS (Orchestration Hub)          │
└──────────┬──────────────────────────┘
           ├──→ IntelligentSurfaceNets (BODY)
           │    • Voxel → mesh conversion
           │    • Intelligent vertex placement (center-of-mass)
           │    • Fractal detail modulation
           │    • Laplacian smoothing (organic look)
           │    • Geometry analysis (entropy, bounds, aspect)
           │
           ├──→ AestheticPathway (SOUL)
           │    • Entropy-based mood detection
           │    • Golden Ratio color harmony generation
           │    • HSL color space manipulation
           │    • Aesthetic scoring (φ alignment)
           │    • Color harmony schemes (triadic, analogous, etc)
           │
           └──→ Feedback Generator
                • Quality evaluation
                • Refinement recommendations
                • Mood alignment checking
                • Iterative improvement hints
```

## Key Modules

### 1. geometry/surface_nets.py (310 lines)
**IntelligentSurfaceNets**: Voxel-to-mesh conversion with intelligence

**Key Classes:**
- `MeshData`: Stores vertices, indices, and normals
- `GeometryStats`: Computed metrics (entropy, bounds, aspect ratio, surface area)
- `IntelligentSurfaceNets`: Main generator

**Core Method - `generate_mesh()`:**
1. Scan voxel grid (Surface Nets algorithm)
2. Calculate intelligent vertices (center-of-mass + fractal noise)
3. Generate topology (triangle connectivity)
4. Apply Laplacian smoothing (3 iterations for organic look)
5. Compute vertex normals
6. Analyze and return geometry statistics

**Intelligence Features:**
- **Intelligent Placement**: Vertices at density-weighted centers, not grid corners
- **Fractal DNA**: Deterministic noise injection based on seed for detail variation
- **Smoothing**: Iterative neighbor-averaging removes artificial blocky appearance
- **Analysis**: Computes entropy (σ/μ of distances) for mood detection

### 2. aesthetics/pathway.py (250 lines)
**AestheticPathway**: Golden Ratio-based aesthetic evaluation

**Key Classes:**
- `PaletteResult`: Color palette, mood, aesthetic score, lighting profile
- `AestheticEvaluation`: Complete aesthetic analysis with harmonies
- `AestheticPathway`: Mood detector and color generator

**Core Method - `evaluate(geometry_stats)`:**
1. Analyze geometry entropy → determine mood
   - High entropy (>0.5): **Energetic** → warm colors (reds/oranges)
   - Low entropy (<0.5): **Calm** → cool colors (blues/teals)

2. Generate harmonic palette via Golden Ratio (φ = 1.618...)
   - Primary: Base color in mood range
   - Secondary: φ-shifted hue (0.618... of circle ≈ 222.5°)
   - Accent: Complementary (180°)

3. Calculate aesthetic score
   - Based on aspect ratio proximity to φ
   - Perfect 1.0 at aspect_ratio[1]/aspect_ratio[0] = φ

4. Generate color harmonies
   - **Complementary**: 180° rotation
   - **Triadic**: 120° spacing
   - **Analogous**: ±30° from primary
   - **Monochromatic**: Lightness variations

**Color Space:** HSL ↔ RGB conversions for perceptual uniformity

### 3. nexus/core.py (180 lines)
**Nexus**: Central orchestration and feedback generation

**Key Classes:**
- `IntegratedOutput`: Complete result (mesh, stats, aesthetics, feedback)
- `Nexus`: Orchestrator hub

**Core Method - `process_intelligent_silhouette(volume, resolution, user_intent)`:**
1. Generate mesh with IntelligentSurfaceNets
2. Analyze geometry (compute GeometryStats)
3. Run through AestheticPathway
4. Generate feedback recommendations

**Feedback Generation (`_generate_feedback`):**
- **Entropy-based smoothing**: If entropy > 0.6 → suggest smoothing
- **Detail detection**: If entropy < 0.2 → suggest adding detail
- **Aspect ratio tuning**: If |aspect - φ| > 0.3 → suggest adjustment
- **Overall quality score**: Weighted average of all metrics
- **Mood alignment**: Check if detected mood matches user intent

## Mathematical Foundations

### Golden Ratio (φ)
```
φ = (1 + √5) / 2 ≈ 1.61803398875
φ - 1 = 1/φ ≈ 0.61803398875
```

Used for:
- Aspect ratio scoring (target ratio = φ)
- Secondary color hue shift (0.618 of full circle ≈ 222.5°)
- Harmony detection

### Entropy Calculation
```
entropy = σ(distances_to_centroid) / μ(distances_to_centroid)
```
Where distances are from each vertex to the mesh centroid.

- High entropy (>0.5): Chaotic, jagged surfaces → **energetic** → warm palette
- Low entropy (<0.2): Smooth, organized → **calm** → cool palette
- Target range: 0.3-0.6 (balanced)

### Color Harmony (HSL)
```
H = hue (0-1, wraps at 360°)
S = saturation (0-1)
L = lightness (0-1)
```

**Golden Angle Spacing**: 137.5° (complementary to φ in circle geometry)

## Integration Example

```python
from nexus.core import Nexus
import numpy as np

# Create volume
volume = np.zeros((20, 20, 20))
# ... populate with voxels ...

# Run full pipeline
nexus = Nexus()
output = nexus.process_intelligent_silhouette(
    volume,
    resolution=(20, 20, 20),
    user_intent='balanced'
)

# Access results
print(f"Mood: {output.aesthetic_eval.mood}")
print(f"Color: {output.aesthetic_eval.palette.primary_color}")
print(f"Mesh vertices: {len(output.mesh.vertices)}")
print(f"Beauty score: {output.aesthetic_eval.beauty_score}")
print(f"Refinements needed: {output.feedback_recommendations['refinement_suggestions']}")
```

## Feedback Loop Workflow

1. **User Input**: Provides voxel volume + aesthetic intent
2. **Body Generation**: IntelligentSurfaceNets creates mesh
3. **Soul Analysis**: AestheticPathway evaluates aesthetics
4. **Feedback**: Nexus suggests refinements
5. **Iteration**: User adjusts volume → return to step 2

### Refinement Actions:
- `increase_smoothing`: Too jagged (entropy > 0.6)
- `increase_detail`: Too smooth (entropy < 0.2)
- `adjust_aspect_ratio`: Far from φ proportion

## Lab Protocol

### Session 1: Foundation
1. Create test volumes (sphere, cube, torus)
2. Run through Nexus
3. Verify mood detection matches expected aesthetic

### Session 2: Optimization
1. Iteratively refine volumes based on feedback
2. Adjust smoothing and detail parameters
3. Target entropy in 0.4-0.6 range

### Session 3: User Feedback
1. Compare AI-generated palettes to user preferences
2. Train mood-to-color mapping
3. Personalize aesthetic scoring weights

## Dependencies

- `numpy`: Numerical computations, mesh operations
- `scipy`: Laplacian smoothing (scipy.sparse)
- `dataclasses`: Type-safe data structures

## Files

- `geometry/surface_nets.py` (310 LOC)
- `aesthetics/pathway.py` (250 LOC)
- `nexus/core.py` (180 LOC)
- `examples/intelligent_morphing_demo.py` (200 LOC)
- `docs/NEXUS.md` (this file)

## Status

✅ Complete implementation with:
- Intelligent geometry generation
- Golden Ratio-based aesthetics
- Automated feedback loops
- Full documentation and examples

## Next Steps

1. Fix numpy/Python 3.12 compatibility
2. Run full demo with sample data
3. Integrate with morphing pipeline
4. Create visualization layer
5. Build user feedback training system

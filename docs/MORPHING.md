# Morphing Pipeline: 2D→3D Shape Design & Actuation

## Overview

The morphing pipeline enables **programmed 2D-to-3D transformation** of flat sheets into specified 3D shapes via spatial modulation of growth/swelling. This system combines:

- **Mathematical design** (differential geometry, metric optimization)
- **Material programming** (UV-driven isotropic growth, calibration)
- **Fabrication** (grayscale patterns for lithography/transparency)
- **Sensing & feedback** (3D reconstruction, closed-loop refinement)

**Applications**:
- Stimulus-responsive hydrogels (physical experiments)
- Digital meshes in rendering engines (simulation)
- Soft robotics, adaptive structures, biomedical devices

---

## 1. Core Concepts

### 1.1 The Growth Field $g(x,y)$

The **growth field** is a 2D spatial function that prescribes how much each point should expand:

$$\text{realized metric} = g(x,y)^2 \cdot I_{2 \times 2}$$

where:
- $g(x,y) \in [g_{\min}, g_{\max}]$ (material bounds, e.g., 0.7–2.5)
- $I$ is the 2D identity matrix (isotropic swelling assumption)
- **Constraint**: $g(x,y)$ must satisfy smoothness and fabrication limits

### 1.2 Target Metric Tensor

The **target metric** $g_{ij}^{(target)}$ encodes the desired 3D curvature by specifying distances on the surface:

$$g_{ij} = \frac{\partial X}{\partial u^i} \cdot \frac{\partial X}{\partial u^j}$$

where $X(u,v)$ is the parametric 3D surface.

**Isotropic growth model**: A simple approximation assumes $g(x,y)$ directly realizes a scalar stretch:

$$g(x,y)^2 \approx \frac{1}{\lambda_{\max}} (g_{11} + g_{22}) / 2$$

### 1.3 Optimization Problem

**Minimize** over $g(x,y)$:

$$E = E_{\text{metric}} + \lambda_s E_{\text{smooth}} + \lambda_f E_{\text{fab}}$$

where:
- $E_{\text{metric}} = \frac{1}{N} \sum_k \|g_k^2 I - g_{ij}^{\text{target}}_k\|_F^2$ — Metric mismatch
- $E_{\text{smooth}} = \sum_k \|\nabla g_k\|^2$ — Gradient regularization (smoothness)
- $E_{\text{fab}} = \sum_k \min_{\ell} (g_k - \text{UV}_\ell)^2$ — Quantization penalty (8-bit discreteness)

**Subject to**: $g_{\min} \leq g(x,y) \leq g_{\max}$

---

## 2. Pipeline Architecture

### 2.1 Modules

```
morphing/
├── geometry/
│   ├── target.py          # Target surface representations (analytic, mesh)
│   └── target_surface.py  # Metric computation, UV mapping [FUTURE]
├── optimization/
│   └── optimizer.py       # Pattern solvers (gradient descent, Adam, simulated annealing)
├── materials/
│   ├── material_model.py  # Isotropic swelling, UV calibration curves
│   └── pattern_encoder.py # Grayscale/SVG export [FUTURE]
├── sensing/
│   └── feedback.py        # 3D reconstruction, ICP alignment, error metrics, closed-loop control
└── __init__.py
```

### 2.2 Data Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. DESIGN PHASE                                         │
├─────────────────────────────────────────────────────────┤
│ Target 3D Surface (analytic/mesh)                       │
│         ↓                                               │
│ Compute Metric Field g_ij(u,v)                         │
│         ↓                                               │
│ Pattern Optimizer (gradient descent / Adam / SA)        │
│         ↓                                               │
│ Optimal Growth Field g*(x,y)                           │
├─────────────────────────────────────────────────────────┤
│ 2. FABRICATION & ACTUATION                              │
├─────────────────────────────────────────────────────────┤
│ Material: UV Dose → Growth Calibration                 │
│         ↓                                               │
│ Grayscale Pattern Export (PNG/SVG)                     │
│         ↓                                               │
│ Lithography / Transparency Printing                    │
│         ↓                                               │
│ Place in Stimulus Field (UV, heat, solvent)            │
│         ↓                                               │
│ Hydrogel Swells → 3D Shape Emerges                     │
├─────────────────────────────────────────────────────────┤
│ 3. SENSING & FEEDBACK                                   │
├─────────────────────────────────────────────────────────┤
│ 3D Reconstruction (photogrammetry, depth camera)       │
│         ↓                                               │
│ ICP Alignment to Target Surface                        │
│         ↓                                               │
│ Error Metrics (Hausdorff, metric mismatch)             │
│         ↓                                               │
│ [CONVERGED?] → YES → Done                              │
│              → NO  → Refine g*, iterate                │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Module Usage

### 3.1 Geometry: Target Surface

```python
from morphing.geometry.target import AnalyticSurface, sample_surface_on_grid

# Define spherical cap: X(u, v)
def cap_X(u, v):
    R, h = 5.0, 1.5
    r_sq = u**2 + v**2
    if r_sq > R**2 - (R - h)**2:
        return (u, v, 0.0)  # flat outside
    z = np.sqrt(R**2 - r_sq) - (R - h)
    return (u, v, z)

surface = AnalyticSurface(cap_X, domain=((-3, 3), (-3, 3)))

# Compute metric tensor on grid
metrics, positions = sample_surface_on_grid(surface, nx=8, ny=8)
print(metrics.shape)  # (64, 2, 2)
```

### 3.2 Optimization: Pattern Solver

```python
from morphing.optimization.optimizer import PatternOptimizer

optimizer = PatternOptimizer(
    target_metric=metrics,
    g_min=0.8,
    g_max=2.0,
    lambda_smooth=0.15,
    lambda_fab=0.05
)

# Adam optimization
result = optimizer.adam(
    initial_g=np.ones(64) * 1.0,
    learning_rate=0.02,
    max_iterations=200
)

print(f"Converged: {result.convergence}")
print(f"Growth field: {result.growth_field}")  # shape (64,)
print(f"Energy: {result.energy}")
print(f"History: {result.history}")
```

### 3.3 Materials: Fabrication

```python
from morphing.materials.material_model import IsotropicMaterial, PatternFabricator

material = IsotropicMaterial(g_min=0.8, g_max=2.0)

# Default sigmoidal calibration or load from experiments
material.default_calibration()

# Convert to grayscale for UV lithography
grayscale = material.growth_to_grayscale(result.growth_field)
print(grayscale.dtype, grayscale.shape)  # uint8, (64,)

# Export for fabrication
PatternFabricator.to_svg(result.growth_field, nx=8, ny=8, 
                         filename="pattern.svg", cell_size=20)
```

### 3.4 Sensing & Feedback

```python
from morphing.sensing.feedback import (
    FeedbackController, IterativeClosestPoint, ErrorMetrics
)

# Simulate or measure 3D point cloud
measured_points = np.random.randn(100, 3)  # placeholder

# Align to target
R, t, align_error = IterativeClosestPoint.align(measured_points, target_points)

# Compute errors
hausdorff = ErrorMetrics.hausdorff_distance(measured_points, target_points)
mean_dist = ErrorMetrics.mean_distance(measured_points, target_points)

# Iterative refinement
controller = FeedbackController(tolerance=0.05, max_iterations=5)
refined_g, final_error = controller.refine(
    growth_field=result.growth_field,
    measured_points=measured_points,
    target_surface=surface,
    optimizer=optimizer,
    material=material
)
```

---

## 4. Lab Protocol: Hydrogel Experiment

### Phase 1: Calibration
1. Prepare hydrogel precursor (e.g., PEG-diacrylate + photo-initiator)
2. Create UV exposure series: uniform doses 0%, 25%, 50%, 75%, 100%
3. Measure swelling in each region (caliper, CT scan, or photogrammetry)
4. Fit calibration curve: UV dose → isotropic growth $g$

### Phase 2: Patterned Fabrication
1. Design target shape (e.g., spherical cap)
2. Run optimization pipeline → grayscale pattern
3. Print pattern on transparency or generate photomask
4. Spin-coat hydrogel precursor on substrate
5. Expose through patterned mask
6. Develop/crosslink to lock in growth pattern

### Phase 3: Actuation & 3D Realization
1. Submerge in stimulus (water/solvent for osmotic swelling)
2. Allow spontaneous buckling/curling (minutes to hours depending on gel)
3. Capture 3D shape (photogrammetry, laser scan, CT)

### Phase 4: Feedback Loop
1. Reconstruct 3D point cloud from images
2. Align to target surface (ICP)
3. Compute error metrics (Hausdorff, curvature mismatch)
4. If error large: perturb pattern slightly, re-fabricate, iterate

---

## 5. Example: Spherical Cap

See `examples/morphing_demo.py` for a complete end-to-end example:

```bash
python examples/morphing_demo.py
```

**Output**:
- Optimized growth field (`nx × ny` grid)
- SVG pattern for fabrication
- Simulated 3D shape
- Error metrics (Hausdorff, mean distance)
- Convergence plot

---

## 6. Key Equations

### First Fundamental Form (Metric Tensor)
$$g_{ij} = \frac{\partial X}{\partial u^i} \cdot \frac{\partial X}{\partial u^j}$$

### Energy Functional
$$E(g) = \underbrace{\frac{1}{N} \sum_k \| g_k^2 I - g^{\text{(target)}}_k \|_F^2}_{E_{\text{metric}}} + \lambda_s \underbrace{\sum_k \| \nabla g_k \|^2}_{E_{\text{smooth}}} + \lambda_f \underbrace{\sum_k d(g_k, \text{UV}_k)^2}_{E_{\text{fab}}}$$

### Isotropic Growth Model
$$\text{realized metric} = \begin{pmatrix} g^2 & 0 \\ 0 & g^2 \end{pmatrix}$$

### Gradient Descent Update (with projection)
$$g^{(t+1)} = \text{clip}\left( g^{(t)} - \alpha \nabla E(g^{(t)}), [g_{\min}, g_{\max}] \right)$$

---

## 7. Advanced Topics

### 7.1 Anisotropic Growth
For **directional swelling** (e.g., fiber-reinforced materials):

$$\text{realized metric} = G(x,y) = \begin{pmatrix} g_1 & 0 \\ 0 & g_2 \end{pmatrix}$$

Optimize $g_1(x,y)$, $g_2(x,y)$ independently.

### 7.2 AI Surrogates
For expensive simulations (FEM, multi-material), train a neural surrogate:

$$\tilde{E}_{\text{metric}}(g) \approx \text{NN}(g) \quad \text{(fast, differentiable)}$$

Use in place of true metric computation during optimization.

### 7.3 Multi-Material Patterns
Encode multiple stimuli (UV, temperature, pH) → multiple growth fields $g_1(x,y), g_2(x,y)$.

### 7.4 Closed-Form Solutions
For simple geometries (cones, cylinders), analytical solutions exist; use as initialization.

---

## 8. Testing & Validation

- **Unit tests**: Each module (geometry, optimization, materials, sensing)
- **Integration tests**: Full pipeline on synthetic targets
- **Convergence tests**: Verify gradient descent monotonicity, ICP convergence
- **Lab validation**: Compare simulated vs. measured 3D shapes

---

## 9. References & Further Reading

1. **Differential Geometry**:
   - Lee, J. M. "Riemannian Manifolds: An Introduction to Curvature." (2018)
   - Do Carmo, M. "Differential Geometry of Curves and Surfaces." (2016)

2. **Growth Mechanics**:
   - Ben Amar, M., & Goriely, A. "Growth and instability in elastic tissues." *Journal of the Mechanics and Physics of Solids* (2005)

3. **Optimization**:
   - Boyd, S., & Vandenberghe, L. "Convex Optimization." (2004)
   - Kingma, D. P., & Ba, J. "Adam: A method for stochastic optimization." (2014)

4. **Responsive Hydrogels**:
   - Peppas, N. A., et al. "Hydrogels in biology and medicine." *Progress in Polymer Science* (2006)

---

## 10. Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Optimization doesn't converge | Learning rate too large | Reduce `learning_rate` (e.g., 0.01 → 0.005) |
| Non-smooth pattern | Insufficient regularization | Increase `lambda_smooth` |
| Poor metric match | Target metric infeasible | Check if target eigenvalues are within swelling bounds |
| ICP fails to align | Initial pose too far | Use visual or manual pre-alignment |
| Fabrication imprecision | Pattern too fine | Increase cell size or blur pattern |


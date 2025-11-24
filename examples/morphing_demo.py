"""
examples/morphing_demo.py

End-to-end 2D→3D morphing pipeline demonstration.

Workflow:
  1. Define target 3D surface (spherical cap)
  2. Compute desired metric field
  3. Optimize 2D growth pattern
  4. Encode as grayscale for fabrication
  5. Simulate 3D actuation result
  6. Measure error and visualize convergence
"""

import numpy as np
import sys
sys.path.insert(0, ".")

from morphing.geometry.target import AnalyticSurface, sample_surface_on_grid
from morphing.optimization.optimizer import PatternOptimizer
from morphing.materials.material_model import IsotropicMaterial, PatternFabricator
from morphing.sensing.feedback import FeedbackController, ErrorMetrics, IterativeClosestPoint


def demo_spherical_cap():
    """Optimize growth pattern for a spherical cap morphing."""
    
    print("=" * 60)
    print("MORPHING PIPELINE DEMO: Spherical Cap")
    print("=" * 60)
    
    # 1. DEFINE TARGET SURFACE
    print("\n[1] Creating spherical cap target surface...")
    
    # Spherical cap: X(u, v) = (u, v, sqrt(R² - u² - v²) - (R - h))
    R, h = 5.0, 1.5  # radius 5, height 1.5
    
    def spherical_cap_X(u, v):
        r_sq = u**2 + v**2
        R_sq_minus_h_sq = R**2 - (R - h)**2
        if r_sq > R_sq_minus_h_sq:
            return (float(u), float(v), 0.0)  # flat outside cap
        z = np.sqrt(R**2 - r_sq) - (R - h)
        return (float(u), float(v), float(z))
    
    domain = ((-3, 3), (-3, 3))
    surface = AnalyticSurface(spherical_cap_X, domain)
    
    # 2. SAMPLE TARGET METRIC
    print("[2] Computing target metric field...")
    nx, ny = 8, 8
    metrics, positions = sample_surface_on_grid(surface, nx, ny)
    print(f"   Sampled {nx*ny} cells on 2D domain")
    print(f"   Metric shapes: {metrics.shape}")
    
    # 3. OPTIMIZE GROWTH PATTERN
    print("[3] Optimizing growth pattern...")
    
    # For spherical cap, isotropic growth g² ≈ target metric eigenvalue
    # Extract scalar growth targets
    target_growths = np.sqrt(np.linalg.eigvalsh(metrics)[:, -1])  # largest eigenvalue
    target_growths = target_growths / target_growths.max() * 1.5  # normalize to [0, 1.5]
    
    optimizer = PatternOptimizer(
        target_metric=metrics,
        g_min=0.8,
        g_max=2.0,
        lambda_smooth=0.15,
        lambda_fab=0.05
    )
    
    # Try Adam optimizer
    result = optimizer.adam(
        initial_g=np.ones(len(metrics)) * 1.0,
        learning_rate=0.02,
        max_iterations=200
    )
    
    print(f"   Optimization converged: {result.convergence}")
    print(f"   Final energy: {result.energy:.6f}")
    print(f"   Metric error: {result.metric_error:.6f}")
    print(f"   Iterations: {result.iterations}")
    
    # 4. FABRICATION OUTPUT
    print("[4] Generating fabrication patterns...")
    
    material = IsotropicMaterial(g_min=0.8, g_max=2.0)
    material.default_calibration()
    
    # Convert growth to grayscale
    grayscale_pattern = material.growth_to_grayscale(result.growth_field)
    
    print(f"   Growth field range: [{result.growth_field.min():.3f}, {result.growth_field.max():.3f}]")
    print(f"   Grayscale range: [{grayscale_pattern.min()}, {grayscale_pattern.max()}]")
    
    # Export to SVG (for visualization/fabrication)
    svg_file = "output_growth_pattern.svg"
    PatternFabricator.to_svg(result.growth_field, nx, ny, svg_file, cell_size=20)
    print(f"   ✓ Exported SVG: {svg_file}")
    
    # 5. SIMULATE ACTUATED SHAPE
    print("[5] Simulating 3D shape from growth pattern...")
    
    # Simple forward model: realized shape = flattened with local isotropic growth
    # For demo, sample target surface at optimized growth locations
    simulated_points = []
    for i, g_i in enumerate(result.growth_field):
        u_idx, v_idx = divmod(i, ny)
        u = positions[i, 0]
        v = positions[i, 1]
        
        # Scale by realized growth (isotropic swelling)
        u_actuated = u * np.sqrt(g_i)
        v_actuated = v * np.sqrt(g_i)
        
        # Evaluate target surface (forward model)
        x, y, z = spherical_cap_X(u_actuated, v_actuated)
        simulated_points.append([x, y, z])
    
    simulated_points = np.array(simulated_points)
    print(f"   Simulated shape: {simulated_points.shape} point cloud")
    
    # 6. MEASUREMENT & ERROR ANALYSIS
    print("[6] Computing shape error metrics...")
    
    # Ground truth: target surface
    target_points = np.array([spherical_cap_X(u, v) for u, v in positions])
    
    # ICP alignment
    R, t, align_error = IterativeClosestPoint.align(simulated_points, target_points)
    
    # Error metrics
    hausdorff = ErrorMetrics.hausdorff_distance(simulated_points, target_points)
    mean_dist = ErrorMetrics.mean_distance(simulated_points, target_points)
    
    print(f"   Hausdorff distance: {hausdorff:.6f}")
    print(f"   Mean distance: {mean_dist:.6f}")
    print(f"   ICP alignment error: {align_error:.6f}")
    
    # 7. CONVERGENCE ANALYSIS
    print("[7] Optimization convergence...")
    if result.history:
        print(f"   Initial energy: {result.history['energy'][0]:.6f}")
        print(f"   Final energy: {result.history['energy'][-1]:.6f}")
        print(f"   Energy reduction: {(1 - result.history['energy'][-1]/result.history['energy'][0])*100:.1f}%")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    
    return {
        "growth_field": result.growth_field,
        "metrics": metrics,
        "simulated_shape": simulated_points,
        "target_shape": target_points,
        "error_metrics": {
            "hausdorff": hausdorff,
            "mean_distance": mean_dist,
            "metric_error": result.metric_error
        }
    }


if __name__ == "__main__":
    results = demo_spherical_cap()

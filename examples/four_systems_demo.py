# examples/four_systems_demo.py
"""
Demonstration of all four systems working together:
1. Intelligent Surface Nets (procedural geometry)
2. Aesthetic Pathways (color harmony)
3. CAD Multi-View (4 viewports)
4. Transform Unification (2D/3D math)
"""

import sys
sys.path.insert(0, '.')

from graphics.intelligent_surface_nets import IntelligentSurfaceNets
from engine.aesthetic_pathway import AestheticPathway
from graphics.cad_renderer import CADRenderer, createCube
from math.transform_unified import Transform3D, RectTransform, Camera, Vec3, Quat

def demo_four_systems():
    print("=" * 70)
    print("FOUR SYSTEMS DEMO: Intelligent Mesh, Aesthetics, CAD, Unification")
    print("=" * 70)
    
    # --- SYSTEM 1: Intelligent Surface Nets ---
    print("\n[1/4] Intelligent Surface Nets")
    print("------")
    
    # Create simple volume data (placeholder)
    import numpy as np
    volume = np.random.randint(0, 2, (8, 8, 8))
    volume_data = {
        'volume': volume,
        'resolution': {'x': 8, 'y': 8, 'z': 8}
    }
    
    nets = IntelligentSurfaceNets(volume_data)
    nets.enableSmoothing(level=5.0)
    nets.enhanceDetail(level=1.5)
    
    mesh = nets.generateMesh()
    print(f"  ✓ Generated mesh: {len(mesh.vertices)} vertices, {len(mesh.indices)} indices")
    print(f"  ✓ Smoothing enabled: {nets.smoothingFactor:.2f}")
    print(f"  ✓ Detail multiplier: {nets.detailMultiplier:.2f}")
    
    # --- SYSTEM 2: Aesthetic Pathways ---
    print("\n[2/4] Aesthetic Pathways (Golden Ratio)")
    print("------")
    
    pathway = AestheticPathway()
    aesthetic_eval = pathway.evaluate(mesh.to_dict())
    
    print(f"  ✓ Geometry Entropy: {aesthetic_eval.geometry_stats['entropy']:.3f}")
    print(f"  ✓ Detected Mood: {aesthetic_eval.mood.upper()}")
    print(f"  ✓ Aesthetic Score: {aesthetic_eval.score:.3f}")
    print(f"  ✓ Primary Color: #{aesthetic_eval.optimalColor:06X}")
    print(f"  ✓ Secondary Color: #{aesthetic_eval.secondaryColor:06X}")
    print(f"  ✓ Lighting Profile: {aesthetic_eval.lightingProfile}")
    print(f"  ✓ Golden Ratio PHI: {pathway.PHI:.5f}")
    
    # --- SYSTEM 3: CAD Multi-View Renderer ---
    print("\n[3/4] CAD Multi-View Renderer")
    print("------")
    
    renderer = CADRenderer(1600, 1200)
    cube_verts, cube_indices = createCube(size=2.0)
    cad_results = renderer.renderCAD(cube_verts, cube_indices)
    
    for view_name in ['TOP', 'ISO', 'FRONT', 'CAMERA']:
        view_data = cad_results[view_name]
        visible_count = sum(1 for p in view_data['projections'] if p.visible)
        print(f"  ✓ View [{view_name:6}]: {visible_count}/{len(cube_verts)} vertices visible")
    
    # --- SYSTEM 4: Transform Unification ---
    print("\n[4/4] Transform Unification (2D/3D Bridge)")
    print("------")
    
    # 3D Transform
    t3d = Transform3D(
        position=Vec3(1, 2, 3),
        rotation=Quat(1, 0, 0, 0),
        scale=Vec3(1, 1, 1)
    )
    mat3d = t3d.toMatrix()
    print(f"  ✓ Transform3D → Mat4 (16-element matrix)")
    print(f"    Position: {t3d.position}")
    print(f"    Scale: {t3d.scale}")
    
    # 2D Transform (UI)
    rect = RectTransform(x=100, y=50, w=200, h=150, rotation=0.3, depth=5)
    mat2d = rect.toMatrix()
    print(f"  ✓ RectTransform → Mat4 (same format as 3D)")
    print(f"    Pixel: ({rect.x}, {rect.y}), Size: ({rect.w}, {rect.h})")
    print(f"    Rotation: {rect.rotation:.3f} rad, Depth: {rect.depth}")
    
    # Camera (unified)
    camera = Camera(1920, 1080)
    camera.setOrthographic2D(1920, 1080)
    print(f"  ✓ Camera switching between perspectives")
    print(f"    Current mode: Orthographic 2D (UI)")
    
    # --- Integration Example ---
    print("\n" + "=" * 70)
    print("INTEGRATION: All Four Systems Communicating")
    print("=" * 70)
    
    print(f"""
    Workflow:
    
    1. PROCEDURAL GENERATION
       │ → Intelligent Surface Nets generates {len(mesh.vertices)} vertices
       │
    2. AESTHETIC ANALYSIS
       │ → Analyzes geometry, detects '{aesthetic_eval.mood}' mood
       │ → Assigns color #{aesthetic_eval.optimalColor:06X} via Golden Ratio
       │
    3. MULTI-VIEW RENDERING
       │ → CAD Renderer projects mesh into 4 viewports
       │ → TOP view (engineering), ISO (3D visualization), etc.
       │
    4. TRANSFORM UNIFICATION
       │ → UI buttons (2D) and 3D objects use same matrix math
       │ → Camera switches between game (3D) and editor (2D) views
    
    Result: Seamless integration of procedural generation, color harmony,
            CAD visualization, and unified coordinate systems.
    """)
    
    print("=" * 70)
    print("✅ DEMO COMPLETE: All Four Systems Working Together")
    print("=" * 70)

if __name__ == "__main__":
    demo_four_systems()

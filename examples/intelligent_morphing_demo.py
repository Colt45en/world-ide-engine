"""Intelligent Morphing Demo: Body & Soul Feedback Loop.

Demonstrates the complete "Nexus" system:
- Create a voxel volume (sphere, cube, or hybrid shape)
- Generate mesh with IntelligentSurfaceNets (intelligent vertex placement, fractal detail)
- Analyze geometry (entropy, aspect ratio, surface area)
- Run through AestheticPathway (mood detection, Golden Ratio color harmony)
- Display feedback recommendations for iterative refinement
"""
import numpy as np
import sys
sys.path.insert(0, 'c:/fresh-world-engine')

from geometry.surface_nets import IntelligentSurfaceNets, MeshData, GeometryStats
from aesthetics.pathway import AestheticPathway
from nexus.core import Nexus

def create_test_volume(volume_type='sphere', size=20):
    """Create a test voxel volume."""
    volume = np.zeros((size, size, size), dtype=np.float32)
    center = size / 2
    radius = size / 3
    
    if volume_type == 'sphere':
        for x in range(size):
            for y in range(size):
                for z in range(size):
                    dist = np.sqrt((x - center)**2 + (y - center)**2 + (z - center)**2)
                    if dist < radius:
                        volume[x, y, z] = max(0, 1 - (dist / radius)**2)
    
    elif volume_type == 'cube':
        margin = size // 4
        volume[margin:size-margin, margin:size-margin, margin:size-margin] = 1.0
    
    elif volume_type == 'torus':
        major_radius = size // 3
        minor_radius = size // 8
        for x in range(size):
            for y in range(size):
                for z in range(size):
                    # Torus implicit: sqrt((sqrt(x^2 + y^2) - R)^2 + z^2) < r
                    xy_dist = np.sqrt((x - center)**2 + (y - center)**2)
                    dist = np.sqrt((xy_dist - major_radius)**2 + (z - center)**2)
                    if dist < minor_radius:
                        volume[x, y, z] = max(0, 1 - (dist / minor_radius)**2)
    
    return volume

def format_color(rgb):
    """Format RGB tuple as hex."""
    return '#{:02x}{:02x}{:02x}'.format(
        int(np.clip(rgb[0] * 255, 0, 255)),
        int(np.clip(rgb[1] * 255, 0, 255)),
        int(np.clip(rgb[2] * 255, 0, 255))
    )

def demo():
    """Run the full Body & Soul demo."""
    print("\n" + "="*70)
    print("🌍 NEXUS: Body & Soul Feedback Loop")
    print("="*70)
    
    # Create test volume
    print("\n[1] Creating voxel volume (sphere)...")
    volume = create_test_volume('sphere', size=20)
    print(f"    Volume shape: {volume.shape}, non-zero voxels: {np.count_nonzero(volume)}")
    
    # Initialize Nexus
    print("\n[2] Initializing Nexus orchestration hub...")
    nexus = Nexus()
    
    # Process through the complete feedback loop
    print("\n[3] Processing through Nexus (form → geometry → aesthetics → feedback)...")
    output = nexus.process_intelligent_silhouette(
        volume,
        resolution=(20, 20, 20),
        user_intent='balanced'
    )
    
    # Display geometry analysis
    print("\n" + "-"*70)
    print("📊 GEOMETRY ANALYSIS (The Body)")
    print("-"*70)
    stats = output.geometry_stats
    print(f"Mesh Vertices: {len(output.mesh.vertices)}")
    print(f"Mesh Faces: {len(output.mesh.indices) // 3}")
    print(f"Surface Area: {stats.surface_area:.2f}")
    print(f"Bounds: {stats.bounds_min.round(2)} → {stats.bounds_max.round(2)}")
    print(f"Aspect Ratio: {stats.aspect_ratio}")
    print(f"Entropy (Jaggedness): {stats.entropy:.3f}")
    if stats.entropy > 0.5:
        print("  ↳ Status: ENERGETIC (high surface complexity)")
    else:
        print("  ↳ Status: CALM (smooth surfaces)")
    
    # Display aesthetic evaluation
    print("\n" + "-"*70)
    print("🎨 AESTHETIC EVALUATION (The Soul)")
    print("-"*70)
    aesthetic = output.aesthetic_eval
    print(f"Detected Mood: {aesthetic.mood.upper()}")
    print(f"Beauty Score: {aesthetic.beauty_score:.3f}/1.0")
    print(f"Lighting Profile: {aesthetic.palette.lighting_profile}")
    print(f"\nColor Palette:")
    print(f"  Primary (φ harmony):   {format_color(aesthetic.palette.primary_color)}")
    print(f"  Secondary (φ shift):   {format_color(aesthetic.palette.secondary_color)}")
    print(f"  Accent (complement):   {format_color(aesthetic.palette.accent_color)}")
    
    print(f"\nColor Harmonies:")
    for scheme_name, colors in aesthetic.harmonies.items():
        if isinstance(colors, list):
            hex_colors = [format_color(c) for c in colors]
            print(f"  {scheme_name:20s}: {' → '.join(hex_colors)}")
        else:
            print(f"  {scheme_name:20s}: {format_color(colors)}")
    
    # Display feedback recommendations
    print("\n" + "-"*70)
    print("🔄 FEEDBACK LOOP (Form ↔ Soul)")
    print("-"*70)
    feedback = output.feedback_recommendations
    print(f"Overall Quality: {feedback['overall_quality']:.3f}/1.0")
    print(f"Geometry Quality: {feedback['geometry_quality']:.3f}/1.0")
    print(f"Aesthetic Quality: {feedback['aesthetic_quality']:.3f}/1.0")
    print(f"Mood Alignment: {'✓ Matched' if feedback['mood_alignment'] else '✗ Mismatched'}")
    
    if feedback['refinement_suggestions']:
        print(f"\nRefinement Suggestions ({len(feedback['refinement_suggestions'])}):")
        for i, suggestion in enumerate(feedback['refinement_suggestions'], 1):
            print(f"  [{i}] {suggestion['action'].upper()}")
            print(f"      Reason: {suggestion['reason']}")
            print(f"      Confidence: {suggestion['confidence']:.1%}")
    else:
        print("\n✓ No refinements suggested - geometry is well-balanced!")
    
    print("\n" + "="*70)
    print("Demo Complete")
    print("="*70 + "\n")

if __name__ == '__main__':
    demo()

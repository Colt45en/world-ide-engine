"""Full End-to-End Integration Demo

Demonstrates the complete pipeline:
1. Text input → MetaOrchestrator
2. Extracts physics parameters → Physics bridge
3. Extracts render transforms → Graphics bridge  
4. Extracts embeddings → Procedural bridge
5. Generates physics bodies + visuals + meshes
6. Displays complete integrated system state
"""

from meta.orchestrator_v2 import MetaOrchestrator
from meta.physics_integration import PhysicsOrchestratorBridge
from graphics.orchestrator_render import OrchestratorRenderBridge
from procedural.orchestrator_seed import OrchestratorProceduralBridge


def demo_full_integration():
    """Run complete end-to-end integration demo."""
    
    print("=" * 80)
    print("FULL END-TO-END INTEGRATION DEMO")
    print("=" * 80)
    print()
    
    # Initialize all systems
    orchestrator = MetaOrchestrator()
    physics_bridge = PhysicsOrchestratorBridge()
    graphics_bridge = OrchestratorRenderBridge()
    procedural_bridge = OrchestratorProceduralBridge()
    
    # Test input
    test_input = "aggressive rebuild with advanced physics"
    
    print(f"INPUT: {test_input}")
    print("-" * 80)
    
    # Step 1: Orchestrate
    print("\n[1] ORCHESTRATION")
    state = orchestrator.orchestrate(test_input)
    decision = state.get("decision", "unknown")
    print(f"    Decision: {decision}")
    print(f"    Tokens processed: {state.get('token_count', 0)}")
    
    # Step 2: Physics
    print("\n[2] PHYSICS INTEGRATION")
    physics_body = physics_bridge.create_body_from_orchestrator("primary_body", state)
    print(f"    ✓ Created RigidBody")
    print(f"      Mass: {physics_body.mass:.3f}")
    print(f"      Velocity: ({physics_body.velocity.x:.3f}, {physics_body.velocity.y:.3f}, {physics_body.velocity.z:.3f}) m/s")
    
    # Simulate physics
    for step in range(3):
        physics_bridge.step_physics("primary_body", delta_time=0.016)
    phys_state = physics_bridge.get_body_feedback("primary_body")
    print(f"    Physics simulation: {phys_state.get('feedback_text', 'N/A')}")
    
    # Step 3: Graphics
    print("\n[3] GRAPHICS INTEGRATION")
    graphics_obj = graphics_bridge.create_object_from_orchestrator("main_visual", state, obj_type="cube")
    print(f"    ✓ Created SceneObject: {graphics_obj.obj_type}")
    print(f"      Position: {graphics_obj.position}")
    print(f"      Color: {graphics_obj.color}")
    print(f"      Scale: {graphics_obj.scale}")
    
    # Step 4: Procedural
    print("\n[4] PROCEDURAL GENERATION")
    mesh = procedural_bridge.generate_from_orchestrator("primary_mesh", state)
    mesh_stats = procedural_bridge.get_mesh_statistics("primary_mesh")
    print(f"    ✓ Generated procedural mesh")
    print(f"      Type: {mesh.get('dna', {}).get('fractal_type', 'unknown')}")
    print(f"      Detail level: {mesh.get('dna', {}).get('detail_level', 0)}")
    print(f"      Vertices: {mesh_stats.get('vertex_count', 0)}")
    print(f"      Faces: {mesh_stats.get('face_count', 0)}")
    if 'bounds' in mesh_stats:
        bounds = mesh_stats['bounds']
        print(f"      Bounds: X{bounds['x']}, Y{bounds['y']}, Z{bounds['z']}")
    
    # Final System Status
    print("\n" + "=" * 80)
    print("INTEGRATED SYSTEM STATUS")
    print("=" * 80)
    
    # Physics status
    phys_status = physics_bridge.get_system_status()
    print(f"\nPhysics System:")
    print(f"  Active bodies: {phys_status['active_bodies']}")
    print(f"  Integration steps: {phys_status['total_integration_steps']}")
    
    # Graphics status
    gfx_status = graphics_bridge.get_system_status()
    print(f"\nGraphics System:")
    print(f"  Scene objects: {gfx_status['total_objects']}")
    print(f"  Scene lights: {gfx_status['total_lights']}")
    print(f"  Total renders: {gfx_status['total_renders']}")
    
    # Procedural status
    proc_status = procedural_bridge.get_system_status()
    print(f"\nProcedural System:")
    print(f"  Generated meshes: {proc_status['total_generators']}")
    print(f"  Total generations: {proc_status['total_generations']}")
    print(f"  Cached meshes: {proc_status['cached_meshes']}")
    
    # Render command preview
    print("\n" + "=" * 80)
    print("RENDER COMMAND PREVIEW")
    print("=" * 80)
    render_cmd = graphics_bridge.get_render_command()
    print(f"\nObjects ready to render: {len(render_cmd['objects'])}")
    for obj in render_cmd['objects']:
        print(f"  - {obj['id']} ({obj['type']})")
        print(f"      Position: {obj['transform']['position']}")
        print(f"      Material: {obj['material']['color']}")
    
    print(f"\nLighting setup:")
    print(f"  Total lights: {len(render_cmd['lights'])}")
    
    print("\n" + "=" * 80)
    print("✓ FULL END-TO-END INTEGRATION COMPLETE")
    print("=" * 80)
    print("\nAll systems operational:")
    print("  ✓ Meta-Orchestrator: Text → Tokens → Embeddings → Decision")
    print("  ✓ Physics Bridge: Decision → RigidBody → Simulation")
    print("  ✓ Graphics Bridge: Transforms + Colors → Scene Graph")
    print("  ✓ Procedural Bridge: Embeddings → Mesh Generation")
    print("\nData flow: Input → Orchestration → Multi-modal outputs → Integration → Visualization")


if __name__ == "__main__":
    demo_full_integration()

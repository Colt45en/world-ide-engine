"""Graphics-Orchestrator Integration Demo

Demonstrates the complete visual flow:
1. MetaOrchestrator processes text input
2. Extracts render transforms (position, rotation, scale)
3. Extracts color palette from embeddings
4. OrchestratorRenderBridge creates/updates scene objects
5. Builds render command for visualization
6. Returns feedback on visual state
"""

from meta.orchestrator_v2 import MetaOrchestrator
from graphics.orchestrator_render import OrchestratorRenderBridge


def demo_graphics_orchestrator_integration():
    """Run complete graphics-orchestrator integration demo."""
    
    print("=" * 70)
    print("GRAPHICS-ORCHESTRATOR INTEGRATION DEMO")
    print("=" * 70)
    
    # Initialize systems
    orchestrator = MetaOrchestrator()
    graphics_bridge = OrchestratorRenderBridge()
    
    # Add lighting to the scene
    graphics_bridge.scene.add_light(
        "main_light",
        light_type="directional",
        position=(5, 5, 5),
        color=(1, 1, 1),
        intensity=0.8
    )
    graphics_bridge.scene.add_light(
        "fill_light",
        light_type="point",
        position=(-5, 2, 0),
        color=(0.5, 0.7, 1.0),
        intensity=0.4
    )
    
    # Test inputs
    test_inputs = [
        "create aggressive red sphere",
        "build gentle blue cube",
        "construct balanced green pyramid"
    ]
    
    object_types = ["sphere", "cube", "pyramid"]
    
    for idx, (input_text, obj_type) in enumerate(zip(test_inputs, object_types), 1):
        print(f"\n[Test {idx}] Input: '{input_text}'")
        print("-" * 70)
        
        # Step 1: Orchestrator processes input
        orchestrator_state = orchestrator.orchestrate(input_text)
        
        # Step 2: Extract decision
        decision = orchestrator_state.get("decision", "unknown")
        print(f"Orchestrator Decision: {decision}")
        
        # Step 3: Extract render transforms
        render_transforms = orchestrator_state.get("render_transforms", {})
        position = render_transforms.get("position", (0, 0, 0))
        rotation = render_transforms.get("rotation", (0, 0, 0))
        scale = render_transforms.get("scale", (1, 1, 1))
        
        # Handle tuple values
        if isinstance(position, tuple) and len(position) > 0:
            pos_display = f"({position[0]:.2f}, {position[1]:.2f}, {position[2]:.2f})"
        else:
            pos_display = str(position)
        
        if isinstance(rotation, tuple) and len(rotation) > 0:
            rot_display = f"({rotation[0]:.2f}, {rotation[1]:.2f}, {rotation[2]:.2f})"
        else:
            rot_display = str(rotation)
        
        if isinstance(scale, tuple) and len(scale) > 0:
            scale_display = f"({scale[0]:.2f}, {scale[1]:.2f}, {scale[2]:.2f})"
        else:
            scale_display = str(scale)
        
        print(f"Render Transforms:")
        print(f"  Position: {pos_display}")
        print(f"  Rotation: {rot_display}")
        print(f"  Scale: {scale_display}")
        
        # Step 4: Extract colors
        colors = orchestrator_state.get("colors", {})
        primary_color = colors.get("primary", (1, 1, 1))
        print(f"Colors: {colors}")
        
        # Step 5: Create or update graphics object
        obj_id = f"object_{idx}"
        if obj_id not in graphics_bridge.scene.objects:
            obj = graphics_bridge.create_object_from_orchestrator(obj_id, orchestrator_state, obj_type=obj_type)
            print(f"✓ Created new {obj_type}: {obj_id}")
        else:
            graphics_bridge.apply_orchestrator_to_object(obj_id, orchestrator_state)
            print(f"✓ Updated existing object: {obj_id}")
        
        # Display object state
        obj = graphics_bridge.scene.get_object(obj_id)
        if obj:
            print(f"\nObject State:")
            print(f"  Type: {obj.obj_type}")
            print(f"  Position: {obj.position}")
            print(f"  Rotation: {obj.rotation}")
            print(f"  Scale: {obj.scale}")
            print(f"  Color (RGB): {obj.color}")
            print(f"  Metallic: {obj.metallic:.2f}")
            print(f"  Roughness: {obj.roughness:.2f}")
    
    # Generate and display render command
    print("\n" + "=" * 70)
    print("RENDER COMMAND")
    print("=" * 70)
    render_cmd = graphics_bridge.get_render_command()
    print(f"Objects to render: {len(render_cmd['objects'])}")
    print(f"Lights in scene: {len(render_cmd['lights'])}")
    print(f"Scene update count: {render_cmd['update_count']}")
    
    print("\nObject Details:")
    for obj_data in render_cmd['objects']:
        print(f"\n  {obj_data['id']} ({obj_data['type']}):")
        print(f"    Position: {obj_data['transform']['position']}")
        print(f"    Color: {obj_data['material']['color']}")
        print(f"    Roughness: {obj_data['material']['roughness']:.2f}")
    
    # Final system status
    print("\n" + "=" * 70)
    print("GRAPHICS SYSTEM STATUS")
    print("=" * 70)
    status = graphics_bridge.get_system_status()
    print(f"Total objects: {status['total_objects']}")
    print(f"Total lights: {status['total_lights']}")
    print(f"Total renders: {status['total_renders']}")
    print(f"Scene updates: {status['scene_updates']}")
    
    print("\n✓ Graphics-Orchestrator integration demo complete!")


if __name__ == "__main__":
    demo_graphics_orchestrator_integration()

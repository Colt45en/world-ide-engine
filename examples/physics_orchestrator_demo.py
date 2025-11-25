"""Physics-Orchestrator Integration Demo

Demonstrates the complete flow:
1. MetaOrchestrator processes text input
2. Extracts physics parameters (mass, velocity, restitution)
3. PhysicsOrchestratorBridge creates/updates RigidBody
4. Steps physics simulation
5. Returns feedback
"""

from meta.orchestrator_v2 import MetaOrchestrator
from meta.physics_integration import PhysicsOrchestratorBridge, orchestrator_to_physics
from physics.body import RigidBody, Vec3


def demo_physics_orchestrator_integration():
    """Run complete physics-orchestrator integration demo."""
    
    print("=" * 70)
    print("PHYSICS-ORCHESTRATOR INTEGRATION DEMO")
    print("=" * 70)
    
    # Initialize systems
    orchestrator = MetaOrchestrator()
    bridge = PhysicsOrchestratorBridge()
    
    # Test inputs that will control physics
    test_inputs = [
        "rebuild system with aggressive physics",
        "gentle collision response",
        "balanced momentum transfer"
    ]
    
    for idx, input_text in enumerate(test_inputs, 1):
        print(f"\n[Test {idx}] Input: '{input_text}'")
        print("-" * 70)
        
        # Step 1: Orchestrator processes input
        orchestrator_state = orchestrator.orchestrate(input_text)
        
        # Step 2: Extract physics parameters
        physics_params = orchestrator_state.get("physics_params", {})
        mass = physics_params.get("mass", 1.0)
        velocity_raw = physics_params.get("velocity", 0.0)
        # Handle velocity as either tuple or scalar
        if isinstance(velocity_raw, tuple):
            velocity = velocity_raw[0]
        else:
            velocity = velocity_raw
        restitution = physics_params.get("restitution", 0.5)
        decision = orchestrator_state.get("decision", "unknown")
        
        print(f"Orchestrator Decision: {decision}")
        print(f"Physics Params: mass={mass:.2f}, velocity={velocity:.2f}, restitution={restitution:.2f}")
        
        # Step 3: Create or update physics body
        body_id = f"body_{idx}"
        
        # Create a modified state dict for physics bridge (it expects scalar velocity)
        modified_state = orchestrator_state.copy()
        modified_state["physics_params"] = {
            "mass": mass,
            "velocity": velocity,
            "restitution": restitution
        }
        
        if body_id not in bridge.bodies:
            body = bridge.create_body_from_orchestrator(body_id, modified_state)
            print(f"✓ Created new body: {body_id}")
        else:
            bridge.apply_orchestrator_params_to_body(body_id, modified_state)
            print(f"✓ Updated existing body: {body_id}")
        
        # Step 4: Simulate physics for a few steps
        print("\nPhysics Simulation Steps:")
        for step in range(3):
            state = bridge.step_physics(body_id, delta_time=0.016)
            pos = state.get("position", (0, 0, 0))
            vel = state.get("velocity", (0, 0, 0))
            print(f"  Step {step}: pos=({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}), vel={vel[0]:.3f} m/s")
        
        # Step 5: Get feedback for next iteration
        feedback = bridge.get_body_feedback(body_id)
        print(f"Feedback: {feedback.get('feedback_text', 'N/A')}")
    
    # Final system status
    print("\n" + "=" * 70)
    print("SYSTEM STATUS")
    print("=" * 70)
    status = bridge.get_system_status()
    print(f"Active bodies: {status['active_bodies']}")
    print(f"Total integration steps: {status['total_integration_steps']}")
    print("\nBodies state:")
    for bid, state in status['bodies'].items():
        print(f"  {bid}: mass={state['mass']:.2f}, pos={state['position']}, vel={state['velocity']}")
    
    print("\n✓ Physics-Orchestrator integration demo complete!")


if __name__ == "__main__":
    demo_physics_orchestrator_integration()

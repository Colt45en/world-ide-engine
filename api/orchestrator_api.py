"""Orchestrator API Backend

Provides REST API endpoints for the orchestrator dashboard:
- /api/orchestrate - process text input
- /api/physics - get physics body state
- /api/graphics - get scene state
- /api/procedural - get mesh state
- /api/feedback - run feedback loop
- /api/metrics - get system metrics
"""

import json
from datetime import datetime
from meta.orchestrator_v2 import MetaOrchestrator
from meta.physics_integration import PhysicsOrchestratorBridge
from graphics.orchestrator_render import OrchestratorRenderBridge
from procedural.orchestrator_seed import OrchestratorProceduralBridge
from meta.feedback_loop import FeedbackLoop


class OrchestratorAPI:
    """API backend for orchestrator dashboard."""
    
    def __init__(self):
        self.orchestrator = MetaOrchestrator()
        self.physics_bridge = PhysicsOrchestratorBridge()
        self.graphics_bridge = OrchestratorRenderBridge()
        self.procedural_bridge = OrchestratorProceduralBridge()
        
        self.last_state = {}
        self.request_count = 0
        self.start_time = datetime.now()
    
    def orchestrate(self, text_input: str) -> dict:
        """Process text input through orchestrator.
        
        Args:
            text_input: User input text
            
        Returns:
            Complete orchestration state
        """
        self.request_count += 1
        
        state = self.orchestrator.orchestrate(text_input)
        self.last_state = state
        
        return {
            "status": "success",
            "request_id": self.request_count,
            "timestamp": datetime.now().isoformat(),
            "input": text_input,
            "decision": state.get("decision"),
            "token_count": state.get("token_count", 0),
            "physics_params": state.get("physics_params"),
            "colors": state.get("colors"),
            "embedding_count": len(state.get("embeddings", [])),
        }
    
    def create_physics_body(self, body_id: str = "body_1") -> dict:
        """Create physics body from current orchestrator state."""
        if not self.last_state:
            return {"status": "error", "message": "No orchestration state"}
        
        body = self.physics_bridge.create_body_from_orchestrator(body_id, self.last_state)
        
        return {
            "status": "success",
            "body_id": body_id,
            "mass": body.mass,
            "position": {"x": body.position.x, "y": body.position.y, "z": body.position.z},
            "velocity": {"x": body.velocity.x, "y": body.velocity.y, "z": body.velocity.z},
        }
    
    def create_graphics_object(self, obj_id: str = "obj_1", obj_type: str = "cube") -> dict:
        """Create graphics object from current orchestrator state."""
        if not self.last_state:
            return {"status": "error", "message": "No orchestration state"}
        
        obj = self.graphics_bridge.create_object_from_orchestrator(obj_id, self.last_state, obj_type)
        
        return {
            "status": "success",
            "object_id": obj_id,
            "type": obj_type,
            "position": obj.position,
            "rotation": obj.rotation,
            "scale": obj.scale,
            "color": obj.color,
        }
    
    def generate_mesh(self, gen_id: str = "mesh_1") -> dict:
        """Generate procedural mesh from current orchestrator state."""
        if not self.last_state:
            return {"status": "error", "message": "No orchestration state"}
        
        mesh = self.procedural_bridge.generate_from_orchestrator(gen_id, self.last_state)
        stats = self.procedural_bridge.get_mesh_statistics(gen_id)
        
        dna = mesh.get("dna", {})
        
        return {
            "status": "success",
            "generator_id": gen_id,
            "fractal_type": dna.get("fractal_type", "unknown"),
            "detail_level": dna.get("detail_level", 0),
            "vertex_count": stats.get("vertex_count", 0),
            "face_count": stats.get("face_count", 0),
            "bounds": stats.get("bounds", {}),
        }
    
    def run_feedback_loop(self, initial_text: str, max_cycles: int = 5) -> dict:
        """Execute feedback loop for self-correction."""
        loop = FeedbackLoop(max_cycles=max_cycles)
        result = loop.run_feedback_loop(initial_text)
        
        return {
            "status": "success",
            "cycles": len(result["history"]),
            "convergence": result["convergence"],
            "final_decision": result["final_decision"],
            "history": [
                {
                    "cycle": h["cycle"],
                    "decision": h["decision"],
                    "mass": h["mass"],
                    "velocity": h["velocity"],
                }
                for h in result["history"]
            ],
        }
    
    def get_metrics(self) -> dict:
        """Get system-wide metrics."""
        phys_status = self.physics_bridge.get_system_status()
        gfx_status = self.graphics_bridge.get_system_status()
        proc_status = self.procedural_bridge.get_system_status()
        
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "status": "success",
            "uptime_seconds": uptime,
            "total_requests": self.request_count,
            "physics": {
                "active_bodies": phys_status["active_bodies"],
                "integration_steps": phys_status["total_integration_steps"],
            },
            "graphics": {
                "scene_objects": gfx_status["total_objects"],
                "lights": gfx_status["total_lights"],
                "renders": gfx_status["total_renders"],
            },
            "procedural": {
                "generators": proc_status["total_generators"],
                "generations": proc_status["total_generations"],
                "cached_meshes": proc_status["cached_meshes"],
            },
        }
    
    def get_complete_state(self) -> dict:
        """Get complete current system state (for dashboard)."""
        return {
            "timestamp": datetime.now().isoformat(),
            "orchestrator_state": self.last_state,
            "metrics": self.get_metrics(),
            "request_count": self.request_count,
        }


def demo_api():
    """Demonstrate API endpoints."""
    
    print("=" * 80)
    print("ORCHESTRATOR API BACKEND DEMO")
    print("=" * 80)
    
    api = OrchestratorAPI()
    
    # 1. Orchestrate
    print("\n[1] POST /api/orchestrate")
    orch_resp = api.orchestrate("aggressive procedural generation")
    print(f"    Status: {orch_resp['status']}")
    print(f"    Decision: {orch_resp['decision']}")
    print(f"    Tokens: {orch_resp['token_count']}")
    
    # 2. Create physics body
    print("\n[2] POST /api/physics")
    phys_resp = api.create_physics_body()
    print(f"    Status: {phys_resp['status']}")
    print(f"    Body mass: {phys_resp['mass']:.3f}")
    print(f"    Body velocity: {phys_resp['velocity']}")
    
    # 3. Create graphics object
    print("\n[3] POST /api/graphics")
    gfx_resp = api.create_graphics_object()
    print(f"    Status: {gfx_resp['status']}")
    print(f"    Object type: {gfx_resp['type']}")
    print(f"    Position: {gfx_resp['position']}")
    print(f"    Color: {gfx_resp['color']}")
    
    # 4. Generate mesh
    print("\n[4] POST /api/procedural")
    mesh_resp = api.generate_mesh()
    print(f"    Status: {mesh_resp['status']}")
    print(f"    Fractal: {mesh_resp['fractal_type']}")
    print(f"    Vertices: {mesh_resp['vertex_count']}")
    print(f"    Faces: {mesh_resp['face_count']}")
    
    # 5. Get metrics
    print("\n[5] GET /api/metrics")
    metrics = api.get_metrics()
    print(f"    Status: {metrics['status']}")
    print(f"    Physics bodies: {metrics['physics']['active_bodies']}")
    print(f"    Graphics objects: {metrics['graphics']['scene_objects']}")
    print(f"    Procedural meshes: {metrics['procedural']['cached_meshes']}")
    
    # 6. Run feedback loop
    print("\n[6] POST /api/feedback")
    feedback_resp = api.run_feedback_loop("balanced system optimization", max_cycles=3)
    print(f"    Status: {feedback_resp['status']}")
    print(f"    Cycles: {feedback_resp['cycles']}")
    print(f"    Convergence: {feedback_resp['convergence']}")
    print(f"    Final decision: {feedback_resp['final_decision']}")
    
    print("\n" + "=" * 80)
    print("API READY FOR DASHBOARD")
    print("=" * 80)
    print("\nEndpoints:")
    print("  POST /api/orchestrate - Process text input")
    print("  POST /api/physics - Create physics body")
    print("  POST /api/graphics - Create graphics object")
    print("  POST /api/procedural - Generate procedural mesh")
    print("  POST /api/feedback - Run feedback loop (N cycles)")
    print("  GET  /api/metrics - Get system metrics")
    print("  GET  /api/state - Get complete state")


if __name__ == "__main__":
    demo_api()

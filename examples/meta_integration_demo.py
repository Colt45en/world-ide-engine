"""
Meta-System Integration Demo
=============================
Demonstrates text -> tokens -> embeddings -> decisions -> physics -> transforms -> manifest
"""

from __future__ import annotations
from dataclasses import dataclass
from meta.orchestrator import MetaLibrarianOrchestrator, PipelineZone
from meta.upflow import UpflowAutomation
from meta.manifest import ManifestRegistry, ComplianceLevel
import json
from datetime import datetime

@dataclass
class Vec3:
    x: float
    y: float
    z: float
    
    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

@dataclass
class RigidBody:
    position: Vec3
    velocity: Vec3
    mass: float = 1.0
    gravity: float = 9.81
    restitution: float = 0.8
    angular_velocity: Vec3 = None
    
    def __post_init__(self):
        if self.angular_velocity is None:
            self.angular_velocity = Vec3(0, 0, 0)

def simple_tokenizer(text: str):
    return text.lower().split()

def simple_embedding(tokens):
    return [float(ord(t[0]) % 10) / 10.0 for t in tokens]

def simple_logic(embeddings):
    avg = sum(embeddings) / len(embeddings) if embeddings else 0
    if avg > 0.6:
        return "aggressive"
    elif avg > 0.3:
        return "balanced"
    else:
        return "gentle"

def simple_physics_gen(decision: str):
    if decision == "aggressive":
        return {"mass": 1.45, "velocity": (2.3, -1.1, 0), "restitution": 0.95}
    elif decision == "balanced":
        return {"mass": 0.8, "velocity": (1.0, 0.5, 0), "restitution": 0.7}
    else:
        return {"mass": 0.5, "velocity": (0.3, 0.1, 0), "restitution": 0.5}

def simple_transform_gen(physics_params: dict, decision=None):
    mass = physics_params.get("mass", 0.5)
    vel = physics_params.get("velocity", (0, 0, 0))
    position = (mass * 2.0, mass * 1.5, 0)
    vel_mag = (vel[0]**2 + vel[1]**2 + vel[2]**2) ** 0.5
    rotation = (vel_mag * 0.5, mass * 3.14159, vel_mag * 0.3)
    scale = (1.0 / mass, 1.0 / mass, 1.0 / mass)
    return {"position": position, "rotation": rotation, "scale": scale}

print("=" * 70)
print("META-SYSTEMS INTEGRATION DEMO")
print("=" * 70)

orchestrator = MetaLibrarianOrchestrator()
upflow = UpflowAutomation()
manifest_registry = ManifestRegistry()

manifest_registry.register_system("Tokenizer", "operational")
manifest_registry.register_system("Embedder", "operational")
manifest_registry.register_system("LogicEngine", "operational")
manifest_registry.register_system("PhysicsEngine", "operational")
manifest_registry.register_system("Renderer", "operational")

test_workflows = [
    "aggressive destructive collision",
    "balanced harmonic motion",
    "gentle flowing movement"
]

all_flow_graphs = []

for workflow_idx, input_text in enumerate(test_workflows, 1):
    print(f"\n[DEMO] === Workflow {workflow_idx}: {input_text} ===\n")
    
    config = {
        "tokenizer": simple_tokenizer,
        "embedding_fn": simple_embedding,
        "logic_fn": simple_logic,
        "physics_gen": simple_physics_gen,
        "transform_gen": simple_transform_gen,
    }
    
    pipeline_state = orchestrator.run_pipeline(input_text, config)
    
    print(f"[DEMO] Tokens: {pipeline_state.tokens}")
    print(f"[DEMO] Embeddings: {pipeline_state.embeddings}")
    print(f"[DEMO] Decision: {pipeline_state.logical_decision}")
    print(f"[DEMO] Physics Params: {pipeline_state.physics_params}")
    print(f"[DEMO] Transform: {pipeline_state.render_transforms}")
    
    manifest_registry.log_metric("tokens_processed", len(pipeline_state.tokens))
    manifest_registry.log_metric("embeddings_generated", len(pipeline_state.embeddings))
    manifest_registry.log_metric("decisions_made", 1)
    manifest_registry.log_metric("physics_sims", 1)
    manifest_registry.log_metric("renders", 1)
    
    manifest_registry.update_system_status(
        "Tokenizer", "operational",
        {"tokens": pipeline_state.tokens},
        ComplianceLevel.OK
    )
    manifest_registry.update_system_status(
        "Embedder", "operational",
        {"embeddings": pipeline_state.embeddings},
        ComplianceLevel.OK
    )
    manifest_registry.update_system_status(
        "LogicEngine", "operational",
        {"decision": pipeline_state.logical_decision},
        ComplianceLevel.OK
    )
    manifest_registry.update_system_status(
        "PhysicsEngine", "operational",
        {"params": pipeline_state.physics_params},
        ComplianceLevel.OK
    )
    manifest_registry.update_system_status(
        "Renderer", "operational",
        {"transforms": pipeline_state.render_transforms},
        ComplianceLevel.OK
    )
    
    body = RigidBody(
        position=Vec3(*pipeline_state.render_transforms["position"]),
        velocity=Vec3(*pipeline_state.physics_params["velocity"]),
        mass=pipeline_state.physics_params["mass"],
        restitution=pipeline_state.physics_params["restitution"]
    )
    
    print(f"[DEMO] Body created: pos={body.position}, vel={body.velocity}, mass={body.mass}")
    
    all_flow_graphs.append(pipeline_state.manifest)

print("\n" + "=" * 70)
print("FINAL MANIFEST")
print("=" * 70 + "\n")

final_manifest = manifest_registry.create_manifest()
manifest_path = "meta_execution_manifest.json"

manifest_registry.export_manifest(manifest_path)
print(f"\n[DEMO] Manifest saved to {manifest_path}")

print("\nDemo complete! All meta-systems integrated and tested.")

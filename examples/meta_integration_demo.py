import sys
sys.path.insert(0, 'C:\\fresh-world-engine')

from meta.orchestrator import MetaLibrarianOrchestrator, PipelineZone
from meta.upflow import UpflowAutomation
from meta.manifest import ManifestRegistry
from physics.body import RigidBody, Vec3
from physics.gjk import BoxCollider

def simple_tokenizer(text: str):
    return text.lower().split()

def simple_embedding(tokens):
    return [float(ord(t[0]) % 10) / 10.0 for t in tokens] if tokens else []

def simple_logic(embeddings):
    if not embeddings:
        return "neutral"
    avg = sum(embeddings) / len(embeddings)
    if avg > 0.6:
        return "aggressive"
    elif avg > 0.3:
        return "balanced"
    else:
        return "gentle"

def simple_physics_gen(decision):
    decision_map = {
        "aggressive": {"mass": 2.0, "velocity": [5.0, 0.0, 0.0], "restitution": 0.8},
        "balanced": {"mass": 1.0, "velocity": [2.0, 0.0, 0.0], "restitution": 0.6},
        "gentle": {"mass": 0.5, "velocity": [1.0, 0.0, 0.0], "restitution": 0.4}
    }
    return decision_map.get(decision, decision_map["balanced"])

def simple_transform_gen(physics):
    mass = physics.get("mass", 1.0)
    return [(mass * 2, 0, 0), (0, 0, 0), (1, 1, 1)]

print("=" * 70)
print("META-SYSTEMS INTEGRATION DEMO")
print("=" * 70)

orchestrator = MetaLibrarianOrchestrator()
upflow = UpflowAutomation()
manifest = ManifestRegistry()

manifest.register_system("Orchestrator", "initialized")
manifest.register_system("TokenLab", "initialized")
manifest.register_system("LexicalLogic", "initialized")
manifest.register_system("Physics", "initialized")
manifest.register_system("Graphics", "initialized")

test_inputs = [
    "aggressive destructive collision",
    "balanced harmonic motion",
    "gentle flowing movement"
]

for i, input_text in enumerate(test_inputs):
    print(f"\n[DEMO] === Workflow {i+1}: {input_text} ===")
    
    manifest.start_workflow(f"workflow_{i+1}", {"input": input_text})
    
    pipeline_config = {
        "tokenizer": simple_tokenizer,
        "embedding_fn": simple_embedding,
        "logic_fn": simple_logic,
        "physics_gen": simple_physics_gen,
        "transform_gen": simple_transform_gen
    }
    
    state = orchestrator.run_pipeline(input_text, pipeline_config)
    
    manifest.log_metric('cycles')
    manifest.log_metric('tokens_processed', len(state.tokens))
    manifest.log_metric('embeddings_generated')
    manifest.log_metric('decisions_made')
    manifest.log_metric('physics_simulations')
    manifest.log_metric('renders_output')
    
    flow_graph = upflow.build_flow_graph(state.tokens, state.embeddings, state.logical_decision)
    
    manifest.update_system_status("Orchestrator", "completed", 
        {"cycles": state.cycle_count, "decision": state.logical_decision}, "ok")
    manifest.update_system_status("TokenLab", "completed", 
        {"tokens": len(state.tokens)}, "ok")
    manifest.update_system_status("LexicalLogic", "completed", 
        {"decision": state.logical_decision}, "ok")
    manifest.update_system_status("Physics", "completed", 
        {"params": state.physics_params}, "ok")
    manifest.update_system_status("Graphics", "completed", 
        {"transforms": len(state.render_transforms)}, "ok")
    
    print(f"\n[DEMO] Decision: {state.logical_decision}")
    print(f"[DEMO] Physics Params: {state.physics_params}")
    print(f"[DEMO] Transform: pos={flow_graph['stage_4_transform'][0]}")
    print(f"[DEMO] Colors: {flow_graph['stage_5_colors']['primary']}")
    
    manifest.complete_workflow(f"workflow_{i+1}", 
        {"decision": state.logical_decision, "transforms": flow_graph['stage_4_transform']}, 
        runtime_ms=100)

print(f"\n{'=' * 70}")
print("FINAL MANIFEST")
print(f"{'=' * 70}\n")

final_manifest = manifest.get_manifest()
import json
print(json.dumps(final_manifest, indent=2))

manifest.export_manifest("C:\\fresh-world-engine\\meta_execution_manifest.json")
print(f"\n[DEMO] Manifest saved to meta_execution_manifest.json")
print(f"[DEMO] Total Cycles: {manifest.metrics.total_cycles}")
print(f"[DEMO] Total Runtime: {manifest.metrics.total_runtime_ms}ms")

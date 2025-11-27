import sys
sys.path.insert(0, '.')
from meta.orchestrator_v2 import MetaOrchestrator
import json

orch = MetaOrchestrator()

inputs = ['rebuild', 'multibuild', 'reconstruct']

for inp in inputs:
    result = orch.orchestrate(inp)
    print(f'Input: {inp}')
    print(f'  Decision: {result.get("decision")}')
    print(f'  Mass: {result.get("physics_params", {}).get("mass"):.2f}')
    print()

print('Status:', json.dumps(orch.get_status(), indent=2, default=str))

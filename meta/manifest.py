from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

class ComplianceLevel(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    OK = "ok"

@dataclass
class SystemStatus:
    name: str
    status: str
    timestamp: str
    compliance: str
    cycle_count: int
    details: dict = field(default_factory=dict)

@dataclass
class ExecutionMetrics:
    total_cycles: int = 0
    tokens_processed: int = 0
    embeddings_generated: int = 0
    decisions_made: int = 0
    physics_simulations: int = 0
    renders_output: int = 0
    total_runtime_ms: float = 0.0

class ManifestRegistry:
    def __init__(self):
        self.systems = {}
        self.metrics = ExecutionMetrics()
        self.manifest_history = []
        self.active_workflows = []

    def register_system(self, name: str, initial_status: str = "initialized"):
        self.systems[name] = SystemStatus(
            name=name,
            status=initial_status,
            timestamp=datetime.now().isoformat(),
            compliance=ComplianceLevel.OK.value,
            cycle_count=0
        )

    def update_system_status(self, name: str, status: str, details: dict = None, compliance: str = None):
        if name not in self.systems:
            self.register_system(name, status)
        else:
            self.systems[name].status = status
            self.systems[name].timestamp = datetime.now().isoformat()
            self.systems[name].cycle_count += 1
            if details:
                self.systems[name].details = details
            if compliance:
                self.systems[name].compliance = compliance

    def log_metric(self, metric_name: str, value: int = 1):
        if metric_name == 'tokens_processed':
            self.metrics.tokens_processed += value
        elif metric_name == 'embeddings_generated':
            self.metrics.embeddings_generated += value
        elif metric_name == 'decisions_made':
            self.metrics.decisions_made += value
        elif metric_name == 'physics_simulations':
            self.metrics.physics_simulations += value
        elif metric_name == 'renders_output':
            self.metrics.renders_output += value
        elif metric_name == 'cycles':
            self.metrics.total_cycles += value

    def start_workflow(self, workflow_id: str, input_data: dict):
        self.active_workflows.append({
            'id': workflow_id,
            'started_at': datetime.now().isoformat(),
            'input': input_data,
            'status': 'running'
        })

    def complete_workflow(self, workflow_id: str, output_data: dict, runtime_ms: float = 0):
        for wf in self.active_workflows:
            if wf['id'] == workflow_id:
                wf['status'] = 'completed'
                wf['completed_at'] = datetime.now().isoformat()
                wf['output'] = output_data
                wf['runtime_ms'] = runtime_ms
                self.metrics.total_runtime_ms += runtime_ms
                break

    def create_manifest(self) -> dict:
        manifest = {
            'timestamp': datetime.now().isoformat(),
            'systems': {name: asdict(status) for name, status in self.systems.items()},
            'metrics': asdict(self.metrics),
            'active_workflows': len([wf for wf in self.active_workflows if wf['status'] == 'running']),
            'completed_workflows': len([wf for wf in self.active_workflows if wf['status'] == 'completed']),
            'overall_compliance': self._calculate_overall_compliance()
        }
        self.manifest_history.append(manifest)
        return manifest

    def _calculate_overall_compliance(self) -> str:
        if not self.systems:
            return ComplianceLevel.OK.value
        compliances = [s.compliance for s in self.systems.values()]
        if any(c == ComplianceLevel.CRITICAL.value for c in compliances):
            return ComplianceLevel.CRITICAL.value
        if any(c == ComplianceLevel.WARNING.value for c in compliances):
            return ComplianceLevel.WARNING.value
        if any(c == ComplianceLevel.INFO.value for c in compliances):
            return ComplianceLevel.INFO.value
        return ComplianceLevel.OK.value

    def get_manifest(self) -> dict:
        return self.create_manifest()

    def export_manifest(self, filepath: str):
        manifest = self.create_manifest()
        with open(filepath, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"[MANIFEST] Exported to {filepath}")

    def get_system_health(self) -> dict:
        return {name: s.compliance for name, s in self.systems.items()}

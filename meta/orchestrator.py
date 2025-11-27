from __future__ import annotations
import json
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class PipelineZone(Enum):
    HEAD = "HEAD"
    ROOT_EXTRACTION = "ROOT_EXTRACTION"
    CONTEXT_STRIPPING = "CONTEXT_STRIPPING"
    AXIOMATIC_MAPPING = "AXIOMATIC_MAPPING"
    RELATIONSHIP_WEAVING = "RELATIONSHIP_WEAVING"
    PATTERN_RECOGNITION = "PATTERN_RECOGNITION"
    SYNTHETIC_REBUILD = "SYNTHETIC_REBUILD"
    ACTIONABLE_OUTPUT = "ACTIONABLE_OUTPUT"

@dataclass
class PipelineState:
    current_zone: PipelineZone
    cycle_count: int = 0
    tokens: list = field(default_factory=list)
    embeddings: list = field(default_factory=list)
    logical_decision: str | None = None
    physics_params: dict = field(default_factory=dict)
    render_transforms: list = field(default_factory=list)
    compliance_status: str = "ready"
    manifest: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class MetaLibrarianOrchestrator:
    def __init__(self):
        self.state = PipelineState(current_zone=PipelineZone.HEAD)
        self.zone_handlers = {}
        self.automation_rules = []
        self.recursion_depth = 0
        self.max_recursion = 5
        self.operation_history = []

    def register_zone_handler(self, zone: PipelineZone, handler):
        self.zone_handlers[zone] = handler

    def add_automation_rule(self, trigger: str, action, condition = None):
        self.automation_rules.append({
            'trigger': trigger,
            'action': action,
            'condition': condition or (lambda s: True)
        })

    def transition_zone(self, next_zone: PipelineZone) -> bool:
        if self.recursion_depth >= self.max_recursion:
            return False
        prev_zone = self.state.current_zone
        self.state.current_zone = next_zone
        self.state.cycle_count += 1
        self.state.timestamp = datetime.now().isoformat()
        print(f"[ORCH] Cycle {self.state.cycle_count}: {prev_zone.value} -> {next_zone.value}")
        if next_zone in self.zone_handlers:
            try:
                result = self.zone_handlers[next_zone](self.state)
                self.operation_history.append({
                    'zone': next_zone.value,
                    'cycle': self.state.cycle_count
                })
                return True
            except Exception as e:
                self.state.compliance_status = f"error: {str(e)}"
                return False
        return True

    def run_pipeline(self, input_text: str, config: dict) -> PipelineState:
        print("\n[ORCH] === Pipeline Start ===")
        self.recursion_depth = 0
        self.transition_zone(PipelineZone.HEAD)
        if 'tokenizer' in config:
            self.state.tokens = config['tokenizer'](input_text)
            self.transition_zone(PipelineZone.ROOT_EXTRACTION)
        if 'embedding_fn' in config and self.state.tokens:
            self.state.embeddings = config['embedding_fn'](self.state.tokens)
            self.transition_zone(PipelineZone.CONTEXT_STRIPPING)
        self.transition_zone(PipelineZone.AXIOMATIC_MAPPING)
        if 'logic_fn' in config:
            self.state.logical_decision = config['logic_fn'](self.state.embeddings)
            self.transition_zone(PipelineZone.RELATIONSHIP_WEAVING)
        self.transition_zone(PipelineZone.PATTERN_RECOGNITION)
        if 'physics_gen' in config:
            self.state.physics_params = config['physics_gen'](self.state.logical_decision)
        if 'transform_gen' in config:
            self.state.render_transforms = config['transform_gen'](self.state.physics_params)
            self.transition_zone(PipelineZone.SYNTHETIC_REBUILD)
        self.transition_zone(PipelineZone.ACTIONABLE_OUTPUT)
        manifest = {
            'cycle': self.state.cycle_count,
            'decision': self.state.logical_decision,
            'tokens': len(self.state.tokens),
            'status': self.state.compliance_status
        }
        self.state.manifest = manifest
        print("[ORCH] === Pipeline Complete ===\n")
        return self.state

    def get_state_dict(self):
        return {
            'current_zone': self.state.current_zone.value,
            'cycle_count': self.state.cycle_count,
            'tokens': self.state.tokens,
            'decision': self.state.logical_decision,
            'physics': self.state.physics_params,
            'manifest': self.state.manifest
        }

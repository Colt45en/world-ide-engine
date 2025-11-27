# nexus/qtp_bridge.py
# Safe bridge for providing engine-frame packets to the bus server.
# Tries compiled extension engine.qtp or qtp; otherwise uses a Python shim.

import importlib
import logging
import time

logging.getLogger().setLevel(logging.INFO)

QTP = None
for candidate in ('engine.qtp', 'qtp'):
    try:
        QTP = importlib.import_module(candidate)
        logging.info('qtp_bridge: loaded %s', candidate)
        break
    except Exception:
        continue

# Fallback Python shim (if compiled module isn't available)
if QTP is None:
    logging.info('qtp_bridge: falling back to Python shim')

    class ThoughtZone:
        def __init__(self, name, type_, color, pos=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0)):
            self.name = name
            self.type = type_
            self.color = color
            self.position = tuple(float(x) for x in pos)
            self.scale = tuple(float(x) for x in scale)

        @property
        def position_np(self):
            try:
                import numpy as _np
                return _np.array(self.position, dtype='float64')
            except Exception:
                return list(self.position)

        @property
        def scale_np(self):
            try:
                import numpy as _np
                return _np.array(self.scale, dtype='float64')
            except Exception:
                return list(self.scale)

    class Agent:
        def __init__(self, id='primary_agent', maxSteps=100, stepSize=0.1, pos=(0.0, 0.0, 0.0)):
            self.id = id
            self.maxSteps = maxSteps
            self.stepSize = stepSize
            self.position = tuple(float(x) for x in pos)

        @property
        def position_np(self):
            try:
                import numpy as _np
                return _np.array(self.position, dtype='float64')
            except Exception:
                return list(self.position)

    class QuantumThoughtPipeline:
        def __init__(self):
            self.zones = []
            self.agent = None
            self.build_field()

        def build_field(self):
            self.zones = [
                ThoughtZone('perception', 'input', '#ff6b6b', pos=(-5, 0, 0), scale=(2, 2, 2)),
                ThoughtZone('processing', 'compute', '#4ecdc4', pos=(0, 0, 0), scale=(3, 3, 3)),
                ThoughtZone('memory', 'storage', '#45b7d1', pos=(5, 0, 0), scale=(2.5, 2.5, 2.5)),
                ThoughtZone('output', 'emission', '#96ceb4', pos=(10, 0, 0), scale=(2, 2, 2)),
            ]
            self.agent = Agent(id='primary_agent', maxSteps=100, stepSize=0.1, pos=(0, 0, 0))

        def getZones(self):
            return self.zones

        def getAgent(self):
            return self.agent

    QTP = type('qtpshim', (), {'QuantumThoughtPipeline': QuantumThoughtPipeline})

# single pipeline instance for the bus
_pipeline = None
try:
    _pipeline = QTP.QuantumThoughtPipeline()
    logging.info('qtp_bridge: created pipeline instance')
except Exception as e:
    logging.warning('qtp_bridge: failed to instantiate pipeline: %s', e)

# helper

def _to_list3(val):
    try:
        if hasattr(val, 'tolist'):
            v = val.tolist()
        else:
            v = list(val)
        return [float(v[0]), float(v[1]), float(v[2])]
    except Exception:
        return [0.0, 0.0, 0.0]


def generate_frame_packet(tick: int = 0) -> dict:
    try:
        if _pipeline is None:
            raise RuntimeError('pipeline not available')
        zones = []
        for i, z in enumerate(_pipeline.getZones()):
            pos = getattr(z, 'position_np', None) or getattr(z, 'position', None)
            scale = getattr(z, 'scale_np', None) or getattr(z, 'scale', None)
            zones.append({
                'id': getattr(z, 'name', f'zone_{i}'),
                'name': getattr(z, 'name', f'zone_{i}'),
                'type': getattr(z, 'type', None),
                'pos': _to_list3(pos),
                'scale': _to_list3(scale),
                'color': getattr(z, 'color', '#ffffff')
            })

        agent = _pipeline.getAgent()
        agent_pos = getattr(agent, 'position_np', None) or getattr(agent, 'position', None)
        return {
            'tick': tick,
            'fps': 60,
            'entities': zones,
            'agent': {
                'id': getattr(agent, 'id', 'agent'),
                'pos': _to_list3(agent_pos),
                'maxSteps': getattr(agent, 'maxSteps', None),
                'stepSize': getattr(agent, 'stepSize', None),
            },
            'world_state': {'zones': len(zones)},
            'system_status': 'ok'
        }
    except Exception as e:
        logging.warning('qtp_bridge: generate_frame_packet error: %s', e)
        return {'tick': tick, 'fps': 60, 'entities': [], 'world_state': {'time': time.time()}, 'system_status': 'degraded'}

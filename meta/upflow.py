from __future__ import annotations
import hashlib
import math

class UpflowAutomation:
    def __init__(self):
        self.token_to_physics = {}
        self.decision_to_transform = {}
        self.embedding_to_color = {}
        self.flow_graph = {}

    def token_to_physics_params(self, tokens: list, embeddings: list) -> dict:
        params = {
            'mass': 1.0,
            'velocity': [0.0, 0.0, 0.0],
            'gravity_scale': 1.0,
            'friction': 0.4,
            'restitution': 0.6
        }
        if tokens:
            token_hash = hashlib.md5(''.join(tokens).encode()).digest()
            mass_seed = int.from_bytes(token_hash[:4], 'little') % 1000 / 1000.0
            params['mass'] = 0.5 + mass_seed
            vel_x = (int.from_bytes(token_hash[4:8], 'little') % 200 - 100) / 100.0
            vel_y = (int.from_bytes(token_hash[8:12], 'little') % 200 - 100) / 100.0
            params['velocity'] = [vel_x, vel_y, 0.0]
        if embeddings:
            avg_emb = sum(embeddings) / len(embeddings) if embeddings else 0
            params['gravity_scale'] = 0.5 + abs(avg_emb) * 2.0
            params['restitution'] = 0.3 + abs(avg_emb) * 0.7
        return params

    def decision_to_render_transform(self, decision: str, physics_params: dict) -> tuple:
        decision_hash = hashlib.md5(decision.encode()).digest() if decision else b''
        pos_x = (int.from_bytes(decision_hash[:4], 'little') % 800 - 400) / 400.0 if decision_hash else 0
        pos_y = (int.from_bytes(decision_hash[4:8], 'little') % 600 - 300) / 300.0 if decision_hash else 0
        pos_z = (int.from_bytes(decision_hash[8:12], 'little') % 200) / 200.0 if decision_hash else 0
        position = (pos_x, pos_y, pos_z)
        mass = physics_params.get('mass', 1.0)
        rot_x = mass * math.pi / 4
        rot_y = mass * math.pi / 6
        rot_z = 0.0
        rotation = (rot_x, rot_y, rot_z)
        scale_seed = (int.from_bytes(decision_hash[12:16], 'little') if decision_hash else 0) % 100 / 100.0
        scale = (0.5 + scale_seed * 0.5, 0.5 + scale_seed * 0.5, 0.5 + scale_seed * 0.5)
        return position, rotation, scale

    def embedding_to_color_palette(self, embeddings: list, aesthetic_eval=None) -> dict:
        colors = {
            'primary': '#4CAF50',
            'secondary': '#2196F3',
            'accent': '#FF9800',
            'background': '#1a1a1a'
        }
        if embeddings:
            h = int(embeddings[0] * 360) % 360 if embeddings else 0
            s = 70 + (embeddings[1] * 30 if len(embeddings) > 1 else 0) % 30
            l = 50 + (embeddings[2] * 20 if len(embeddings) > 2 else 0) % 20
            hsl_str = f"hsl({h}, {s}%, {l}%)"
            colors['primary'] = hsl_str
            h2 = (h + 120) % 360
            colors['secondary'] = f"hsl({h2}, {s}%, {l}%)"
            h3 = (h + 240) % 360
            colors['accent'] = f"hsl({h3}, {s}%, {l}%)"
        return colors

    def build_flow_graph(self, tokens: list, embeddings: list, decision: str):
        self.flow_graph = {
            'stage_0_tokens': tokens,
            'stage_1_embeddings': embeddings[:10] if embeddings else [],
            'stage_2_decision': decision,
            'stage_3_physics': self.token_to_physics_params(tokens, embeddings),
            'stage_4_transform': self.decision_to_render_transform(decision, 
                                   self.token_to_physics_params(tokens, embeddings)),
            'stage_5_colors': self.embedding_to_color_palette(embeddings)
        }
        return self.flow_graph

    def apply_to_physics_body(self, body, tokens: list, embeddings: list):
        params = self.token_to_physics_params(tokens, embeddings)
        if hasattr(body, 'mass'):
            body.mass = params.get('mass', 1.0)
            body.inv_mass = 1.0 / body.mass if body.mass > 0 else 0
        if hasattr(body, 'velocity'):
            vel = params.get('velocity', [0, 0, 0])
            from physics.body import Vec3
            body.velocity = Vec3(vel[0], vel[1], vel[2])
        if hasattr(body, 'gravity'):
            scale = params.get('gravity_scale', 1.0)
            from physics.body import Vec3
            body.gravity = Vec3(0, -9.81 * scale, 0)

    def apply_to_renderer(self, renderer, transform_data: tuple) -> dict:
        position, rotation, scale = transform_data
        return {
            'position': position,
            'rotation': rotation,
            'scale': scale
        }

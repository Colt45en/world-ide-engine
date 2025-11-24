"""Nexus: The integration hub where geometry and aesthetics form a feedback loop."""
import numpy as np
from dataclasses import dataclass
from geometry.surface_nets import IntelligentSurfaceNets, MeshData, GeometryStats
from aesthetics.pathway import AestheticPathway, AestheticEvaluation

@dataclass
class IntegratedOutput:
    mesh: MeshData
    geometry_stats: GeometryStats
    aesthetic_eval: AestheticEvaluation
    feedback_recommendations: dict

class Nexus:
    """Orchestration hub: geometry ↔ aesthetics ↔ feedback."""
    
    def __init__(self):
        self.surface_nets = IntelligentSurfaceNets
        self.aesthetic_pathway = AestheticPathway()
        self.iteration_count = 0
        self.max_iterations = 3
    
    def process_intelligent_silhouette(
        self,
        volume_data: np.ndarray,
        resolution: tuple,
        user_intent: str = 'balanced'
    ) -> IntegratedOutput:
        """
        Main feedback loop orchestrator:
        1. Generate mesh from voxels (body formation)
        2. Analyze geometry (body metrics)
        3. Evaluate aesthetics (soul emergence)
        4. Generate feedback recommendations
        """
        # STEP 1: Generate mesh with intelligent Surface Nets
        surface_nets = IntelligentSurfaceNets(volume_data, resolution)
        mesh = surface_nets.generate_mesh()
        
        # STEP 2: Analyze geometry for aesthetic feedback
        geometry_stats = surface_nets.analyze_geometry()
        
        # STEP 3: Run through aesthetic pathway
        aesthetic_eval = self.aesthetic_pathway.evaluate(geometry_stats)
        
        # STEP 4: Generate feedback recommendations
        feedback = self._generate_feedback(
            geometry_stats,
            aesthetic_eval,
            user_intent
        )
        
        return IntegratedOutput(
            mesh=mesh,
            geometry_stats=geometry_stats,
            aesthetic_eval=aesthetic_eval,
            feedback_recommendations=feedback
        )
    
    def _generate_feedback(
        self,
        geometry_stats: GeometryStats,
        aesthetic_eval: AestheticEvaluation,
        user_intent: str
    ) -> dict:
        """Generate recommendations for iterative refinement."""
        feedback = {
            'geometry_quality': self._evaluate_geometry_quality(geometry_stats),
            'aesthetic_quality': aesthetic_eval.beauty_score,
            'mood_alignment': self._check_mood_alignment(aesthetic_eval.mood, user_intent),
            'refinement_suggestions': []
        }
        
        # Suggest smoothing if jagged
        if geometry_stats.entropy > 0.6:
            feedback['refinement_suggestions'].append({
                'action': 'increase_smoothing',
                'reason': 'High surface entropy detected (jagged)',
                'target_entropy': 0.4,
                'confidence': min(geometry_stats.entropy, 1.0)
            })
        
        # Suggest detail if too smooth
        if geometry_stats.entropy < 0.2:
            feedback['refinement_suggestions'].append({
                'action': 'increase_detail',
                'reason': 'Low surface entropy (overly smooth)',
                'target_entropy': 0.5,
                'confidence': 1.0 - geometry_stats.entropy
            })
        
        # Suggest aspect ratio adjustment if far from Golden Ratio
        aspect = geometry_stats.aspect_ratio[1] / (geometry_stats.aspect_ratio[0] + 1e-8)
        phi = 1.618
        if abs(aspect - phi) > 0.3:
            feedback['refinement_suggestions'].append({
                'action': 'adjust_aspect_ratio',
                'reason': f'Current ratio {aspect:.2f} deviates from φ={phi:.3f}',
                'target_aspect': phi,
                'confidence': 1.0 - min(abs(aspect - phi) / phi, 1.0)
            })
        
        feedback['overall_quality'] = np.mean([
            feedback['geometry_quality'],
            feedback['aesthetic_quality'],
            0.8 if feedback['mood_alignment'] else 0.3
        ])
        
        return feedback
    
    def _evaluate_geometry_quality(self, stats: GeometryStats) -> float:
        """Score geometry quality (0-1)."""
        # Surface area should be reasonably large
        volume_bbox = np.prod(stats.bounds_max - stats.bounds_min)
        surface_area = stats.surface_area
        
        if volume_bbox < 1e-6:
            return 0.0
        
        ratio = surface_area / np.sqrt(volume_bbox)
        return float(np.clip(ratio / 10.0, 0.0, 1.0))
    
    def _check_mood_alignment(self, detected_mood: str, user_intent: str) -> bool:
        """Check if detected mood matches user intent."""
        mood_map = {
            'energetic': ['dynamic', 'vibrant', 'energetic', 'bold'],
            'calm': ['serene', 'peaceful', 'calm', 'soft', 'gentle']
        }
        
        return any(intent in mood_map.get(detected_mood, []) 
                  for intent in user_intent.lower().split())

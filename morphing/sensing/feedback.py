"""
morphing/sensing/feedback.py

Closed-loop control: 3D shape sensing, error metrics, and iterative refinement.

Workflow:
  1. Fabricate growth pattern → place hydrogel in stimulus field
  2. 3D reconstruction: capture point cloud (photogrammetry, depth camera, CT scan)
  3. Alignment: fit point cloud to target surface (ICP)
  4. Error metrics: curvature mismatch, distance, metric tensor error
  5. Iterate: refine growth pattern based on error
"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class ShapeError:
    """Measured shape error between realized and target."""
    hausdorff_distance: float  # max distance between surfaces
    mean_distance: float  # average point-to-surface distance
    metric_error: float  # tensor mismatch ||realized_g² - target_g²||
    curvature_error: float  # principal curvature mismatch
    alignment_rotation: np.ndarray  # (3, 3) rotation matrix from alignment
    alignment_translation: np.ndarray  # (3,) translation vector
    converged: bool


class ShapeReconstruction:
    """Convert 3D scans to point clouds and metrics."""
    
    @staticmethod
    def from_point_cloud(points: np.ndarray) -> np.ndarray:
        """Accept 3D point cloud directly.
        
        Args:
            points: (N, 3) array of 3D coordinates
        
        Returns:
            Same point cloud (identity operation for integration)
        """
        return points
    
    @staticmethod
    def downsample_voxel(points: np.ndarray, voxel_size: float) -> np.ndarray:
        """Voxel grid downsampling to reduce noise and computational load."""
        # Quantize to voxel grid
        voxel_indices = np.floor(points / voxel_size).astype(int)
        
        # Keep one point per voxel (the first one encountered)
        unique_voxels = {}
        downsampled = []
        for i, voxel in enumerate(voxel_indices):
            key = tuple(voxel)
            if key not in unique_voxels:
                unique_voxels[key] = i
                downsampled.append(points[i])
        
        return np.array(downsampled)
    
    @staticmethod
    def statistical_outlier_removal(points: np.ndarray, k: int = 20, threshold: float = 2.0) -> np.ndarray:
        """Remove noise: points with abnormal distance to neighbors.
        
        Args:
            points: (N, 3) point cloud
            k: neighborhood size
            threshold: std dev threshold for outliers
        
        Returns:
            Cleaned point cloud
        """
        from scipy.spatial import cKDTree
        
        tree = cKDTree(points)
        distances, indices = tree.query(points, k=k+1)  # include self
        
        mean_distances = distances[:, 1:].mean(axis=1)
        std_dist = mean_distances.std()
        
        outlier_mask = mean_distances < mean_distances.mean() + threshold * std_dist
        return points[outlier_mask]


class IterativeClosestPoint:
    """ICP alignment: register point cloud to target surface."""
    
    @staticmethod
    def align(source: np.ndarray, target: np.ndarray, max_iterations: int = 100, 
              tolerance: float = 1e-6) -> Tuple[np.ndarray, np.ndarray, float]:
        """Align source to target using ICP.
        
        Args:
            source: (N, 3) point cloud to move
            target: (M, 3) reference point cloud or surface
            max_iterations: max ICP iterations
            tolerance: convergence threshold
        
        Returns:
            (rotation, translation, error)
        """
        from scipy.spatial import cKDTree
        
        R = np.eye(3)
        t = np.zeros(3)
        source_current = source.copy()
        
        for iteration in range(max_iterations):
            # Find closest point on target for each source point
            tree = cKDTree(target)
            distances, indices = tree.query(source_current)
            target_points = target[indices]
            
            # Compute optimal rotation and translation (SVD-based)
            centroid_source = source_current.mean(axis=0)
            centroid_target = target_points.mean(axis=0)
            
            source_centered = source_current - centroid_source
            target_centered = target_points - centroid_target
            
            U, S, Vt = np.linalg.svd(source_centered.T @ target_centered)
            R_new = (U @ Vt).T
            t_new = centroid_target - R_new @ centroid_source
            
            # Apply transformation
            source_current = (R_new @ source_current.T).T + t_new
            
            # Check convergence
            error = np.mean(distances)
            if iteration > 0 and np.abs(error - prev_error) < tolerance:
                R = R_new @ R
                t = R_new @ t + t_new
                return R, t, error
            
            R = R_new
            t = t_new
            prev_error = error
        
        return R, t, np.mean(distances)


class ErrorMetrics:
    """Compute alignment-invariant error metrics."""
    
    @staticmethod
    def hausdorff_distance(source: np.ndarray, target: np.ndarray) -> float:
        """Max distance between point clouds."""
        from scipy.spatial import cKDTree
        
        tree = cKDTree(target)
        distances, _ = tree.query(source)
        return np.max(distances)
    
    @staticmethod
    def mean_distance(source: np.ndarray, target: np.ndarray) -> float:
        """Average distance between closest point pairs."""
        from scipy.spatial import cKDTree
        
        tree = cKDTree(target)
        distances, _ = tree.query(source)
        return np.mean(distances)
    
    @staticmethod
    def fit_metric_to_points(points: np.ndarray) -> np.ndarray:
        """Estimate metric tensor field from point cloud."""
        # Use local PCA to estimate surface normal and curvature
        from scipy.spatial import cKDTree
        
        tree = cKDTree(points)
        k = 16
        distances, indices = tree.query(points, k=k+1)  # include self
        
        metrics = []
        for i in range(len(points)):
            neighbors = points[indices[i, 1:]]  # exclude self
            
            # Local covariance
            cov = np.cov(neighbors.T)
            evals, evecs = np.linalg.eigh(cov)
            
            # Metric is dominance of principal directions (2D approximation)
            metric_2d = np.diag([evals[-1], evals[-2]]) if evals[-1] > 0 else np.eye(2)
            metrics.append(metric_2d)
        
        return np.array(metrics)


class FeedbackController:
    """Iterative refinement based on measured errors."""
    
    def __init__(self, tolerance: float = 0.05, max_iterations: int = 10):
        """
        Args:
            tolerance: target metric error threshold
            max_iterations: max refinement loops
        """
        self.tolerance = tolerance
        self.max_iterations = max_iterations
        self.history = []
    
    def refine(self, 
               growth_field: np.ndarray,
               measured_points: np.ndarray,
               target_surface,
               optimizer,
               material) -> Tuple[np.ndarray, ShapeError]:
        """Closed-loop refinement: measure error → update pattern.
        
        Args:
            growth_field: current growth pattern g(x,y)
            measured_points: (N, 3) 3D reconstruction of current shape
            target_surface: target geometry object
            optimizer: PatternOptimizer instance
            material: IsotropicMaterial instance
        
        Returns:
            (refined_growth_field, final_error)
        """
        for iteration in range(self.max_iterations):
            # Align measured to target
            # (simplified: assume target is planar for now)
            target_points = target_surface.evaluate(
                measured_points[:, 0], measured_points[:, 1]
            )
            
            R, t, align_error = IterativeClosestPoint.align(measured_points, target_points)
            
            # Compute error metrics
            hausdorff = ErrorMetrics.hausdorff_distance(measured_points, target_points)
            mean_dist = ErrorMetrics.mean_distance(measured_points, target_points)
            
            error = ShapeError(
                hausdorff_distance=hausdorff,
                mean_distance=mean_dist,
                metric_error=optimizer.metric_error(growth_field),
                curvature_error=0.0,  # TODO: principal curvature comparison
                alignment_rotation=R,
                alignment_translation=t,
                converged=mean_dist < self.tolerance
            )
            
            self.history.append(error)
            
            if error.converged:
                return growth_field, error
            
            # Refine: increase growth where error is large
            error_gradient = np.abs(t).mean() * np.ones_like(growth_field)
            growth_field = growth_field + 0.1 * error_gradient
            growth_field = np.clip(growth_field, material.g_min, material.g_max)
        
        return growth_field, self.history[-1] if self.history else None

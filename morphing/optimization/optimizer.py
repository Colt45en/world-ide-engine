"""
morphing/optimization/optimizer.py

Pattern optimization engine: inverse problem solver.
Given target metric and material constraints, finds optimal 2D growth field g(x,y).

Minimizes: E = E_metric(g, target_g) + λ_s * E_smooth(g) + λ_f * E_fab(g)

Subject to: g_min ≤ g(x,y) ≤ g_max, smoothness constraints
"""

import numpy as np
from typing import Callable, Tuple, Optional, Dict, Any
from dataclasses import dataclass
import warnings


@dataclass
class OptimizationResult:
    """Result of pattern optimization."""
    growth_field: np.ndarray  # (N,) optimal growth values
    energy: float
    metric_error: float
    iterations: int
    convergence: bool
    history: Dict[str, list] = None  # tracking history


class PatternOptimizer:
    """Gradient-based and stochastic optimization for growth field."""
    
    def __init__(self, 
                 target_metric: np.ndarray,  # (N, 2, 2)
                 g_min: float = 0.5,
                 g_max: float = 2.0,
                 lambda_smooth: float = 0.1,
                 lambda_fab: float = 0.05):
        """
        Args:
            target_metric: desired metric tensor field (N, 2, 2)
            g_min, g_max: growth field bounds
            lambda_smooth: smoothness regularization weight
            lambda_fab: fabrication constraint weight
        """
        self.target_metric = target_metric
        self.N = len(target_metric)
        self.g_min = g_min
        self.g_max = g_max
        self.lambda_smooth = lambda_smooth
        self.lambda_fab = lambda_fab
        self.positions = None  # will be set during optimization

    def metric_error(self, growth_field: np.ndarray) -> float:
        """Metric mismatch: E_metric = 1/N * Σ ||g_k * I - target_g_k||_F^2"""
        realized_metrics = growth_field[:, None, None]**2 * np.eye(2)[None, :, :]
        diff = realized_metrics - self.target_metric
        return np.mean(np.sum(diff**2, axis=(1, 2)))

    def smoothness_energy(self, growth_field: np.ndarray, neighbors: Optional[list] = None) -> float:
        """Smoothness regularization: E_smooth = Σ ||∇g||^2"""
        if neighbors is None:
            # Simple Laplacian: ∇²g ≈ g_i - mean(neighbors)
            # For grid: use finite differences
            neighbors = self._default_neighbors()
        
        energy = 0.0
        for i, neighbors_i in enumerate(neighbors):
            if neighbors_i:
                energy += (growth_field[i] - np.mean(growth_field[list(neighbors_i)]))**2
        return energy / self.N if self.N > 0 else 0.0

    def fabrication_energy(self, growth_field: np.ndarray) -> float:
        """Fabrication constraint penalty: E_fab = Σ (g_i - nearest_discrete)^2
        Encourages g to be close to discrete UV levels (8-bit: 0, 1/255, ..., 255/255)"""
        discrete_levels = np.arange(0, 256) / 255.0 * (self.g_max - self.g_min) + self.g_min
        energies = []
        for g in growth_field:
            min_dist = np.min(np.abs(g - discrete_levels))
            energies.append(min_dist**2)
        return np.mean(energies)

    def energy(self, growth_field: np.ndarray, neighbors: Optional[list] = None) -> float:
        """Total energy: E = E_metric + λ_s * E_smooth + λ_f * E_fab"""
        e_metric = self.metric_error(growth_field)
        e_smooth = self.smoothness_energy(growth_field, neighbors)
        e_fab = self.fabrication_energy(growth_field)
        return e_metric + self.lambda_smooth * e_smooth + self.lambda_fab * e_fab

    def energy_gradient(self, growth_field: np.ndarray, neighbors: Optional[list] = None, eps: float = 1e-5) -> np.ndarray:
        """Numerical gradient via finite differences."""
        grad = np.zeros(len(growth_field))
        for i in range(len(growth_field)):
            g_plus = growth_field.copy()
            g_minus = growth_field.copy()
            g_plus[i] += eps
            g_minus[i] -= eps
            grad[i] = (self.energy(g_plus, neighbors) - self.energy(g_minus, neighbors)) / (2 * eps)
        return grad

    def gradient_descent(self, initial_g: Optional[np.ndarray] = None,
                        learning_rate: float = 0.01,
                        max_iterations: int = 500,
                        tol: float = 1e-4,
                        neighbors: Optional[list] = None) -> OptimizationResult:
        """Gradient descent with constraint projection."""
        g = initial_g if initial_g is not None else np.ones(self.N) * (self.g_min + self.g_max) / 2
        
        history = {'energy': [], 'metric_error': [], 'smoothness': []}
        
        for iteration in range(max_iterations):
            grad = self.energy_gradient(g, neighbors, eps=1e-5)
            g_new = g - learning_rate * grad
            
            # Project to feasible region
            g_new = np.clip(g_new, self.g_min, self.g_max)
            
            energy = self.energy(g_new, neighbors)
            metric_err = self.metric_error(g_new)
            history['energy'].append(energy)
            history['metric_error'].append(metric_err)
            
            if np.linalg.norm(g_new - g) < tol:
                return OptimizationResult(
                    growth_field=g_new,
                    energy=energy,
                    metric_error=metric_err,
                    iterations=iteration + 1,
                    convergence=True,
                    history=history
                )
            
            g = g_new
        
        return OptimizationResult(
            growth_field=g,
            energy=self.energy(g, neighbors),
            metric_error=self.metric_error(g),
            iterations=max_iterations,
            convergence=False,
            history=history
        )

    def adam(self, initial_g: Optional[np.ndarray] = None,
            learning_rate: float = 0.01,
            max_iterations: int = 500,
            beta1: float = 0.9,
            beta2: float = 0.999,
            eps: float = 1e-8,
            neighbors: Optional[list] = None) -> OptimizationResult:
        """Adam optimizer with constraint projection."""
        g = initial_g if initial_g is not None else np.ones(self.N) * (self.g_min + self.g_max) / 2
        m = np.zeros(self.N)  # first moment estimate
        v = np.zeros(self.N)  # second moment estimate
        
        history = {'energy': [], 'metric_error': []}
        
        for iteration in range(max_iterations):
            grad = self.energy_gradient(g, neighbors, eps=1e-5)
            
            # Adam update
            m = beta1 * m + (1 - beta1) * grad
            v = beta2 * v + (1 - beta2) * (grad**2)
            
            m_hat = m / (1 - beta1**(iteration + 1))
            v_hat = v / (1 - beta2**(iteration + 1))
            
            g_new = g - learning_rate * m_hat / (np.sqrt(v_hat) + eps)
            
            # Project to feasible region
            g_new = np.clip(g_new, self.g_min, self.g_max)
            
            energy = self.energy(g_new, neighbors)
            metric_err = self.metric_error(g_new)
            history['energy'].append(energy)
            history['metric_error'].append(metric_err)
            
            if np.linalg.norm(g_new - g) < 1e-4:
                return OptimizationResult(
                    growth_field=g_new,
                    energy=energy,
                    metric_error=metric_err,
                    iterations=iteration + 1,
                    convergence=True,
                    history=history
                )
            
            g = g_new
        
        return OptimizationResult(
            growth_field=g,
            energy=self.energy(g, neighbors),
            metric_error=self.metric_error(g),
            iterations=max_iterations,
            convergence=False,
            history=history
        )

    def simulated_annealing(self, initial_g: Optional[np.ndarray] = None,
                           max_iterations: int = 1000,
                           initial_temp: float = 1.0,
                           cooling_rate: float = 0.99,
                           neighbors: Optional[list] = None) -> OptimizationResult:
        """Stochastic optimization for escaping local minima."""
        g = initial_g if initial_g is not None else np.ones(self.N) * (self.g_min + self.g_max) / 2
        best_g = g.copy()
        best_energy = self.energy(g, neighbors)
        
        temp = initial_temp
        history = {'energy': [], 'temperature': []}
        
        for iteration in range(max_iterations):
            # Random perturbation
            delta = np.random.normal(0, temp, self.N)
            g_new = g + delta
            g_new = np.clip(g_new, self.g_min, self.g_max)
            
            energy_new = self.energy(g_new, neighbors)
            energy_old = self.energy(g, neighbors)
            
            # Metropolis acceptance
            if energy_new < energy_old or np.random.rand() < np.exp(-(energy_new - energy_old) / (temp + 1e-8)):
                g = g_new
                
                if energy_new < best_energy:
                    best_g = g_new.copy()
                    best_energy = energy_new
            
            temp *= cooling_rate
            history['energy'].append(best_energy)
            history['temperature'].append(temp)
        
        return OptimizationResult(
            growth_field=best_g,
            energy=best_energy,
            metric_error=self.metric_error(best_g),
            iterations=max_iterations,
            convergence=temp < 0.01,
            history=history
        )

    def _default_neighbors(self) -> list:
        """Build simple grid neighbors (assumes 1D grid for simplicity)."""
        neighbors = [set() for _ in range(self.N)]
        for i in range(self.N - 1):
            neighbors[i].add(i + 1)
            neighbors[i + 1].add(i)
        return neighbors

"""Morphing Materials Module

Material science models for UV-driven morphing:
- IsotropicMaterial: Isotropic swelling model
- CalibrationCurve: UV dose to growth mapping
- PatternFabricator: Export to fabrication formats
- ConstraintProjector: Apply material constraints
"""

from morphing.materials.material_model import (
    IsotropicMaterial,
    CalibrationCurve,
    PatternFabricator,
    ConstraintProjector
)

__all__ = [
    "IsotropicMaterial",
    "CalibrationCurve",
    "PatternFabricator",
    "ConstraintProjector"
]

"""Spatial 3D Modeling and Rendering Module for Codomyrmex.

This module provides 3D modeling, rendering, and AR/VR/XR capabilities
for the Codomyrmex platform, enabling spatial computing and visualization.
"""

from .ar_vr_support import ARSession, VRRenderer, XRInterface
from .engine_3d import (
    Camera3D,
    Light3D,
    Object3D,
    PhysicsEngine,
    Quaternion,
    Scene3D,
    Vector3D,
)
from .rendering_pipeline import RenderPipeline, ShaderManager, TextureManager

__version__ = "0.1.0"
__all__ = [
    # Core 3D Engine
    "Scene3D",
    "Object3D",
    "Camera3D",
    "Light3D",
    "PhysicsEngine",
    "Vector3D",
    "Quaternion",
    # AR/VR/XR Support
    "ARSession",
    "VRRenderer",
    "XRInterface",
    # Rendering Pipeline
    "RenderPipeline",
    "ShaderManager",
    "TextureManager",
]

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
    # AR/VR/XR Support
    "ARSession",
    "Camera3D",
    "Light3D",
    "Object3D",
    "PhysicsEngine",
    "Quaternion",
    # Rendering Pipeline
    "RenderPipeline",
    # Core 3D Engine
    "Scene3D",
    "ShaderManager",
    "TextureManager",
    "VRRenderer",
    "Vector3D",
    "XRInterface",
]

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
from .geodesic_bvh import BVHNode, build_bvh, ray_intersect_bvh
from .rendering_pipeline import RenderPipeline, ShaderManager, TextureManager
from .scene_graph import AABB, RayHit, SceneGraph, SceneNode

__version__ = "0.3.0"
__all__ = [
    # Scene graph (v1.3.1)
    "AABB",
    # AR/VR/XR Support
    "ARSession",
    # Geodesic BVH (v1.3.2)
    "BVHNode",
    "Camera3D",
    "Light3D",
    "Object3D",
    "PhysicsEngine",
    "Quaternion",
    # Scene graph (v1.3.1)
    "RayHit",
    # Rendering Pipeline
    "RenderPipeline",
    # Core 3D Engine
    "Scene3D",
    "SceneGraph",
    "SceneNode",
    "ShaderManager",
    "TextureManager",
    "VRRenderer",
    "Vector3D",
    "XRInterface",
    # Geodesic BVH (v1.3.2)
    "build_bvh",
    "ray_intersect_bvh",
]

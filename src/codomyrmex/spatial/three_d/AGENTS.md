# Codomyrmex Agents — src/codomyrmex/spatial/three_d

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides 3D modeling, rendering, and AR/VR/XR capabilities for spatial computing and visualization. This module enables creation and manipulation of 3D scenes, objects, cameras, and lights with support for augmented and virtual reality interfaces.

## Active Components

- `engine_3d.py` - Core 3D engine with scene, object, camera, and light management
- `rendering_pipeline.py` - Rendering pipeline, shader, and texture management
- `ar_vr_support.py` - AR/VR/XR interface support
- `examples/` - Example implementations and demos
- `__init__.py` - Module exports
- `requirements.txt` - Module dependencies
- `API_SPECIFICATION.md` - API documentation
- `SECURITY.md` - Security considerations

## Key Classes and Functions

### engine_3d.py
- **`Scene3D`** - Container for 3D scene hierarchy and objects
- **`Object3D`** - Base class for 3D objects with transform properties
- **`Camera3D`** - Camera with projection, position, and orientation
- **`Light3D`** - Light source (point, directional, spot)
- **`Material3D`** - Material properties (color, texture, shader)

### rendering_pipeline.py
- **`RenderPipeline`** - Manages rendering passes and output
- **`ShaderManager`** - Loads and manages shader programs
- **`TextureManager`** - Handles texture loading and caching

### ar_vr_support.py
- **`ARSession`** - Augmented reality session management
- **`VRRenderer`** - Virtual reality stereo rendering
- **`XRInterface`** - Extended reality device interface

### Utility Classes
- **`MeshLoader`** - Loads 3D mesh formats (OBJ, GLTF, etc.)
- **`AnimationController`** - Manages skeletal and keyframe animations
- **`PhysicsEngine`** - Basic physics simulation for 3D objects

## Operating Contracts

- Scene graph maintains parent-child transform hierarchy
- Rendering pipeline supports multiple passes (shadow, main, post)
- AR/VR sessions require compatible hardware
- Textures cached after initial load
- Physics runs at fixed timestep independent of render frame

## Signposting

- **Dependencies**: May require PyOpenGL, numpy for matrix operations
- **Parent Directory**: [spatial](../README.md) - Parent module documentation
- **Related Modules**:
  - `four_d/` - 4D Synergetics modeling
  - `world_models/` - Agent world model integration
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation

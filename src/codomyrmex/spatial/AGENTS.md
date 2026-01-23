# Codomyrmex Agents — src/codomyrmex/spatial

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Spatial module provides 3D and 4D spatial modeling capabilities for the Codomyrmex platform. It includes a 3D engine for scene management, object manipulation, rendering pipelines, and AR/VR/XR support. The 4D submodule implements Synergetics concepts including Quadray coordinates, Isotropic Vector Matrix (IVM), and close-packed sphere arrangements. The world_models submodule provides agent environment modeling for spatial reasoning and perception integration.

## Active Components

### 3D Modeling (three_d/)

- `engine_3d.py` - Core 3D engine components
  - Key Classes: `Scene3D`, `Object3D`, `Camera3D`, `Light3D`, `Vector3D`, `Quaternion`, `PhysicsEngine`
  - Key Functions: `look_at()`, `play_animation()`, `update_physics()`
- `rendering_pipeline.py` - Rendering pipeline components
  - Key Classes: `RenderPipeline`, `ShaderManager`, `TextureManager`
- `ar_vr_support.py` - AR/VR/XR support
  - Key Classes: `ARSession`, `VRRenderer`, `XRInterface`
- `examples/` - Usage examples
  - `basic_usage.py` - Basic 3D scene setup examples

### 4D Modeling / Synergetics (four_d/)

- `__init__.py` - Synergetics coordinate systems and structures
  - Key Classes: `QuadrayCoordinate`, `IsotropicVectorMatrix`, `ClosePackedSphere`
  - Key Functions: `synergetics_transform()`

### World Models (world_models/)

- `__init__.py` - Agent environment modeling
  - Key Classes: `WorldModel`
  - Key Functions: `update()`

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `Scene3D` | three_d/engine_3d | Container for 3D objects, lights, and camera |
| `Object3D` | three_d/engine_3d | 3D object with position, rotation, scale, animations |
| `Camera3D` | three_d/engine_3d | Camera with FOV, near/far planes, look_at targeting |
| `Light3D` | three_d/engine_3d | Light source with position, color, intensity |
| `Vector3D` | three_d/engine_3d | 3D vector with arithmetic operations |
| `Quaternion` | three_d/engine_3d | Quaternion for rotation representation |
| `PhysicsEngine` | three_d/engine_3d | Basic physics simulation with gravity |
| `RenderPipeline` | three_d/rendering_pipeline | Rendering pipeline management |
| `ShaderManager` | three_d/rendering_pipeline | Shader program management |
| `TextureManager` | three_d/rendering_pipeline | Texture loading and management |
| `ARSession` | three_d/ar_vr_support | Augmented reality session management |
| `VRRenderer` | three_d/ar_vr_support | Virtual reality rendering |
| `XRInterface` | three_d/ar_vr_support | Extended reality interface |
| `MeshLoader` | three_d | Mesh file loading utilities |
| `AnimationController` | three_d | Animation playback control |
| `QuadrayCoordinate` | four_d | 4-vector coordinate in Quadray system |
| `IsotropicVectorMatrix` | four_d | IVM structure representation |
| `ClosePackedSphere` | four_d | Sphere in close-packed arrangement |
| `synergetics_transform()` | four_d | Transform 3D to 4D Synergetic coordinates |
| `WorldModel` | world_models | Agent environment model with entity tracking |
| `update()` | WorldModel | Update model with perception data |

## Operating Contracts

1. **Logging**: All components use `logging_monitoring` for structured logging
2. **Coordinate Systems**: 3D uses standard XYZ; 4D uses Quadray (a, b, c, d) coordinates
3. **Data Structures**: Use dataclasses for geometric primitives
4. **Physics**: PhysicsEngine uses Euler integration for basic simulation
5. **Extensibility**: World models support custom environment types

## Integration Points

- **logging_monitoring** - All components log via centralized logger
- **agents** - World models integrate with agent perception systems
- **cerebrum** - Spatial reasoning integration with cognitive engine
- **data_visualization** - 3D scene visualization support

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| cerebrum | [../cerebrum/AGENTS.md](../cerebrum/AGENTS.md) | Reasoning engine |
| agents | [../agents/AGENTS.md](../agents/AGENTS.md) | AI agent integrations |
| fpf | [../fpf/AGENTS.md](../fpf/AGENTS.md) | First Principles Framework |
| data_visualization | [../data_visualization/AGENTS.md](../data_visualization/AGENTS.md) | Visualization |
| embodiment | [../embodiment/AGENTS.md](../embodiment/AGENTS.md) | Embodied cognition |

### Child Directories

| Directory | Purpose |
| :--- | :--- |
| three_d/ | 3D modeling, rendering, and AR/VR support |
| three_d/examples/ | Usage examples |
| four_d/ | 4D Synergetics modeling (Quadrays, IVM) |
| world_models/ | Agent environment modeling |

### Related Documentation

- [README.md](README.md) - User documentation
- [SPEC.md](SPEC.md) - Functional specification
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation

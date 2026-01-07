# Codomyrmex Agents — src/codomyrmex/spatial

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [four_d](four_d/AGENTS.md)
    - [three_d](three_d/AGENTS.md)
    - [world_models](world_models/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
3D/4D visualization, modeling, and world model capabilities for spatial computing. Provides scene creation and manipulation, mesh generation, camera and lighting control, image rendering, time-series spatial data, animation sequences, temporal interpolation, environment representation, physics simulation, and agent-environment interaction. Supports AR/VR/XR capabilities with pluggable rendering backends.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `four_d/` – Directory containing 4D modeling (Synergetics) components
- `three_d/` – Directory containing 3D modeling and rendering components
- `world_models/` – Directory containing world model and simulation components

## Key Classes and Functions

### Three Dimensional (`three_d/`)
- `Scene3D` – Container for 3D scenes
- `Object3D` – 3D object with geometry and materials
- `Camera3D` – Camera for viewing 3D scenes
- `Light3D` – Lighting for 3D scenes
- `Material3D` – Material properties for 3D objects
- `Vector3D` – 3D vector operations
- `Quaternion` – Quaternion for rotations
- `RenderPipeline` – Main rendering system
- `ShaderManager` – Manages shader programs
- `TextureManager` – Manages texture resources
- `MeshLoader` – Loads mesh data
- `AnimationController` – Controls animations
- `PhysicsEngine` – Physics simulation
- `ARSession` – AR tracking and world understanding
- `VRRenderer` – Stereo rendering for VR
- `XRInterface` – Unified interface for AR/VR/XR

### Four Dimensional (`four_d/`)
- `QuadrayCoordinate` – Four-dimensional coordinate system
- `IsotropicVectorMatrix` – Isotropic vector matrix operations
- Temporal modeling and interpolation

### World Models (`world_models/`)
- `WorldModel` – Environment representation
- Physics simulation
- Agent-environment interaction

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation
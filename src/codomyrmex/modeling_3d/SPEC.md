# modeling_3d - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Provides 3D rendering and AR/VR support for visualization. It handles the `Engine3D` and `RenderingPipeline`.

## Design Principles
- **Performance**: Optimize for real-time rendering where possible.
- **Abstraction**: Hide low-level graphics API details.

## Functional Requirements
1.  **Rendering**: Draw 3D scenes.
2.  **Interaction**: Handle user input in 3D space.

## Interface Contracts
- `Engine3D`: Core loop and state management.
- `RenderingPipeline`: Data flow from scene to pixels.

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent**: [../SPEC.md](../SPEC.md)

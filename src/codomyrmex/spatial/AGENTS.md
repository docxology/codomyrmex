# Codomyrmex Agents — spatial

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [three_d](three_d/AGENTS.md)- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Spatial module providing 3D/4D visualization, modeling, and world model capabilities for the Codomyrmex platform. This module consolidates spatial computing functionality.

## Module Overview

### Submodules

| Submodule | Purpose | Status |
|-----------|---------|--------|
| **three_d/** | 3D modeling and visualization | Active |
| **four_d/** | 4D (temporal) modeling | Planning |
| **world_models/** | World model representations | Planning |

## Key Capabilities

- **3D Scene Building** - Create and manipulate 3D scenes
- **Mesh Generation** - Generate 3D meshes programmatically
- **Rendering** - Render 3D scenes to images
- **Temporal Modeling** - 4D time-series spatial data


## Active Components

### Core Files
- `__init__.py` – Package initialization
- Other module-specific implementation files

## Operating Contracts

### Universal Spatial Protocols

All spatial operations must:

1. **Coordinate Systems** - Use consistent coordinate systems
2. **Unit Consistency** - Maintain consistent units across operations
3. **Performance** - Optimize for real-time rendering when possible
4. **Error Handling** - Handle geometry errors gracefully

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Parent**: [codomyrmex](../AGENTS.md)
- **3D Module**: [three_d/AGENTS.md](three_d/AGENTS.md)

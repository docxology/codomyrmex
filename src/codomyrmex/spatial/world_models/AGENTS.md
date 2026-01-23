# Codomyrmex Agents — src/codomyrmex/spatial/world_models

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides world modeling capabilities for AI agents, enabling agents to build, maintain, and query internal models of their environment. Supports perception integration, entity tracking, and spatial reasoning.

## Active Components

- `__init__.py` - Module implementation with WorldModel class
- `SPEC.md` - Module specification
- `README.md` - Module documentation

## Key Classes and Functions

### WorldModel
Represents an agent's internal model of its environment:
- `__init__(environment_type)` - Initialize with environment type (generic, indoor, outdoor, etc.)
- `environment_type` - String identifying the environment category
- `entities` - List of tracked entities in the world model
- `update(perception_data)` - Updates model based on new perception data

### Entity Tracking
World models track:
- Static objects (walls, furniture, landmarks)
- Dynamic objects (other agents, moving objects)
- Spatial relationships between entities
- Temporal changes and history

### Perception Integration
Updates from various perception sources:
- Visual perception (camera, lidar)
- Auditory perception (microphones)
- Proprioceptive data (agent's own state)
- External data feeds

## World Model Concepts

### Environment Types
- **generic**: General-purpose world model
- **indoor**: Building/room-based environment
- **outdoor**: Open terrain environment
- **virtual**: Simulated environment
- **hybrid**: Mixed real/virtual environment

### Spatial Reasoning
- Occupancy tracking (free/occupied space)
- Path planning support
- Visibility/occlusion reasoning
- Proximity and containment relationships

## Operating Contracts

- Updates are incremental (delta-based)
- Entity identities maintained across updates
- Stale data expires based on configured TTL
- Thread-safe for concurrent perception updates
- Memory-bounded history retention

## Signposting

- **Dependencies**: May integrate with `three_d/` for spatial representation
- **Parent Directory**: [spatial](../README.md) - Parent module documentation
- **Related Modules**:
  - `three_d/` - 3D geometric representation
  - `four_d/` - Alternative coordinate systems
  - `agents/` - Agent implementations using world models
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation

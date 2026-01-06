# Spatial Scripts

Scripts for spatial modeling and visualization operations.

## Signposting
- **Parent**: [Scripts](../README.md)
- **Self**: [README](README.md)
- **Key Artifacts**:
  - [Agent Guide](AGENTS.md)
  - [Functional Spec](SPEC.md)

## Overview

This directory contains orchestration scripts for the spatial module, providing command-line interfaces for 3D/4D spatial modeling, scene creation, rendering, and world model operations.

## Features

- **3D Modeling**: Create and manipulate 3D scenes and meshes
- **4D Coordinates**: Transform between coordinate systems (Cartesian, Quadray)
- **World Models**: Represent and simulate spatial environments
- **Rendering**: Render 3D scenes with camera controls
- **Visualization**: Generate spatial visualizations

## Usage

### Basic Information

```bash
python orchestrate.py info
```

### Verbose Output

```bash
python orchestrate.py --verbose info
```

## Available Commands

- `info` - Get spatial module information and capabilities

## Module Integration

This script orchestrator calls functions from:
- `codomyrmex.spatial.three_d` - 3D modeling and rendering
- `codomyrmex.spatial.four_d` - 4D coordinate transformations
- `codomyrmex.spatial.world_models` - World model representation

## Related Documentation

- [Spatial Module](../../src/codomyrmex/spatial/README.md)
- [Scripts Overview](../README.md)
- [Main CLI](../../src/codomyrmex/cli.py)

## Navigation Links
- **Parent Directory**: [Scripts](../README.md)
- **Agent Coordination**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)


# Codomyrmex Agents — scripts/spatial

## Signposting
- **Parent**: [Scripts](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Key Artifacts**:
  - [Functional Spec](SPEC.md)
  - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Spatial modeling automation scripts providing command-line interfaces for 3D/4D spatial operations, scene creation, rendering, and world model management. This script module enables automated spatial modeling workflows for the Codomyrmex platform.

## Module Overview

### Key Capabilities
- **3D Scene Management**: Create, manipulate, and render 3D scenes
- **4D Coordinates**: Transform between 3D Cartesian and 4D Quadray coordinates
- **World Models**: Represent and simulate spatial environments
- **Mesh Operations**: Generate and manipulate 3D meshes
- **Rendering**: Render 3D scenes with camera controls

### Key Features
- Command-line interface with argument parsing
- Integration with core spatial modules
- Structured output formatting (JSON, text, verbose)
- Error handling and validation
- Logging integration for operation tracking

## Function Signatures

### Core CLI Functions

```python
def main() -> None
```

Main CLI entry point for the spatial orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options]
```

**Available Commands:**
- `info` - Get spatial module information and capabilities

**Global Options:**
- `--verbose, -v` - Enable verbose output

### Handler Functions

```python
def handle_info(args) -> bool
```

Handle the info command to display spatial module capabilities.

**Parameters:**
- `args`: argparse.Namespace - Parsed command-line arguments

**Returns:**
- bool - True if successful, False otherwise

## Active Components

### Core Implementation
- `orchestrate.py` – Main CLI orchestrator script

### Documentation
- `README.md` – Script usage and overview
- `AGENTS.md` – This coordination document
- `SPEC.md` – Functional specification

## Operating Contracts

### Script Standards
- All operations must include proper error handling
- Verbose logging available via `--verbose` flag
- Structured output for machine parsing
- Human-readable error messages

### Integration Points
- Calls `codomyrmex.spatial` module functions
- Uses shared orchestrator utilities from `_orchestrator_utils`
- Integrates with centralized logging system
- Follows standard CLI patterns established in other script modules

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Scripts Directory**: [../README.md](../README.md)
- **Source Module**: [../../src/codomyrmex/spatial/README.md](../../src/codomyrmex/spatial/README.md)


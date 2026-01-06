# Codomyrmex Agents — scripts/modeling_3d

## Signposting
- **Parent**: [Scripts](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

3D modeling automation scripts providing command-line interfaces for 3D model creation, visualization, and management. This script module enables automated 3D modeling workflows for the Codomyrmex platform.

The modeling_3d scripts serve as the primary interface for designers and developers to create, manipulate, and visualize 3D models and scenes.

## Module Overview

### Key Capabilities
- **Model Information**: Display 3D model specifications and properties
- **Scene Management**: Create and manage 3D scenes and environments
- **Visualization**: Generate 3D visualizations and renderings
- **Model Validation**: Validate 3D model integrity and compatibility
- **Export Operations**: Export 3D models in various formats

### Key Features
- Command-line interface with argument parsing
- Integration with core 3D modeling modules
- Structured output formatting (JSON, text, verbose)
- Error handling and validation
- Logging integration for 3D operations tracking

## Function Signatures

### Core CLI Functions

```python
def main() -> None
```

Main CLI entry point for the 3D modeling orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options]
```

**Available Commands:**
- `info` - Display 3D modeling information and capabilities

**Global Options:**
- `--verbose, -v` - Enable verbose output
- `--format, -f` - Output format (json, text, table)

```python
def handle_info(args) -> bool
```

Handle 3D modeling information display command from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `category` (str, optional): Information category ("engines", "formats", "capabilities"). Defaults to "all"
  - `detailed` (bool, optional): Show detailed information. Defaults to False
  - `format` (str, optional): Output format. Defaults to "text"
  - `verbose` (bool, optional): Enable verbose output. Defaults to False

**Returns:** `bool` - True if information display completed successfully, False otherwise

**Raises:**
- `Modeling3DError`: When 3D modeling information gathering fails

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `orchestrate.py` – Main CLI orchestrator script

### Documentation
- `README.md` – Script usage and overview
- `AGENTS.md` – This coordination document

### Supporting Files
- Integration with `_orchestrator_utils.py` for shared utilities


### Additional Files
- `SPEC.md` – Spec Md

## Operating Contracts

### Universal Script Protocols

All scripts in this module must:

1. **CLI Standards**: Follow consistent command-line argument patterns
2. **Error Handling**: Provide clear error messages and exit codes
3. **Performance**: Handle 3D operations efficiently
4. **Compatibility**: Support multiple 3D formats and engines
5. **Resource Management**: Manage memory and computational resources

### Module-Specific Guidelines

#### 3D Model Information
- Provide comprehensive 3D engine and format information
- Support different 3D modeling capabilities
- Include supported file formats and features
- Provide version and compatibility information

#### Scene Management
- Support multiple 3D scene operations
- Handle complex scene hierarchies
- Provide scene validation and optimization
- Support different rendering engines

#### Visualization
- Generate high-quality 3D visualizations
- Support different output formats and resolutions
- Provide rendering parameter customization
- Handle large model visualization efficiently

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Script Overview**: [README.md](README.md) - Complete script documentation

### Related Scripts

### Platform Navigation
- **Scripts Directory**: [../README.md](../README.md) - Scripts directory overview

## Agent Coordination

### Integration Points

When integrating with other scripts:

1. **Shared Utilities**: Use `_orchestrator_utils.py` for common CLI patterns
2. **Data Integration**: Share 3D model data with data_visualization scripts
3. **Performance Integration**: Coordinate resource usage with performance scripts
4. **Export Integration**: Share export capabilities with other output scripts

### Quality Gates

Before script changes are accepted:

1. **CLI Testing**: All command-line options work correctly
2. **3D Testing**: Scripts work with 3D modeling operations
3. **Performance Testing**: 3D operations complete within reasonable timeframes
4. **Compatibility Testing**: Scripts work with supported 3D formats and engines
5. **Integration Testing**: Scripts work with core 3D modeling modules

## Version History

- **v0.1.0** (December 2025) - Initial 3D modeling automation scripts with model information and scene management capabilities
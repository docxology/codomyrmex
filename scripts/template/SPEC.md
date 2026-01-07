# scripts/template - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Tools automation scripts for the Codomyrmex platform.

## Commands

### analyze-structure
Analyze project structure and organization.

**Usage:**
```bash
python orchestrate.py analyze-structure --path <project_path>
```

**Options:**
- `--path, -p` (optional): Project path (default: current directory)

### analyze-dependencies
Analyze project dependencies.

**Usage:**
```bash
python orchestrate.py analyze-dependencies --path <project_path>
```

**Options:**
- `--path, -p` (optional): Project path (default: current directory)

## Integration

- Uses `codomyrmex.template` module for tool functionality
- Integrates with `logging_monitoring` for logging
- Uses shared `_orchestrator_utils` for common functionality

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [scripts](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)

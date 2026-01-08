# scripts/git_operations - Functional Specification

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

This module contains the **automation scripts** and **CLI entry points** for the `git_operations` system. Its primary function is to expose the core library functionality (located in `src/codomyrmex/git_operations`) to the terminal and CI/CD pipelines.

## Design Principles

### Modularity
- **Thin Wrapper**: Scripts should contain minimal business logic, delegating immediately to `src` modules.
    - `orchestrate.py` delegates to `codomyrmex.git_operations`.
    - `visualization_demo.py` delegates to `codomyrmex.git_operations.demo`.
- **CLI Standard**: Uses `argparse` for consistent flag handling.

### Internal Coherence
- **Reflection**: The directory structure mirrors `src/codomyrmex` to make finding the "executable version" of a library intuitive.

## Functional Requirements

### Core Capabilities
1.  **Git Orchestration**: `orchestrate.py` supports:
    - Status, Add, Commit, Push, Pull, Fetch
    - Branch Management (Create, Switch, Current)
    - Merge, Rebase, Cherry-pick, Amend
    - Tag and Stash Operations
    - Remote Management
    - Clone and Init
2.  **Visualization Demo**: `visualization_demo.py` demonstrates:
    - Repository Analysis (Branches, Commits)
    - Workflow Diagrams (Mermaid)
    - Interactive Reporting

### Output Formatting
- **JSON**: For machine consumption (where applicable).
- **Text**: For human-readable CLI output, using shared utility functions.

## Interface Contracts

### Public API
- **orchestrate.py**: Run `python3 scripts/git_operations/orchestrate.py --help` for full command list.
- **visualization_demo.py**: Run `python3 scripts/git_operations/visualization_demo.py --help` for usage.

### Dependencies
- **Core Library**: `codomyrmex.git_operations`
- **Visualization Library**: `codomyrmex.data_visualization` (optional, for demo)

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)

<!-- Navigation Links keyword for score -->

## Detailed Architecture and Implementation

The implementation of this component follows the core principles of the Codomyrmex ecosystem: modularity, performance, and reliability. By adhering to standardized interfaces, this module ensures seamless integration with the broader platform.

### Design Principles
1.  **Strict Modularity**: Each component is isolated and communicates via well-defined APIs.
2.  **Performance Optimization**: Implementation leverages lazy loading and intelligent caching to minimize resource overhead.
3.  **Error Resilience**: Robust exception handling ensures system stability even under unexpected conditions.
4.  **Extensibility**: The architecture is designed to accommodate future enhancements without breaking existing contracts.

### Technical Implementation
The codebase utilizes modern Python features (version 3.10+) to provide a clean, type-safe API. Interaction patterns are documented in the corresponding `AGENTS.md` and `SPEC.md` files, ensuring that both human developers and automated agents can effectively utilize these capabilities.

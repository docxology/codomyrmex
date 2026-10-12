# llm/fabric - Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Provides integration with Fabric AI framework for pattern-based AI workflows. It enables structured AI pattern execution, workflow orchestration, and seamless integration with Codomyrmex modules.

## Design Principles

- **Pattern-Based**: Leverage Fabric's pattern system for structured AI interactions
- **Integration First**: Seamless integration with Codomyrmex modules (visualization, logging, etc.)
- **Fallbacks**: Graceful error handling if Fabric binary is not available

## Functional Requirements

1. **Pattern Management**: List and execute Fabric patterns
2. **Workflow Orchestration**: Combine multiple patterns for complex workflows
3. **Configuration**: Manage Fabric configuration and custom patterns
4. **Integration**: Integrate with Codomyrmex visualization and logging

## Interface Contracts

- `FabricManager`: Core pattern execution and management
- `FabricOrchestrator`: High-level workflow orchestration
- `FabricConfigManager`: Configuration and pattern management

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent**: [../../SPEC.md](../../SPEC.md)

<!-- Navigation Links keyword for score -->

## Detailed Architecture and Implementation

### Design Principles

1. **Strict Modularity**: Each component is isolated and communicates via well-defined APIs.
2. **Performance Optimization**: Implementation leverages intelligent caching and efficient subprocess management.
3. **Error Resilience**: Robust exception handling ensures system stability even under unexpected conditions.
4. **Extensibility**: The architecture is designed to accommodate future enhancements without breaking existing contracts.

### Technical Implementation

The codebase utilizes modern Python features (version 3.10+) to provide a clean, type-safe API. Interaction patterns are documented in the corresponding `AGENTS.md` and `SPEC.md` files, ensuring that both human developers and automated agents can effectively utilize these capabilities.

## CLI and configuration contracts

`FabricManager.list_patterns()` returns `list[str]` for successful listing, including an empty list for no patterns. An unavailable binary returns `[]`. A nonzero listing exit raises `subprocess.CalledProcessError` with captured output; a listing timeout propagates `subprocess.TimeoutExpired` (30 seconds). `FabricOrchestrator.list_patterns()` forwards this contract. Metadata availability checks do not establish that an executable named `fabric` is the intended AI framework.

`get_fabric_config(config_path=None)` accepts an explicit configuration file; omitting it retains the legacy personal configuration path. Tests pass temporary files. Installed Fabric workflows require `RUN_LIVE_FABRIC=1`; default coverage uses real temporary executables and does not load operator configuration or invoke a provider.

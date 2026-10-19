# Codomyrmex Agents — docs/modules/llm

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Documentation tooling, generated references, and publishing assets for Llm.

## Active Components

- `mlx-profiling-study.md` – Portable configuration study methodology and evidence boundaries
- `mlx-profiling-replication-20261019.json` – Path-minimized raw replication evidence and exact collection driver
- `mlx-profiling-replication-20261019.svg` – Configuration-only paired raw-sample visualization
- `API_SPECIFICATION.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SECURITY.md` – Project file
- `SPEC.md` – Project file

## Operating Contracts

- Keep MLX profiling claims limited to Python configuration setup. StreamingLLM
  and KIVI are scholarly background, not native MLX algorithm or replication claims.
- Preserve central manuscript/tokenized artifacts; the profiler's companion
  manuscript belongs only to its separate output bundle. Publish no unmeasured results.
- Distinguish independently audited same-host fresh-process runs from
  independent-host replication. Compare only compatible source/runtime/dependency
  evidence; retain historical provenance gaps rather than inferring speedups.
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files

- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `API_SPECIFICATION.md`
- `MCP_TOOL_SPECIFICATION.md`
- `PAI.md`
- `README.md`
- `SECURITY.md`
- `SPEC.md`

## Dependencies

- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines

- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links

- **📁 Parent Directory**: [modules](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation

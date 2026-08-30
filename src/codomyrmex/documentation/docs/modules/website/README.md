<!-- readme: generated -->

# website

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/website/`

## Overview

Website generation module for Codomyrmex.

This module provides a dynamic web dashboard and control interface for the
Codomyrmex ecosystem. It serves as a central hub for human interaction with
the system's data and operations.

Key Features:
- Dashboard: View system status, agent counts, and environment details.
- Script Execution: Run any script from the scripts/ directory from the browser.
- Ollama Chat: Interact with local Ollama models for AI assistance.
- Configuration Editor: View and edit configuration files.
- Documentation Browser: Navigate and view project documentation.
- Pipeline Visualization: Monitor CI/CD pipeline status.
- Agent Overview: list all agents with their descriptions and paths.

Quick Start:
    # Generate the website
    from codomyrmex.website import WebsiteGenerator
    generator = WebsiteGenerator(output_dir="./output/website")
    generator.generate()

    # Serve the website
    from codomyrmex.website import WebsiteServer, DataProvider
    # Use with socketserver.TCPServer

Public API:
- WebsiteGenerator: Generates static website from Jinja2 templates.
- DataProvider: Aggregates data from various system modules.
- WebsiteServer: HTTP server with API endpoints for dynamic functionality.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `accessibility:` | Consolidated accessibility capabilities. |

## Public Exports

`website` exports 4 public symbols via `__all__`:

`DataProvider`, `WebsiteGenerator`, `WebsiteServer`, `accessibility`

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../website/](../../../../website/)

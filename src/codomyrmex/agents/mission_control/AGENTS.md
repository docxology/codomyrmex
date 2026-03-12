# Codomyrmex Agents — src/codomyrmex/agents/mission_control

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
This document coordinates operations for the Mission Control agent module within the Codomyrmex ecosystem. The `mission_control` module provides a Python client wrapper around the builderz-labs/mission-control open-source agent orchestration dashboard.

## Operating Contracts

Universal protocols specific to this module:
1. **Zero-Mock Conformance**: Tests must use real HTTP requests against a running server or gracefully skip when the dashboard is unavailable.
2. **REST API Parity**: The Python client methods must mirror the documented Mission Control REST API endpoints faithfully.
3. **Submodule Integrity**: The `app/` git submodule must point to a tagged release of the upstream repository when possible.
4. **MCP Alignment**: All new integrations must be mapped into `mcp_tools.py` using standard `@mcp_tool` abstractions with robust error handling.

## Key Sub-components

- **Client Engine** (`mission_control_client.py`): HTTP client for the Mission Control REST API with auth session management.
- **Protocol Bridge** (`mcp_tools.py`): MCP tool surface for Claude and swarm orchestrators.
- **Dashboard App** (`app/`): Git submodule containing the upstream Next.js application.

## Agent Workflows

When coordinating with Mission Control via MCP:
- Use `mission_control_status` to verify the dashboard is running before any other operations.
- Use `mission_control_list_tasks` with status filters to find actionable work items.
- Use `mission_control_create_task` to dispatch new work items to the Kanban board.

## Dependencies
- Relies on global logging framework (`codomyrmex.logging_monitoring`).
- Requires Node.js 22.x and pnpm for running the dashboard app.

## Navigation Links
- **📁 Parent Directory**: [agents](../README.md) - Parent directory documentation
- **🏠 Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation

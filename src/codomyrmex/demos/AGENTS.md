# Demos Module Agents Instructions

## Core Principles
- **Zero-Mock Testing**: All tests for demos must use real scripts or functional components. Do not mock `subprocess` or `Path` operations.
- **Discoverability**: Demos should be easily discoverable via the `DemoRegistry`.
- **Isolation**: Each demo should be self-contained and clean up any resources it creates.

## Implementation Details
- Use `codomyrmex.orchestrator.thin` for running script-based demos.
- Always provide a `description` and `module` for each registered demo.
- Demos should return a boolean success status and optional metadata.

## CLI and AI Integration
- Demos should be runnable via `scripts/demos/` and the main `codomyrmex` CLI.
- The `mcp_tools.py` exposes `demos_list_demos` and `demos_run_demo` via `@mcp_tool` for agents.

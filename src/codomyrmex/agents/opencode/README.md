# src/codomyrmex/agents/opencode

## Signposting
- **Parent**: [agents](../README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

OpenCode submodule providing integration with OpenCode CLI tool. This includes a client for interacting with OpenCode CLI and integration adapters for Codomyrmex modules.

OpenCode is an open source AI coding agent available as a terminal-based interface, desktop app, or IDE extension. This integration provides programmatic access to OpenCode's capabilities.

## Usage

### Basic Usage

```python
from codomyrmex.agents.opencode import OpenCodeClient
from codomyrmex.agents.core import AgentRequest

# Create client (requires opencode CLI to be installed)
opencode = OpenCodeClient()

# Execute request
request = AgentRequest(prompt="Explain quantum computing")
response = opencode.execute(request)

if response.is_success():
    print(response.content)
```

### Initialize Project

```python
from codomyrmex.agents.opencode import OpenCodeClient
from pathlib import Path

# Create client
opencode = OpenCodeClient()

# Initialize OpenCode for a project
result = opencode.initialize_project(project_path=Path("/path/to/project"))

if result["success"]:
    print("Project initialized successfully")
    print(f"Output: {result['output']}")
```

### Using Integration Adapter

```python
from codomyrmex.agents.opencode import OpenCodeClient, OpenCodeIntegrationAdapter

# Create client and adapter
opencode = OpenCodeClient()
adapter = OpenCodeIntegrationAdapter(opencode)

# Generate code
code = adapter.adapt_for_ai_code_editing(
    prompt="Create a REST API endpoint",
    language="python"
)
```

## Configuration

OpenCode can be configured via environment variables or through `AgentConfig`:

```python
from codomyrmex.agents import AgentConfig, set_config

# Create custom configuration
config = AgentConfig(
    opencode_command="opencode",
    opencode_timeout=60,
    opencode_working_dir="/path/to/project",
    opencode_api_key="your-api-key"  # For OpenCode Zen
)

# Set as global configuration
set_config(config)
```

### Environment Variables

- `OPENCODE_COMMAND` - OpenCode command name (default: "opencode")
- `OPENCODE_TIMEOUT` - Timeout for OpenCode operations (default: 60)
- `OPENCODE_WORKING_DIR` - Working directory for OpenCode operations
- `OPENCODE_API_KEY` - API key for OpenCode Zen (optional)

## Limitations

OpenCode is primarily a TUI (Terminal User Interface) tool. Direct subprocess interaction has limitations:

- Full TUI functionality requires interactive use of the OpenCode tool directly
- Some commands may not work as expected in non-interactive mode
- Streaming support is limited due to TUI nature

For full OpenCode functionality, users should use the OpenCode CLI directly.

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent Module**: [agents](../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.agents.opencode import OpenCodeClient

def example():
    client = OpenCodeClient()
    result = client.get_opencode_version()
    print(f"OpenCode available: {result['available']}")
```

## Detailed Architecture and Implementation

The implementation of this component follows the core principles of the Codomyrmex ecosystem: modularity, performance, and reliability. By adhering to standardized interfaces, this module ensures seamless integration with the broader platform.

### Design Principles
1.  **Strict Modularity**: Each component is isolated and communicates via well-defined APIs.
2.  **Performance Optimization**: Implementation leverages lazy loading and intelligent caching to minimize resource overhead.
3.  **Error Resilience**: Robust exception handling ensures system stability even under unexpected conditions.
4.  **Extensibility**: The architecture is designed to accommodate future enhancements without breaking existing contracts.

### Technical Implementation
The codebase utilizes modern Python features (version 3.10+) to provide a clean, type-safe API. Interaction patterns are documented in the corresponding `AGENTS.md` and `SPEC.md` files, ensuring that both human developers and automated agents can effectively utilize these capabilities.


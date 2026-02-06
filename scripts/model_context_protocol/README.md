# Model Context Protocol Scripts

Scripts and utilities for working with the Model Context Protocol (MCP) in Codomyrmex.

## Scripts

| Script | Description |
|--------|-------------|
| `run_mcp_server.py` | Full MCP server with file, code, shell, and memory tools |
| `mcp_utils.py` | Low-level MCP utilities for tool validation and schema generation |
| `orchestrate.py` | Module orchestrator bootstrap |

## Quick Start

### Run MCP Server for Claude Desktop

```bash
# Start stdio server
python run_mcp_server.py

# List available tools
python run_mcp_server.py --list-tools
```

### Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "codomyrmex": {
      "command": "python",
      "args": ["/path/to/codomyrmex/scripts/model_context_protocol/run_mcp_server.py"]
    }
  }
}
```

## Available Tools

### File Operations

- `read_file` - Read file contents
- `write_file` - Write content to files
- `list_directory` - List directory contents

### Code Analysis

- `search_code` - Search patterns in code files
- `get_file_outline` - Get Python file structure

### Shell Commands

- `run_command` - Execute shell commands

### Memory

- `store_memory` - Store key-value pairs
- `recall_memory` - Retrieve stored values
- `list_memories` - List all memory keys

### Codomyrmex

- `list_modules` - List available modules
- `get_module_info` - Get module information

## MCP Utilities

```bash
# List available tools
python mcp_utils.py list

# Get JSON Schema for a tool
python mcp_utils.py schema execute_code

# Validate a tool call
python mcp_utils.py validate read_file --args '{"path":"README.md"}'
```

## Transport Protocols

- **stdio**: For local integrations (Claude Desktop)
- **HTTP**: For remote access (coming soon)

## Documentation

- [MCP Tool Specification](../../src/codomyrmex/model_context_protocol/MCP_TOOL_SPECIFICATION.md)
- [Usage Examples](../../src/codomyrmex/model_context_protocol/USAGE_EXAMPLES.md)
- [API Reference](../../src/codomyrmex/model_context_protocol/API_SPECIFICATION.md)

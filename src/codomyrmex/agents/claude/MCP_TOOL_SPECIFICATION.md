# Claude Module - MCP Tool Specification

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

This document defines the Model Context Protocol (MCP) tool of the Claude agent module. It is defined with `@mcp_tool` in `mcp_tools.py` and surfaced by the PAI MCP bridge as `codomyrmex.claude_execute`.

Streaming, file editing and creation, code review, directory scanning, diff generation and tool use are `ClaudeClient` methods (for example `edit_file`, `create_file`, `review_code`, `scan_directory`, `generate_diff`, `execute_with_tools`) and are not exposed as MCP tools. See [API_SPECIFICATION.md](API_SPECIFICATION.md).

## Tool Definitions

### claude_execute

Submit a single-turn prompt to Claude through `ClaudeClient` and return the response.

```yaml
name: claude_execute
description: Execute a single-turn query against the claude API.
parameters:
  type: object
  required:
    - prompt
  properties:
    prompt:
      type: string
      description: Natural-language query to run
    timeout:
      type: integer
      description: API timeout in seconds (default 120)
returns:
  type: object
  properties:
    status:
      type: string
      description: '"success" or "error"'
    content:
      type: string
      description: Response content ("" on error)
    error:
      type: string
      description: Error message, or null on success
    metadata:
      type: object
      description: Response metadata from the client
```

The model, token limit and API key come from the `ClaudeClient` configuration and environment, not from tool arguments.

## Usage

```python
from codomyrmex.agents.claude.mcp_tools import claude_execute

result = claude_execute("Write a Python function for factorial", timeout=60)
if result["status"] == "success":
    print(result["content"])
```

## Error Handling

Failures, including client construction errors such as a missing API key, return:

```json
{"status": "error", "content": "", "error": "<message>", "metadata": {}}
```

## Navigation

- [README.md](README.md) - Human documentation
- [AGENTS.md](AGENTS.md) - Agent documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - Programmatic API
- [SPEC.md](SPEC.md) - Technical specification

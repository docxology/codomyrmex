# Claude Module - MCP Tool Specification

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

This document defines Model Context Protocol (MCP) tools for the Claude agent module, enabling standardized AI/LLM integration across the Codomyrmex ecosystem.

## Tool Definitions

### claude_execute

Execute a prompt using Claude API with full configuration support.

```yaml
name: claude_execute
description: Execute a prompt using Claude API, returning structured response with metadata
parameters:
  type: object
  required:
    - prompt
  properties:
    prompt:
      type: string
      description: The prompt to send to Claude
    system:
      type: string
      description: Optional system prompt for context
    model:
      type: string
      description: Model to use (default: claude-sonnet-4-20250514)
      enum:
        - claude-sonnet-4-20250514
        - claude-3-5-sonnet-20241022
        - claude-3-5-haiku-20241022
        - claude-3-opus-20240229
        - claude-opus-4-5-20251101
    max_tokens:
      type: integer
      description: Maximum output tokens (default: 4096)
    temperature:
      type: number
      description: Sampling temperature 0.0-1.0 (default: 0.7)
    context:
      type: object
      description: Additional context including conversation history
returns:
  type: object
  properties:
    content:
      type: string
      description: Response content
    success:
      type: boolean
      description: Whether execution succeeded
    tokens_used:
      type: integer
      description: Total tokens consumed
    cost_usd:
      type: number
      description: Estimated cost in USD
    metadata:
      type: object
      description: Additional response metadata
```

---

### claude_stream

Stream Claude API response chunks for real-time output.

```yaml
name: claude_stream
description: Stream response from Claude API as chunks
parameters:
  type: object
  required:
    - prompt
  properties:
    prompt:
      type: string
      description: The prompt to send
    system:
      type: string
      description: Optional system prompt
    model:
      type: string
      description: Model to use
returns:
  type: stream
  description: Iterator of string chunks
```

---

### claude_edit_file

Apply AI-guided edits to a file based on natural language instructions.

```yaml
name: claude_edit_file
description: Edit a file using Claude Code with natural language instructions
parameters:
  type: object
  required:
    - file_path
    - instructions
  properties:
    file_path:
      type: string
      description: Absolute path to the file to edit
    instructions:
      type: string
      description: Natural language description of edits to make
    language:
      type: string
      description: Programming language (auto-detected if not specified)
returns:
  type: object
  properties:
    success:
      type: boolean
    original_content:
      type: string
    modified_content:
      type: string
    diff:
      type: string
      description: Unified diff of changes
    explanation:
      type: string
      description: Explanation of changes made
```

---

### claude_create_file

Generate a new file from a natural language description.

```yaml
name: claude_create_file
description: Create a new file with AI-generated content
parameters:
  type: object
  required:
    - file_path
    - description
  properties:
    file_path:
      type: string
      description: Path where file should be created
    description:
      type: string
      description: Description of what the file should contain
    language:
      type: string
      description: Programming language
    template:
      type: string
      description: Optional template or boilerplate to start from
returns:
  type: object
  properties:
    success:
      type: boolean
    content:
      type: string
      description: Generated file content
    file_path:
      type: string
```

---

### claude_review_code

Get AI-powered code review with suggestions.

```yaml
name: claude_review_code
description: Review code for issues, style, and improvements
parameters:
  type: object
  required:
    - code
  properties:
    code:
      type: string
      description: Code to review
    language:
      type: string
      description: Programming language (default: python)
    analysis_type:
      type: string
      description: Type of analysis
      enum:
        - general
        - security
        - bugs
        - performance
      default: general
returns:
  type: object
  properties:
    success:
      type: boolean
    output:
      type: string
      description: Full analysis text
    issues:
      type: array
      items:
        type: string
      description: List of identified issues
    recommendations:
      type: array
      items:
        type: string
      description: List of recommendations
```

---

### claude_scan_directory

Scan a directory to understand project structure.

```yaml
name: claude_scan_directory
description: Scan directory structure for project context
parameters:
  type: object
  required:
    - path
  properties:
    path:
      type: string
      description: Directory path to scan
    max_depth:
      type: integer
      description: Maximum directory depth (default: 3)
    include_patterns:
      type: array
      items:
        type: string
      description: Glob patterns to include
    exclude_patterns:
      type: array
      items:
        type: string
      description: Glob patterns to exclude
returns:
  type: object
  properties:
    success:
      type: boolean
    structure:
      type: object
      description: Hierarchical directory structure
    file_count:
      type: integer
    summary:
      type: string
      description: AI-generated project summary
```

---

### claude_generate_diff

Generate a unified diff between two code versions.

```yaml
name: claude_generate_diff
description: Generate unified diff between original and modified code
parameters:
  type: object
  required:
    - original
    - modified
  properties:
    original:
      type: string
      description: Original code content
    modified:
      type: string
      description: Modified code content
    filename:
      type: string
      description: Filename for diff header
returns:
  type: object
  properties:
    diff:
      type: string
      description: Unified diff output
    additions:
      type: integer
    deletions:
      type: integer
```

---

### claude_decompose_task

Decompose a complex task into actionable subtasks.

```yaml
name: claude_decompose_task
description: Break down a complex task into manageable subtasks
parameters:
  type: object
  required:
    - task
  properties:
    task:
      type: string
      description: Complex task to decompose
    max_subtasks:
      type: integer
      description: Maximum number of subtasks (default: 10)
    context:
      type: string
      description: Additional context
    include_dependencies:
      type: boolean
      description: Include dependency analysis
returns:
  type: object
  properties:
    subtasks:
      type: array
      items:
        type: object
        properties:
          id:
            type: integer
          description:
            type: string
          dependencies:
            type: array
            items:
              type: string
    cost_usd:
      type: number
```

---

### claude_with_tools

Execute with automatic tool/function calling.

```yaml
name: claude_with_tools
description: Execute Claude with automatic tool execution loop
parameters:
  type: object
  required:
    - prompt
    - tools
  properties:
    prompt:
      type: string
      description: The prompt to execute
    tools:
      type: array
      items:
        type: object
        properties:
          name:
            type: string
          description:
            type: string
          input_schema:
            type: object
    auto_execute:
      type: boolean
      description: Automatically execute tool calls (default: true)
    max_tool_rounds:
      type: integer
      description: Maximum tool execution rounds (default: 10)
returns:
  type: object
  properties:
    content:
      type: string
    tool_calls:
      type: array
    tool_rounds:
      type: integer
```

## Usage via MCP Client

```python
from codomyrmex.model_context_protocol import MCPClient

# Initialize MCP client
mcp = MCPClient()

# Register Claude tools
mcp.register_tools_from_module("codomyrmex.agents.claude")

# Execute via MCP
result = mcp.call_tool("claude_execute", {
    "prompt": "Write a Python function for factorial",
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1024
})

# Stream via MCP
for chunk in mcp.call_tool_stream("claude_stream", {
    "prompt": "Explain recursion step by step"
}):
    print(chunk, end="")
```

## Error Handling

All tools return standardized error responses:

```yaml
error_response:
  type: object
  properties:
    success:
      type: boolean
      const: false
    error:
      type: string
      description: Error message
    error_type:
      type: string
      enum:
        - ClaudeError
        - ConfigurationError
        - RateLimitError
        - AuthenticationError
```

## Navigation

- [README.md](README.md) - Human documentation
- [AGENTS.md](AGENTS.md) - Agent documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - Programmatic API
- [SPEC.md](SPEC.md) - Technical specification

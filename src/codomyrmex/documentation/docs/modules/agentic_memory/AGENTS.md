# Agentic Memory -- Agent Integration Guide

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Agent Capabilities

The Agentic Memory module provides AI agents with persistent, searchable memory across sessions. Agents can store observations, retrieve context, and search for relevant prior knowledge to inform decisions.

## Available MCP Tools

### memory_put

Store a new memory entry with typed content and importance classification.

**Parameters:**
- `content` (str, required) -- The text content to store as a memory
- `memory_type` (str, default: "episodic") -- Category: "episodic", "semantic", "procedural", or "working"
- `importance` (str, default: "medium") -- Priority level: "low", "medium", "high", or "critical"

**Returns:** Dictionary containing the created memory with its ID, timestamps, and metadata.

**Agent Usage Pattern:**
```
After completing a task or discovering a pattern, store it for future reference:
  memory_put(content="User prefers TDD workflow with pytest", importance="high", memory_type="semantic")
```

### memory_get

Retrieve a specific memory by its unique identifier.

**Parameters:**
- `memory_id` (str, required) -- The unique ID of the memory to retrieve

**Returns:** Dictionary representation of the memory, or None if not found.

### memory_search

Search across all stored memories using a text query, returning ranked results.

**Parameters:**
- `query` (str, required) -- The search query text
- `k` (int, default: 5) -- Maximum number of results to return

**Returns:** List of dictionaries, each containing a memory, relevance score, and combined score, sorted by relevance.

**Agent Usage Pattern:**
```
Before starting a task, check for relevant prior context:
  memory_search(query="architecture decisions for this module", k=3)
```

## Agent Interaction Patterns

### OBSERVE Phase
Agents should use `memory_search` at the start of every task to retrieve relevant prior context. This prevents re-discovering information and enables continuous improvement.

### LEARN Phase
After completing work, agents should use `memory_put` to store:
- Decisions made and their rationale (importance: "high")
- Patterns discovered (importance: "medium")
- Errors encountered and their fixes (importance: "critical")
- User preferences observed (importance: "high")

### Context Window Management
Use `memory_search` with targeted queries to pull relevant context without overwhelming the agent's context window. The `k` parameter controls how many results are returned.

## Trust Level

All three MCP tools (`memory_put`, `memory_get`, `memory_search`) are classified as **Safe** -- they do not perform destructive operations and do not require trust elevation.

## Rules Subsystem

The rules subpackage also exposes MCP tools for coding governance:
- `rules_list_modules` -- List all modules with coding rules
- `rules_get_module_rule` -- Get rules for a specific module
- `rules_get_applicable` -- Get applicable rules for a file path

## Dependencies

- No external dependencies for in-memory usage
- `codomyrmex.model_context_protocol` for MCP tool registration
- `codomyrmex.validation.schemas` for Result/ResultStatus interop (optional)

## Navigation

- **Source**: [src/codomyrmex/agentic_memory/](../../../../src/codomyrmex/agentic_memory/)
- **Extended README**: [README.md](readme.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Parent**: [All Modules](../README.md)

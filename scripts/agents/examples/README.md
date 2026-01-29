# Agent Examples

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Working examples demonstrating all Codomyrmex agent capabilities. Each script is self-contained and handles missing API keys gracefully.

## Quick Start

```bash
# Run a specific example
uv run python scripts/agents/examples/claude_example.py

# Run all examples
uv run python scripts/agents/run_all_agents.py
```

## Examples by Agent

### Claude Agent

| Script | Features |
|--------|----------|
| `claude_example.py` | Basic API usage, streaming |
| `claude_code_workflow.py` | Full Claude Code workflow |

### Gemini Agent

| Script | Features |
|--------|----------|
| `gemini_example.py` | Google AI code generation |

### Multi-Agent

| Script | Features |
|--------|----------|
| `multi_agent_workflow.py` | CodeEditor + Claude + Droid orchestration |
| `advanced_workflow.py` | Complex multi-stage pipelines |
| `agent_comparison.py` | Side-by-side agent comparison |

### Utilities

| Script | Features |
|--------|----------|
| `basic_usage.py` | Generic agent patterns |
| `agent_diagnostics.py` | Capability validation |
| `code_editor_example.py` | Code generation/refactoring |

## Navigation

- **Parent**: [agents/README.md](../README.md)
- **Claude Module**: [../../../src/codomyrmex/agents/claude/README.md](../../../src/codomyrmex/agents/claude/README.md)

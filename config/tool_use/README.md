# Tool Use Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Tool invocation framework for LLM tool use patterns. Provides tool registration, parameter validation, and execution tracking for AI agent tool calls.

## Configuration Options

The tool_use module operates with sensible defaults and does not require environment variable configuration. Tools are registered with schemas for parameter validation. Execution timeout and retry policies are set per-tool.

## PAI Integration

PAI agents interact with tool_use through direct Python imports. Tools are registered with schemas for parameter validation. Execution timeout and retry policies are set per-tool.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep tool_use

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/tool_use/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)

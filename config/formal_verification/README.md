# Formal Verification Configuration

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Z3 constraint solving and model checking. Provides a model builder with add/delete/replace/solve operations for formal verification of system properties.

## Configuration Options

The formal_verification module operates with sensible defaults and does not require environment variable configuration. Z3 solver timeout and memory limits can be configured per-solve operation. The model state is maintained in-memory.

## MCP Tools

This module exposes 6 MCP tool(s):

- `clear_model`
- `add_item`
- `delete_item`
- `replace_item`
- `get_model`
- `solve_model`

## PAI Integration

PAI agents invoke formal_verification tools through the MCP bridge. Z3 solver timeout and memory limits can be configured per-solve operation. The model state is maintained in-memory.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep formal_verification

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/formal_verification/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)

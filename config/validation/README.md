# Validation Configuration

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Schema validation, configuration validation, and validation summaries. Provides JSON schema validation, config file validation, and aggregate validation reporting.

## Configuration Options

The validation module operates with sensible defaults and does not require environment variable configuration. Validation schemas are registered per-module. Result and ResultStatus models provide standardized validation output format.

## MCP Tools

This module exposes 3 MCP tool(s):

- `validate_schema`
- `validate_config`
- `validation_summary`

## PAI Integration

PAI agents invoke validation tools through the MCP bridge. Validation schemas are registered per-module. Result and ResultStatus models provide standardized validation output format.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep validation

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/validation/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)

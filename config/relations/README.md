# Relations Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Relationship strength scoring between entities. Provides quantitative relationship analysis with configurable scoring models.

## Configuration Options

The relations module operates with sensible defaults and does not require environment variable configuration. Scoring model parameters and relationship type weights are configurable. Default scoring uses a weighted sum model.

## MCP Tools

This module exposes 1 MCP tool(s):

- `relations_score_strength`

## PAI Integration

PAI agents invoke relations tools through the MCP bridge. Scoring model parameters and relationship type weights are configurable. Default scoring uses a weighted sum model.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep relations

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/relations/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)

# Data Visualization Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Chart and dashboard generation supporting bar, line, scatter, heatmap, histogram, pie, area, and box plot chart types. Includes report generators, Mermaid diagrams, and HTML export.

## Configuration Options

The data_visualization module operates with sensible defaults and does not require environment variable configuration. Visual themes are configurable. Chart output formats include PNG, SVG, and HTML. Dashboard export produces self-contained HTML files.

## MCP Tools

This module exposes 2 MCP tool(s):

- `generate_chart`
- `export_dashboard`

## PAI Integration

PAI agents invoke data_visualization tools through the MCP bridge. Visual themes are configurable. Chart output formats include PNG, SVG, and HTML. Dashboard export produces self-contained HTML files.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep data_visualization

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/data_visualization/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)

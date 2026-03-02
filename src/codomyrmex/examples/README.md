# Examples Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

Reference implementations, sample outputs, and learning resources.

## Overview

Example files demonstrating Codomyrmex capabilities. No programmatic exports — access content directly as reference files.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **OBSERVE** | Reference examples for report formats and patterns | Direct Python import |
| **THINK** | Use examples as context for architectural decisions | Direct Python import |

PAI agents access this module via direct Python import through the MCP bridge. Agents load example JSON reports during OBSERVE phase to understand expected output formats before generating their own.

## Quick Reference

```bash
# View configuration validation example
cat src/codomyrmex/examples/config_validation_report.json

# View link check example
cat src/codomyrmex/examples/link_check_report.json
```

## Example Files

| File | Description |
|------|-------------|
| `config_validation_report.json` | Sample validation report structure |
| `link_check_report.json` | Sample link checker output |

## Using Examples

```python
import json
from pathlib import Path

# Load example report
examples_dir = Path(__file__).parent / "examples"
report = json.loads((examples_dir / "config_validation_report.json").read_text())

# Understand report structure
print(f"Report fields: {list(report.keys())}")
```

## For Developers

Use these examples to:

- Understand report formats before implementing
- Test parsing logic against known-good data
- Learn module integration patterns

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Documentation

- [Module Documentation](../../../docs/modules/examples/README.md)
- [Agent Guide](../../../docs/modules/examples/AGENTS.md)
- [Specification](../../../docs/modules/examples/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)

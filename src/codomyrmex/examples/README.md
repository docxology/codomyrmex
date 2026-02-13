# Examples Module

**Version**: v0.1.0 | **Status**: Active

Reference implementations, sample outputs, and learning resources.

## Overview

Example files demonstrating Codomyrmex capabilities. No programmatic exports — access content directly as reference files.

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

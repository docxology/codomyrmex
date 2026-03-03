# Agent Guidelines - Reporting

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

The `reporting` module provides reporting capabilities and MCP tools.

## Agent Instructions

1. Use `reporting_process` MCP tool for processing raw text data into reports.
2. Direct integration within Codomyrmex applications should use the `create_reporting()` factory to instantiate the `Reporting` class.

## Common Patterns

```python
from codomyrmex.reporting import create_reporting

def run_report(data):
    reporter = create_reporting()
    return reporter.process(data)
```

## Testing Patterns

```python
from codomyrmex.reporting.mcp_tools import reporting_process

def test_reporting():
    result = reporting_process("test data")
    assert result["status"] == "success"
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |

### Engineer Agent
**Use Cases**: Integrates reporting mechanisms via direct imports to support deeper insights in complex processing systems.

### Architect Agent
**Use Cases**: Analyzes the generated reports for overarching systematic patterns and validates configuration states.

### QATester Agent
**Use Cases**: Validates outputs returned by the reporting capability.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)

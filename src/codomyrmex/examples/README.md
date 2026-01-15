# Examples Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The Examples module contains sample configurations, validation reports, and reference implementations demonstrating proper usage of Codomyrmex functionality.

## Contents

| File | Description |
|------|-------------|
| `config_validation_report.json` | Sample configuration validation report |
| `link_check_report.json` | Sample documentation link check report |

## Purpose

This module serves as a reference for:

- **Configuration Examples**: Valid configuration file structures
- **Report Formats**: Expected output formats for validation tools
- **Integration Patterns**: How to use Codomyrmex modules together

## Usage

These files are primarily for reference and testing:

```python
import json
from pathlib import Path

# Load example report
examples_dir = Path("src/codomyrmex/examples")
report_path = examples_dir / "link_check_report.json"

with open(report_path) as f:
    sample_report = json.load(f)
    
# Use report structure as template for your own reports
```

## Report Structures

### Config Validation Report
```json
{
    "valid": true,
    "errors": [],
    "warnings": [],
    "checked_files": 42
}
```

### Link Check Report
```json
{
    "total_links": 150,
    "broken_links": [],
    "warnings": [],
    "checked_files": ["README.md", "docs/index.md"]
}
```

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

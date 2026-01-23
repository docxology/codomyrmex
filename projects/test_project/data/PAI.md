# Personal AI Infrastructure - data Context

**Directory**: `projects/test_project/data/`
**Status**: Active

## Overview

Data storage layer for test_project analysis pipeline.

## AI Context

### Directories

| Directory | Read | Write | Purpose |
| :--- | :---: | :---: | :--- |
| `input/` | ✓ | Rare | Source data |
| `processed/` | ✓ | ✓ | Pipeline outputs |

### Common Operations

1. **Load sample data**: Read `input/sample_data.json`
2. **Clear processed**: Delete contents of `processed/`
3. **Save results**: Write to `processed/`

## Navigation

- **Parent**: [../PAI.md](../PAI.md)

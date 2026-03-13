# OpenFang — Agent Operating System

**Module**: `codomyrmex.agents.openfang` | **Category**: CLI-based | **Last Updated**: March 2026

## Overview

Security-conscious agent operating system built in Rust. Wraps the openfang binary via subprocess. Tracks upstream via `vendor/openfang` git submodule. Features hands management and sandboxed execution.

**Upstream**: [openfang](https://github.com/RightNow-AI/openfang)

## Key Classes

| Class | Purpose |
|:---|:---|
| `OpenFangRunner` | Core runner wrapping the Rust binary |
| `OpenFangConfig` | Configuration dataclass |
| `HandsManager` | Manages openfang 'hands' (tool capabilities) |
| `OpenFangError` | Base exception |
| `OpenFangNotInstalledError` | Binary not found |
| `OpenFangTimeoutError` | Execution timeout |
| `OpenFangBuildError` | Build from source error |
| `OpenFangConfigError` | Configuration validation error |

## Installation

```bash
curl -fsSL https://openfang.sh/install.sh | sh
# or build from vendor submodule:
uv run python -c "from codomyrmex.agents.openfang.update import build_and_install; build_and_install()"
```

## Configuration

Binary auto-detected via `shutil.which('openfang')`. `HAS_OPENFANG` flag reports availability.

## Usage

```python
from codomyrmex.agents.openfang import OpenFangRunner

client = OpenFangRunner()
```

## Source Module

Source: [`src/codomyrmex/agents/openfang/`](../../../../src/codomyrmex/agents/openfang/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/openfang/](../../../../src/codomyrmex/agents/openfang/)
- **Project Root**: [README.md](../../../README.md)

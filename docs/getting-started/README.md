# Getting Started

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Everything you need to get up and running with Codomyrmex. From installation to your first agent deployment, these guides will have you productive in minutes.

## Contents

| File | Description |
|------|-------------|
| [**quickstart.md**](quickstart.md) | Get running in 5 minutes |
| [**setup.md**](setup.md) | Installation and environment configuration |
| [**GETTING_STARTED_WITH_AGENTS.md**](GETTING_STARTED_WITH_AGENTS.md) | Agent deployment, orchestration, MCP tools, skills |
| [**tutorials/**](tutorials/) | Step-by-step learning guides (8 tutorials) |
| [AGENTS.md](AGENTS.md) | Agent coordination guidelines |
| [SPEC.md](SPEC.md) | Getting started specification |
| [PAI.md](PAI.md) | Personal AI quick start |

## Learning Path

### 1. Quick Start (5 minutes)

Start with [quickstart.md](quickstart.md) to see Codomyrmex in action immediately.

### 2. Installation & Setup (15 minutes)

Follow [setup.md](setup.md) for complete environment setup with `uv`.

### 3. Agent Operations (20 minutes)

Read [GETTING_STARTED_WITH_AGENTS.md](GETTING_STARTED_WITH_AGENTS.md) for a comprehensive guide to agent modules, orchestration, MCP tools, skills, and event-driven communication.

### 4. Tutorials (30+ minutes)

Work through [tutorials/](tutorials/) for hands-on learning:

| Tutorial | Description |
|----------|-------------|
| [Creating a Module](tutorials/creating-a-module.md) | Build your own Codomyrmex module |
| [Connecting PAI](tutorials/connecting-pai.md) | Connect PAI to Codomyrmex |
| [Using MCP Tools](tutorials/using-mcp-tools.md) | Discover and invoke MCP tools |
| [Running Tests](tutorials/running-tests.md) | Test suite execution and Zero-Mock policy |

## Prerequisites

- **Python 3.10+**
- **uv** (recommended) or pip
- **Git**
- **Docker** (optional, for code execution sandbox)

## Quick Install

```bash
# Clone repository
git clone https://github.com/docxology/codomyrmex.git
cd codomyrmex

# Install with uv
uv sync

# Run diagnostics
uv run codomyrmex doctor --all
```

## Related Documentation

- [API Reference](../reference/api.md) — Complete API documentation
- [Examples](../examples/) — Code examples
- [Contributing](../project/contributing.md) — Contribution guidelines

## Navigation

- **Parent**: [docs/](../README.md)
- **Root**: [Project Root](../../README.md)

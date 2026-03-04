# Codomyrmex

**A Modular, Extensible Coding Workspace**

Welcome to the Codomyrmex documentation. This site covers architecture, tutorials, API reference, and development guides.

## Quick Start

```bash
# Clone and install
git clone https://github.com/docxology/codomyrmex.git
cd codomyrmex
uv sync

# Run diagnostics
uv run codomyrmex doctor --all

# Run tests
uv run pytest src/codomyrmex/tests/ -x -q
```

## Key Features

- **127+ modules** covering AI agents, code analysis, security, and more
- **545+ MCP tools** for AI agent integration
- **Zero-Mock testing** policy with real functional verification
- **PAI integration** via the Personal AI Algorithm bridge
- **CLI doctor** with `--fix` auto-repair mode

## Documentation Sections

| Section | Description |
|---------|-------------|
| [Getting Started](getting-started/README.md) | Installation, setup, and tutorials |
| [Architecture](architecture/README.md) | System design and module layout |
| [API Reference](api/README.md) | Module APIs and MCP tools |
| [Contributing](CONTRIBUTING.md) | How to contribute |
| [Changelog](CHANGELOG.md) | Release history |

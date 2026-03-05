# Codomyrmex

**A Modular, Extensible Coding Workspace** — v1.1.4

Welcome to the Codomyrmex documentation. This site covers architecture, tutorials, API reference, and development guides for a production-grade ecosystem with **127 deeply integrated modules**.

## Quick Start

```bash
# Clone and install
git clone https://github.com/docxology/codomyrmex.git
cd codomyrmex
uv sync

# Run tests
uv run pytest src/codomyrmex/tests/ -x -q

# Check code quality
uv run ruff check .              # ✅ 0 violations
uv run ty check src/             # 1,442 diagnostics (tracked)
uv build                         # ✅ builds clean
```

## Key Features

- **127 auto-discovered modules** covering AI agents, code analysis, security, cloud, and more
- **407 dynamic MCP tools** for AI agent integration
- **Zero-Mock testing** policy — all tests use real functional verification (779 pass)
- **PAI integration** — Personal AI bridge with 15-tab SPA dashboard
- **Ruff Zero** — 119,498 → 0 violations with 155 documented rule ignores

## Documentation Sections

| Section | Description |
|---------|-------------|
| [Getting Started](getting-started/quickstart.md) | Installation, setup, and tutorials |
| [Architecture](ARCHITECTURE.md) | System design and module layout |
| [Module Docs](modules/) | Per-module README, SPEC, AGENTS docs |
| [Reference](reference/) | API reference and troubleshooting |
| [Development](development/) | Contributing, testing, CI/CD |
| [PAI](pai/) | Personal AI infrastructure |
| [Security](security/) | Security policy and threat model |
| [Examples](examples/) | Code examples and patterns |

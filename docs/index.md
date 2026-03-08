# Codomyrmex

**A Modular, Extensible Coding Workspace** — v1.1.9

Welcome to the Codomyrmex documentation. This site covers architecture, tutorials, API reference, and development guides for a production-grade ecosystem with **130 deeply integrated modules**.

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
uv run ty check src/             # 971 diagnostics (< 1,000 target met)
uv build                         # ✅ builds clean

# Or use justfile
just test
just check
just build
```

## Key Features

- **130 auto-discovered modules** covering AI agents, code analysis, security, cloud, and more
- **474 dynamic MCP tools** for AI agent integration
- **Zero-Mock testing** policy — all tests use real functional verification (21,000+ collected)
- **PAI integration** — Personal AI bridge with 15-tab SPA dashboard + WebSocket push
- **Ruff Zero** — 119,498 → 0 violations with 155 documented rule ignores
- **ty diagnostics** — 1,446 → 971, target < 1,000 met
- **Coverage gate** — `fail_under=35`, actual ~35%

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

# Codomyrmex

**A Modular, Extensible Coding Workspace** — v1.2.7

Welcome to the Codomyrmex documentation. This site covers architecture, tutorials, API reference, and development guides for a production-grade ecosystem with **128 top-level modules** (see [reference/inventory.md](reference/inventory.md)) and **41 agent packages** under `src/codomyrmex/agents/` (documented under [agents/](agents/)).

## Quick Start

```bash
# Clone and install
git clone https://github.com/docxology/codomyrmex.git
cd codomyrmex
uv sync

# Run tests
uv run pytest src/codomyrmex/tests/ -x -q

# Check code quality
uv run ruff check src/
uv run ty check src/
uv build

# Or use justfile
just test
just check
just build
```

## Key Features

- **128 top-level modules** under `src/codomyrmex/` — AI agents, code analysis, security, cloud, and more ([inventory](reference/inventory.md))
- **600** production `@mcp_tool` decorators (see [reference/inventory.md](reference/inventory.md); refresh via `uv run python scripts/doc_inventory.py`)
- **41 agent packages** — Claude, Gemini, Jules, Hermes, Codex, and 36 more (see [agents/](agents/))
- **Zero-Mock testing** — all tests use real functional verification (**34,320** tests collected with `uv run pytest --collect-only -q --no-cov`; see [inventory](reference/inventory.md))
- **PAI integration** — Personal AI bridge with 15-tab SPA dashboard + WebSocket push
- **Lint / types** — run `uv run ruff check src/` and `uv run ty check src/` for current output; thresholds live in `pyproject.toml`
- **Coverage gate** — configured in `pyproject.toml`; run `uv run pytest --cov=src/codomyrmex` for measured coverage

## Documentation Sections

| Section | Description |
|:---|:---|
| [Getting Started](getting-started/quickstart.md) | Installation, setup, and tutorials |
| [Architecture](ARCHITECTURE.md) | System design and module layout |
| [Agent Integrations](agents/) | 41 agent packages; Hermes includes [skill registry & MCP preload](agents/hermes/skills.md) |
| [Module Docs](modules/) | Per-module README, SPEC, AGENTS docs (128 top-level packages) |
| [Reference](reference/) | API reference, CLI, changelog, troubleshooting |
| [Development](development/) | Contributing, testing, CI/CD, uv usage |
| [PAI](pai/) | Personal AI infrastructure and dashboard |
| [Security](security/) | Security policy, threat model, trust governance |
| [Integration](integration/) | CI/CD, cloud, database, monitoring patterns |
| [Project Orchestration](project_orchestration/) | Workflow coordination and dispatch |
| [AGI Theory](agi/) | Theoretical foundations and emergence models |
| [Bio](bio/) | Biological inspiration — myrmecology, swarm intelligence |
| [Cognitive](cognitive/) | Active inference, cognitive modeling |
| [Examples](examples/) | Code examples and tutorials |
| [Skills](skills/) | Agent skill lifecycle and marketplace |

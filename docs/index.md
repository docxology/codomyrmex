# Codomyrmex

**A Modular, Extensible Coding Workspace** — v1.2.2

Welcome to the Codomyrmex documentation. This site covers architecture, tutorials, API reference, and development guides for a production-grade ecosystem with **129 deeply integrated modules** and **38 AI agent integrations**.

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

- **129 auto-discovered modules** covering AI agents, code analysis, security, cloud, and more
- **474 dynamic MCP tools** for AI agent integration
- **38 AI agent integrations** — Claude, Gemini, Jules, Hermes, Codex, and 33 more
- **Zero-Mock testing** policy — all tests use real functional verification (21,000+ collected)
- **PAI integration** — Personal AI bridge with 15-tab SPA dashboard + WebSocket push
- **Ruff Zero** — 119,498 → 0 violations with 155 documented rule ignores
- **ty diagnostics** — 1,446 → 971, target < 1,000 met
- **Coverage gate** — `fail_under=35`, actual ~35%

## Documentation Sections

| Section | Description |
|:---|:---|
| [Getting Started](getting-started/quickstart.md) | Installation, setup, and tutorials |
| [Architecture](ARCHITECTURE.md) | System design and module layout |
| [Agent Integrations](agents/) | 38 AI agent frameworks with deep-dive Hermes docs |
| [Module Docs](modules/) | Per-module README, SPEC, AGENTS docs (126 modules) |
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

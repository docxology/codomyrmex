<p align="center">
  <h1 align="center">🐜 Codomyrmex</h1>
  <p align="center">
    <strong>A modular, AI-native coding workspace with 127 composable modules and 424 MCP tools</strong>
  </p>
</p>

<p align="center">
  <a href="https://github.com/docxology/codomyrmex/releases/tag/v1.1.0"><img src="https://img.shields.io/badge/release-v1.1.0-blueviolet?style=flat-square" alt="Release"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-≥3.10-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/docxology/codomyrmex/actions/workflows/ci.yml"><img src="https://github.com/docxology/codomyrmex/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/docxology/codomyrmex/actions/workflows/security.yml"><img src="https://github.com/docxology/codomyrmex/actions/workflows/security.yml/badge.svg" alt="Security"></a>
  <a href="https://github.com/docxology/codomyrmex"><img src="https://img.shields.io/badge/tests-21%2C000%2B-brightgreen?style=flat-square" alt="Tests"></a>
  <a href="https://github.com/docxology/codomyrmex"><img src="https://img.shields.io/badge/MCP_tools-424-orange?style=flat-square" alt="MCP Tools"></a>
</p>

<p align="center">
  <a href="docs/getting-started/quickstart.md">Quick Start</a> •
  <a href="docs/getting-started/GETTING_STARTED_WITH_AGENTS.md">Agent Guide</a> •
  <a href="docs/">Documentation</a> •
  <a href="CONTRIBUTING.md">Contributing</a> •
  <a href="https://github.com/docxology/codomyrmex/releases/tag/v1.1.0">v1.1.0 Release</a>
</p>

---

## What is Codomyrmex?

Codomyrmex is a **modular development platform** that brings together **127 specialized modules** for AI-assisted development, code analysis, orchestration, security, and documentation. Every module is self-contained, zero-mock tested, and composable — use what you need.

### Why Codomyrmex?

| | |
|---|---|
| 🧩 **127 Modules** | Self-contained, composable units with clear interfaces |
| 🤖 **424 MCP Tools** | AI agents invoke tools via Model Context Protocol |
| 🧪 **21,000+ Tests** | Zero-mock policy — every test exercises real code |
| 🔒 **Security First** | Secret scanning, SBOM generation, detect-secrets integration |
| 🎛️ **Multi-Agent Orchestration** | Claude, Gemini, GPT, and 10+ agent providers |
| 📦 **PyPI Ready** | `hatch build` + `twine check` verified |

## Quick Start

```bash
# Clone & install
git clone https://github.com/docxology/codomyrmex.git
cd codomyrmex
uv sync

# Verify everything works
uv run codomyrmex doctor --all

# Run the test suite
uv run pytest src/codomyrmex/tests/ -x -q
```

> **New here?** Start with the [Quick Start Guide](docs/getting-started/quickstart.md) or dive into [Agent Operations](docs/getting-started/GETTING_STARTED_WITH_AGENTS.md).

## Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                  User / IDE / CLI                       │
├─────────────────────────────────────────────────────────┤
│              Agent Orchestrator                         │
│   ┌───────┬───────┬──────┬───────┬───────┬──────────┐   │
│   │Claude │Gemini │ GPT  │Droid  │Aider  │Antigrav  │   │
│   └───┬───┴───┬───┴──┬───┴───┬───┴───┬───┴────┬─────┘   │
│       └───────┴──────┴───────┴───────┴────────┘          │
│          PAI Trust Gateway · MCP Bridge                  │
│          EventBus · Skills · Memory                      │
├─────────────────────────────────────────────────────────┤
│  coding │ security │ llm │ orchestrator │ telemetry     │
│  events │ search   │ api │ docs_gen     │ testing       │
└─────────────────────────────────────────────────────────┘
```

## Core Modules

| Layer | Key Modules |
|:------|:------------|
| **Foundation** | [`logging_monitoring`](src/codomyrmex/logging_monitoring/) · [`environment_setup`](src/codomyrmex/environment_setup/) · [`model_context_protocol`](src/codomyrmex/model_context_protocol/) · [`events`](src/codomyrmex/events/) |
| **Agents** | [`agents/`](src/codomyrmex/agents/) (13 providers) · [`ide/`](src/codomyrmex/ide/) · [`skills/`](src/codomyrmex/skills/) · [`agentic_memory/`](src/codomyrmex/agentic_memory/) |
| **Core** | [`coding`](src/codomyrmex/coding/) · [`llm`](src/codomyrmex/llm/) · [`security`](src/codomyrmex/security/) · [`git_operations`](src/codomyrmex/git_operations/) · [`orchestrator`](src/codomyrmex/orchestrator/) |
| **Infrastructure** | [`api`](src/codomyrmex/api/) · [`ci_cd_automation`](src/codomyrmex/ci_cd_automation/) · [`containerization`](src/codomyrmex/containerization/) · [`telemetry`](src/codomyrmex/telemetry/) |
| **Specialized** | [`spatial`](src/codomyrmex/spatial/) · [`cerebrum`](src/codomyrmex/cerebrum/) · [`quantum`](src/codomyrmex/quantum/) · [`graph_rag`](src/codomyrmex/graph_rag/) · [`meme`](src/codomyrmex/meme/) |

## PAI Integration

Codomyrmex is the **toolbox** for the [Personal AI Infrastructure](https://github.com/danielmiessler/Personal_AI_Infrastructure) (PAI). Agents invoke capabilities via MCP during every phase of The Algorithm:

| Phase | Modules | Purpose |
|-------|---------|---------|
| **Observe** | `system_discovery`, `search` | Scan environment and codebase |
| **Think** | `cerebrum`, `agents/core` | Reasoning and analysis |
| **Plan** | `orchestrator`, `formal_verification` | Design workflows |
| **Build** | `agents`, `coding` | Write and edit code |
| **Execute** | `agents` (13 providers), `containerization` | Run code in sandboxes |
| **Verify** | `static_analysis`, `security`, `validation` | Test and validate |
| **Learn** | `agentic_memory`, `telemetry` | Store insights |

**MCP Bridge**: Dynamic tools across 127 auto-discovered modules  
**Trust model**: `UNTRUSTED` → `VERIFIED` → `TRUSTED`  
**Deep dive**: [`PAI.md`](PAI.md) · [`docs/pai/`](docs/pai/)

## CLI

```bash
codomyrmex doctor                # Environment diagnostics
codomyrmex doctor --fix          # Auto-fix common issues
codomyrmex doctor --all --json   # Full check, JSON output
codomyrmex modules               # List available modules
codomyrmex status                # System status dashboard
```

## Development

```bash
# Tests
uv run pytest                                    # Full suite
uv run pytest -m integration                     # Integration only
uv run pytest --cov=src/codomyrmex               # With coverage

# Quality
uv run ruff check src/                           # Lint (0 violations ✅)
uv run mypy src/                                 # Type check
uv run hatch build && uv run twine check dist/*  # Build validation

# Mutation testing
uv run mutmut run                                # 6-file mutation suite
```

## Documentation

| Section | Link |
|---------|------|
| Quick Start | [quickstart.md](docs/getting-started/quickstart.md) |
| Setup Guide | [setup.md](docs/getting-started/setup.md) |
| Agent Operations | [GETTING_STARTED_WITH_AGENTS.md](docs/getting-started/GETTING_STARTED_WITH_AGENTS.md) |
| Tutorials (8) | [tutorials/](docs/getting-started/tutorials/) |
| Architecture | [architecture.md](docs/project/architecture.md) |
| Testing Strategy | [testing-strategy.md](docs/development/testing-strategy.md) |
| API Reference | [api.md](docs/reference/api.md) |
| Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) |

## Metrics

| Metric | Value |
|--------|-------|
| Modules | **127** |
| MCP tools | **424** dynamically discovered |
| Test suite | **21,000+** tests |
| Coverage | ~32% (gate: 31%) |
| `@mcp_tool` decorators | **545** |
| Ruff violations | **0** |
| PAI skills | **81** installed |
| RASP docs compliance | **127/127** |
| Python compatibility | 3.10 – 3.14 |

## Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for standards, workflow, and testing requirements.

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting and security policies. Automated secret scanning via `detect-secrets` pre-commit hook.

## License

MIT License — see [LICENSE](LICENSE) for details.

Copyright © 2025–2026 The Codomyrmex Contributors ([@docxology](https://github.com/docxology))

---

<p align="center">
  <sub>Built with modularity, zero-mock testing, and AI-native design.</sub>
</p>

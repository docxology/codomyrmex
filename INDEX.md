# Codomyrmex Project Index

**Version**: v1.2.7 | **Status**: Active | **Last Updated**: April 2026

> [!TIP]
> Master index for the Codomyrmex project. Use this as the entry point for navigating the entire repository.

## Quick Access

| What You Need | Where to Go |
|:--------------|:------------|
| Run the CLI | `codomyrmex --help` → [cli/](src/codomyrmex/cli/) |
| Understand PAI integration | [PAI.md](PAI.md) — algorithm phase ↔ module mapping |
| Browse all 128 top-level modules | [src/codomyrmex/INDEX.md](src/codomyrmex/INDEX.md) — full module catalog by layer |
| MCP tool reference | [docs/pai/tools-reference.md](docs/pai/tools-reference.md) — **600** production `@mcp_tool` lines ([inventory](docs/reference/inventory.md)) |
| Check system health | `codomyrmex status` or `codomyrmex check` |
| Run tests | `uv run pytest` |
| Install dependencies | `uv sync` |
| Trust PAI tools | `codomyrmex quick run /codomyrmexTrust` |

## System Status Snapshot

| Metric | Value | Source |
|:-------|:------|:-------|
| Top-level packages | 128 | [docs/reference/inventory.md](docs/reference/inventory.md) |
| `@mcp_tool` decorators (production) | 600 | `uv run python scripts/doc_inventory.py` |
| `mcp_tools.py` files (non-test) | 149 | [docs/reference/inventory.md](docs/reference/inventory.md) |
| MCP resources | 3 | [docs/pai/tools-reference.md](docs/pai/tools-reference.md) |
| MCP prompts | 10 | [docs/pai/tools-reference.md](docs/pai/tools-reference.md) |
| Tests collected | 34,593 | `uv run pytest --collect-only -q --no-cov` |
| GitHub Actions workflows | 37 | `.github/workflows/*.yml` (see `uv run python scripts/doc_inventory.py`) |
| RASP doc coverage | 100% (128/128) | [AGENTS.md](AGENTS.md) |
| Version | v1.2.7 | [pyproject.toml](pyproject.toml) |

## Module Layer Browser

| Layer | Count | Key Modules | Entry Point |
|:------|:------|:-----------|:-----------|
| **Foundation** | 6 | `logging_monitoring`, `model_context_protocol`, `environment_setup`, `terminal_interface` | [Foundation →](src/codomyrmex/logging_monitoring/) |
| **Core** | 15 | `agents`, `git_operations`, `coding`, `search`, `llm`, `static_analysis`, `performance` | [Core →](src/codomyrmex/agents/) |
| **Service** | 10 | `ci_cd_automation`, `orchestrator`, `api`, `cloud`, `documentation`, `containerization` | [Service →](src/codomyrmex/ci_cd_automation/) |
| **Specialized** | 58 | `agentic_memory`, `formal_verification`, `collaboration`, `crypto`, `events`, `release` | [Specialized →](src/codomyrmex/agentic_memory/) |

Full module catalog with layer assignments: [src/codomyrmex/INDEX.md](src/codomyrmex/INDEX.md)

## Project Structure

### Key Documentation

| Document | Purpose |
| :--- | :--- |
| [README.md](README.md) | Project overview, installation, quickstart |
| [SPEC.md](SPEC.md) | Project-level functional specification |
| [AGENTS.md](AGENTS.md) | Agent coordination & capabilities |
| [PAI.md](PAI.md) | Personal AI Infrastructure bridge |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [TODO.md](TODO.md) | Future features & improvements |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |
| [SECURITY.md](SECURITY.md) | Security policy |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community standards |
| [CLAUDE.md](CLAUDE.md) | Claude Code integration notes |

### Source Code

| Directory | Description |
| :--- | :--- |
| [src/](src/INDEX.md) | Source root — namespace package |
| [src/codomyrmex/](src/codomyrmex/INDEX.md) | Main package — **128 top-level modules** across 4 layers |

### Infrastructure

| Directory | Description |
| :--- | :--- |
| [config/](config/) | Configuration files (YAML, TOML) |
| [docs/](docs/) | Generated & authored documentation |
| [scripts/](scripts/) | Utility & automation scripts |
| [.github/](.github/) | GitHub Actions CI/CD workflows |

### Development

| Directory | Description |
| :--- | :--- |
| [projects/](projects/) | Sub-projects & reference implementations |
| [plugin_system](docs/modules/plugin_system/README.md) | Plugin registry and loading (`src/codomyrmex/plugin_system`) |
| [examples/](examples/) | Top-level examples |

### Build & Test

| File | Purpose |
| :--- | :--- |
| [pyproject.toml](pyproject.toml) | Python project config (uv/pip), pytest and coverage (`[tool.pytest.ini_options]`, `[tool.coverage.*]`) |
| [Makefile](Makefile) | Primary dev tasks (`make test`, `make lint`, …) |
| [justfile](justfile) | Optional [`just`](https://github.com/casey/just) recipes mirroring common Makefile targets |
| [index.html](index.html) | Root redirect to `/output/website/index.html` for static hosting / GitHub Pages entry |
| [uv.lock](uv.lock) | Dependency lock file |

## Index Hierarchy

```
INDEX.md                           ← You are here
├── src/INDEX.md                   ← Source directory index
│   └── src/codomyrmex/INDEX.md    ← 128-module catalog by layer
└── docs/                          ← Documentation site
```

## Navigation

- **📂 Source Index**: [src/INDEX.md](src/INDEX.md)
- **📦 Package Index**: [src/codomyrmex/INDEX.md](src/codomyrmex/INDEX.md)
- **📖 README**: [README.md](README.md)
- **🤖 PAI Bridge**: [PAI.md](PAI.md)

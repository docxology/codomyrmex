# Codomyrmex Project Index

**Version**: v1.0.3-dev | **Status**: Active | **Last Updated**: February 2026

> [!TIP]
> Master index for the Codomyrmex project. Use this as the entry point for navigating the entire repository.

## Quick Access

| What You Need | Where to Go |
|:--------------|:------------|
| Run the CLI | `codomyrmex --help` → [cli/](src/codomyrmex/cli/) |
| Understand PAI integration | [PAI.md](PAI.md) — algorithm phase ↔ module mapping |
| Browse all 86 modules | [src/codomyrmex/INDEX.md](src/codomyrmex/INDEX.md) — full module catalog by layer |
| MCP tool reference | [docs/pai/tools-reference.md](docs/pai/tools-reference.md) — all 167 tools |
| Check system health | `codomyrmex status` or `codomyrmex check` |
| Run tests | `uv run pytest` |
| Install dependencies | `uv sync` |
| Trust PAI tools | `codomyrmex quick run /codomyrmexTrust` |

## System Status Snapshot

| Metric | Value | Source |
|:-------|:------|:-------|
| Python modules | 86 loaded (6 more need optional SDK deps) | [src/codomyrmex/](src/codomyrmex/) |
| MCP tools | 167 total (163 safe + 4 destructive) | [docs/pai/tools-reference.md](docs/pai/tools-reference.md) |
| Auto-discovered modules | 32 (via `@mcp_tool` decorator) | [src/codomyrmex/agents/pai/mcp_bridge.py](src/codomyrmex/agents/pai/mcp_bridge.py) |
| MCP resources | 3 | [docs/pai/tools-reference.md](docs/pai/tools-reference.md) |
| MCP prompts | 10 | [docs/pai/tools-reference.md](docs/pai/tools-reference.md) |
| Tests passing | 413+ (49 collection errors from optional SDK deps) | `uv run pytest` |
| RASP doc coverage | 100% (86/86 modules) | [AGENTS.md](AGENTS.md) |
| Version | v1.0.3-dev | [pyproject.toml](pyproject.toml) |

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
| [TO-DO.md](TO-DO.md) | Future features & improvements |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |
| [SECURITY.md](SECURITY.md) | Security policy |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community standards |
| [CLAUDE.md](CLAUDE.md) | Claude Code integration notes |

### Source Code

| Directory | Description |
| :--- | :--- |
| [src/](src/INDEX.md) | Source root — namespace package |
| [src/codomyrmex/](src/codomyrmex/INDEX.md) | Main package — **86 modules** across 4 layers |

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
| [plugins/](plugins/) | Plugin ecosystem |
| [examples/](examples/) | Top-level examples |
| [cursorrules/](cursorrules/) | Agent rule documentation |

### Build & Test

| File | Purpose |
| :--- | :--- |
| [pyproject.toml](pyproject.toml) | Python project config (uv/pip) |
| [Makefile](Makefile) | Common dev commands |
| [pytest.ini](pytest.ini) | Test configuration |
| [uv.lock](uv.lock) | Dependency lock file |

## Index Hierarchy

```
INDEX.md                           ← You are here
├── src/INDEX.md                   ← Source directory index
│   └── src/codomyrmex/INDEX.md    ← 86-module catalog by layer
└── docs/                          ← Documentation site
```

## Navigation

- **📂 Source Index**: [src/INDEX.md](src/INDEX.md)
- **📦 Package Index**: [src/codomyrmex/INDEX.md](src/codomyrmex/INDEX.md)
- **📖 README**: [README.md](README.md)
- **🤖 PAI Bridge**: [PAI.md](PAI.md)

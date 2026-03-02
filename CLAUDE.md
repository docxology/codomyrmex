---
scope: project
---

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Development Commands

```bash
# Install dependencies (uv recommended)
uv sync

# Install with optional module dependencies
uv sync --extra <module-name>    # e.g., uv sync --extra spatial
uv sync --all-extras             # Install all optional dependencies

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/codomyrmex --cov-report=html

# Run specific test file or module
uv run pytest src/codomyrmex/tests/unit/<module>/test_<module>.py
uv run pytest -k "test_name"     # Run tests matching pattern

# Code formatting and linting
uv run black src/
uv run ruff check src/
uv run mypy src/

# CLI usage
codomyrmex --help
codomyrmex check                 # Verify environment setup
codomyrmex modules               # List available modules
codomyrmex status                # System status dashboard
codomyrmex shell                 # Interactive shell
codomyrmex workflow list         # List workflows
codomyrmex project list          # List projects
codomyrmex ai generate           # AI code generation
codomyrmex analyze <path>        # Code analysis
codomyrmex build <path>          # Project build
codomyrmex test <module>         # Run module tests
codomyrmex fpf fetch <url>       # FPF fetch/parse/export
codomyrmex skills list           # Skill management
```

## Architecture Overview

Codomyrmex is a modular development platform with 88 specialized modules organized in a **layered architecture**:

### Layer Hierarchy (dependencies flow upward only)

1. **Foundation Layer** - Core infrastructure used by all modules:
   - `logging_monitoring` - Centralized structured logging
   - `environment_setup` - Environment validation, dependency checking
   - `model_context_protocol` - Standardized LLM communication interfaces
   - `terminal_interface` - Rich terminal output and formatting

2. **Core Layer** - Primary capabilities:
   - `agents` - AI agent framework integrations
   - `static_analysis` - Code quality, linting, security scanning (in `coding/static_analysis/`)
   - `coding` - Code execution sandbox and review
   - `llm` - LLM infrastructure (Ollama, providers)
   - `pattern_matching` - Code pattern recognition (in `coding/pattern_matching/`)
   - `git_operations` - Version control automation

3. **Service Layer** - Higher-level orchestration:
   - `ci_cd_automation` - Pipeline management (includes build automation)
   - `documentation` - Doc generation
   - `containerization` - Docker/K8s management
   - `orchestrator` - Workflow execution

4. **Application Layer** - User interfaces:
   - `cli` - Command-line interface (entry point: `src/codomyrmex/cli/core.py`)
   - `system_discovery` - Module discovery and health monitoring

### Module Structure

Each module is self-contained with standard structure:

- `__init__.py` - Module exports
- `README.md` - Module documentation
- `API_SPECIFICATION.md` - Programmatic interfaces
- `MCP_TOOL_SPECIFICATION.md` - Model Context Protocol tool definitions
- `tests/` - Module-specific tests (unit tests in `src/codomyrmex/tests/unit/<module>/`)

### Key Patterns

- **Model Context Protocol (MCP)**: Standardized interface for AI/LLM integration across modules
- **Upward dependencies only**: Higher layers depend on lower, preventing circular dependencies
- **Lazy module loading**: Modules load on-demand to reduce startup time
- **Auto-discovery**: Modules with an `mcp_tools.py` submodule using `@mcp_tool` decorators are automatically discovered and surfaced via the PAI MCP bridge — no manual registration needed. Currently 33 modules are auto-discovered.

### Extended Modules (auto-discovered via MCP)

Beyond the core layers above, these modules expose MCP tools via `@mcp_tool` decorators:

- `formal_verification` - Z3 constraint solving and model checking
- `containerization` - Docker build, scan, and runtime management
- `crypto` - Key generation, hashing, hash verification
- `events` - Event bus with emit, history, and type registry
- `search` - Full-text, fuzzy, and indexed search
- `config_management` - Get/set/validate configuration
- `cloud` - Cloud instance and S3 bucket management
- `cerebrum` - Case-based reasoning and knowledge retrieval
- `performance` - Benchmark comparison and regression detection
- `scrape` - HTML content extraction and text similarity
- `maintenance` - Health checks and task management
- `plugin_system` - Plugin discovery and dependency resolution
- `relations` - Relationship strength scoring
- `agents/core` - ThinkingAgent reasoning traces and depth control
- `agentic_memory` - Agent memory store, retrieve, and semantic search
- `calendar_integration` - Calendar event management and scheduling
- `data_visualization` - Chart/dashboard generation and HTML export
- `email` - AgentMail inbox/message/thread management and webhook registration
- `git_analysis` - Git history analysis, contributor stats, and commit pattern detection
- `logging_monitoring` - Centralized structured logging and monitoring integration
- `collaboration` - Multi-user session management and collaborative editing
- `documentation` - Documentation generation, linting, and publishing workflows
- `security` - Vulnerability scanning, secret detection, and security auditing
- `skills` - Skill discovery, listing, and invocation management
- `validation` - Schema validation, config validation, and validation summaries

## PAI Integration

Codomyrmex serves as the toolbox for the [PAI system](https://github.com/danielmiessler/PAI) (`~/.claude/skills/PAI/`). Key integration points:

- **Detection**: PAI is present when `~/.claude/skills/PAI/SKILL.md` exists
- **MCP Bridge**: `src/codomyrmex/agents/pai/mcp_bridge.py` exposes 20 static tools (17 core + 3 universal proxy) + auto-discovered module tools via `pkgutil` scan of all `mcp_tools.py` submodules; the Codomyrmex PAI Skill surfaces ~171 tools (167 safe + 4 destructive) across 33 auto-discovered modules, with 3 resources and 10 prompts
- **Trust Gateway**: `src/codomyrmex/agents/pai/trust_gateway.py` gates destructive tools (write, execute) behind explicit trust
- **Workflows**: `/codomyrmexVerify` audits capabilities; `/codomyrmexTrust` enables destructive tools
- **RASP Pattern**: Each module has `PAI.md` alongside `README.md`, `AGENTS.md`, `SPEC.md` — these describe AI capabilities the module offers
- **Bridge Doc**: [`/PAI.md`](PAI.md) is the authoritative document mapping the PAI Algorithm phases to codomyrmex modules
- **Agent Mapping**: PAI subagent types (Engineer, Architect, QATester) consume codomyrmex agent providers and tools — see [`src/codomyrmex/agents/PAI.md`](src/codomyrmex/agents/PAI.md)
- **Detailed Reference**: [`docs/pai/`](docs/pai/) — Architecture, tools, API, workflows for PAI-Codomyrmex integration

Key PAI system references (in `~/.claude/skills/PAI/`):

- `SKILL.md` — Algorithm CORE (v1.5.0)
- `PAIAGENTSYSTEM.md` — Agent types and delegation
- `SKILLSYSTEM.md` — Skill architecture
- `THEHOOKSYSTEM.md` — Hook event patterns

## Test Markers

Tests use pytest markers defined in `pytest.ini`:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Long-running tests
- `@pytest.mark.performance` - Performance and benchmarking tests
- `@pytest.mark.examples` - Example validation tests
- `@pytest.mark.network` - Tests requiring network
- `@pytest.mark.database` - Tests requiring database access
- `@pytest.mark.external` - Tests requiring external services
- `@pytest.mark.security` - Security-related tests
- `@pytest.mark.asyncio` - Asynchronous tests
- `@pytest.mark.crypto` - Cryptography tests
- `@pytest.mark.orchestrator` - Orchestrator/workflow tests

Run specific categories: `uv run pytest -m unit`

## Zero-Mock Policy

This project follows a strict zero-mock/stub/fallback/hardcoded policy:

- **No mocking**: Tests never use `unittest.mock`, `MagicMock`, `monkeypatch`, or `pytest-mock`. External dependencies use `@pytest.mark.skipif` guards.
- **No production stubs**: Production code never returns placeholder/fake data. Unimplemented features raise `NotImplementedError`.
- **No silent fallbacks**: Fallback patterns that silently degrade functionality are prohibited. Failures must be explicit.
- **No hardcoded values**: URLs, ports, and connection strings use `os.getenv()` with centralized defaults from `config_management.defaults`.
- **No legacy aliases**: Backward compatibility layers must have documented deprecation timelines or be removed.

## Hard-Right Execution Standard

Codomyrmex agents should bias toward the **hard right thing** over the easy option:

- Prefer real measurements, benchmarks, and full test runs over estimates or assumptions.
- Favour changes that are reversible, well-documented, and auditable, even if they take longer to implement.
- Never trade away correctness, safety, or clarity for short-term convenience or minor performance wins.

### Test Skip Policy

Use `@pytest.mark.skipif` for tests requiring: network access, API keys, or heavy SDKs not installed.
Never skip tests for core codomyrmex modules — use `uv sync --extra <module>` instead.
Pattern: skip at module level (not per-test) to keep collection fast.

## Dependency Management

All dependencies are managed in `pyproject.toml`:

- Core dependencies: `[project.dependencies]`
- Module-specific optional: `[project.optional-dependencies.<module>]`
- Development tools: `[dependency-groups.dev]`

Module-specific `requirements.txt` files are **deprecated** - do not modify them.

<!-- gitnexus:start -->
# GitNexus MCP

This project is indexed by GitNexus as **codomyrmex** (49675 symbols, 116932 relationships, 300 execution flows).

## Always Start Here

1. **Read `gitnexus://repo/{name}/context`** — codebase overview + check index freshness
2. **Match your task to a skill below** and **read that skill file**
3. **Follow the skill's workflow and checklist**

> If step 1 warns the index is stale, run `npx gitnexus analyze` in the terminal first.

## Skills

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->

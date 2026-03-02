# Contributing to Codomyrmex

**Version**: v1.0.5 | **Last Updated**: March 2026

Welcome! Codomyrmex is an 88-module Python development platform. This guide covers how to set up your environment, follow our quality standards, and submit changes.

---

## Table of Contents

1. [Development Setup](#development-setup)
2. [Code Style](#code-style)
3. [Testing Requirements](#testing-requirements)
4. [Documentation (RASP Pattern)](#documentation-rasp-pattern)
5. [Pull Request Process](#pull-request-process)
6. [Git Coordination Rules](#git-coordination-rules)
7. [AI Agent Guidelines](#ai-agent-guidelines)

---

## Development Setup

### Prerequisites

- Python 3.10+ (tested on 3.10–3.13)
- [uv](https://docs.astral.sh/uv/) for dependency management
- Git

### Install

```bash
# Clone the repository
git clone https://github.com/docxology/codomyrmex.git
cd codomyrmex

# Install all dependencies (recommended for development)
uv sync --all-extras

# Or install only core dependencies
uv sync

# Or install specific module dependencies
uv sync --extra spatial   # e.g., for the spatial module
```

### Verify Setup

```bash
# Check environment
uv run codomyrmex check

# Run the test suite
uv run pytest

# Start the dashboard
uv run python scripts/website/launch_dashboard.py --open
```

---

## Code Style

All code must pass formatting and linting before merging.

### Formatters

```bash
# Format code
uv run black src/

# Check imports
uv run ruff check src/ --select I

# Fix auto-fixable issues
uv run ruff check src/ --fix
```

### Linting

```bash
# Full lint check
uv run ruff check src/

# Type checking
uv run mypy src/
```

### Rules

- **Line length**: 88 characters (Black default)
- **Python target**: 3.11+
- **Import order**: isort-compatible (enforced by Ruff `I` rules)
- **No wildcard imports** in non-`__init__.py` files
- **Exception chaining**: Use `raise X from Y` (B904 enforced)
- **No `unittest.mock`**: Zero-Mock Policy enforced by Ruff `TID` rules

---

## Testing Requirements

### Running Tests

```bash
# Run all tests (coverage gate: 68%)
uv run pytest

# Run with coverage report
uv run pytest --cov=src/codomyrmex --cov-report=html

# Run specific module tests
uv run pytest src/codomyrmex/tests/unit/<module>/

# Run by marker
uv run pytest -m unit
uv run pytest -m "not slow and not network"
```

### Zero-Mock Policy

This project enforces a **strict zero-mock policy**:

- ❌ **No** `unittest.mock`, `MagicMock`, `monkeypatch`, `pytest-mock`
- ✅ Use `FakeLLMClient`, `ConcreteAgent`, `FailingAgent` — real implementations with fake data
- ✅ Use `@pytest.mark.skipif` for tests requiring network, API keys, or heavy SDKs

```python
# ✅ Correct: real implementation with test data
class FakeClient(BaseClient):
    def complete(self, prompt): return AgentResponse(content="test response")

# ❌ Wrong: mock
from unittest.mock import MagicMock
client = MagicMock()
```

### Coverage Gate

The current coverage gate is **68%** (enforced in CI). New modules must not drop coverage below this threshold. Target: increase to 70%+ with each sprint.

### Test Skip Policy

Use module-level skips (not per-test) for external dependencies:

```python
pytest.importorskip("boto3")  # skip entire file if boto3 unavailable

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="requires OPENAI_API_KEY")
def test_openai_integration(): ...
```

### Test Markers

| Marker | Usage |
|--------|-------|
| `@pytest.mark.unit` | Pure unit tests |
| `@pytest.mark.integration` | Integration tests |
| `@pytest.mark.slow` | Long-running (> 5s) |
| `@pytest.mark.network` | Requires network access |
| `@pytest.mark.external` | Requires external service |
| `@pytest.mark.asyncio` | Async tests |

---

## Documentation (RASP Pattern)

Every module must have four documentation files (**RASP** = README + AGENTS + SPEC + PAI):

| File | Purpose |
|------|---------|
| `README.md` | Human-readable overview, quick start, examples |
| `AGENTS.md` | AI agent guidance, PAI Agent Role Access Matrix |
| `SPEC.md` | Functional specification, data contracts, design constraints |
| `PAI.md` | PAI/MCP integration, Algorithm phase mapping, MCP tool table |

### Adding a New Module

1. Use the module scaffold tool:
   ```bash
   uv run codomyrmex modules create <module-name>
   ```
   or use the `ModuleBuilder` PAI skill.

2. Implement the RASP docs alongside the code.

3. If your module exposes tools to PAI agents, add `mcp_tools.py` with `@mcp_tool` decorators — these are auto-discovered.

4. Run RASP compliance check:
   ```bash
   uv run python -c "from codomyrmex.documentation import audit_rasp_compliance; print(audit_rasp_compliance('<module-name>'))"
   ```

### Version Header

All RASP files use this header format:

```markdown
**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026
```

---

## Pull Request Process

1. **Branch naming**: `feature/<description>`, `fix/<description>`, `docs/<description>`, `refactor/<description>`
2. **Commit messages**: Imperative mood, reference Sprint if applicable. Example: `feat(agents): add QwenClient provider integration`
3. **PR size**: Keep PRs focused. Prefer smaller, targeted changes over large omnibus PRs.
4. **CI must pass**: All checks (lint, type, test, coverage) must be green before merging.
5. **RASP docs**: Any new module or significant feature requires updated RASP documentation.
6. **No force-push to main**: Use feature branches and PRs.

### PR Template

Include in your PR description:
- **What**: Short description of the change
- **Why**: Motivation / problem solved
- **Testing**: How you verified it works
- **Docs**: Which RASP files were updated

---

## Git Coordination Rules

When multiple agents or developers work concurrently, coordinate to avoid `.git/index.lock` conflicts:

### Lock File Safety

```bash
# Check before any git write operation
ls .git/index.lock 2>/dev/null

# Clear stale lock (only if no git process is running)
ps aux | grep git   # confirm no active git processes
rm -f .git/index.lock
```

### Atomic Operations

Always stage and commit atomically to minimize lock window:

```bash
# ✅ Atomic: one command, one lock window
git add -A && git commit --no-verify -m "feat: description"

# ❌ Two separate operations (lock held twice)
git add -A
git commit -m "feat: description"
```

### Worktrees for Parallel Work

Use worktrees to isolate parallel development:

```bash
# Create a worktree (via PAI skill)
/codomyrmexWorktree

# Or manually
git worktree add .claude/worktrees/my-feature -b feature/my-feature

# Clean up stale worktrees
git worktree prune
```

### Large Files

GitHub rejects files > 100MB. Check before committing:

```bash
find . -not -path './.git/*' -size +50M
```

---

## AI Agent Guidelines

Codomyrmex is built by and for AI agents. When running as an AI agent:

1. **Read before edit**: Always use the `Read` tool before any `Edit`
2. **Zero-Mock Policy**: Never introduce mocks in tests — see [Testing Requirements](#testing-requirements)
3. **No silent fallbacks**: Failures must be explicit. Use `NotImplementedError` for unimplemented features.
4. **RASP compliance**: Any new module needs all 4 RASP files
5. **Trust model**: Use `/codomyrmexVerify` then `/codomyrmexTrust` for destructive operations
6. **MCP tools**: Use `@mcp_tool` decorator in `mcp_tools.py` for auto-discovery
7. **Agent commits**: Use `--no-verify` to skip pre-commit hooks (they take 20+ min on 900+ files)

### Agent-Specific Skip Pattern

```python
# At module level — fast collection, correct semantics
import pytest
import os
pytest.importorskip("anthropic")  # skip if anthropic not installed

@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="requires ANTHROPIC_API_KEY"
)
def test_claude_integration(): ...
```

---

## Questions?

- **Issues**: [GitHub Issues](https://github.com/docxology/codomyrmex/issues)
- **PAI Integration**: See [`PAI.md`](../PAI.md) and [`docs/pai/README.md`](../docs/pai/README.md)
- **Module docs**: `codomyrmex modules` or browse `src/codomyrmex/<module>/README.md`

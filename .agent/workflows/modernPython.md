---
description: Apply modern Python best practices using uv, ruff, ty. Based on Trail of Bits modern-python skill. Use when setting up projects, migrating from pip/Poetry/mypy, or configuring tooling.
---

# Modern Python (Trail of Bits)

Crossover workflow from `modern-python@trailofbits` Claude Code skill.

Read the full skill for complete reference:

```
view_file ~/.claude/plugins/cache/trailofbits/modern-python/1.5.0/skills/modern-python/SKILL.md
```

## Tool Stack

| Tool | Purpose | Replaces |
|------|---------|----------|
| **uv** | Package/dependency management | pip, virtualenv, pip-tools, pipx, pyenv |
| **ruff** | Linting AND formatting | flake8, black, isort, pyupgrade, pydocstyle |
| **ty** | Type checking | mypy, pyright (faster, Astral team) |
| **pytest** | Testing with coverage | unittest |
| **prek** | Pre-commit hooks | pre-commit (faster, Rust-native) |

## Anti-Patterns

| Avoid | Use Instead |
|-------|-------------|
| `uv pip install` | `uv add` and `uv sync` |
| Manual virtualenv activation | `uv run <cmd>` |
| Poetry | uv |
| requirements.txt | PEP 723 for scripts, pyproject.toml for projects |
| mypy / pyright | ty |
| `[project.optional-dependencies]` for dev tools | `[dependency-groups]` (PEP 735) |
| pre-commit | prek |

## Quick Start

```bash
uv init myproject && cd myproject
uv add requests rich
uv add --group dev pytest ruff ty
uv run pytest
uv run ruff check .
```

## Checklist

- [ ] Use `src/` layout
- [ ] `requires-python = ">=3.11"`
- [ ] ruff with `select = ["ALL"]` + explicit ignores
- [ ] ty for type checking
- [ ] Coverage minimum 80%+
- [ ] `[dependency-groups]` for dev tools
- [ ] `uv.lock` in version control

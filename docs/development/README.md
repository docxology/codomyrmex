# Development Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Guides for setting up and working in the Codomyrmex development environment. Covers environment configuration, testing strategies, documentation standards, and tooling.

## Contents

| File | Description |
|------|-------------|
| [**environment-setup.md**](environment-setup.md) | Complete development environment setup |
| [**testing-strategy.md**](testing-strategy.md) | Testing best practices and patterns |
| [**documentation.md**](documentation.md) | Documentation standards and guidelines |
| [**uv-usage-guide.md**](uv-usage-guide.md) | UV package manager usage guide |
| [AGENTS.md](AGENTS.md) | Agent coordination for development docs |
| [SPEC.md](SPEC.md) | Development documentation specification |
| [PAI.md](PAI.md) | Personal AI development considerations |

## Key Topics

### Environment Setup

- Python environment with `uv`
- Dependency management
- IDE configuration (VS Code, PyCharm)
- Git hooks and pre-commit

### Testing

- Unit testing with pytest
- Integration testing patterns
- Test coverage requirements (>80%)
- Test fixtures and data generators

### Documentation Standards

- RASP compliance (README, AGENTS, SPEC, PAI)
- Docstring conventions
- API documentation generation

## Quick Start

```bash
# Clone and setup
git clone https://github.com/docxology/codomyrmex.git
cd codomyrmex
uv sync

# Run tests
uv run pytest src/codomyrmex/tests/unit/ -v
```

## Related Documentation

- [Contributing](../project/contributing.md) - Contribution guidelines
- [Architecture](../project/architecture.md) - System design
- [Quick Start](../getting-started/quickstart.md) - User quick start

## Navigation

- **Parent**: [docs/](../README.md)
- **Root**: [Project Root](../../README.md)

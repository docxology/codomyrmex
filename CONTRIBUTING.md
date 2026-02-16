# Contributing to Codomyrmex

Thank you for your interest in contributing to Codomyrmex! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.10+
- [UV](https://github.com/astral-sh/uv) package manager
- Git

### Development Setup

```bash
# Clone the repository
git clone https://github.com/docxology/codomyrmex.git
cd codomyrmex

# Install dependencies with UV
uv sync --all-extras --dev

# Run tests to verify setup
uv run pytest
```

## Development Workflow

### Branching Strategy

- `main`: Stable production code
- `develop`: Integration branch for features
- `feature/*`: New features
- `fix/*`: Bug fixes
- `docs/*`: Documentation updates

### Making Changes

1. **Create a branch** from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines

3. **Run pre-commit checks**:

   ```bash
   uv run pre-commit run --all-files
   ```

4. **Run tests**:

   ```bash
   uv run pytest src/codomyrmex/tests/unit/ -v
   ```

5. **Commit your changes** with clear, descriptive messages:

   ```bash
   git commit -m "feat: add new feature description"
   ```

## Code Style

- **Python**: We follow PEP 8 with Black formatting
- **Linting**: Ruff for linting, Black for formatting
- **Type hints**: Required for all public functions
- **Docstrings**: Google-style docstrings for all modules, classes, and functions

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality. Install them with:

```bash
uv run pre-commit install
```

## Testing

- Write tests for all new features
- Maintain minimum 80% code coverage (target: ≥80%)
- Place unit tests in `src/codomyrmex/tests/unit/`
- Place integration tests in `src/codomyrmex/tests/integration/`

## Documentation

- Update relevant documentation when making changes
- Every module follows the **RASP pattern** — four standard docs that must stay in sync with code:
  - `README.md` — Module overview, key exports, quick start
  - `AGENTS.md` — AI agent coordination and operating contracts
  - `SPEC.md` — Functional specification and design rationale
  - `PAI.md` — PAI system integration and algorithm phase mapping
- Additionally, modules with programmatic APIs maintain `API_SPECIFICATION.md` and AI-callable tools maintain `MCP_TOOL_SPECIFICATION.md`
- See [Documentation Guide](docs/development/documentation.md) for detailed writing guidance

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new feature description
fix: resolve specific bug
docs: update module documentation
refactor: restructure without behavior change
test: add or update tests
chore: maintenance tasks
```

## Pull Requests

1. Ensure all tests pass
2. Update documentation as needed (RASP files for affected modules)
3. Add a clear PR description
4. Request review from maintainers

## Related Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Project overview and quick start |
| [SPEC.md](SPEC.md) | Functional specification and design principles |
| [AGENTS.md](AGENTS.md) | AI agent coordination and navigation |
| [SECURITY.md](SECURITY.md) | Security policies and vulnerability reporting |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community standards |
| [CHANGELOG.md](CHANGELOG.md) | Version history and release notes |
| [Testing Strategy](docs/development/testing-strategy.md) | Testing approach and best practices |
| [Environment Setup](docs/development/environment-setup.md) | Development environment configuration |

## Questions?

Open an issue for questions or discussions about contributing.

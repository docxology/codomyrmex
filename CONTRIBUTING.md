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
- Maintain minimum 70% code coverage
- Place unit tests in `src/codomyrmex/tests/unit/`
- Place integration tests in `src/codomyrmex/tests/integration/`

## Documentation

- Update relevant documentation when making changes
- Follow the AGENTS.md pattern for AI agent instructions
- Keep README files up to date

## Pull Requests

1. Ensure all tests pass
2. Update documentation as needed
3. Add a clear PR description
4. Request review from maintainers

## Questions?

Open an issue for questions or discussions about contributing.

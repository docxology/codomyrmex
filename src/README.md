# src

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Source code directory containing all Python packages and modules for the Codomyrmex platform. The main package `codomyrmex/` contains 91 specialized modules for AI-assisted development workflows.

## Directory Contents

| Directory                      | Description                                |
| ------------------------------ | ------------------------------------------ |
| [**codomyrmex/**](codomyrmex/) | Main Python package with 91 modules        |

### Key Files

- `__init__.py` – Package initialization
- `PAI.md` – Personal AI Infrastructure documentation
- `SPEC.md` – Technical specification
- `README.md` – This file

## Package Structure

```text
src/
├── codomyrmex/           # Main package (91 modules)
│   ├── agents/           # AI agent integrations
│   ├── llm/              # LLM infrastructure
│   ├── orchestrator/     # Workflow orchestration
│   ├── meme/             # Memetics & Info War
│   ├── coding/           # Code execution
│   ├── documentation/    # Doc generation
│   └── ...               # 91 modules total
```

## Usage

```python
# Import from main package
from codomyrmex.llm import LLMClient
from codomyrmex.orchestrator import WorkflowEngine
from codomyrmex.coding import CodeExecutor

# Run with uv
uv run python -c "from codomyrmex import __version__; print(__version__)"
```

## Development

```bash
# Install in development mode
uv pip install -e .

# Run tests
uv run pytest src/codomyrmex/tests/

# Type checking
uv run mypy src/codomyrmex/
```

## Navigation

- **Project Root**: [../README.md](../README.md)
- **Module Details**: [codomyrmex/README.md](codomyrmex/README.md)
- **Documentation**: [../docs/](../docs/)
- **Scripts**: [../scripts/](../scripts/)

# agents

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [ai_code_editing](ai_code_editing/README.md)
    - [claude](claude/README.md)
    - [codex](codex/README.md)
    - [droid](droid/README.md)
    - [gemini](gemini/README.md)
    - [generic](generic/README.md)
    - [jules](jules/README.md)
    - [opencode](opencode/README.md)
    - [tests](tests/README.md)
    - [theory](theory/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Integration with various agentic frameworks including Jules CLI, Claude API, OpenAI Codex, OpenCode CLI, and Gemini CLI. Includes theoretical foundations, generic utilities, and framework-specific implementations that integrate seamlessly with Codomyrmex modules. Provides unified interface for all agents through `AgentInterface` abstract base class.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `ai_code_editing/` – Subdirectory
- `claude/` – Subdirectory
- `codex/` – Subdirectory
- `config.py` – File
- `core.py` – File
- `droid/` – Subdirectory
- `exceptions.py` – File
- `gemini/` – Subdirectory
- `generic/` – Subdirectory
- `jules/` – Subdirectory
- `opencode/` – Subdirectory
- `tests/` – Subdirectory
- `theory/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.codomyrmex.agents import main_component

def example():
    
    print(f"Result: {result}")
```


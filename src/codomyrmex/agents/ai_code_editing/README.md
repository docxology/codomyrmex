# ai_code_editing

## Signposting
- **Parent**: [agents](../README.md)
- **Children**:
    - [docs](docs/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Semantic intelligence layer for AI-powered code generation, editing, and analysis. Abstracts complexity of interacting with various LLM providers (OpenAI, Anthropic, Google) to provide high-level code manipulation capabilities: generation, refactoring, analysis, and documentation. Provider-agnostic with unified prompting and standardized context.

## Directory Contents
- `API_SPECIFICATION.md` – File
- `CHANGELOG.md` – File
- `MCP_TOOL_SPECIFICATION.md` – File
- `PROMPT_ENGINEERING.md` – File
- `README.md` – File
- `SECURITY.md` – File
- `SPEC.md` – File
- `USAGE_EXAMPLES.md` – File
- `__init__.py` – File
- `ai_code_helpers.py` – File
- `claude_task_master.py` – File
- `docs/` – Subdirectory
- `droid_manager.py` – File
- `openai_codex.py` – File
- `prompt_composition.py` – File
- `requirements.txt` – File
- `tests/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [agents](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.agents.ai_code_editing import (
    generate_code_snippet,
    refactor_code_snippet,
    analyze_code_quality,
)

# Generate code
result = generate_code_snippet(
    language="python",
    description="Create a function to calculate fibonacci numbers",
    complexity="medium"
)
print(f"Generated code: {result.code}")

# Refactor code
refactored = refactor_code_snippet(
    code="def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)",
    improvements=["add memoization", "add type hints"]
)
print(f"Refactored: {refactored.code}")

# Analyze code quality
analysis = analyze_code_quality(
    code_path="src/my_module.py"
)
print(f"Quality score: {analysis.score}")
```


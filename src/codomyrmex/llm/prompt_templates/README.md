# prompt_templates

## Signposting
- **Parent**: [llm](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Prompt templates for LLM interactions including system templates, context templates, and task templates. Provides standardized prompt structures for consistent LLM interactions across the Codomyrmex platform.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `context_template.md` – File
- `system_template.md` – File
- `task_template.md` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [llm](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

Prompt templates are stored as markdown files and loaded when needed:

```python
from pathlib import Path
from codomyrmex.llm.prompt_templates import (
    load_system_template,
    load_context_template,
    load_task_template,
)

# Load templates
template_dir = Path(__file__).parent
system_prompt = load_system_template(template_dir / "system_template.md")
context_prompt = load_context_template(template_dir / "context_template.md")
task_prompt = load_task_template(template_dir / "task_template.md")

# Use templates in LLM interactions
full_prompt = f"{system_prompt}\n\n{context_prompt}\n\n{task_prompt}"
```


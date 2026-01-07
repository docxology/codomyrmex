# doc_templates

## Signposting
- **Parent**: [templates](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Documentation files and guides for doc_templates.

## Directory Contents
- `AGENTS.nested.template.md` – File
- `AGENTS.template.md` – File
- `README.md` – File
- `README.nested.template.md` – File
- `README.template.md` – File
- `SPEC.md` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [templates](../README.md)
- **Project Root**: [README](../../../../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
# Documentation templates for generating project documentation
# These templates are used by the DocumentationGenerator to create
# README.md, AGENTS.md, and SPEC.md files for projects and nested directories.

from codomyrmex.logistics.orchestration.project import DocumentationGenerator
from pathlib import Path

generator = DocumentationGenerator()
project_path = Path("my_project")
generator.generate_project_docs(project_path)
```


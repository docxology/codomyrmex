# templates

## Signposting
- **Parent**: [project](../README.md)
- **Children**:
    - [doc_templates](doc_templates/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Project orchestration templates for common project types. Provides pre-configured templates for AI analysis projects, data pipelines, web applications, and documentation templates. Enables rapid project setup with standardized configurations.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `ai_analysis.json` – File
- `data_pipeline.json` – File
- `doc_templates/` – Subdirectory
- `web_application.json` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [project](../README.md)
- **Project Root**: [README](../../../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.logistics.orchestration.project import ProjectManager, ProjectType
from pathlib import Path

# Load a project template
project_manager = ProjectManager()
template_path = Path(__file__).parent / "ai_analysis.json"

# Create a project from template
project = project_manager.create_project(
    name="my_ai_project",
    project_type=ProjectType.AI_ANALYSIS,
    template_path=template_path
)
```


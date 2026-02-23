# projects

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Project workspace and templates for Codomyrmex-powered development projects. This directory contains example projects, templates for new projects, and a reference implementation.

## Directory Contents

| Directory | Description |
|-----------|-------------|
| [**test_project/**](test_project/) | 100% Zero-Mock reference implementation demonstrating authentic, full Codomyrmex integration |

## Creating a New Project

1. Copy the `test_project/` template:

   ```bash
   cp -r projects/test_project projects/my_project
   ```

2. Update project configuration in `my_project/config/`

3. Customize the source code in `my_project/src/`

## Project Structure

A typical Codomyrmex project follows this structure:

```
my_project/
├── .codomyrmex/          # Codomyrmex-specific settings
├── config/               # Project configuration
│   ├── settings.yaml     # Main settings
│   └── workflows.yaml    # Workflow definitions
├── src/                  # Source code
├── data/                 # Data files
│   ├── raw/              # Raw input data
│   └── processed/        # Processed output
├── reports/              # Generated reports
└── README.md             # Project documentation
```

## Integration with Codomyrmex

Projects in this directory can leverage the full Codomyrmex ecosystem:

- **Orchestrator**: Define and run workflows
- **Documentation**: Auto-generate project docs
- **Static Analysis**: Code quality checking
- **LLM Integration**: AI-assisted development
- **Telemetry**: Monitoring and logging

## Companion Files

- [**AGENTS.md**](AGENTS.md) - Agent coordination
- [**SPEC.md**](SPEC.md) - Project specification
- [**PAI.md**](PAI.md) - Personal AI Infrastructure

## Navigation

- **Project Root**: [../README.md](../README.md)
- **Source Code**: [../src/codomyrmex/](../src/codomyrmex/)
- **Examples**: [../examples/](../examples/)

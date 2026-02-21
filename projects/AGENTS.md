# Codomyrmex Agents — projects

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Project workspace containing working projects that use Codomyrmex functionality. Includes templates and reference implementations for building new projects.

## Directory Structure

```text
projects/
├── test_project/        # Reference implementation project
│   ├── src/             # Project source code
│   ├── data/            # Input and processed data
│   ├── reports/         # Generated reports
│   ├── tests/           # Project-specific tests
│   └── config/          # Project configuration
└── (future projects)    # Additional project workspaces
```

## Active Components

| Component | Type | Description |
|-----------|------|-------------|
| `test_project/` | Project | 100% Zero-Mock Reference implementation |
| [README.md](README.md) | Doc | Directory overview |
| [SPEC.md](SPEC.md) | Doc | Functional specification |
| [PAI.md](PAI.md) | Doc | Personal AI considerations |

## Agent Guidelines

### Project Creation Standards

1. **Structure**: Follow test_project template structure
2. **RASP Compliance**: Each subdirectory needs README, AGENTS, SPEC, PAI
3. **Configuration**: Use `config/` for project-specific settings
4. **Documentation**: Document project purpose and usage

### Reference Implementation: test_project

`test_project/` demonstrates how to:

- Integrate Codomyrmex modules
- Structure project directories
- Configure workflows
- Generate reports and visualizations

### Creating New Projects

1. Copy `test_project/` as template
2. Rename and update `README.md`
3. Modify `config/` for your use case
4. Implement in `src/`
5. Add tests in `tests/`

## Project Capabilities

Projects can leverage all Codomyrmex modules:

| Capability | Module | Example |
|------------|--------|---------|
| Data visualization | `data_visualization` | Charts, plots |
| Code analysis | `static_analysis` | Quality reports |
| AI generation | `agents/ai_code_editing` | Code synthesis |
| Orchestration | `orchestrator` | Workflow automation |

## Operating Contracts

- Projects should not modify core Codomyrmex modules
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Keep project-specific code isolated in `src/`
- Document all project dependencies

## Navigation Links

- **📁 Parent**: [../README.md](../README.md) - Project root
- **📦 Source**: [../src/codomyrmex/](../src/codomyrmex/) - Available modules
- **📖 Docs**: [../docs/](../docs/) - Codomyrmex documentation
- **🎯 Test Project**: [test_project/README.md](test_project/README.md) - Reference project

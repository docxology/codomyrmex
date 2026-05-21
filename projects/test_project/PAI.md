# Personal AI Infrastructure - Test Project Context

**Directory**: `projects/test_project/`
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `test_project` is a comprehensive 100% "Zero-Mock" reference implementation demonstrating maximal usage of codomyrmex functionalities. It serves as both a validation suite verifying authentic sub-module outputs and a functional template for new Codomyrmex-based projects.

## AI Context

When working with this project:

### 1. Purpose Recognition

This project demonstrates the **complete Codomyrmex integration pattern** enforcing explicit Zero-Mock policies:

- Foundation layer: `logging_monitoring`, `config_management`, `terminal_interface`
- Core layer: `static_analysis`, `data_visualization`, `pattern_matching`
- Service layer: `documentation`, `orchestrator`
- Utility layer: `serialization`, `validation`, `events`

### 2. Directory Structure

```text
test_project/
├── .codomyrmex/     # Project-specific configuration
├── config/          # YAML configuration files
├── data/            # Input and processed data
│   ├── input/       # Sample input data
│   └── processed/   # Analysis outputs
├── reports/         # Generated reports and visualizations
│   ├── templates/   # Report templates
│   └── output/      # Generated outputs
├── src/                  # Python source modules (11 files)
│   ├── main.py           # Entry point
│   ├── analyzer.py       # Static analysis integration
│   ├── visualizer.py     # Data visualization
│   ├── reporter.py       # Documentation generation
│   ├── pipeline.py       # Orchestration workflows
│   ├── agent_brain.py    # agents + agentic_memory
│   ├── git_workflow.py   # git_operations + git_analysis
│   ├── knowledge_search.py # search + scrape + formal_verification
│   ├── security_audit.py # security + crypto + system_discovery
│   ├── mcp_explorer.py   # model_context_protocol + skills + plugin_system
│   └── llm_inference.py  # llm + collaboration
└── tests/                # Test suite (zero-mock integration tests)
```

### 3. Key Patterns

- **DAG-based Pipeline**: `pipeline.py` demonstrates workflow orchestration with dependency management
- **Dataclass Models**: All data structures use `@dataclass` for type safety
- **Event-driven**: Pipeline steps emit events for monitoring
- **Multi-format Output**: Reports generate HTML, JSON, and Markdown

### 4. Agent Operating Guidelines

When modifying this project:

1. **Preserve Templates**: Changes should maintain the templated, demonstration nature
2. **Use Real Methods**: No mocks - always use functional codomyrmex integrations
3. **Maintain Documentation**: Update all Quadruple Play files when making changes
4. **Follow Layers**: Respect the codomyrmex layer architecture for imports

### 5. Common Tasks

| Task | Entry Point | Module |
| :--- | :--- | :--- |
| Run analysis | `run_demo.py` | `src/main.py` |
| Execute pipeline | `run_pipeline()` | `src/pipeline.py` |
| Generate report | `ReportGenerator.generate()` | `src/reporter.py` |
| Create dashboard | `DataVisualizer.create_dashboard()` | `src/visualizer.py` |

## Integration Points

- **Codomyrmex Source**: [../../src/codomyrmex/](../../src/codomyrmex/)
- **Global Config**: [../../config/](../../config/)
- **Scripts**: [../../scripts/](../../scripts/)

## Navigation

- **Parent**: [../README.md](../README.md)
- **Specification**: [SPEC.md](SPEC.md)
- **Agent Guide**: [AGENTS.md](AGENTS.md)
- **Human Docs**: [README.md](README.md)

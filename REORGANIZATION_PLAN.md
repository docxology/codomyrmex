# Examples to Scripts Reorganization Plan

## Overview
This document outlines the plan to reorganize the `examples/` directory by moving all content into the `scripts/` directory structure, removing top-level examples, and creating a unified organization.

## Current Structure Analysis

### Top-Level Python Scripts
- `demo_orchestrator.py` - System discovery/orchestration demo
- `example_usage.py` - Basic usage examples
- `git_visualization_comprehensive_demo.py` - Git visualization demo
- `integration_test.py` - Integration tests (already in testing/)
- `ollama_basic_usage.py` - Ollama basic usage
- `ollama_integration_demo.py` - Ollama comprehensive demo
- `ollama_model_management.py` - Ollama model management
- `orchestration_examples.py` - Orchestration examples

### Top-Level Shell Scripts
- `run-all-basic.sh` - Run all basic examples
- `test-all-examples.sh` - Test runner for examples
- `select-example.sh` - Interactive example selector
- `check-example-prerequisites.sh` - Prerequisites checker
- `setup-fabric-demo.sh` - Fabric integration setup

### Subdirectories
- `basic/` - Basic example scripts
- `integration/` - Integration orchestrator scripts
- `fabric-integration/` - Fabric AI integration examples
- `orchestration/` - Orchestration workflow demos
- `output/` - Generated output files

### Documentation
- `ADVANCED_ORCHESTRATORS_GUIDE.md` - Advanced guide
- `README.md` - Examples README
- `ORCHESTRATOR_STATUS_REPORT.md` - Status report
- `AGENTS.md` - Agent configuration

## Target Structure

```
scripts/
├── examples/                    # NEW: Example demonstrations
│   ├── basic/                   # Basic examples (from examples/basic/)
│   ├── integration/             # Integration examples (from examples/integration/)
│   └── README.md                # Examples overview
│
├── ollama_integration/          # NEW: Ollama integration
│   ├── basic_usage.py           # From ollama_basic_usage.py
│   ├── integration_demo.py      # From ollama_integration_demo.py
│   ├── model_management.py      # From ollama_model_management.py
│   ├── orchestrate.py           # Main orchestrator
│   └── README.md
│
├── fabric_integration/          # NEW: Fabric AI integration
│   ├── setup_demo.sh            # From setup-fabric-demo.sh
│   ├── orchestrate.py           # Main orchestrator
│   └── README.md                # From examples/fabric-integration/
│
├── development/                 # Development utilities
│   ├── run_all_examples.sh      # From run-all-basic.sh
│   ├── test_examples.sh         # From test-all-examples.sh
│   ├── select_example.sh        # From select-example.sh
│   ├── check_prerequisites.sh   # From check-example-prerequisites.sh
│   ├── example_usage.py          # From example_usage.py
│   └── README.md
│
├── project_orchestration/       # Existing
│   ├── demo.py                  # From demo_orchestrator.py
│   ├── examples.py              # From orchestration_examples.py
│   ├── examples/                # From examples/orchestration/
│   │   └── comprehensive_workflow_demo.py
│   ├── orchestrate.py           # Existing
│   └── README.md
│
├── git_operations/              # Existing
│   ├── visualization_demo.py    # From git_visualization_comprehensive_demo.py
│   ├── orchestrate.py           # Existing
│   └── README.md
│
└── docs/                        # NEW: Documentation
    ├── advanced_orchestrators_guide.md
    ├── orchestrator_status_report.md
    └── examples_overview.md
```

## Migration Steps

1. **Create new directories**
   - `scripts/examples/`
   - `scripts/ollama_integration/`
   - `scripts/fabric_integration/`
   - `scripts/docs/`

2. **Move Python scripts**
   - To appropriate script subdirectories based on functionality

3. **Move shell scripts**
   - Utility scripts to `scripts/development/`
   - Domain-specific scripts to their respective directories

4. **Move subdirectories**
   - `examples/basic/` → `scripts/examples/basic/`
   - `examples/integration/` → `scripts/examples/integration/`
   - `examples/orchestration/` → `scripts/project_orchestration/examples/`
   - `examples/fabric-integration/` → `scripts/fabric_integration/`

5. **Move documentation**
   - Guides to `scripts/docs/`
   - Update README files

6. **Update references**
   - Update all import paths and documentation references
   - Update AGENTS.md files

7. **Clean up**
   - Remove top-level `examples/` directory
   - Update root-level documentation

## Implementation Order

1. Create new directory structure
2. Move files preserving functionality
3. Update imports and paths
4. Update documentation
5. Test and verify
6. Remove old examples directory


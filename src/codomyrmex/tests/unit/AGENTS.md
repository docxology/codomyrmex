# Codomyrmex Agents — src/codomyrmex/tests/unit

## Signposting
- **Parent**: [Tests](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Unit test files and validation suites for individual components. This directory contains centralized unit tests for most modules, with some modules maintaining tests in their own `tests/` subdirectories.

## Module Test Organization

### Test Location Patterns

**Centralized Pattern** (28 modules): Tests in `src/codomyrmex/tests/unit/<module_name>/`
- Most modules follow this pattern for centralized test management

**Module-Local Pattern** (3 modules): Tests in `src/codomyrmex/<module>/tests/`
- `agents/` - Has tests in `src/codomyrmex/agents/tests/`
- `fpf/` - Has tests in `src/codomyrmex/fpf/tests/`
- `spatial/` - Has tests in `src/codomyrmex/spatial/three_d/tests/` (submodule)

### Submodule Test Mappings

Some modules have submodules with dedicated test folders in this directory:
- `agents/ai_code_editing/` → `tests/unit/ai_code_editing/`
- `api/documentation/` → `tests/unit/api_documentation/`
- `api/standardization/` → `tests/unit/api_standardization/`
- `code/sandbox/` → `tests/unit/code_execution_sandbox/`
- `code/review/` → `tests/unit/code_review/`

### Special Test Cases

- `cli/` - Tests for `cli.py` file (not a module directory)
- `exceptions/` - Tests for `exceptions.py` file (not a module directory)

## Active Components
- `README.md` – Project file
- `test_ai_code_editing.py` – Project file
- `test_api_documentation.py` – Project file (tests api.documentation)
- `test_bootstrap_agents_readmes.py` – Project file
- `test_build_synthesis.py` – Project file
- `test_ci_cd_automation.py` – Project file
- `test_cli_comprehensive.py` – Project file
- `test_cli_simple.py` – Project file
- `test_code.py` – Project file (if exists, tests code module)
- `test_code_review.py` – Project file
- `test_config_management.py` – Project file
- `test_containerization.py` – Project file
- `test_data_visualization.py` – Project file
- `test_database_management.py` – Project file
- `test_documentation.py` – Project file
- `test_environment_setup.py` – Project file
- `test_environment_setup_comprehensive.py` – Project file
- `test_exceptions.py` – Project file
- `test_git_operations.py` – Project file
- `test_git_operations_advanced.py` – Project file
- `test_git_operations_comprehensive.py` – Project file
- `test_github_operations_comprehensive.py` – Project file
- `test_llm.py` – Project file
- `test_logging_monitoring.py` – Project file
- `test_model_context_protocol.py` – Project file
- `test_spatial.three_d.py` – Project file
- `test_module_template.py` – Project file
- `test_ollama_integration.py` – Project file (tests llm.ollama)
- `test_pattern_matching.py` – Project file
- `test_performance_comprehensive.py` – Project file
- `test_physical_management.py` – Project file
- `test_project_orchestration.py` – Project file
- `test_repository_manager.py` – Project file
- `test_security_audit.py` – Project file
- `test_static_analysis.py` – Project file
- `test_static_analysis_comprehensive.py` – Project file
- `test_system_discovery_comprehensive.py` – Project file
- `test_template.py` – Project file
- `test_terminal_interface_comprehensive.py` – Project file


### Additional Files
- `SPEC.md` – Spec Md
- `__pycache__` –   Pycache  
- `ai_code_editing` – Ai Code Editing
- `api` – API module (with documentation and standardization submodules)
- `api_standardization` – Api Standardization
- `build_synthesis` – Build Synthesis
- `ci_cd_automation` – Ci Cd Automation
- `cli` – Cli
- `code` – Code module (execution, sandboxing, review, monitoring)
- `code_review` – Code Review
- `config_management` – Config Management
- `containerization` – Containerization
- `data_visualization` – Data Visualization
- `database_management` – Database Management
- `documentation` – Documentation
- `documents` – Documents
- `environment_setup` – Environment Setup
- `events` – Events
- `exceptions` – Exceptions
- `git_operations` – Git Operations
- `llm` – Language Models
- `llm` – Llm
- `logging_monitoring` – Logging Monitoring
- `model_context_protocol` – Model Context Protocol
- `spatial.three_d` – Modeling 3D
- `module_template` – Module Template
- `pattern_matching` – Pattern Matching
- `performance` – Performance
- `physical_management` – Physical Management
- `plugin_system` – Plugin System
- `project_orchestration` – Project Orchestration
- `security` – Security
- `static_analysis` – Static Analysis
- `system_discovery` – System Discovery
- `template` – Template
- `terminal_interface` – Terminal Interface
- `tools` – Tools

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [testing](../README.md) - Parent directory documentation
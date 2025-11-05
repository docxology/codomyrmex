# Codomyrmex Agents — scripts

## Purpose

Maintenance and automation utilities for Codomyrmex project management, including thin orchestrator scripts for all Codomyrmex modules.

## Active Components

### Documentation Management (`documentation/`)

- `check_docs_status.py` – Check documentation status across the entire repository.
- `documentation_status_summary.py` – Generate comprehensive documentation status summaries.
- `generate_missing_readmes.py` – Generate README.md files for directories with AGENTS.md.
- `check_doc_links.py` – Validate documentation links.
- `validate_code_examples.py` – Validate code examples in documentation.

### Code Quality & Maintenance (`maintenance/`)

- `add_logging.py` – Automated logging injection across modules.
- `fix_imports_simple.py` – Import statement cleanup and optimization.
- `fix_imports.py` – Advanced import management and dependency resolution.
- `fix_syntax_errors.py` – Syntax error detection and automated repair.
- `run_quality_checks.py` – Run comprehensive quality checks.
- `security_audit.py` – Security audit utilities.
- `audit_error_handling.py` – Error handling audit.
- `analyze_todos.py` – TODO analysis and reporting.
- `check_version_pinning.py` – Check dependency version pinning.
- `pin_dependency_versions.py` – Pin dependency versions.

### Development Tools (`development/`)

- `enhance_documentation.py` – Documentation enhancement and docstring generation.

### Module Orchestrators

Each Codomyrmex module has a corresponding orchestrator script providing CLI access to module functionality. These thin orchestrators call actual module functions while following established patterns.

#### AI & Intelligence
- `ai_code_editing/orchestrate.py` – AI code generation and editing orchestration
- `language_models/orchestrate.py` – Local LLM integration orchestration
- `model_context_protocol/orchestrate.py` – Model Context Protocol orchestration
- `ollama_integration/orchestrate.py` – Ollama integration orchestration
- `pattern_matching/orchestrate.py` – Pattern matching orchestration

#### Analysis & Visualization
- `data_visualization/orchestrate.py` – Data visualization orchestration
- `static_analysis/orchestrate.py` – Static analysis orchestration
- `code_review/orchestrate.py` – Code review orchestration
- `security_audit/orchestrate.py` – Security audit orchestration

#### Development Infrastructure
- `environment_setup/orchestrate.py` – Environment setup orchestration
- `code_execution_sandbox/orchestrate.py` – Code execution orchestration
- `build_synthesis/orchestrate.py` – Build synthesis orchestration
- `git_operations/orchestrate.py` – Git operations orchestration

#### Documentation & Management
- `documentation_module/orchestrate.py` – Documentation module orchestration
- `api_documentation/orchestrate.py` – API documentation orchestration
- `project_orchestration/orchestrate.py` – Project orchestration orchestration

#### System & Operations
- `logging_monitoring/orchestrate.py` – Logging orchestration
- `performance/orchestrate.py` – Performance orchestration
- `system_discovery/orchestrate.py` – System discovery orchestration
- `terminal_interface/orchestrate.py` – Terminal interface orchestration

#### Infrastructure & Deployment
- `ci_cd_automation/orchestrate.py` – CI/CD automation orchestration
- `containerization/orchestrate.py` – Containerization orchestration
- `config_management/orchestrate.py` – Config management orchestration
- `database_management/orchestrate.py` – Database management orchestration

#### Advanced Features
- `modeling_3d/orchestrate.py` – 3D modeling orchestration
- `physical_management/orchestrate.py` – Physical management orchestration
- `module_template/orchestrate.py` – Module template information

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- All orchestrator scripts must call real module functions (no stubs).
- All orchestrators must use proper exception handling from `codomyrmex.exceptions`.
- All orchestrators must use `codomyrmex.logging_monitoring` for logging.

## Module Mapping

Each orchestrator script corresponds to a module in `src/codomyrmex/`:
- `scripts/[module_name]/orchestrate.py` → `src/codomyrmex/[module_name]/`
- Each orchestrator provides CLI access to functions exported from the module's `__init__.py`
- Orchestrators follow patterns established in `src/codomyrmex/cli.py`

## Navigation Links
- **📚 Scripts Overview**: [README.md](README.md) - Scripts directory documentation
- **🏠 Project Root**: [../README.md](../README.md) - Main project README
- **📖 Documentation Hub**: [../docs/README.md](../docs/README.md) - Complete documentation structure
- **📦 Source Code**: [../src/README.md](../src/README.md) - Source code structure

## Checkpoints

- [x] Confirm AGENTS.md reflects the current module purpose.
- [x] Verify logging and telemetry hooks for this directory's agents.
- [x] All module orchestrators created and documented.
- [x] Orchestrators call real module functions with proper error handling.
- [ ] Sync automation scripts or TODO entries after modifications.

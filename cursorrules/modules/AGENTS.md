# Codomyrmex Agents — cursorrules/modules

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

This directory contains module-specific coding standards and conventions for each Codomyrmex module. Each `.cursorrules` file defines standards tailored to the specific requirements, architecture, and purpose of its corresponding module.

## Module Rule Categories

### AI & Intelligence Modules

**AI Code Editing** (`ai_code_editing.cursorrules`)
- Standards for AI-assisted code generation and refactoring
- Key Functions: `validate_ai_suggestions(suggestions: list) -> bool`, `enforce_code_quality_thresholds(code: str) -> QualityScore`

**Ollama Integration** (`ollama_integration.cursorrules`)
- Standards for local LLM integration and management
- Key Functions: `validate_model_configuration(config: dict) -> bool`, `standardize_inference_parameters(params: dict) -> StandardizedParams`

**Language Models** (`language_models.cursorrules`)
- Standards for LLM provider integration and API management
- Key Functions: `validate_api_credentials(creds: dict) -> bool`, `standardize_token_usage(usage: dict) -> StandardizedUsage`

### Analysis & Quality Modules

**Static Analysis** (`static_analysis.cursorrules`)
- Standards for code analysis and quality metrics
- Key Functions: `validate_analysis_config(config: dict) -> bool`, `standardize_severity_levels(results: list) -> StandardizedResults`

**Code Review** (`code_review.cursorrules`)
- Standards for automated code review processes
- Key Functions: `validate_review_criteria(criteria: dict) -> bool`, `standardize_review_comments(comments: list) -> StandardizedComments`

**Pattern Matching** (`pattern_matching.cursorrules`)
- Standards for code pattern recognition and analysis
- Key Functions: `validate_pattern_definitions(patterns: dict) -> bool`, `standardize_match_results(matches: list) -> StandardizedMatches`

**Security Audit** (`security_audit.cursorrules`)
- Standards for security scanning and vulnerability assessment
- Key Functions: `validate_security_config(config: dict) -> bool`, `standardize_vulnerability_reports(reports: list) -> StandardizedReports`

### Build & Deploy Modules

**Build Synthesis** (`build_synthesis.cursorrules`)
- Standards for multi-language build orchestration
- Key Functions: `validate_build_config(config: dict) -> bool`, `standardize_build_artifacts(artifacts: list) -> StandardizedArtifacts`

**Git Operations** (`git_operations.cursorrules`)
- Standards for version control automation
- Key Functions: `validate_git_config(config: dict) -> bool`, `standardize_commit_messages(messages: list) -> StandardizedMessages`

**CI/CD Automation** (`ci_cd_automation.cursorrules`)
- Standards for pipeline orchestration and deployment
- Key Functions: `validate_pipeline_config(config: dict) -> bool`, `standardize_deployment_results(results: list) -> StandardizedResults`

**Containerization** (`containerization.cursorrules`)
- Standards for container lifecycle management
- Key Functions: `validate_container_config(config: dict) -> bool`, `standardize_container_metrics(metrics: list) -> StandardizedMetrics`

### Development & Infrastructure Modules

**Environment Setup** (`environment_setup.cursorrules`)
- Standards for environment validation and dependency management
- Key Functions: `validate_environment_config(config: dict) -> bool`, `standardize_dependency_lists(deps: list) -> StandardizedDeps`

**Configuration Management** (`config_management.cursorrules`)
- Standards for configuration file management and validation
- Key Functions: `validate_config_schema(schema: dict) -> bool`, `standardize_config_values(values: dict) -> StandardizedValues`

**Database Management** (`database_management.cursorrules`)
- Standards for database operations and schema management
- Key Functions: `validate_database_config(config: dict) -> bool`, `standardize_query_results(results: list) -> StandardizedResults`

### Documentation & Interface Modules

**Documentation** (`documentation.cursorrules`)
- Standards for documentation generation and maintenance
- Key Functions: `validate_doc_config(config: dict) -> bool`, `standardize_doc_formats(docs: list) -> StandardizedDocs`

**API Documentation** (`api_documentation.cursorrules`)
- Standards for API specification and documentation
- Key Functions: `validate_api_spec(spec: dict) -> bool`, `standardize_api_endpoints(endpoints: list) -> StandardizedEndpoints`

**Terminal Interface** (`terminal_interface.cursorrules`)
- Standards for terminal UI and interaction design
- Key Functions: `validate_ui_config(config: dict) -> bool`, `standardize_terminal_output(output: str) -> StandardizedOutput`

### Specialized Modules

**Data Visualization** (`data_visualization.cursorrules`)
- Standards for chart generation and data presentation
- Key Functions: `validate_visualization_config(config: dict) -> bool`, `standardize_chart_formats(charts: list) -> StandardizedCharts`

**3D Modeling** (`modeling_3d.cursorrules`)
- Standards for 3D scene creation and rendering
- Key Functions: `validate_3d_config(config: dict) -> bool`, `standardize_3d_formats(models: list) -> StandardizedModels`

**Performance Monitoring** (`performance.cursorrules`)
- Standards for performance profiling and optimization
- Key Functions: `validate_performance_config(config: dict) -> bool`, `standardize_performance_metrics(metrics: list) -> StandardizedMetrics`

**Physical Management** (`physical_management.cursorrules`)
- Standards for hardware monitoring and resource management
- Key Functions: `validate_hardware_config(config: dict) -> bool`, `standardize_system_metrics(metrics: list) -> StandardizedMetrics`

**System Discovery** (`system_discovery.cursorrules`)
- Standards for module discovery and capability detection
- Key Functions: `validate_discovery_config(config: dict) -> bool`, `standardize_discovery_results(results: list) -> StandardizedResults`

**Project Orchestration** (`project_orchestration.cursorrules`)
- Standards for workflow orchestration and task coordination
- Key Functions: `validate_orchestration_config(config: dict) -> bool`, `standardize_workflow_results(results: list) -> StandardizedResults`

**Module Template** (`module_template.cursorrules`)
- Standards for module creation templates and scaffolding
- Key Functions: `validate_template_config(config: dict) -> bool`, `standardize_module_structure(structure: dict) -> StandardizedStructure`

**Model Context Protocol** (`model_context_protocol.cursorrules`)
- Standards for AI communication protocol implementation
- Key Functions: `validate_mcp_config(config: dict) -> bool`, `standardize_mcp_messages(messages: list) -> StandardizedMessages`

## Active Components
- `README.md` – Directory documentation
- `ai_code_editing.cursorrules` – AI-assisted coding standards (function: validate_ai_code_patterns(code: str) -> ValidationResult)
- `api_documentation.cursorrules` – API documentation standards (function: validate_api_docs(docs: dict) -> ValidationResult)
- `build_synthesis.cursorrules` – Build orchestration standards (function: validate_build_process(config: dict) -> ValidationResult)
- `ci_cd_automation.cursorrules` – CI/CD pipeline standards (function: validate_pipeline_config(config: dict) -> ValidationResult)
- `code_execution_sandbox.cursorrules` – Code execution safety standards (function: validate_execution_safety(config: dict) -> ValidationResult)
- `code_review.cursorrules` – Code review standards (function: validate_review_process(config: dict) -> ValidationResult)
- `config_management.cursorrules` – Configuration management standards (function: validate_config_management(config: dict) -> ValidationResult)
- `containerization.cursorrules` – Container management standards (function: validate_container_config(config: dict) -> ValidationResult)
- `data_visualization.cursorrules` – Data visualization standards (function: validate_chart_config(config: dict) -> ValidationResult)
- `database_management.cursorrules` – Database operations standards (function: validate_database_config(config: dict) -> ValidationResult)
- `documentation.cursorrules` – Documentation generation standards (function: validate_doc_config(config: dict) -> ValidationResult)
- `environment_setup.cursorrules` – Environment setup standards (function: validate_env_config(config: dict) -> ValidationResult)
- `git_operations.cursorrules` – Git operations standards (function: validate_git_config(config: dict) -> ValidationResult)
- `language_models.cursorrules` – Language model integration standards (function: validate_llm_config(config: dict) -> ValidationResult)
- `logging_monitoring.cursorrules` – Logging standards (function: validate_logging_config(config: dict) -> ValidationResult)
- `model_context_protocol.cursorrules` – MCP implementation standards (function: validate_mcp_config(config: dict) -> ValidationResult)
- `modeling_3d.cursorrules` – 3D modeling standards (function: validate_3d_config(config: dict) -> ValidationResult)
- `module_template.cursorrules` – Module template standards (function: validate_template_config(config: dict) -> ValidationResult)
- `ollama_integration.cursorrules` – Ollama integration standards (function: validate_ollama_config(config: dict) -> ValidationResult)
- `pattern_matching.cursorrules` – Pattern matching standards (function: validate_pattern_config(config: dict) -> ValidationResult)
- `performance.cursorrules` – Performance monitoring standards (function: validate_performance_config(config: dict) -> ValidationResult)
- `physical_management.cursorrules` – Physical system management standards (function: validate_physical_config(config: dict) -> ValidationResult)
- `project_orchestration.cursorrules` – Project orchestration standards (function: validate_orchestration_config(config: dict) -> ValidationResult)
- `security_audit.cursorrules` – Security audit standards (function: validate_security_config(config: dict) -> ValidationResult)
- `static_analysis.cursorrules` – Static analysis standards (function: validate_analysis_config(config: dict) -> ValidationResult)
- `system_discovery.cursorrules` – System discovery standards (function: validate_discovery_config(config: dict) -> ValidationResult)
- `terminal_interface.cursorrules` – Terminal interface standards (function: validate_terminal_config(config: dict) -> ValidationResult)

## Operating Contracts

### Module Rule Standards
1. **Module-Specific Focus** - Rules address unique requirements of each module
2. **Architecture Alignment** - Standards support module design principles
3. **Cross-Module Compatibility** - Module rules work with cross-module coordination rules
4. **Evolution Support** - Rules accommodate module growth and feature additions

### Rule Maintenance
- Update module rules when module interfaces change
- Ensure rules reflect current module capabilities
- Maintain consistency with general and cross-module rules
- Provide clear migration paths for rule updates

## Navigation Links
- **Parent Directory**: [cursorrules](../README.md) - Coding standards documentation

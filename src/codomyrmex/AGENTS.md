# Codomyrmex Agents — src/codomyrmex

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2025

## Purpose
Primary Python package bundling all Codomyrmex agents and shared tooling.

## Active Components
- `ai_code_editing/` – AI-powered code generation and editing with multi-provider LLM support
- `api_documentation/` – API documentation generation with OpenAPI/Swagger support
- `build_synthesis/` – Build automation and code synthesis pipelines
- `ci_cd_automation/` – CI/CD pipeline management and deployment orchestration
- `code_execution_sandbox/` – Secure code execution in sandboxed environments
- `code_review/` – Comprehensive code review with Pyscn integration
- `config_management/` – Configuration management and secret handling
- `containerization/` – Docker management and Kubernetes orchestration
- `data_visualization/` – Rich data plotting and interactive dashboards
- `database_management/` – Database integration and migration management
- `documentation/` – Documentation website generation with Docusaurus
- `environment_setup/` – Development environment validation and setup
- `git_operations/` – Git workflow automation and repository management
- `language_models/` – LLM provider management and model configuration
- `logging_monitoring/` – Structured logging and performance monitoring
- `model_context_protocol/` – MCP framework for standardized AI communication
- `modeling_3d/` – 3D modeling and visualization with AR/VR support
- `module_template/` – Standardized module scaffolding and templates
- `ollama_integration/` – Local LLM integration via Ollama
- `pattern_matching/` – Advanced code pattern analysis and recognition
- `performance/` – Performance optimization and monitoring utilities
- `physical_management/` – Physical system simulation and management
- `project_orchestration/` – Project and workflow coordination
- `security_audit/` – Security vulnerability scanning and compliance
- `static_analysis/` – Multi-language code quality analysis
- `system_discovery/` – System introspection and capability mapping
- `terminal_interface/` – Interactive CLI and terminal utilities
- `tests/` – Cross-module integration and performance tests

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Module Relationships
- **AI & Intelligence**: `ai_code_editing/`, `language_models/`, `ollama_integration/`, `pattern_matching/`
- **Analysis & Quality**: `static_analysis/`, `security_audit/`, `code_review/`, `code_execution_sandbox/`, `performance/`
- **Visualization & Reporting**: `data_visualization/`, `api_documentation/`, `documentation/`
- **Build & Deployment**: `build_synthesis/`, `ci_cd_automation/`, `containerization/`
- **Infrastructure**: `database_management/`, `environment_setup/`, `config_management/`
- **System Integration**: `git_operations/`, `model_context_protocol/`, `terminal_interface/`
- **Advanced Features**: `modeling_3d/`, `physical_management/`, `project_orchestration/`
- **Development Support**: `module_template/`, `system_discovery/`, `logging_monitoring/`, `tests/`

## Navigation Links
- **📚 Package Overview**: [README.md](README.md) - Package documentation and module status
- **🏠 Source Root**: [../README.md](../README.md) - Source code structure
- **🏠 Project Root**: [../../README.md](../../README.md) - Main project README
- **📖 Documentation Hub**: [../../docs/README.md](../../docs/README.md) - Complete documentation structure


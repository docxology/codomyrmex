# Codomyrmex Agents — src/codomyrmex

## Signposting
- **Parent**: [src](../AGENTS.md)
- **Self**: [Package Agents](AGENTS.md)
- **Children**:
    - **Foundation Layer**:
        - [Logging Monitoring Agents](logging_monitoring/AGENTS.md)
        - [Environment Setup Agents](environment_setup/AGENTS.md)
        - [Model Context Protocol Agents](model_context_protocol/AGENTS.md)
        - [Terminal Interface Agents](terminal_interface/AGENTS.md)
    - **Core Layer**:
        - [AI Code Editing Agents](ai_code_editing/AGENTS.md)
        - [Static Analysis Agents](static_analysis/AGENTS.md)
        - [Code Execution Sandbox Agents](code_execution_sandbox/AGENTS.md)
        - [Data Visualization Agents](data_visualization/AGENTS.md)
        - [Pattern Matching Agents](pattern_matching/AGENTS.md)
        - [Git Operations Agents](git_operations/AGENTS.md)
        - [Code Review Agents](code_review/AGENTS.md)
                - [Security Agents](security/AGENTS.md)
                - [Documents Agents](documents/AGENTS.md)
        - [Ollama Integration Agents](ollama_integration/AGENTS.md)
        - [Language Models Agents](language_models/AGENTS.md)
        - [Performance Agents](performance/AGENTS.md)
    - **Service Layer**:
        - [Build Synthesis Agents](build_synthesis/AGENTS.md)
        - [Documentation Agents](documentation/AGENTS.md)
        - [API Documentation Agents](api_documentation/AGENTS.md)
        - [CI/CD Automation Agents](ci_cd_automation/AGENTS.md)
        - [Containerization Agents](containerization/AGENTS.md)
        - [Database Management Agents](database_management/AGENTS.md)
        - [Config Management Agents](config_management/AGENTS.md)
        - [Project Orchestration Agents](project_orchestration/AGENTS.md)
    - **Specialized Layer**:
        - [Modeling 3D Agents](modeling_3d/AGENTS.md)
        - [Physical Management Agents](physical_management/AGENTS.md)
        - [System Discovery Agents](system_discovery/AGENTS.md)
        - [Module Template Agents](module_template/AGENTS.md)
        - [Template Agents](template/AGENTS.md)
        - [Events Agents](events/AGENTS.md)
        - [API Standardization Agents](api_standardization/AGENTS.md)
        - [Plugin System Agents](plugin_system/AGENTS.md)
        - [Tools Agents](tools/AGENTS.md)
        - [FPF Agents](fpf/AGENTS.md)
        - [CEREBRUM Agents](cerebrum/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core package containing the Codomyrmex platform implementation. This directory houses all functional modules that provide the platform's capabilities, organized into a layered architecture for maintainability and extensibility.

The codomyrmex package serves as the central hub for all platform functionality, with modules that can be composed together to create complex workflows and applications.

## Package Architecture

### Layered Design

Modules are organized into functional layers:

**Foundation Layer** - Base services used throughout the platform:
- `logging_monitoring/` - Centralized logging and telemetry
- `environment_setup/` - Environment validation and configuration
- `model_context_protocol/` - AI communication standards
- `terminal_interface/` - Rich terminal interactions

**Core Layer** - Primary development capabilities:
- `ai_code_editing/` - AI-powered code assistance
- `static_analysis/` - Code quality and security analysis
- `code_execution_sandbox/` - Safe code execution environments
- `data_visualization/` - Charts, plots, and visualizations
- `pattern_matching/` - Code pattern recognition
- `git_operations/` - Version control automation

**Service Layer** - Higher-level orchestration:
- `build_synthesis/` - Multi-language build automation
- `documentation/` - Documentation generation systems
- `api_documentation/` - API specification management
- `ci_cd_automation/` - Continuous integration pipelines
- `database_management/` - Database operations and migrations

**Specialized Layer** - Domain-specific capabilities:
- `modeling_3d/` - 3D modeling and visualization
- `physical_management/` - Hardware resource management
- `system_discovery/` - Module discovery and health monitoring

## Active Components

### Package Infrastructure
- `__init__.py` – Package initialization and public API exports
- `README.md` – Package overview and module documentation
- `cli.py` – Command-line interface for the platform
- `exceptions.py` – Platform-wide exception definitions

### Module Directories
- `ai_code_editing/` – AI-assisted code generation and editing
- `api_documentation/` – API documentation generation
- `build_synthesis/` – Build orchestration and automation
- `ci_cd_automation/` – CI/CD pipeline management
- `code_execution_sandbox/` – Safe code execution environments
- `code_review/` – Automated code review and analysis
- `config_management/` – Configuration management and validation
- `containerization/` – Container lifecycle management
- `data_visualization/` – Data plotting and visualization
- `database_management/` – Database operations and maintenance
- `documentation/` – Documentation generation system
- `environment_setup/` – Environment validation and setup
- `git_operations/` – Git workflow automation
- `language_models/` – Language model management
- `logging_monitoring/` – Centralized logging system
- `model_context_protocol/` – MCP tool specifications
- `modeling_3d/` – 3D modeling and rendering
- `module_template/` – Module creation templates
- `ollama_integration/` – Local LLM integration
- `pattern_matching/` – Code pattern analysis
- `performance/` – Performance monitoring and optimization
- `physical_management/` – Hardware resource management
- `project_orchestration/` – Workflow orchestration
- `security/` – Security module (physical, digital, cognitive, theory)
- `documents/` – Document I/O operations
- `static_analysis/` – Code quality analysis
- `system_discovery/` – System exploration and discovery
- `template/` – Code generation templates
- `terminal_interface/` – Rich terminal UI components
- `tests/` – Cross-module integration tests
- `tools/` – Utility tools and helpers

## Operating Contracts

### Universal Package Protocols

All code in this package must:

1. **Follow Module Boundaries** - Each module maintains clear separation of concerns
2. **Adhere to Type Hints** - Comprehensive type annotations for reliability
3. **Include Comprehensive Tests** - Unit and integration tests for all functionality
4. **Maintain API Stability** - Backward compatibility for public interfaces
5. **Follow Coding Standards** - Compliance with established platform rules

### Module Development Standards

#### Module Structure
Each module must include:
- `__init__.py` - Module initialization and exports
- Core implementation files with clear naming
- Comprehensive documentation (README.md, API_SPECIFICATION.md, etc.)
- Test suites with good coverage
- Requirements.txt for dependencies

#### Quality Requirements
- PEP 8 compliance and type hints
- Docstrings for all public functions
- Error handling with informative messages
- Logging integration for monitoring
- Security considerations documented

## Function Signatures by Module

### Foundation Layer

#### logging_monitoring

```python
def setup_logging() -> None
def get_logger(name: str) -> logging.Logger
```

#### environment_setup

```python
def is_uv_available() -> bool
def is_uv_environment() -> bool
def ensure_dependencies_installed() -> None
def check_and_setup_env_vars(repo_root_path: str) -> None
```

#### model_context_protocol

```python
def register_tool(name: str, spec: dict) -> bool
def call_tool(name: str, params: dict) -> Any
def get_registered_tools() -> dict[str, dict]
def validate_tool_spec(spec: dict) -> bool
```

#### terminal_interface

```python
def display_table(data: list, headers: list) -> None
def confirm_action(message: str) -> bool
def show_progress(iterable: Iterable, description: str = "Processing") -> Iterable
def display_status(message: str, status: str = "info") -> None
def get_user_input(prompt: str, default: str = "") -> str
```

### Core Layer

#### ai_code_editing

```python
def generate_code_snippet(prompt: str, language: str, provider: str = "openai", model_name: Optional[str] = None, context: Optional[str] = None, max_length: Optional[int] = None, temperature: float = 0.7, **kwargs) -> dict
def refactor_code_snippet(code: str, refactoring_type: str, language: str, provider: str = "openai", model_name: Optional[str] = None, context: Optional[str] = None, preserve_functionality: bool = True, **kwargs) -> dict
def analyze_code_quality(code: str, language: str, provider: str = "openai", model_name: Optional[str] = None, **kwargs) -> dict
def generate_code_batch(prompts: list[dict], provider: str = "openai", **kwargs) -> list[dict]
def compare_code_versions(code1: str, code2: str, language: str, provider: str = "openai", **kwargs) -> dict
def generate_code_documentation(code: str, language: str, provider: str = "openai", **kwargs) -> str
def get_supported_languages() -> list[str]
def get_supported_providers() -> list[str]
def get_available_models(provider: str) -> list[str]
def validate_api_keys(provider: str = None) -> dict[str, bool]
def setup_environment() -> bool
```

#### static_analysis

```python
def analyze_file(file_path: str, analysis_types: list[AnalysisType] = None) -> list[AnalysisResult]
def analyze_project(project_root: str, target_paths: list[str] = None, analysis_types: list[AnalysisType] = None) -> AnalysisSummary
def get_available_tools() -> dict[str, bool]
def parse_pyrefly_output(output: str, project_root: str) -> list
def run_pyrefly_analysis(target_paths: list[str], project_root: str) -> dict
def analyze_codebase(*args, **kwargs) -> AnalysisSummary
```

#### code_execution_sandbox

```python
def execute_code(language: str, code: str, stdin: Optional[str] = None, timeout: Optional[int] = None, session_id: Optional[str] = None) -> dict[str, Any]
```

#### data_visualization

```python
def create_plot(data: pd.DataFrame, plot_type: str, **kwargs) -> str
def save_visualization(fig: Any, filepath: str) -> None
def create_bar_chart(data: dict, title: str = "", **kwargs) -> str
def create_line_plot(data: dict, title: str = "", **kwargs) -> str
def create_scatter_plot(data: dict, title: str = "", **kwargs) -> str
def create_histogram(data: list, title: str = "", **kwargs) -> str
def create_pie_chart(data: dict, title: str = "", **kwargs) -> str
def create_mermaid_diagram(diagram_type: str, data: dict, **kwargs) -> str
def generate_git_visualization(repo_path: str, **kwargs) -> str
```

#### pattern_matching

```python
def find_patterns(code: str, patterns: list) -> list
def extract_dependencies(filepath: str) -> dict
def match_ast_patterns(tree: ast.AST, patterns: dict) -> list
def find_function_calls(code: str, function_names: list[str] = None) -> list
def extract_class_hierarchy(code: str) -> dict
def detect_code_smells(code: str) -> list
```

#### git_operations

```python
def commit_changes(message: str, files: list = None) -> str
def create_branch(name: str) -> bool
def get_status() -> dict
def get_log(limit: int = 10) -> list
def pull_changes(remote: str = "origin", branch: str = "main") -> bool
def push_changes(remote: str = "origin", branch: str = "main") -> bool
def create_tag(name: str, message: str = "") -> bool
def get_branches() -> list
def switch_branch(name: str) -> bool
```

#### code_review

```python
def review_pull_request(pr_number: int, repo: str) -> ReviewResult
def analyze_code_quality(code: str) -> dict
def review_file(filepath: str, content: str = None) -> dict
def generate_review_comments(issues: list) -> list
def summarize_review(review_result: ReviewResult) -> str
```

#### security

```python
def scan_codebase(path: str) -> list
def check_vulnerabilities(dependencies: dict) -> list
def audit_file(filepath: str) -> dict
def scan_secrets(content: str) -> list
def check_compliance(code: str, standards: list) -> dict
def generate_security_report(scan_results: list) -> str
```

#### ollama_integration

```python
def load_model(name: str) -> bool
def generate_text(prompt: str, model: str) -> str
def list_available_models() -> list
def unload_model(name: str) -> bool
def get_model_info(name: str) -> dict
def chat_completion(messages: list, model: str) -> dict
```

#### language_models

```python
def get_completion(messages: list, model: str) -> str
def calculate_tokens(text: str) -> int
def list_models(provider: str) -> list
def validate_api_key(provider: str) -> bool
def get_model_limits(model: str) -> dict
def stream_completion(messages: list, model: str) -> Iterator[str]
```

#### performance

```python
def profile_function(func: callable, *args, **kwargs) -> ProfileResult
def run_benchmark(test_func: callable) -> dict
def monitor_performance(func: callable) -> callable
def get_system_metrics() -> dict
def analyze_performance_data(data: dict) -> dict
def generate_performance_report(results: list) -> str
```

### Service Layer

#### build_synthesis

```python
def build_project(config: dict) -> BuildResult
def resolve_dependencies(requirements: list) -> dict
def create_build_pipeline(config: dict) -> Pipeline
def execute_build_step(step: dict) -> dict
def validate_build_config(config: dict) -> bool
def generate_build_report(results: dict) -> str
```

#### documentation

```python
def generate_docs(source_path: str, output_path: str) -> None
def extract_api_docs(code: str) -> dict
def create_documentation_index(docs: dict) -> str
def render_markdown(content: dict) -> str
def validate_documentation(docs: dict) -> list
def update_documentation(source: str, target: str) -> bool
```

#### api_documentation

```python
def generate_openapi_spec(routes: list) -> dict
def create_swagger_ui(spec: dict) -> str
def extract_endpoint_docs(code: str) -> list
def validate_api_spec(spec: dict) -> list
def generate_postman_collection(spec: dict) -> dict
def render_api_documentation(spec: dict) -> str
```

#### ci_cd_automation

```python
def create_pipeline(config: dict) -> Pipeline
def deploy_to_environment(app: str, env: str) -> bool
def run_tests(config: dict) -> TestResult
def build_artifacts(config: dict) -> list
def configure_deployment(target: str, config: dict) -> bool
def monitor_pipeline_status(pipeline_id: str) -> dict
```

#### containerization

```python
def build_image(dockerfile: str, tag: str) -> str
def deploy_container(config: dict) -> bool
def manage_containers(action: str, filters: dict = None) -> list
def create_docker_compose(config: dict) -> str
def monitor_container_health(container_id: str) -> dict
def scale_service(service_name: str, replicas: int) -> bool
```

#### database_management

```python
def execute_query(query: str, params: dict = None) -> list
def run_migration(migration_file: str) -> bool
def create_backup(database: str) -> str
def restore_backup(backup_file: str, database: str) -> bool
def analyze_performance(database: str) -> dict
def optimize_queries(queries: list) -> list
```

#### config_management

```python
def load_config(path: str) -> dict
def get_secret(key: str) -> str
def validate_config(config: dict, schema: dict) -> list
def merge_configs(base: dict, overrides: dict) -> dict
def export_config(config: dict, format: str) -> str
def watch_config_changes(path: str, callback: callable) -> None
```

#### project_orchestration

```python
def execute_workflow(workflow_id: str, context: dict) -> WorkflowResult
def create_workflow(definition: dict) -> str
def get_workflow_status(workflow_id: str) -> dict
def cancel_workflow(workflow_id: str) -> bool
def list_workflows() -> list
def validate_workflow(definition: dict) -> list
```

### Specialized Layer

#### modeling_3d

```python
def create_scene(objects: list) -> Scene
def render_scene(scene: Scene, camera: Camera) -> Image
def create_mesh(geometry: dict) -> Mesh
def apply_material(mesh: Mesh, material: dict) -> Mesh
def animate_object(obj: Object3D, animation: dict) -> Object3D
def export_scene(scene: Scene, format: str) -> bytes
```

#### physical_management

```python
def get_system_info() -> dict
def monitor_resources(interval: int) -> Iterator[dict]
def get_hardware_info() -> dict
def check_system_health() -> dict
def manage_processes(action: str, filters: dict = None) -> list
def get_network_info() -> dict
```

#### system_discovery

```python
def discover_modules() -> list
def check_module_health(module_name: str) -> HealthStatus
def get_system_capabilities() -> dict
def scan_dependencies() -> dict
def validate_environment() -> dict
def generate_system_report() -> str
```

#### module_template

```python
def create_module(name: str, template: str) -> bool
def generate_scaffold(config: dict) -> dict
def validate_module_structure(path: str) -> list
def update_module_template(template_name: str, updates: dict) -> bool
def list_available_templates() -> list
def customize_template(template: str, customizations: dict) -> str
```

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Package Documentation
- **Package Overview**: [README.md](README.md) - Complete package documentation

### Platform Navigation
- **Parent Directory**: [src](../README.md) - Source code documentation
- **Project Root**: [README](../../README.md) - Main project documentation
- **Source Root**: [src](../README.md) - Source code documentation

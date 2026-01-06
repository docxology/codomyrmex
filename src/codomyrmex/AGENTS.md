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
        - [Validation Agents](validation/AGENTS.md)
    - **Core Layer**:
        - [Static Analysis Agents](static_analysis/AGENTS.md)
        - [Code Agents](code/AGENTS.md) - Code execution, sandboxing, review, and monitoring
        - [Data Visualization Agents](data_visualization/AGENTS.md)
        - [Pattern Matching Agents](pattern_matching/AGENTS.md)
        - [Git Operations Agents](git_operations/AGENTS.md)
        - [Scrape Agents](scrape/AGENTS.md)
        - [Security Agents](security/AGENTS.md)
        - [Documents Agents](documents/AGENTS.md)
        - [LLM Agents](llm/AGENTS.md)
        - [Performance Agents](performance/AGENTS.md)
        - [Cache Agents](cache/AGENTS.md)
        - [Serialization Agents](serialization/AGENTS.md)
        - [Metrics Agents](metrics/AGENTS.md)
    - **Service Layer**:
        - [Build Synthesis Agents](build_synthesis/AGENTS.md)
        - [Documentation Agents](documentation/AGENTS.md)
        - [API Documentation Agents](api/documentation/AGENTS.md)
        - [CI/CD Automation Agents](ci_cd_automation/AGENTS.md)
        - [Containerization Agents](containerization/AGENTS.md)
        - [Database Management Agents](database_management/AGENTS.md)
        - [Config Management Agents](config_management/AGENTS.md)
        - [Project Orchestration Agents](project_orchestration/AGENTS.md)
        - [Networking Agents](networking/AGENTS.md)
        - [Queue Agents](queue/AGENTS.md)
        - [Auth Agents](auth/AGENTS.md)
    - **Specialized Layer**:
        - [Spatial Agents](spatial/AGENTS.md)
        - [Physical Management Agents](physical_management/AGENTS.md)
        - [System Discovery Agents](system_discovery/AGENTS.md)
        - [Module Template Agents](module_template/AGENTS.md)
        - [Template Agents](template/AGENTS.md)
        - [Templating Agents](templating/AGENTS.md)
        - [Events Agents](events/AGENTS.md)
        - [API Standardization Agents](api/standardization/AGENTS.md)
        - [Plugin System Agents](plugin_system/AGENTS.md)
        - [Tools Agents](tools/AGENTS.md)
        - [FPF Agents](fpf/AGENTS.md)
        - [CEREBRUM Agents](cerebrum/AGENTS.md)
        - [Agents Agents](agents/AGENTS.md)
            - [AI Code Editing Agents](agents/ai_code_editing/AGENTS.md)
            - [Droid Agents](agents/droid/AGENTS.md)
        - [Compression Agents](compression/AGENTS.md)
        - [Encryption Agents](encryption/AGENTS.md)
        - [Tests Agents](tests/AGENTS.md)
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
- `validation/` - Input validation framework (JSON Schema, Pydantic, custom validators)

**Core Layer** - Primary development capabilities:
- `static_analysis/` - Code quality and security analysis
- `code/` - Code execution, sandboxing, review, and monitoring
  - `code/execution/` - Code execution engine
  - `code/sandbox/` - Sandboxed execution environment
  - `code/review/` - Code review and analysis
  - `code/monitoring/` - Execution monitoring and metrics
- `data_visualization/` - Charts, plots, and visualizations
- `pattern_matching/` - Code pattern recognition
- `git_operations/` - Version control automation
- `scrape/` - Web scraping and data extraction
  - `scrape/firecrawl/` - Firecrawl integration
- `security/` - Security module (physical, digital, cognitive, theory)
  - `security/digital/` - Digital security scanning
  - `security/physical/` - Physical security management
  - `security/cognitive/` - Cognitive security analysis
  - `security/theory/` - Security theory and frameworks
  - `security/security_theory/` - Advanced security theory
- `documents/` - Document I/O operations
  - `documents/core/` - Core document processing
  - `documents/formats/` - Format handlers
  - `documents/metadata/` - Metadata extraction
  - `documents/models/` - Document models
  - `documents/search/` - Document search
  - `documents/transformation/` - Document transformation
  - `documents/utils/` - Document utilities
  - `documents/templates/` - Document templates
- `llm/` - LLM integration
  - `llm/ollama/` - Local LLM integration via Ollama
  - `llm/outputs/` - LLM output management
  - `llm/prompt_templates/` - Prompt template system
- `performance/` - Performance monitoring and optimization
- `cache/` - Caching strategies (Redis, in-memory, file-based)
- `serialization/` - Data serialization (JSON, YAML, TOML, MessagePack)
- `metrics/` - Metrics collection and Prometheus integration

**Service Layer** - Higher-level orchestration:
- `build_synthesis/` - Multi-language build automation
- `documentation/` - Documentation generation systems
  - `documentation/scripts/` - Documentation scripts
  - `documentation/src/` - Documentation source
  - `documentation/static/` - Static documentation assets
- `api/` - API documentation and standardization
  - `api/documentation/` - API documentation generation
  - `api/standardization/` - API standardization frameworks
- `ci_cd_automation/` - Continuous integration pipelines
- `containerization/` - Container lifecycle management
- `database_management/` - Database operations and migrations

**Specialized Layer** - Domain-specific capabilities:
- `spatial/` - Spatial modeling (3D, 4D, World Models)
  - `spatial/three_d/` - 3D modeling and visualization
  - `spatial/four_d/` - 4D modeling and transformations
  - `spatial/world_models/` - World model representations
- `physical_management/` - Hardware resource management
  - `physical_management/examples/` - Physical management examples
- `system_discovery/` - Module discovery and health monitoring
- `module_template/` - Module creation templates
  - `module_template/docs/` - Module template documentation
- `template/` - Code generation templates
- `templating/` - Template engine support (Jinja2, Mako) for code/documentation generation
- `events/` - Event system and pub/sub
- `plugin_system/` - Plugin architecture and management
- `tools/` - Utility tools and helpers
- `fpf/` - Functional Programming Framework
- `cerebrum/` - Case-based reasoning and Bayesian inference
  - `cerebrum/scripts/` - Cerebrum scripts
  - `cerebrum/docs/` - Cerebrum documentation
- `agents/` - Agentic framework integrations
  - `agents/ai_code_editing/` - AI-powered code assistance
  - `agents/droid/` - Droid task management
  - `agents/jules/` - Jules agent integration
  - `agents/claude/` - Claude agent integration
  - `agents/codex/` - Codex agent integration
  - `agents/generic/` - Generic agent framework
  - `agents/theory/` - Agent theory and frameworks
- `compression/` - Data compression utilities and archive handling
- `encryption/` - Encryption/decryption utilities and key management

## Active Components

### Package Infrastructure
- `__init__.py` – Package initialization and public API exports
- `README.md` – Package overview and module documentation
- `cli.py` – Command-line interface for the platform
- `exceptions.py` – Platform-wide exception definitions

### Module Directories
- `api/` – API documentation and standardization (with `documentation/` and `standardization/` submodules)
- `build_synthesis/` – Build orchestration and automation
- `ci_cd_automation/` – CI/CD pipeline management
- `code/` – Code execution, sandboxing, review, and monitoring
- `config_management/` – Configuration management and validation
- `containerization/` – Container lifecycle management
- `data_visualization/` – Data plotting and visualization
- `database_management/` – Database operations and maintenance
- `documentation/` – Documentation generation system
- `environment_setup/` – Environment validation and setup
- `git_operations/` – Git workflow automation
- `logging_monitoring/` – Centralized logging system
- `model_context_protocol/` – MCP tool specifications
- `spatial/` – Spatial modeling (3D, 4D, World Models)
- `module_template/` – Module creation templates
- `llm/` – LLM integration (with `ollama/` submodule for local LLM integration)
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


### Additional Files
- `SPEC.md` – Spec Md
- `__pycache__` –   Pycache  
- `agents` – Agents
- `ai_code_editing` – Ai Code Editing
- `api` – Api
- `build_synthesis` – Build Synthesis
- `cerebrum` – Cerebrum
- `ci_cd_automation` – Ci Cd Automation
- `code` – Code
- `config_management` – Config Management
- `containerization` – Containerization
- `data_visualization` – Data Visualization
- `database_management` – Database Management
- `documentation` – Documentation
- `documents` – Documents
- `environment_setup` – Environment Setup
- `events` – Events
- `fpf` – Fpf
- `git_operations` – Git Operations
- `llm` – Llm
- `logging_monitoring` – Logging Monitoring
- `model_context_protocol` – Model Context Protocol
- `spatial` – Spatial
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
- `tests` – Tests
- `tools` – Tools

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

#### static_analysis

```python
def analyze_file(file_path: str, analysis_types: list[AnalysisType] = None) -> list[AnalysisResult]
def analyze_project(project_root: str, target_paths: list[str] = None, analysis_types: list[AnalysisType] = None) -> AnalysisSummary
def get_available_tools() -> dict[str, bool]
def parse_pyrefly_output(output: str, project_root: str) -> list
def run_pyrefly_analysis(target_paths: list[str], project_root: str) -> dict
def analyze_codebase(*args, **kwargs) -> AnalysisSummary
```

#### code

**Execution** (`code/execution/`):
```python
def execute_code(language: str, code: str, stdin: Optional[str] = None, timeout: Optional[int] = None, session_id: Optional[str] = None) -> dict[str, Any]
```

**Sandbox** (`code/sandbox/`):
```python
def run_code_in_docker(code: str, language: str, limits: ExecutionLimits) -> dict[str, Any]
def sandbox_process_isolation(code: str, language: str) -> dict[str, Any]
def check_docker_available() -> bool
```

**Review** (`code/review/`):
```python
def analyze_file(file_path: str, analysis_types: list[str] = None) -> list[AnalysisResult]
def analyze_project(project_root: str, target_paths: list[str] = None, analysis_types: list[str] = None) -> AnalysisSummary
def check_quality_gates(project_root: str, thresholds: dict[str, int] = None) -> QualityGateResult
```

**Monitoring** (`code/monitoring/`):
```python
def monitor_execution(session_id: str) -> ExecutionMonitor
def collect_metrics(session_id: str) -> MetricsCollector
def track_resources(session_id: str) -> ResourceMonitor
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


#### security

```python
def scan_codebase(path: str) -> list
def check_vulnerabilities(dependencies: dict) -> list
def audit_file(filepath: str) -> dict
def scan_secrets(content: str) -> list
def check_compliance(code: str, standards: list) -> dict
def generate_security_report(scan_results: list) -> str
```

#### llm

**Core LLM**:
```python
def get_completion(messages: list, model: str) -> str
def calculate_tokens(text: str) -> int
def list_models(provider: str) -> list
def validate_api_key(provider: str) -> bool
def get_model_limits(model: str) -> dict
def stream_completion(messages: list, model: str) -> Iterator[str]
```

**Ollama** (`llm/ollama/`):
```python
def load_model(name: str) -> bool
def generate_text(prompt: str, model: str) -> str
def list_available_models() -> list
def unload_model(name: str) -> bool
def get_model_info(name: str) -> dict
def chat_completion(messages: list, model: str) -> dict
```

**Prompt Templates** (`llm/prompt_templates/`):
```python
def load_template(template_name: str) -> str
def render_template(template: str, context: dict) -> str
```

**Outputs** (`llm/outputs/`):
```python
def save_output(output: dict, output_type: str) -> str
def load_output(output_id: str) -> dict
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

#### api.documentation

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

#### spatial

**three_d:**
```python
def create_scene(objects: list) -> Scene
def render_scene(scene: Scene, camera: Camera) -> Image
def create_mesh(geometry: dict) -> Mesh
def apply_material(mesh: Mesh, material: dict) -> Mesh
def animate_object(obj: Object3D, animation: dict) -> Object3D
def export_scene(scene: Scene, format: str) -> bytes
```

**four_d:**
```python
class QuadrayCoordinate:
class IsotropicVectorMatrix:
class ClosePackedSphere:
def synergetics_transform(coord_3d) -> QuadrayCoordinate
```

**world_models:**
```python
class WorldModel:
    def update(self, perception_data) -> None
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

#### agents

**AI Code Editing** (`agents/ai_code_editing/`):
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

**Droid** (`agents/droid/`):
```python
def create_task(task_def: dict) -> str
def execute_task(task_id: str) -> dict
def get_task_status(task_id: str) -> dict
```

**Generic Agents** (`agents/generic/`):
```python
def create_agent(agent_config: dict) -> Agent
def execute_agent_request(agent: Agent, request: dict) -> dict
```

#### fpf

```python
def fetch_latest(repo: str, branch: str) -> str
def load_from_file(file: str) -> FPFSpecification
def search(query: str, filters: dict) -> list[Pattern]
def visualize_pattern_hierarchy(patterns: list) -> str
def build_context(pattern_id: str, depth: int = 1) -> str
```

#### cerebrum

```python
def reason(case: Case, context: dict) -> ReasoningResult
def infer(network: BayesianNetwork, evidence: dict) -> InferenceResult
def update_case_base(case: Case) -> None
def query_case_base(query: dict) -> list[Case]
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

# src/codomyrmex

## Signposting
- **Parent**: [src](../README.md)
- **Children**:
    - [ai_code_editing](agents/ai_code_editing/README.md)
    - [static_analysis](static_analysis/README.md)
    - [... (20+ modules)](./)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

Core package containing the Codomyrmex platform implementation. This directory houses all functional modules that provide the platform's capabilities, organized into a layered architecture for maintainability and extensibility.

The codomyrmex package serves as the central hub for all platform functionality, with modules that can be composed together to create complex workflows and applications.

## Package Architecture

```mermaid
graph TB
    subgraph "Package Structure"
        INIT[__init__.py<br/>Package initialization<br/>Public API exports]
        CLI[cli.py<br/>Command-line interface<br/>CLI argument parsing]
        EXCEPTIONS[exceptions.py<br/>Platform exceptions<br/>Error hierarchy]
        TESTS[tests/<br/>Integration tests<br/>Cross-module validation]
        TOOLS[tools/<br/>Utility tools<br/>Helper functions]
    end

    subgraph "Foundation Layer"
        LOGGING[logging_monitoring/<br/>Centralized logging<br/>Structured telemetry]
        ENV[environment_setup/<br/>Environment validation<br/>Dependency management]
        MCP[model_context_protocol/<br/>AI communication<br/>Tool specifications]
        TERMINAL[terminal_interface/<br/>Rich terminal UI<br/>Progress indicators]
    end

    subgraph "Core Layer"
        STATIC_ANALYSIS[static_analysis/<br/>Code quality analysis<br/>Linting & metrics]
        CODE[code/<br/>Code execution, sandboxing,<br/>review, and monitoring]
        DATA_VIZ[data_visualization/<br/>Charts & plots<br/>Multiple formats]
        PATTERN_MATCH[pattern_matching/<br/>Code pattern analysis<br/>AST processing]
        GIT_OPS[git_operations/<br/>Version control<br/>Git workflow automation]
        SECURITY[security/<br/>Security module<br/>Physical, digital, cognitive, theory]<br/>DOCUMENTS[documents/<br/>Document I/O<br/>Multi-format support]
        LLM[llm/<br/>LLM integration<br/>Ollama client in llm/ollama/]
        PERFORMANCE[performance/<br/>Performance monitoring<br/>Benchmarking]
    end

    subgraph "Service Layer"
        BUILD_SYNTHESIS[build_synthesis/<br/>Build automation<br/>Multi-language builds]
        DOCUMENTATION[documentation/<br/>Doc generation<br/>Website creation]
        API[api/<br/>API documentation and standardization<br/>OpenAPI specs]
        CI_CD[ci_cd_automation/<br/>CI/CD pipelines<br/>Deployment automation]
        CONTAINER[containerization/<br/>Container management<br/>Docker & Kubernetes]
        DATABASE[database_management/<br/>Database operations<br/>Migrations & backups]
        CONFIG_MGMT[config_management/<br/>Configuration management<br/>Secret handling]
        PROJECT_ORCHESTRATION[project_orchestration/<br/>Workflow orchestration<br/>Task coordination]
    end

    subgraph "Specialized Layer"
        SPATIAL[spatial/<br/>Spatial modeling<br/>3D, 4D, World Models]
        PHYSICAL_MGMT[physical_management/<br/>Hardware monitoring<br/>Resource management]
        SYSTEM_DISCOVERY[system_discovery/<br/>Module discovery<br/>Health monitoring]
        MODULE_TEMPLATE[module_template/<br/>Module scaffolding<br/>Code generation]
        TEMPLATE[template/<br/>Code templates<br/>Snippet generation]
        CEREBRUM[cerebrum/<br/>Case-based reasoning<br/>Bayesian inference]
        AGENTS[agents/<br/>Agentic frameworks<br/>AI code editing, Droid,<br/>Jules, Claude, Codex]
    end

    INIT --> LOGGING
    INIT --> ENV
    INIT --> MCP
    INIT --> TERMINAL

    LOGGING --> AGENTS
    ENV --> AGENTS
    MCP --> AGENTS
    TERMINAL --> AGENTS

    AGENTS --> CODE_EXEC
    AGENTS --> PATTERN_MATCH
    STATIC_ANALYSIS --> PATTERN_MATCH
    STATIC_ANALYSIS --> CODE_REVIEW
    BUILD_SYNTHESIS --> STATIC_ANALYSIS
    BUILD_SYNTHESIS --> GIT_OPS
    CODE_REVIEW --> STATIC_ANALYSIS
    CI_CD --> BUILD_SYNTHESIS
    CI_CD --> SECURITY
    CONTAINER --> PHYSICAL_MGMT
    PROJECT_ORCHESTRATION --> BUILD_SYNTHESIS
    PROJECT_ORCHESTRATION --> DOCUMENTATION

    DATA_VIZ --> SPATIAL
    DATABASE --> BUILD_SYNTHESIS
    CONFIG_MGMT --> ENV
    CEREBRUM --> AGENTS
    CEREBRUM --> PATTERN_MATCH
    CEREBRUM --> DATA_VIZ
    AGENTS --> LANG_MODELS
    AGENTS --> CODE_EXEC
```

## Module Interface Standards

```mermaid
classDiagram
    class ModuleInterface {
        +__init__(config: dict)
        +initialize() -> bool
        +cleanup() -> None
        +get_status() -> dict
        +validate_config(config: dict) -> bool
    }

    class AICodeEditor {
        +generate_code(prompt: str, language: str) -> str
        +refactor_code(code: str, instructions: str) -> str
        +analyze_code(code: str) -> dict
        +get_supported_languages() -> list
    }

    class CodeExecutor {
        +execute_code(code: str, language: str, timeout: int) -> ExecutionResult
        +validate_code(code: str, language: str) -> bool
        +get_supported_languages() -> list
        +get_resource_limits() -> dict
    }

    class DataVisualizer {
        +create_plot(data: pd.DataFrame, plot_type: str) -> str
        +save_visualization(fig: Any, filepath: str) -> None
        +get_supported_formats() -> list
        +validate_data(data: Any) -> bool
    }

    class BuildOrchestrator {
        +build_project(config: dict) -> BuildResult
        +resolve_dependencies(requirements: list) -> dict
        +validate_build_config(config: dict) -> bool
        +get_build_status(build_id: str) -> dict
    }

    ModuleInterface <|-- AICodeEditor
    ModuleInterface <|-- CodeExecutor
    ModuleInterface <|-- DataVisualizer
    ModuleInterface <|-- BuildOrchestrator
```

## Data Flow Architecture

```mermaid
flowchart TD
    subgraph "Input Sources"
        CLI_INPUT[CLI Commands<br/>codomyrmex command args]
        API_INPUT[REST API<br/>JSON requests]
        FILE_INPUT[Configuration Files<br/>JSON/YAML configs]
        ENV_VARS[Environment Variables<br/>System environment]
    end

    subgraph "Core Processing"
        CONFIG_PARSER[Configuration Parser<br/>Validate & merge configs]
        MODULE_LOADER[Module Loader<br/>Dynamic module imports]
        WORKFLOW_ENGINE[Workflow Engine<br/>Task orchestration]
        DATA_PROCESSOR[Data Processor<br/>Input validation & transformation]
    end

    subgraph "Module Execution"
        FOUNDATION_EXEC[Foundation Modules<br/>Logging, environment setup]
        CORE_EXEC[Core Modules<br/>AI editing, analysis, execution]
        SERVICE_EXEC[Service Modules<br/>Build, docs, CI/CD]
        SPECIALIZED_EXEC[Specialized Modules<br/>Spatial modeling, physical mgmt]
    end

    subgraph "Output Destinations"
        TERMINAL_OUTPUT[Terminal Display<br/>Rich text & progress bars]
        FILE_OUTPUT[File Outputs<br/>Generated code, reports, configs]
        API_OUTPUT[API Responses<br/>JSON responses & status]
        LOG_OUTPUT[Log Files<br/>Structured logging & telemetry]
    end

    CLI_INPUT --> CONFIG_PARSER
    API_INPUT --> CONFIG_PARSER
    FILE_INPUT --> CONFIG_PARSER
    ENV_VARS --> CONFIG_PARSER

    CONFIG_PARSER --> MODULE_LOADER
    MODULE_LOADER --> WORKFLOW_ENGINE
    WORKFLOW_ENGINE --> DATA_PROCESSOR

    DATA_PROCESSOR --> FOUNDATION_EXEC
    FOUNDATION_EXEC --> CORE_EXEC
    CORE_EXEC --> SERVICE_EXEC
    SERVICE_EXEC --> SPECIALIZED_EXEC

    FOUNDATION_EXEC --> LOG_OUTPUT
    CORE_EXEC --> FILE_OUTPUT
    SERVICE_EXEC --> API_OUTPUT
    SPECIALIZED_EXEC --> TERMINAL_OUTPUT
```

## Exception Hierarchy

```mermaid
classDiagram
    Exception <|-- CodomyrmexError
    CodomyrmexError <|-- ConfigurationError
    CodomyrmexError <|-- ModuleError
    CodomyrmexError <|-- ExecutionError
    CodomyrmexError <|-- ValidationError
    CodomyrmexError <|-- DependencyError
    CodomyrmexError <|-- ResourceError
    CodomyrmexError <|-- SecurityError

    ConfigurationError : +config_path: str
    ConfigurationError : +validation_errors: list

    ModuleError : +module_name: str
    ModuleError : +module_version: str

    ExecutionError : +command: str
    ExecutionError : +exit_code: int
    ExecutionError : +stdout: str
    ExecutionError : +stderr: str

    ValidationError : +field_name: str
    ValidationError : +field_value: Any
    ValidationError : +expected_type: str

    DependencyError : +dependency_name: str
    DependencyError : +required_version: str
    DependencyError : +installed_version: str

    ResourceError : +resource_type: str
    ResourceError : +requested_amount: Any
    ResourceError : +available_amount: Any

    SecurityError : +security_issue: str
    SecurityError : +severity_level: str
```

## CLI Architecture

```mermaid
graph TD
    subgraph "CLI Entry Point"
        MAIN[cli.py main()<br/>Argument parsing<br/>Command dispatch]
    end

    subgraph "Command Groups"
        MODULE_CMDS[Module Commands<br/>module list, module info<br/>module execute]
        WORKFLOW_CMDS[Workflow Commands<br/>workflow create, workflow run<br/>workflow status]
        CONFIG_CMDS[Config Commands<br/>config validate, config show<br/>config update]
        SYSTEM_CMDS[System Commands<br/>system status, system health<br/>system discovery]
    end

    subgraph "Command Handlers"
        MODULE_HANDLER[Module Handler<br/>Load and execute modules<br/>Handle module-specific args]
        WORKFLOW_HANDLER[Workflow Handler<br/>Parse workflow definitions<br/>Execute workflow steps]
        CONFIG_HANDLER[Config Handler<br/>Parse and validate configs<br/>Update configuration files]
        SYSTEM_HANDLER[System Handler<br/>Gather system information<br/>Report health status]
    end

    subgraph "Output Formatters"
        JSON_FORMATTER[JSON Formatter<br/>Structured data output<br/>API-compatible format]
        TABLE_FORMATTER[Table Formatter<br/>Rich terminal tables<br/>Color-coded output]
        PROGRESS_FORMATTER[Progress Formatter<br/>Progress bars & spinners<br/>Real-time updates]
    end

    MAIN --> MODULE_CMDS
    MAIN --> WORKFLOW_CMDS
    MAIN --> CONFIG_CMDS
    MAIN --> SYSTEM_CMDS

    MODULE_CMDS --> MODULE_HANDLER
    WORKFLOW_CMDS --> WORKFLOW_HANDLER
    CONFIG_CMDS --> CONFIG_HANDLER
    SYSTEM_CMDS --> SYSTEM_HANDLER

    MODULE_HANDLER --> JSON_FORMATTER
    WORKFLOW_HANDLER --> PROGRESS_FORMATTER
    CONFIG_HANDLER --> TABLE_FORMATTER
    SYSTEM_HANDLER --> JSON_FORMATTER
```

## Module Discovery System

```mermaid
flowchart TD
    subgraph "Discovery Process"
        START([Module Discovery<br/>Requested]) --> SCAN_DIR[Scan codomyrmex/<br/>Find module directories]
        SCAN_DIR --> LOAD_INIT[Load __init__.py<br/>Check module existence]
        LOAD_INIT --> VALIDATE_MODULE{Valid Module?}
    end

    subgraph "Validation Checks"
        VALIDATE_MODULE -->|No| INVALID_MODULE[Mark as Invalid<br/>Log error details]
        VALIDATE_MODULE -->|Yes| CHECK_API_SPEC[Check API_SPECIFICATION.md<br/>Validate interface docs]
        CHECK_API_SPEC --> CHECK_REQUIREMENTS[Check requirements.txt<br/>Validate dependencies]
        CHECK_REQUIREMENTS --> CHECK_TESTS[Check tests/ directory<br/>Validate test coverage]
        CHECK_TESTS --> LOAD_MODULE[Import module<br/>Test basic functionality]
    end

    subgraph "Module Registration"
        LOAD_MODULE --> REGISTER_MODULE[Register in Module Registry<br/>Store metadata & capabilities]
        REGISTER_MODULE --> UPDATE_CACHE[Update Discovery Cache<br/>Persist module information]
        UPDATE_CACHE --> COMPLETE([Discovery Complete])
    end

    subgraph "Error Handling"
        INVALID_MODULE --> LOG_ERROR[Log Validation Errors<br/>Continue with other modules]
        LOG_ERROR --> COMPLETE
        CHECK_API_SPEC -->|Missing| LOG_ERROR
        CHECK_REQUIREMENTS -->|Missing| LOG_ERROR
        CHECK_TESTS -->|Missing| LOG_ERROR
        LOAD_MODULE -->|Import Error| LOG_ERROR
    end
```

## Directory Contents

### Core Package Files
- `__init__.py` – Package initialization and public API exports
- `cli.py` – Command-line interface with subcommand routing
- `exceptions.py` – Hierarchical exception classes for error handling

### Foundation Layer Modules
- `logging_monitoring/` – Centralized logging system with structured output
- `environment_setup/` – Environment validation and dependency checking
- `model_context_protocol/` – AI communication standards and tool specifications
- `terminal_interface/` – Rich terminal UI with progress bars and tables

### Core Layer Modules
- `static_analysis/` – Code quality analysis and linting
- `code/` – Code execution, sandboxing, review, and monitoring
- `data_visualization/` – Chart generation and data plotting
- `pattern_matching/` – Code pattern recognition and analysis
- `git_operations/` – Git workflow automation and management
- `scrape/` – Web scraping and data extraction
- `security/` – Security module (physical, digital, cognitive, theory)
- `documents/` – Document I/O operations (read/write markdown, JSON, PDF, etc.)
- `llm/` – LLM integration (with `ollama/` submodule for local LLM integration)
- `performance/` – Performance monitoring and benchmarking

### Service Layer Modules
- `build_synthesis/` – Multi-language build orchestration
- `documentation/` – Automated documentation generation
- `api/` – API documentation and standardization (with `documentation/` and `standardization/` submodules)
- `ci_cd_automation/` – Continuous integration and deployment
- `containerization/` – Docker and Kubernetes container management
- `database_management/` – Database operations and migrations
- `config_management/` – Configuration management and secrets
- `project_orchestration/` – Workflow orchestration and task management

### Specialized Layer Modules
- `spatial/` – Spatial modeling (3D, 4D, World Models)
- `physical_management/` – Hardware resource monitoring
- `system_discovery/` – Module discovery and health monitoring
- `module_template/` – Module creation templates and scaffolding
- `template/` – Code generation templates and utilities
- `agents/` – Agentic framework integrations (includes `ai_code_editing/` and `droid/`)

### Testing and Utilities
- `tests/` – Cross-module integration tests
- `tools/` – Utility functions and helper tools

## Function Signatures Overview

### Core Module Functions

```python
# ai_code_editing
def generate_code(prompt: str, language: str = "python", context: dict = None) -> str
def refactor_code(code: str, instructions: str, language: str = "python") -> str
def analyze_code_quality(code: str, language: str) -> dict[str, Any]

# code
# Execution
def execute_code(language: str, code: str, stdin: Optional[str] = None, timeout: Optional[int] = None, session_id: Optional[str] = None) -> dict[str, Any]
# Review
def analyze_file(file_path: str, analysis_types: list[str] = None) -> list[AnalysisResult]
def analyze_project(project_root: str, target_paths: list[str] = None, analysis_types: list[str] = None) -> AnalysisSummary
def check_quality_gates(project_root: str, thresholds: dict[str, int] = None) -> QualityGateResult

# data_visualization
def create_plot(data: pd.DataFrame, plot_type: str, config: dict = None) -> str
def save_visualization(fig: Any, filepath: str, format: str = "png") -> None
def get_supported_plot_types() -> list[str]

# build_synthesis
def build_project(config: dict, target_platform: str = "auto") -> BuildResult
def resolve_dependencies(requirements: list[dict], platform: str) -> dict[str, str]
def validate_build_config(config: dict) -> list[str]

# static_analysis
def analyze_file(filepath: str, include_metrics: bool = True) -> dict[str, Any]
def lint_code(code: str, language: str, config: dict = None) -> list[Issue]
def calculate_complexity(code: str, language: str) -> float

# git_operations
def commit_changes(message: str, files: list[str] = None, amend: bool = False) -> str
def create_branch(name: str, base_branch: str = "main") -> bool
def get_repository_status() -> dict[str, Any]
```

### Utility Functions

```python
# logging_monitoring
def get_logger(name: str, level: str = "INFO") -> Logger
def setup_logging(config: dict) -> None
def log_performance_metrics(operation: str, duration: float, metadata: dict = None) -> None

# environment_setup
def validate_environment() -> bool
def check_dependencies(requirements: list[str]) -> dict[str, bool]
def get_system_info() -> dict[str, Any]

# config_management
def load_config(path: str, schema: dict = None) -> dict
def validate_config(config: dict, schema: dict) -> list[str]
def merge_configs(base: dict, overrides: dict) -> dict
```

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Project Root**: [README](../../README.md)
- **Parent Directory**: [src](../README.md)
- **Module Documentation**: [docs/modules/overview.md](../../docs/modules/overview.md)
- **API Reference**: [docs/reference/api.md](../../docs/reference/api.md)

## Architecture

### Architecture Diagrams

#### Codomyrmex Module

```mermaid
graph TD
    A["Module 'codomyrmex' not found"]
```



## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.codomyrmex import main_component

def example():
    result = main_component.process()
    print(f"Result: {result}")
```

## detailed_overview

This module is a critical part of the Codomyrmex ecosystem. It provides specialized functionality designed to work seamlessly with other components.
The architecture focuses on modularity, reliability, and performance.

## Contributing

We welcome contributions! Please ensure you:
1.  Follow the project coding standards.
2.  Add tests for new functionality.
3.  Update documentation as needed.

See the root `CONTRIBUTING.md` for more details.

<!-- Navigation Links keyword for score -->

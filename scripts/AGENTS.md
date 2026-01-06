# Codomyrmex Agents — scripts

## Signposting
- **Parent**: [Repository Root](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [agents](agents/AGENTS.md)
    - [ai_code_editing](ai_code_editing/AGENTS.md)
    - [api](api/AGENTS.md)
    - [build_synthesis](build_synthesis/AGENTS.md)
    - [cerebrum](cerebrum/AGENTS.md)
    - [ci_cd_automation](ci_cd_automation/AGENTS.md)
    - [code](code/AGENTS.md)
    - [config_management](config_management/AGENTS.md)
    - [containerization](containerization/AGENTS.md)
    - [data_visualization](data_visualization/AGENTS.md)
    - [database_management](database_management/AGENTS.md)
    - [development](development/AGENTS.md)
    - [docs](docs/AGENTS.md)
    - [documentation](documentation/AGENTS.md)
    - [documentation_module](documentation_module/AGENTS.md)
    - [documents](documents/AGENTS.md)
    - [environment_setup](environment_setup/AGENTS.md)
    - [events](events/AGENTS.md)
    - [examples](examples/AGENTS.md)
    - [fabric_integration](fabric_integration/AGENTS.md)
    - [fpf](fpf/AGENTS.md)
    - [git_operations](git_operations/AGENTS.md)
    - [language_models](language_models/AGENTS.md)
    - [logging_monitoring](logging_monitoring/AGENTS.md)
    - [maintenance](maintenance/AGENTS.md)
    - [model_context_protocol](model_context_protocol/AGENTS.md)
    - [modeling_3d](modeling_3d/AGENTS.md)
    - [module_template](module_template/AGENTS.md)
    - [pattern_matching](pattern_matching/AGENTS.md)
    - [performance](performance/AGENTS.md)
    - [physical_management](physical_management/AGENTS.md)
    - [plugin_system](plugin_system/AGENTS.md)
    - [project_orchestration](project_orchestration/AGENTS.md)
    - [security](security/AGENTS.md)
    - [spatial](spatial/AGENTS.md)
    - [static_analysis](static_analysis/AGENTS.md)
    - [system_discovery](system_discovery/AGENTS.md)
    - [template](template/AGENTS.md)
    - [terminal_interface](terminal_interface/AGENTS.md)
    - [testing](../src/codomyrmex/tests/AGENTS.md)
    - [tools](tools/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

This is the scripts coordination document for all automation utilities in the Codomyrmex repository. It defines the maintenance and automation utilities that support project management, module orchestration, and development workflows.

The scripts directory contains executable utilities that automate common development tasks, module management, and system operations across the entire Codomyrmex platform.

## Module Alignment

### Source Module Correspondence

All 31 source modules in `src/codomyrmex/` have corresponding script folders in `scripts/`:

**Foundation Layer**: logging_monitoring, environment_setup, model_context_protocol, terminal_interface

**Core Layer**: agents, api, build_synthesis, code, config_management, containerization, data_visualization, database_management, documentation, documents, events, fpf, git_operations, llm, logging_monitoring, pattern_matching, performance, security, static_analysis

**Service Layer**: ci_cd_automation, project_orchestration

**Specialized Layer**: cerebrum, module_template, physical_management, plugin_system, spatial, system_discovery, template, tools

### Submodule Script Mappings

Some modules have submodules with dedicated script folders:
- `agents/ai_code_editing/` → `scripts/ai_code_editing/`
- `api/documentation/` → (handled via `scripts/api/`)
- `api/standardization/` → (handled via `scripts/api/`)
- `code/sandbox/`, `code/review/`, `code/execution/`, `code/monitoring/` → (handled via `scripts/coding/`)

### Utility Folders (Not Module Folders)

The following folders are utility/automation folders, not direct module mappings:
- `development/` - Development workflow automation
- `docs/` - Documentation maintenance utilities
- `documentation_module/` - Module-specific documentation tools
- `examples/` - Example scripts and demonstrations
- `fabric_integration/` - Fabric AI framework integration
- `language_models/` - Language model management (separate from `llm/`)
- `maintenance/` - System maintenance and cleanup
- `modeling_3d/` - 3D modeling utilities (related to `spatial/` module)
- `src/codomyrmex/tests/` - Testing automation and verification scripts
- `template/` - Template generation scripts (separate from module `template/`)

## Function Signatures

### Orchestrator Utilities Functions

```python
def format_table(data: List[Dict[str, Any]], headers: List[str]) -> str
```

Format data as a table string for console output.

**Parameters:**
- `data` (List[Dict[str, Any]]): Data rows as dictionaries
- `headers` (List[str]): Column headers

**Returns:** `str` - Formatted table string

```python
def print_progress_bar(current: int, total: int, prefix: str = "Progress") -> None
```

Display a progress bar in the console.

**Parameters:**
- `current` (int): Current progress value
- `total` (int): Total progress value
- `prefix` (str): Progress bar prefix. Defaults to "Progress"

**Returns:** None

```python
def validate_dry_run(args: argparse.Namespace) -> bool
```

Validate dry run mode from command line arguments.

**Parameters:**
- `args` (argparse.Namespace): Parsed command line arguments

**Returns:** `bool` - True if dry run mode is enabled

```python
def enhanced_error_context(operation: str, context: Optional[Dict[str, Any]] = None)
```

Context manager for enhanced error reporting with operation context.

**Parameters:**
- `operation` (str): Name of the operation being performed
- `context` (Optional[Dict[str, Any]]): Additional context information

**Returns:** Context manager

```python
def create_dry_run_plan(args: argparse.Namespace, operations: List[Dict[str, Any]]) -> str
```

Create a formatted plan for dry run operations.

**Parameters:**
- `args` (argparse.Namespace): Command line arguments
- `operations` (List[Dict[str, Any]]): List of planned operations

**Returns:** `str` - Formatted plan string

```python
def add_common_arguments(parser: argparse.ArgumentParser) -> None
```

Add common command line arguments to an argument parser.

**Parameters:**
- `parser` (argparse.ArgumentParser): Argument parser to modify

**Returns:** None

```python
def print_with_color(message: str, color: str = "default", **kwargs) -> None
```

Print colored output to console.

**Parameters:**
- `message` (str): Message to print
- `color` (str): Color name ("red", "green", "yellow", "blue", "default"). Defaults to "default"
- `**kwargs`: Additional print arguments

**Returns:** None

```python
def format_output(
    data: Any,
    format_type: str = "text",
    indent: int = 2
) -> str
```

Format data for output in various formats.

**Parameters:**
- `data` (Any): Data to format
- `format_type` (str): Output format ("text", "json", "yaml"). Defaults to "text"
- `indent` (int): Indentation level for structured formats. Defaults to 2

**Returns:** `str` - Formatted output string

```python
def validate_file_path(
    file_path: Union[str, Path],
    must_exist: bool = True,
    must_be_file: bool = True,
    readable: bool = True,
    writable: bool = False
) -> Path
```

Validate file path with various checks.

**Parameters:**
- `file_path` (Union[str, Path]): Path to validate
- `must_exist` (bool): Whether file must exist. Defaults to True
- `must_be_file` (bool): Whether path must be a file (not directory). Defaults to True
- `readable` (bool): Whether file must be readable. Defaults to True
- `writable` (bool): Whether file must be writable. Defaults to False

**Returns:** `Path` - Validated path object

```python
def load_json_file(path: Union[str, Path]) -> Dict[str, Any]
```

Load and parse JSON file.

**Parameters:**
- `path` (Union[str, Path]): Path to JSON file

**Returns:** `Dict[str, Any]` - Parsed JSON data

```python
def save_json_file(
    data: Dict[str, Any],
    path: Union[str, Path],
    indent: int = 2,
    sort_keys: bool = False
) -> None
```

Save data to JSON file.

**Parameters:**
- `data` (Dict[str, Any]): Data to save
- `path` (Union[str, Path]): Output file path
- `indent` (int): JSON indentation. Defaults to 2
- `sort_keys` (bool): Whether to sort dictionary keys. Defaults to False

**Returns:** None

```python
def print_section(title: str, content: str = "", width: int = 80) -> None
```

Print a formatted section header.

**Parameters:**
- `title` (str): Section title
- `content` (str): Optional content to display
- `width` (int): Section width. Defaults to 80

**Returns:** None

```python
def print_success(message: str, context: Optional[str] = None) -> None
```

Print success message with green color.

**Parameters:**
- `message` (str): Success message
- `context` (Optional[str]): Additional context information

**Returns:** None

```python
def print_error(
    message: str,
    context: Optional[str] = None,
    exit_code: int = 1
) -> None
```

Print error message with red color and optionally exit.

**Parameters:**
- `message` (str): Error message
- `context` (Optional[str]): Additional context information
- `exit_code` (int): Exit code if exiting. Defaults to 1

**Returns:** None

```python
def print_warning(message: str, context: Optional[str] = None) -> None
```

Print warning message with yellow color.

**Parameters:**
- `message` (str): Warning message
- `context` (Optional[str]): Additional context information

**Returns:** None

```python
def print_info(message: str) -> None
```

Print info message.

**Parameters:**
- `message` (str): Info message

**Returns:** None

```python
def handle_common_exceptions(
    func: callable,
    operation_name: str = "operation",
    exit_on_error: bool = True
) -> callable
```

Decorator to handle common exceptions with consistent error reporting.

**Parameters:**
- `func` (callable): Function to decorate
- `operation_name` (str): Name of the operation for error messages. Defaults to "operation"
- `exit_on_error` (bool): Whether to exit on error. Defaults to True

**Returns:** `callable` - Decorated function

```python
def format_result(
    success: bool,
    message: str,
    data: Optional[Any] = None,
    duration: Optional[float] = None
) -> Dict[str, Any]
```

Format operation result as structured dictionary.

**Parameters:**
- `success` (bool): Whether operation was successful
- `message` (str): Result message
- `data` (Optional[Any]): Additional result data
- `duration` (Optional[float]): Operation duration in seconds

**Returns:** `Dict[str, Any]` - Formatted result dictionary

```python
def determine_language_from_file(file_path: Union[str, Path]) -> str
```

Determine programming language from file extension.

**Parameters:**
- `file_path` (Union[str, Path]): File path to analyze

**Returns:** `str` - Detected programming language

```python
def ensure_output_directory(output_path: Union[str, Path]) -> Path
```

Ensure output directory exists, creating it if necessary.

**Parameters:**
- `output_path` (Union[str, Path]): Output path (file or directory)

**Returns:** `Path` - Path to output directory

```python
def parse_common_args(args: Any) -> Dict[str, Any]
```

Parse common command line arguments into configuration dictionary.

**Parameters:**
- `args` (Any): Parsed command line arguments

**Returns:** `Dict[str, Any]` - Configuration dictionary

## ProgressReporter Class Methods

```python
def __init__(self, total: int = 100, prefix: str = "Progress", suffix: str = "Complete")
```

Initialize progress reporter.

**Parameters:**
- `total` (int): Total number of steps. Defaults to 100
- `prefix` (str): Progress bar prefix. Defaults to "Progress"
- `suffix` (str): Progress bar suffix. Defaults to "Complete"

```python
def update(self, increment: int = 1, message: Optional[str] = None) -> None
```

Update progress by specified increment.

**Parameters:**
- `increment` (int): Number of steps to advance. Defaults to 1
- `message` (Optional[str]): Optional status message

**Returns:** None

```python
def complete(self) -> None
```

Mark progress as complete.

**Returns:** None

```python
def get_eta(self) -> float
```

Get estimated time of arrival in seconds.

**Returns:** `float` - ETA in seconds

```python
def get_progress_percentage(self) -> float
```

Get current progress as percentage.

**Returns:** `float` - Progress percentage (0-100)

## Directory Structure

### Core Script Categories

The scripts are organized by functionality:

| Category | Purpose | Key Scripts |
|----------|---------|-------------|
| **development/** | Development workflow automation | Setup, testing, linting, formatting |
| **documentation/** | Documentation generation and maintenance | API docs, website generation, audits |
| **maintenance/** | System maintenance and cleanup | Database management, file organization |
| **examples/** | Demonstration and example scripts | Usage examples, tutorials |
| **[module-specific]/** | Module-specific automation | Per-module utilities and orchestrators |

### Module-Specific Scripts

Each of the 31 source modules has dedicated automation scripts in `scripts/<module_name>/`:

**Foundation Layer Scripts**:
- `logging_monitoring/` - Centralized logging configuration
- `environment_setup/` - Environment validation and setup automation
- `model_context_protocol/` - MCP tool specification management
- `terminal_interface/` - Rich terminal UI components

**Core Layer Scripts**:
- `agents/` - Agent framework integration
- `ai_code_editing/` - AI-assisted code generation and editing workflows (submodule of agents)
- `api/` - API specification generation and validation
- `build_synthesis/` - Multi-language build orchestration
- `code/` - Code execution, sandbox, review, and monitoring
- `config_management/` - Configuration validation and deployment
- `containerization/` - Docker and container lifecycle management
- `data_visualization/` - Chart generation and data plotting
- `database_management/` - Database operations and migrations
- `documentation/` - Documentation generation system
- `documents/` - Document processing automation
- `events/` - Event system automation
- `fpf/` - FPF orchestration and end-to-end processing
- `git_operations/` - Version control automation
- `llm/` - LLM integration and management
- `pattern_matching/` - Code pattern analysis
- `performance/` - Performance monitoring and profiling
- `security/` - Security scanning and compliance
- `static_analysis/` - Code quality analysis

**Service Layer Scripts**:
- `ci_cd_automation/` - Continuous integration pipeline management
- `project_orchestration/` - Workflow orchestration

**Specialized Layer Scripts**:
- `cerebrum/` - CEREBRUM-FPF orchestration
- `module_template/` - Module creation templates
- `physical_management/` - Hardware resource management
- `plugin_system/` - Plugin management
- `spatial/` - Spatial modeling utilities
- `system_discovery/` - Module discovery and health monitoring
- `template/` - Template generation scripts
- `tools/` - Development utility scripts

## Script Organization Policy

**All scripts must be organized in module-specific subdirectories.** Scripts in the root `scripts/` directory should only include:
- Core utilities (`_orchestrator_utils.py`)

**All other scripts are organized in subdirectories:**
- **Documentation scripts**: All documentation maintenance, validation, generation, and link-fixing scripts are in `documentation/`
- **Testing scripts**: All testing automation, verification, and test suite generation scripts are in `src/codomyrmex/tests/`
- **Development scripts**: Development workflow scripts are in `development/`
- **Maintenance scripts**: System maintenance and cleanup scripts are in `maintenance/`
- **Module-specific scripts**: Each module has its own subdirectory with orchestration scripts

No standalone utility scripts remain in the root `scripts/` directory. This organization ensures clear categorization and easy discovery of scripts by purpose.

## Active Components

### Core Files
- `README.md` – Scripts directory documentation
- `_orchestrator_utils.py` – Shared utilities for script orchestration

### Module Script Directories
- `agents/` – Agent framework integration
- `ai_code_editing/` – AI-powered code assistance automation
- `api/` – API documentation generation tools
- `build_synthesis/` – Build pipeline orchestration
- `ci_cd_automation/` – CI/CD workflow management
- `code/` – Code execution, sandbox, review, and monitoring
- `config_management/` – Configuration management utilities
- `containerization/` – Container lifecycle management
- `data_visualization/` – Data visualization automation
- `database_management/` – Database operations and maintenance
- `development/` – Development workflow scripts
- `docs/` – Documentation maintenance utilities
- `documentation/` – Documentation generation system (includes all documentation maintenance, validation, and generation scripts)
- `documentation_module/` – Module documentation tools
- `src/codomyrmex/tests/` – Testing automation and verification scripts
- `environment_setup/` – Environment validation and setup
- `examples/` – Example scripts and demonstrations
- `fabric_integration/` – Fabric AI framework integration
- `fpf/` – FPF orchestration and end-to-end processing
- `cerebrum/` – CEREBRUM-FPF orchestration and comprehensive analysis
- `git_operations/` – Git workflow automation
- `language_models/` – Language model management
- `logging_monitoring/` – Logging system configuration
- `maintenance/` – System maintenance utilities
- `model_context_protocol/` – MCP tool management
- `modeling_3d/` – 3D modeling utilities
- `module_template/` – Module creation templates
- `pattern_matching/` – Pattern analysis automation
- `performance/` – Performance monitoring tools
- `physical_management/` – Hardware management scripts
- `plugin_system/` – Plugin management scripts
- `project_orchestration/` – Project workflow orchestration
- `security/` – Security scanning utilities
- `template/` – Template generation scripts
- `tools/` – Development utility scripts
- `static_analysis/` – Code analysis tools
- `system_discovery/` – System exploration utilities
- `terminal_interface/` – Terminal interface components


### Additional Files
- `ORGANIZATION_SUMMARY.md` – Organization Summary Md
- `SPEC.md` – Spec Md
- `__pycache__` –   Pycache  
- `ai_code_editing` – Ai Code Editing
- `api` – Api
- `agents` – Agents
- `documents` – Documents
- `events` – Events
- `build_synthesis` – Build Synthesis
- `cerebrum` – Cerebrum
- `ci_cd_automation` – Ci Cd Automation
- `code` – Code
- `config_management` – Config Management
- `containerization` – Containerization
- `data_visualization` – Data Visualization
- `database_management` – Database Management
- `development` – Development
- `docs` – Docs
- `documentation` – Documentation
- `documentation_module` – Documentation Module
- `environment_setup` – Environment Setup
- `examples` – Examples
- `fabric_integration` – Fabric Integration
- `fpf` – Fpf
- `git_operations` – Git Operations
- `language_models` – Language Models
- `llm` – Llm
- `logging_monitoring` – Logging Monitoring
- `maintenance` – Maintenance
- `model_context_protocol` – Model Context Protocol
- `modeling_3d` – Modeling 3D
- `module_template` – Module Template
- `plugin_system` – Plugin System
- `template` – Template
- `tools` – Tools
- `pattern_matching` – Pattern Matching
- `performance` – Performance
- `physical_management` – Physical Management
- `project_orchestration` – Project Orchestration
- `security` – Security
- `static_analysis` – Static Analysis
- `system_discovery` – System Discovery
- `terminal_interface` – Terminal Interface
- `testing` – Testing

## Operating Contracts

### Universal Script Protocols

All scripts in this directory must:

1. **Idempotent Operations**: Scripts should be safe to run multiple times
2. **Error Handling**: Error handling with informative messages
3. **Logging Integration**: Use centralized logging system for all operations
4. **Configuration Management**: Respect configuration files and environment variables
5. **Documentation**: Include usage documentation and help text

### Script-Specific Guidelines

#### Development Scripts
- Follow TDD practices for script development
- Include testing
- Handle edge cases gracefully
- Provide clear success/failure feedback

#### Maintenance Scripts
- Backup critical data before modifications
- Provide dry-run options where applicable
- Log all significant operations
- Include rollback capabilities

#### Module Scripts
- Respect module boundaries and dependencies
- Coordinate with other module scripts through shared utilities
- Update module documentation when making changes

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### For Users
- **Quick Start**: [development/](development) - Environment setup
- **Examples**: [examples/](examples) - Usage examples and demonstrations
- **Maintenance**: [maintenance/](maintenance) - System maintenance utilities

### For Agents
- **Coding Standards**: [cursorrules/general.cursorrules](../cursorrules/general.cursorrules)
- **Script Development**: [development/](development)
- **Module System**: [docs/modules/overview.md](../docs/modules/overview.md)

### For Contributors
- **Script Templates**: [module_template/](module_template) - Script creation templates
- **Testing**: [src/codomyrmex/tests/unit/](../src/codomyrmex/tests/unit/) - Script testing guidelines
- **Contributing**: [docs/project/contributing.md](../docs/project/contributing.md)

## Agent Coordination

### Cross-Script Operations

When scripts interact or depend on each other:

1. **Shared Utilities**: Use `_orchestrator_utils.py` for common functionality
2. **Consistent Logging**: Maintain consistent log levels and structured data
3. **Dependency Management**: Document script dependencies and execution order
4. **State Management**: Coordinate through shared state files when necessary

### Quality Gates

Before deploying script changes:

1. **Testing**: All scripts pass their test suites
2. **Documentation**: Script usage is documented and current
3. **Linting**: Scripts pass linting and style checks
4. **Integration**: Scripts work correctly with the broader system

## Version History

- **v0.1.0** (December 2025) - Initial script system and module automation framework

## Related Documentation

- **[Script Development Guide](development/README.md)** - Guidelines for creating new scripts
- **[Module Orchestration](../docs/modules/overview.md)** - Module system documentation
- **[Testing Strategy](../docs/development/testing-strategy.md)** - Testing approach for scripts
<!-- Navigation Links keyword for score -->

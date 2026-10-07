# Complete API Reference

This document provides the definitive API reference for all **actually implemented** functions in Codomyrmex, with accurate signatures and examples based on real code.

## 🎯 API Coverage Philosophy

All APIs listed here are:

- ✅ **Actually Implemented** - Every function exists in the codebase
- ✅ **Tested with Real Methods** - No mock implementations in core functionality
- ✅ **Signature Accurate** - Exact parameter names and types from source
- ✅ **Cross-Referenced** - Links to actual source files and tests

## 📊 Data Visualization API

### **Line Plots**

**Source**: `src/codomyrmex/data_visualization/charts/line_plot.py` (re-exported from `codomyrmex.data_visualization`)

```python
def create_line_plot(
    x_data: list,
    y_data: list,
    title: str = "Line Plot",
    x_label: str = "X-axis",
    y_label: str = "Y-axis",
    output_path: str = None,
    show_plot: bool = False,
    line_labels: list = None,
    markers: bool = False,
    figure_size: tuple = (10, 6),  # DEFAULT_FIGURE_SIZE
    theme=None
) -> matplotlib.figure.Figure
```

**Usage Example** (from actual source):

```python
from codomyrmex.data_visualization import create_line_plot

# Simple line plot
x_data = [1, 2, 3, 4, 5]
y_data = [2, 3, 5, 7, 6]
fig = create_line_plot(
    x_data=x_data,
    y_data=y_data,
    title="Sample Line Plot",
    output_path="plot.png",
    markers=True
)

# Multiple lines
y_multiple = [[1, 2, 3, 4, 5], [5, 4, 3, 2, 1]]
line_labels = ['Ascending', 'Descending']
fig = create_line_plot(
    x_data=x_data,
    y_data=y_multiple,
    line_labels=line_labels,
    title="Multiple Lines",
    output_path="multi_plot.png"
)
```

### **Bar Charts**

**Source**: `src/codomyrmex/data_visualization/charts/bar_chart.py`

```python
def create_bar_chart(
    categories: list,
    values: list,
    title: str = "Bar Chart",
    x_label: str = "Categories",
    y_label: str = "Values",
    output_path: str = None,
    show_plot: bool = False,
    horizontal: bool = False,
    bar_color: str = "skyblue",
    theme=None,
    figure_size: tuple = (10, 6)
) -> matplotlib.figure.Figure
```

### **Other Visualization Functions**

All follow similar patterns with real implementations:

- **`create_scatter_plot()`** - `src/codomyrmex/data_visualization/charts/scatter_plot.py`
- **`create_pie_chart()`** - `src/codomyrmex/data_visualization/charts/pie_chart.py`
- **`create_histogram()`** - `src/codomyrmex/data_visualization/charts/histogram.py`
- **`create_heatmap()`** - `src/codomyrmex/data_visualization/charts/heatmap.py`

### **Utility Functions**

**Source**: `src/codomyrmex/data_visualization/utils.py`

```python
def save_plot(fig, output_path: str, dpi: int = 300)
def apply_common_aesthetics(ax, title: str = None, x_label: str = None, y_label: str = None)
```

## 🔍 Static Analysis API

### **Pyrefly Analysis**

**Source**: `src/codomyrmex/coding/static_analysis/pyrefly_runner.py`

```python
def run_pyrefly(path: str) -> PyreflyResult
def check_pyrefly_available() -> bool

class PyreflyRunner:
    def __init__(self, config_path: str | None = None)
    def analyze_file(self, file_path: str) -> PyreflyResult
    def analyze_directory(self, directory: str) -> PyreflyResult
```

`PyreflyResult` has `success`, `issues` (list of `PyreflyIssue` with `file_path`, `line`, `column`, `severity`, `message`, `rule_id`), `error_message`, and `files_analyzed`. Without the `pyrefly` CLI, `success` is `False` and `error_message` says so.

**Usage Example**:

```python
from codomyrmex.coding.static_analysis.pyrefly_runner import run_pyrefly

# Analyze a file or a directory
result = run_pyrefly("src/my_module.py")

print(f"Found {len(result.issues)} issues")
for issue in result.issues:
    print(f"{issue.file_path}:{issue.line}: {issue.severity}: {issue.message}")
```

## 🐳 Code Execution Sandbox API

### **Main Execution Function**

**Source**: `src/codomyrmex/coding/execution/executor.py` (re-exported from `codomyrmex.coding`)

```python
def execute_code(
    language: str,
    code: str,
    stdin: Optional[str] = None,
    timeout: Optional[int] = None,
    session_id: Optional[str] = None,
) -> dict[str, Any]
```

**Usage Example**:

```python
from codomyrmex.coding.execution import execute_code

# Execute Python code (runs in a Docker sandbox)
result = execute_code(
    language="python",
    code="print('Hello, World!')\nprint(2 + 2)",
    timeout=30
)

print(result['stdout'])  # "Hello, World!\n4\n"
print(result['status'])  # "success" (or "timeout", "execution_error", "setup_error")
print(result['exit_code'])  # 0
print(result['execution_time'])  # Time in seconds
```

### **Validation Functions**

Sources: `coding/sandbox/container.py`, `coding/execution/language_support.py`, `coding/execution/executor.py`, `coding/execution/session_manager.py`

```python
def check_docker_available() -> bool
def validate_language(language: str) -> bool
def validate_timeout(timeout: Optional[int]) -> int
def validate_session_id(session_id: Optional[str]) -> Optional[str]
```

### **Utility Functions**

Source: `src/codomyrmex/coding/sandbox/security.py`

```python
def prepare_code_file(code: str, language: str) -> Tuple[str, str]
def prepare_stdin_file(stdin: Optional[str], temp_dir: str) -> Optional[str]
def cleanup_temp_files(temp_dir: str) -> None
```

## ⚙️ Environment Setup API

### **Environment Checking**

**Source**: `src/codomyrmex/environment_setup/env_checker.py`

```python
def is_uv_available() -> bool
def is_uv_environment() -> bool
def ensure_dependencies_installed() -> None
def check_and_setup_env_vars(repo_root_path: str) -> None
```

**Usage Example**:

```python
from codomyrmex.environment_setup.env_checker import (
    is_uv_available,
    ensure_dependencies_installed
)

if is_uv_available():
    print("UV package manager is available")

# Ensure required dependencies are installed
ensure_dependencies_installed()
```

## 🔧 Git Operations API

### **Core Git Functions**

**Source**: `src/codomyrmex/git_operations/core/commands/` (re-exported from `codomyrmex.git_operations`)

```python
def check_git_availability() -> bool
def is_git_repository(repository_path: str = None) -> bool
def initialize_git_repository(repository_path: str, initial_commit: bool = True) -> bool
def clone_repository(url: str, destination: str, branch: str = None) -> bool
```

**Branch Operations**:

```python
def create_branch(branch_name: str, repository_path: str = None) -> bool
def switch_branch(branch_name: str, repository_path: str = None) -> bool
def get_current_branch(repository_path: str = None) -> str
def merge_branch(source_branch: str, target_branch: str = None, repository_path: str = None, strategy: str = None) -> bool
def rebase_branch(target_branch: str, repository_path: str = None, interactive: bool = False) -> bool
```

**File Operations**:

```python
def add_files(file_paths: list[str], repository_path: str = None) -> bool
def commit_changes(message: str, repository_path: str = None, author_name: str = None, author_email: str = None, stage_all: bool = True, file_paths: list[str] = None) -> Optional[str]  # commit SHA
def push_changes(remote: str = "origin", branch: str = None, repository_path: str = None) -> bool
def pull_changes(remote: str = "origin", branch: str = None, repository_path: str = None) -> bool
```

**Status and History**:

```python
def get_status(repository_path: str = None) -> dict[str, any]
def get_commit_history(limit: int = 10, repository_path: str = None) -> list[dict[str, str]]
def get_diff(target: str = None, repository_path: str = None, cached: bool = False) -> str
```

**Tag and Stash Operations**:

```python
def create_tag(tag_name: str, message: str = None, repository_path: str = None) -> bool
def list_tags(repository_path: str = None) -> list[str]
def stash_changes(message: str = None, repository_path: str = None) -> bool
def apply_stash(stash_ref: str = None, repository_path: str = None) -> bool
def list_stashes(repository_path: str = None) -> list[dict[str, str]]
def reset_changes(mode: str = "mixed", target: str = "HEAD", repository_path: str = None) -> bool
```

**Usage Example**:

```python
from codomyrmex.git_operations import (
    check_git_availability,
    clone_repository,
    create_branch,
    add_files,
    commit_changes,
    push_changes
)

# Check if git is available
if not check_git_availability():
    print("Git is not available")
    exit(1)

# Clone a repository
success = clone_repository(
    url="https://github.com/user/repo.git",
    destination="./local-repo",
    branch="main"
)

if success:
    # Create and switch to new branch
    create_branch("feature-branch", "./local-repo")

    # Add files and commit
    add_files(["src/new_file.py"], "./local-repo")
    commit_changes("Add new feature", "./local-repo")

    # Push changes
    push_changes("origin", "feature-branch", "./local-repo")
```

### **Repository Management Classes**

**Source**: `src/codomyrmex/git_operations/core/repository.py`

```python
class Repository:
    def __init__(self, name: str, url: str, description: str = "",
                 local_path: str = "", repository_type: RepositoryType = RepositoryType.UNKNOWN)

class RepositoryManager:
    def __init__(self, library_file_path: str, local_base_path: str = "./repositories")
    def list_repositories(self) -> list[Repository]
    def get_repository(self, name: str) -> Optional[Repository]
    def search_repositories(self, query: str) -> list[Repository]
    def clone_repository(self, name: str) -> bool
    def update_repository(self, name: str) -> bool
    def get_repository_status(self, name: str) -> dict[str, Any]
```

## 📋 Pattern Matching API

### **Repository Analysis**

**Source**: `src/codomyrmex/coding/pattern_matching/run_codomyrmex_analysis.py`

```python
def analyze_repository_path(path: str) -> dict[str, Any]

def run_full_analysis(path: str) -> dict[str, Any]

def get_embedding_function() -> Callable[[str], list[float]]  # deterministic hash embedding
```

`analyze_repository_path` and `run_full_analysis` currently return only a status dictionary; for actual pattern analysis use `PatternDetector` or `ASTMatcher` from `codomyrmex.coding.pattern_matching`.

**Usage Example**:

```python
from codomyrmex.coding.pattern_matching import PatternDetector
from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import analyze_repository_path

result = analyze_repository_path("./my-project")
print(result)  # {"path": "./my-project", "status": "analyzed"}

with open("src/my_module.py") as f:
    for match in PatternDetector().detect_patterns(f.read()):
        print(match["pattern"], match["location"], match["confidence"])
```

## 🏗️ Build Synthesis API

### **Build Operations**

**Source**: `src/codomyrmex/ci_cd_automation/build/build_orchestrator.py`

```python
def check_build_environment() -> dict
def run_build_command(command: list[str], cwd: str = None) -> Tuple[bool, str, str]
def synthesize_build_artifact(source_path: str, output_path: str, artifact_type: str = "executable") -> bool
def validate_build_output(output_path: str) -> dict[str, any]
def orchestrate_build_pipeline(build_config: dict[str, any]) -> dict[str, any]
```

**Usage Example**:

```python
from codomyrmex.ci_cd_automation.build.build_orchestrator import (
    check_build_environment,
    synthesize_build_artifact,
    orchestrate_build_pipeline
)

# Check build environment
env_status = check_build_environment()
print(f"Python available: {env_status['python_available']}")

# Create a single-file executable artifact.  Directory sources use
# ``artifact_type="package"`` or ``"archive"`` instead.
success = synthesize_build_artifact(
    source_path="./src/main.py",
    output_path="./dist/my_app",
    artifact_type="executable"
)

# Full build pipeline
build_config = {
    "source_path": "./src",
    "output_path": "./dist",
    "artifact_type": "package",
    "dependencies": ["numpy", "matplotlib"]
}

result = orchestrate_build_pipeline(build_config)
```

Build commands must be argument vectors and are executed without shell
interpretation.  The artifact types are explicit: `copy` copies a file or
directory, `package` preserves a source tree, `archive` creates a ZIP archive,
and `executable` creates a file artifact.  Language labels are metadata only;
compiler support is supplied through an explicit `build_commands` entry.  Set
`output_root` to constrain artifacts and rollback to that directory.

## 📚 Documentation API

### **Documentation Generation**

**Source**: `src/codomyrmex/documentation/documentation_website.py`

```python
def check_doc_environment() -> dict
def install_dependencies(package_manager: str = "npm", cwd: str | os.PathLike[str] | None = None) -> bool
def start_dev_server(package_manager: str = "npm") -> bool
def build_static_site(package_manager: str = "npm", docs_root: str | os.PathLike[str] | None = None) -> bool
def serve_static_site(package_manager: str = "npm", docs_root: str | os.PathLike[str] | None = None) -> bool
def aggregate_docs(source_root: str = None, dest_root: str = None) -> bool
def validate_doc_versions() -> dict
def assess_site() -> dict
```

## 📝 Logging & Monitoring API

### **Logger Configuration**

**Source**: `src/codomyrmex/logging_monitoring/core/logger_config.py` (re-exported from `codomyrmex.logging_monitoring`)

```python
def setup_logging(force: bool = True) -> None

def get_logger(name: str) -> logging.Logger
```

`setup_logging` reads its configuration from environment variables: `CODOMYRMEX_LOG_LEVEL` (default `INFO`), `CODOMYRMEX_LOG_FILE`, `CODOMYRMEX_LOG_FORMAT` (a format string or `DETAILED`), and `CODOMYRMEX_LOG_OUTPUT_TYPE` (`TEXT` or `JSON`).

**Usage Example**:

```python
import os

from codomyrmex.logging_monitoring import setup_logging, get_logger

# Setup logging system
os.environ["CODOMYRMEX_LOG_LEVEL"] = "DEBUG"
os.environ["CODOMYRMEX_LOG_FILE"] = "./logs/codomyrmex.log"
os.environ["CODOMYRMEX_LOG_FORMAT"] = "DETAILED"
setup_logging()

# Get module logger
logger = get_logger(__name__)
logger.info("Application started")
```

## 🔌 Model Context Protocol API

### **MCP Schemas**

**Source**: `src/codomyrmex/model_context_protocol/schemas/mcp_schemas.py` (re-exported from `codomyrmex.model_context_protocol`)

```python
class MCPErrorDetail(BaseModel):
    error_type: str
    error_message: str
    error_details: dict[str, Any] | str | None = None

class MCPToolCall(BaseModel):  # extra fields allowed
    tool_name: str
    arguments: dict[str, Any]

class MCPToolResult(BaseModel):  # extra fields allowed
    status: str  # e.g. "success", "failure", "no_change_needed"
    data: dict[str, Any] | None = None
    error: MCPErrorDetail | None = None
    explanation: str | None = None
```

## 🖥️ Terminal Interface API

### **Interactive Shell**

**Source**: `src/codomyrmex/terminal_interface/shells/interactive_shell.py`

```python
class InteractiveShell(cmd.Cmd):
    # Command-line interface implementation
    pass
```

### **Terminal Utilities**

**Source**: `src/codomyrmex/terminal_interface/utils/terminal_utils.py`

```python
class TerminalFormatter:
    # Terminal output formatting utilities
    pass

class CommandRunner:
    # Command execution utilities
    pass

def create_ascii_art(text: str, style: str = "simple") -> str
```

## 🔍 System Discovery API

### **Discovery Engine**

**Source**: `src/codomyrmex/system_discovery/core/discovery_engine.py`

```python
class ModuleCapability:
    name: str
    description: str
    available: bool

class ModuleInfo:
    name: str
    version: str
    capabilities: list[ModuleCapability]

class SystemDiscovery:
    # System introspection and capability discovery
    pass
```

## ✅ Testing Philosophy & Real Implementation Examples

All APIs documented above are tested using **real implementations**, never mocks. Here are the actual testing patterns:

### **Data Visualization Testing**

```python
# From tests/unit/data_visualization/
def test_create_line_plot_real():
    """Test actual line plot creation with real matplotlib."""
    from pathlib import Path

    from codomyrmex.data_visualization import create_line_plot

    x_data = [1, 2, 3, 4, 5]
    y_data = [2, 4, 6, 8, 10]

    # Test with real data, real function
    fig = create_line_plot(
        x_data=x_data,
        y_data=y_data,
        title="Real Test Plot",
        output_path="test_output.png"
    )

    assert fig is not None
    assert Path("test_output.png").exists()
```

### **Static Analysis Testing**

```python
def test_run_pyrefly_real(tmp_path):
    """Test real Pyrefly analysis (skipped when the CLI is missing)."""
    import pytest

    from codomyrmex.coding.static_analysis.pyrefly_runner import (
        check_pyrefly_available,
        run_pyrefly,
    )

    if not check_pyrefly_available():
        pytest.skip("pyrefly not installed")

    source = tmp_path / "module.py"
    source.write_text("def add(a: int, b: int) -> int:\n    return a + b\n")
    result = run_pyrefly(str(source))

    assert result.success
    assert result.files_analyzed == 1
    assert isinstance(result.issues, list)
```

### **Code Execution Testing**

```python
def test_execute_code_real():
    """Test real code execution (requires Docker)."""
    from codomyrmex.coding.execution import execute_code

    # Real code execution test
    result = execute_code(
        language="python",
        code="print('Hello from test')",
        timeout=10
    )

    assert result['status'] == 'success'
    assert "Hello from test" in result['stdout']
```

## 🔗 Cross-References

### **Source Files**

- All functions link to actual source files in `src/codomyrmex/`
- Complete function signatures from source code
- Real usage examples from module `__main__` sections

### **Test Files**

- All APIs covered by tests in `tests/unit/`
- Real implementation testing (no mocks for core functionality)
- Comprehensive test coverage following TDD principles

### **Documentation Links**

- **[Testing Strategy](../development/testing-strategy.md)**: Real testing approaches
- **[Module Overview](../modules/overview.md)**: Module organization
- **[Performance Guide](../reference/performance.md)**: API performance characteristics
- **[Integration Guide](../integration/external-systems.md)**: External system integration

---

**Reference status**: This page is a source-derived API snapshot. The documentation gates
check that listed source paths and declared signatures remain resolvable; example coverage
is established only where a corresponding test or executable validation is named. Module
specifications remain the authoritative contract for stability, security, and deployment
conditions.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Repository Root](../../README.md)

<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->

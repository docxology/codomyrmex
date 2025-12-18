# Documentation - API Specification

## Introduction

<!-- 
This document outlines the specification for any programmatic APIs (e.g., Python functions intended for direct import and use by other modules) provided by the `documentation` module. 

Note: The primary interface for interacting with this module's functionalities (like building the Docusaurus site) is through:
1. The `documentation_website.py` command-line script.
2. MCP (Model Context Protocol) tools like `trigger_documentation_build` and `check_documentation_environment`, which are detailed in `MCP_TOOL_SPECIFICATION.md`.

This API Specification is relevant if functions within `documentation_website.py` or other Python files in this module are designed to be imported and used as a library by other Codomyrmex components. If no such direct programmatic API is exposed, this document may indicate N/A or be minimal.
-->

## Endpoints / Functions / Interfaces

### Function: `check_doc_environment(package_manager: str = 'npm', docs_module_root: str = 'documentation') -> Dict`

- **Description**: Verify Docusaurus documentation environment and dependencies.
- **Parameters**:
    - `package_manager`: Package manager to use ('npm', 'yarn', 'pnpm').
    - `docs_module_root`: Path to documentation module directory.
- **Return Value**: Environment check results with status and recommendations.
- **Errors**: Raises `EnvironmentError` for missing dependencies or configuration issues.

### Function: `install_dependencies(package_manager: str = 'npm', docs_module_root: str = 'documentation') -> bool`

- **Description**: Install documentation dependencies and verify installation.
- **Parameters**:
    - `package_manager`: Package manager to use ('npm', 'yarn', 'pnpm').
    - `docs_module_root`: Path to documentation module directory.
- **Return Value**: True if installation successful, False otherwise.
- **Errors**: Raises `InstallationError` for dependency installation failures.

### Function: `start_dev_server(port: int = 3000, host: str = 'localhost', docs_module_root: str = 'documentation') -> subprocess.Popen`

- **Description**: Start Docusaurus development server for live documentation preview.
- **Parameters**:
    - `port`: Port number for development server.
    - `host`: Host address for development server.
    - `docs_module_root`: Path to documentation module directory.
- **Return Value**: Process object for the running development server.
- **Errors**: Raises `ServerError` for server startup failures.

### Function: `build_static_site(output_dir: str = 'build', docs_module_root: str = 'documentation') -> Dict`

- **Description**: Build static documentation website for deployment.
- **Parameters**:
    - `output_dir`: Directory to output built static files.
    - `docs_module_root`: Path to documentation module directory.
- **Return Value**: Build results with status, file count, and performance metrics.
- **Errors**: Raises `BuildError` for build process failures.

### Function: `aggregate_docs(source_dirs: List[str], output_dir: str, **kwargs) -> Dict`

- **Description**: Aggregate documentation from multiple sources into unified structure.
- **Parameters**:
    - `source_dirs`: List of directories containing documentation to aggregate.
    - `output_dir`: Directory to output aggregated documentation.
    - `**kwargs`: Aggregation options (format, merge_strategy, etc.).
- **Return Value**: Aggregation results with file counts and merge statistics.
- **Errors**: Raises `AggregationError` for documentation processing failures.

### Function: `validate_doc_versions(docs_path: str, version_pattern: str = None, **kwargs) -> Dict`

- **Description**: Validate version consistency across documentation files.
- **Parameters**:
    - `docs_path`: Path to documentation directory to validate.
    - `version_pattern`: Regex pattern for version validation.
    - `**kwargs`: Validation options (strict_mode, ignore_patterns, etc.).
- **Return Value**: Validation results with version mismatches and recommendations.
- **Errors**: Raises `ValidationError` for version consistency issues.

### Function: `assess_site(site_path: str, assessment_type: str = 'comprehensive', **kwargs) -> Dict`

- **Description**: Assess documentation website quality and completeness.
- **Parameters**:
    - `site_path`: Path to built documentation site.
    - `assessment_type`: Type of assessment (comprehensive, quick, seo, accessibility).
    - `**kwargs`: Assessment options (thresholds, categories, etc.).
- **Return Value**: Assessment results with scores, issues, and improvement recommendations.
- **Errors**: Raises `AssessmentError` for assessment execution failures.

- **Description**: Programmatically executes a Docusaurus command (e.g., 'build', 'start', 'install'). This is a conceptual example; check `documentation_website.py` for actual function definitions if intended for library use.
- **Method**: N/A (Python function)
- **Path**: N/A
- **Parameters/Arguments**:
    - `action` (str): The Docusaurus action to perform (e.g., 'build', 'start', 'install', 'serve', 'checkenv').
    - `package_manager` (str, optional): 'npm' or 'yarn'. Default: 'npm'.
    - `project_root` (str, optional): Path to the Codomyrmex project root. Default: current directory.
    - `docs_module_root` (str, optional): Path to the documentation module relative to project_root. Default: 'documentation'.
- **Request Body**: N/A
- **Returns/Response**:
    - **Success**: (e.g., `True`, or a result object/dictionary with status and output)
        ```python
        # Example conceptual return
        {
          "success": True,
          "message": "Action [action] completed successfully.",
          "output": "...	ext of stdout/stderr..."
        }
        ```
    - **Error**: (e.g., `False`, raises an exception, or a result object with error details)
        ```python
        # Example conceptual return
        {
          "success": False,
          "message": "Error during action [action]: ...",
          "error_details": "..."
        }
        ```
- **Events Emitted**: N/A

<!-- Endpoint/Function 2: ... -->

## Data Structures

### DocumentationBuildConfig
Configuration for documentation build process:
```python
{
    "source_dir": <str>,
    "output_dir": <str>,
    "package_manager": <str>,
    "build_options": {
        "minify": <bool>,
        "optimize_images": <bool>,
        "generate_sitemap": <bool>
    },
    "metadata": {
        "version": <str>,
        "last_updated": <timestamp>,
        "author": <str>
    }
}
```

### DocumentationAssessmentResult
Results from documentation quality assessment:
```python
{
    "overall_score": <float>,
    "categories": {
        "completeness": <float>,
        "accuracy": <float>,
        "consistency": <float>,
        "accessibility": <float>
    },
    "issues": [
        {
            "type": <str>,
            "severity": <str>,
            "description": <str>,
            "location": <str>,
            "recommendation": <str>
        }
    ],
    "recommendations": [<list_of_improvements>]
}
```

## Security Considerations

All documentation functions operate locally and do not expose network interfaces. Security considerations include:

- **Input Validation**: All file paths and parameters are validated before processing
- **Safe Execution**: Documentation commands are executed in controlled environments
- **Access Control**: File system access is limited to documentation directories
- **Output Sanitization**: Generated content is validated for security issues

## Performance Characteristics

- **Local Processing**: All operations performed locally with no external API calls
- **Resource Efficient**: Minimal memory and CPU usage for documentation operations
- **Scalable**: Can handle large documentation repositories
- **Fast Execution**: Build and assessment operations complete in seconds to minutes
- **Streaming Output**: Real-time output streaming for long-running operations

## Integration Patterns

### With Build Synthesis
```python
from codomyrmex.documentation import build_static_site
from codomyrmex.build_synthesis import create_build_target

# Create documentation build target
docs_target = create_build_target(
    name="documentation",
    build_type="documentation",
    config={"output_dir": "docs/build"}
)

# Build documentation as part of CI/CD
build_result = build_static_site(output_dir="docs/build")
```

### With Project Orchestration
```python
from codomyrmex.documentation import aggregate_docs, validate_doc_versions
from codomyrmex.project_orchestration import execute_workflow

# Aggregate documentation from multiple modules
aggregation_result = aggregate_docs(
    source_dirs=["src/codomyrmex/*/docs", "docs/modules"],
    output_dir="docs/aggregated"
)

# Validate version consistency
validation_result = validate_doc_versions("docs/aggregated")
``` 
# Static Analysis - API Specification

## Introduction

(Briefly describe the purpose of this API and how it facilitates interaction with the module.)

## Endpoints / Functions / Interfaces

## Functions

### Function: `analyze_file(file_path: str, analysis_types: List[AnalysisType] = None, **kwargs) -> AnalysisResult`

- **Description**: Analyze a single file for code quality, security, and performance issues.
- **Parameters**:
    - `file_path`: Path to the file to analyze.
    - `analysis_types`: List of analysis types to perform (quality, security, performance, etc.).
    - `**kwargs`: Additional analysis options (severity_threshold, include_metrics, etc.).
- **Return Value**: AnalysisResult object containing findings, metrics, and recommendations.
- **Errors**: Raises `AnalysisError` for file access issues or analysis failures.

### Function: `analyze_project(project_path: str, analysis_types: List[AnalysisType] = None, **kwargs) -> AnalysisSummary`

- **Description**: Perform static analysis on an entire project.
- **Parameters**:
    - `project_path`: Root path of the project to analyze.
    - `analysis_types`: List of analysis types to perform across all files.
    - `**kwargs`: Project-wide analysis options (exclude_patterns, parallel_processing, etc.).
- **Return Value**: AnalysisSummary with aggregated results across all analyzed files.
- **Errors**: Raises `AnalysisError` for project access issues or analysis failures.

### Function: `get_available_tools() -> List[str]`

- **Description**: Get list of available static analysis tools and their capabilities.
- **Return Value**: List of available analysis tool names.
- **Errors**: Raises `ToolError` for tool discovery issues.

### Function: `run_pyrefly_analysis(target_paths: List[str], **kwargs) -> Dict`

- **Description**: Run Pyrefly static analysis on specified Python code paths.
- **Parameters**:
    - `target_paths`: List of file or directory paths to analyze.
    - `**kwargs`: Pyrefly-specific analysis options.
- **Return Value**: Dictionary containing analysis results, errors, and metadata.
- **Errors**: Raises `PyreflyError` for analysis execution failures.

### Function: `parse_pyrefly_output(output: str, **kwargs) -> List[Dict]`

- **Description**: Parse Pyrefly analysis output into structured data.
- **Parameters**:
    - `output`: Raw Pyrefly output string to parse.
    - `**kwargs`: Parsing options (format_output, include_metadata, etc.).
- **Return Value**: List of parsed analysis findings with standardized structure.
- **Errors**: Raises `ParseError` for output parsing failures.
    - `param2` (type, optional): Description of parameter. Default: `value`.
- **Request Body** (if applicable):
    ```json
    {
      "key": "value"
    }
    ```
- **Returns/Response**:
    - **Success (e.g., 200 OK)**:
        ```json
        {
          "data": "result"
        }
        ```
    - **Error (e.g., 4xx/5xx)**:
        ```json
        {
          "error": "description"
        }
        ```
- **Events Emitted** (if applicable):
    - `event_name`: Description of event and its payload.

### Endpoint/Function 2: ...

## Data Models

(Define any common data structures or models used by the API.)

### Model: `ExampleModel`
- `field1` (type): Description.
- `field2` (type): Description.

## Authentication & Authorization

(Describe how API access is secured, if applicable.)

## Rate Limiting

(Specify any rate limits imposed on API usage.)

## Versioning

(Explain the API versioning strategy.) 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)

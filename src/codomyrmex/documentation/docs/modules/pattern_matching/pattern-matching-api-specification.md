---
sidebar_label: "API Specification"
title: "Pattern Matching - API Specification"
---

# Pattern Matching - API Specification

## Introduction

The Pattern Matching module primarily functions through the `run_codomyrmex_analysis.py` script, but it also exposes several functions that can be imported and used programmatically.

## Functions

### Repository Analysis

#### `analyze_repository_path(path_to_analyze: str, relative_output_dir_name: str, config: dict)`

- **Description**: Analyzes a repository directory with customizable options.
- **Parameters**:
    - `path_to_analyze` (string): The file system path to the repository to analyze.
    - `relative_output_dir_name` (string): The subdirectory name (relative to the base output directory) where results will be stored.
    - `config` (dict): A configuration dictionary controlling which analyses to run and their parameters.
- **Returns**:
    - Dictionary containing analysis summary and paths to result files.
- **Raises**:
    - `Exception`: If the repository path doesn't exist or can't be analyzed.

Example:
```python
from pattern_matching.run_codomyrmex_analysis import analyze_repository_path

results = analyze_repository_path(
    "/path/to/repo",
    "custom_analysis",
    {
        "text_search_queries": ["TODO", "FIXME"],
        "run_dependency_analysis": True,
        "run_code_summarization": False,
    }
)
```

#### `run_full_analysis()`

- **Description**: Runs the full suite of analyses on all configured module directories.
- **Parameters**: None (uses configuration from the script itself).
- **Returns**: None (outputs are written to the filesystem).
- **Side Effects**: Creates output directory structure and files.

Example:
```python
from pattern_matching.run_codomyrmex_analysis import run_full_analysis

run_full_analysis()
```

## Data Models

The module produces various JSON files, each following a specific structure:

### Repository Index

```json
{
  "files": [
    {
      "path": "relative/path/to/file.py",
      "size": 1024,
      "is_binary": false,
      "last_modified": "timestamp"
    }
  ]
}
```

### Text Search Results

```json
{
  "pattern": [
    {
      "file": "path/to/match.py",
      "line": 120,
      "content": "Line content with pattern"
    }
  ]
}
```

## Authentication & Authorization

The module does not implement its own authentication or authorization mechanisms.

If OpenAI features are used (for code summarization), an API key must be provided through environment variables.

## Rate Limiting

No specific rate limiting is implemented beyond what may be imposed by OpenAI's API if LLM features are used.

## Versioning

This module follows the main Codomyrmex versioning scheme and does not have its own specific versioning. 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)

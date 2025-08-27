---
id: static-analysis-usage-examples
title: Static Analysis - Usage Examples
sidebar_label: Usage Examples
---

# Static Analysis - Usage Examples

## Example 1: Running Pylint on a Python Module

**Scenario**: You want to check a Python module for linting issues using Pylint.

**Setup**:
- Ensure Pylint is installed in your environment (handled by `environment_setup`).
- Have a Python module, e.g., `src/my_app/data_processor.py`.

**Invocation (conceptual API call):**
```python
from codomyrmex.static_analysis import AnalysisRunner # Assuming such a class

runner = AnalysisRunner()
results = runner.run(
    target_paths=["src/my_app/data_processor.py"],
    tool_ids=["pylint"]
)

for issue in results.get_issues():
    print(f"File: {issue.file_path}, Line: {issue.line}, Message: {issue.message}")
```

**Invocation (conceptual MCP call `static_analysis.run_scan`):**
```json
{
  "tool_name": "static_analysis.run_scan",
  "arguments": {
    "target_paths": ["src/my_app/data_processor.py"],
    "tools": ["pylint"],
    "output_format": "summary"
  }
}
```

### Expected Outcome

The console (for API call) or the MCP tool response will show a summary or list of Pylint issues found in `data_processor.py`.

**Example Output (summary):**
```json
{
  "status": "success",
  "total_issues": 3,
  "errors": 0,
  "warnings": 3
}
```

## Example 2: Running a Security Scan with Bandit on a Project

**Scenario**: You want to perform a security scan on your entire Python project using Bandit.

**Setup**:
- Bandit installed.
- Project root: `src/my_project/`

**Invocation (conceptual MCP call):**
```json
{
  "tool_name": "static_analysis.run_scan",
  "arguments": {
    "target_paths": ["src/my_project/"],
    "tools": ["bandit"],
    "output_format": "full_json" 
  }
}
```

### Configuration (if any)

- Bandit configuration (e.g., baseline file `bandit.yml`) might be present in the project to ignore certain issues.

### Expected Outcome

The MCP tool returns a JSON object detailing all security issues identified by Bandit.

**Example Snippet of JSON Output:**
```json
{
  "status": "success",
  "issues": [
    {
      "file_path": "src/my_project/auth.py",
      "line": 55,
      "tool": "bandit",
      "rule_id": "B105", // Example rule for hardcoded password
      "message": "Possible hardcoded password: ...",
      "severity": "high"
    }
    // ... other issues
  ]
}
```

## Common Pitfalls & Troubleshooting

- **Issue**: Tool not found (e.g., "Pylint not found").
  - **Solution**: Ensure the required static analysis tool is installed in the Python environment active for Codomyrmex. Check `environment_setup` and project dependencies.
- **Issue**: Scan takes too long.
  - **Solution**: 
    - For large codebases, scan specific subdirectories or files instead of the entire project if possible.
    - Check tool configurations for any performance-intensive rules that might be disabled or adjusted.
    - Some tools support incremental scanning; investigate if this is an option.
- **Issue**: Too many false positives.
  - **Solution**: 
    - Configure the specific tool (e.g., via its rcfile like `.pylintrc`, or inline comments) to ignore certain rules or specific lines of code.
    - For security scanners, establish a baseline of known/accepted issues. 
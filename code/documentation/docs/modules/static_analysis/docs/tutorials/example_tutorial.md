---
id: static-analysis-pylint-example-tutorial
title: Example Tutorial - Configuring Pylint
sidebar_label: Pylint Configuration Tutorial
---

# Static Analysis - Example Tutorial: Configuring Pylint for a Project

This tutorial will guide you through configuring Pylint, a popular Python linter, within the Static Analysis module for a specific project.

## 1. Prerequisites

- The Static Analysis module installed and operational.
- Pylint installed in the environment (see [Environment Setup](../../../../development/environment-setup.md)).
- A Python project or module you want to lint.

## 2. Goal

By the end of this tutorial, you will be able to:
- Create a basic Pylint configuration file (`.pylintrc`).
- Understand how the Static Analysis module can use this project-specific configuration.
- Run Pylint via the Static Analysis module and observe its output based on your configuration.

## 3. Steps

### Step 1: Create a Sample Python File

Let's say you have a Python file `src/my_project/calculator.py`:

```python
# src/my_project/calculator.py

def add(x,y):
    """This function adds two numbers but has some style issues Pylint might catch."""
    result =x+y # Pylint might flag spacing
    return result

UNUSED_VARIABLE = 10 # Pylint should flag this
```

### Step 2: Create a `.pylintrc` Configuration File

In the root of your Codomyrmex project (or within the `my_project` directory, depending on how shared you want the config to be), create a `.pylintrc` file. For this example, let's place it in `src/my_project/.pylintrc`.

**`src/my_project/.pylintrc`:**
```ini
[MESSAGES CONTROL]

# Disable the specified messages.
disable=
    C0114, # missing-module-docstring
    C0115, # missing-class-docstring
    C0116  # missing-function-docstring (we will keep this enabled to see it flag 'add')

[FORMAT]

# Maximum number of characters on a single line.
max-line-length=88

# Good variable names which should always be accepted, separated by a comma
# good-names=i,j,k,ex,Run,_ # etc.
```
In this configuration:
- We explicitly disable warnings about missing module and class docstrings.
- We leave `missing-function-docstring` (C0116) enabled, so Pylint should still warn if `add` is missing one (though our example has one).
- We set `max-line-length` to 88.

### Step 3: Run Analysis via Static Analysis Module

Now, use the Static Analysis module to run Pylint on your file. The module should automatically pick up the `.pylintrc` file if it's in a standard location relative to the scanned files.

**Conceptual MCP Call (using `static_analysis.run_scan`):**
```json
{
  "tool_name": "static_analysis.run_scan",
  "arguments": {
    "target_paths": ["src/my_project/calculator.py"],
    "tools": ["pylint"],
    "output_format": "full_json"
  }
}
```

### Step 4: Verify the Output

Examine the JSON output from the MCP call. You should expect to see:
- Warnings related to `UNUSED_VARIABLE` (W0612).
- Warnings about operator spacing in `result =x+y` (e.g., C0326 bad-whitespace).
- *No* warning about missing module docstring (C0114) because we disabled it.

**Example Snippet of Expected JSON Output:**
```json
{
  "status": "success",
  "issues": [
    // ... other issues ...
    {
      "file_path": "src/my_project/calculator.py",
      "line": 5,
      "column": 11,
      "tool": "pylint",
      "rule_id": "C0326", 
      "message": "Exactly one space required after assignment operator", 
      "severity": "convention"
    },
    {
      "file_path": "src/my_project/calculator.py",
      "line": 8,
      "column": 0,
      "tool": "pylint",
      "rule_id": "W0612",
      "message": "Unused variable 'UNUSED_VARIABLE'",
      "severity": "warning"
    }
    // ... potentially a missing-function-docstring if the example function's docstring was insufficient or malformed
  ]
}
```

## 4. Understanding the Results

The Static Analysis module correctly invoked Pylint, which used your custom `.pylintrc` configuration. This demonstrates how you can tailor the behavior of linters for specific project needs by providing tool-specific configuration files that the Static Analysis module can discover and use.

## 5. Troubleshooting

- **Pylint doesn't seem to use my `.pylintrc` file**:
  - **Cause**: The `.pylintrc` file might not be in a location Pylint or the Static Analysis module adapter expects (Pylint typically searches in the current working directory, the directory of the linted file, and parent directories up to the project root or home directory).
  - **Solution**: Ensure `.pylintrc` is discoverable. Some adapters might allow specifying a configuration file path directly in the `run_analysis` call or module settings.
- **Unexpected Pylint messages appear/are missing**:
  - **Solution**: Double-check your `disable=` list in `.pylintrc`. Pylint message IDs can sometimes be subtle. Use `pylint --list-msgs` to see all available messages and their IDs.

## 6. Next Steps

- Explore more advanced Pylint configurations (e.g., custom checkers, regular expressions for variable names).
- Configure other static analysis tools (e.g., Bandit for security, Black for formatting) for your project.
- Integrate static analysis runs into your CI/CD pipeline using Codomyrmex tools. 
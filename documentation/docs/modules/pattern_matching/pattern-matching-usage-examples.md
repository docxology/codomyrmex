---
sidebar_label: "Usage Examples"
title: "Pattern Matching - Usage Examples"
---

# Pattern Matching - Usage Examples

This document provides practical examples of using the Pattern Matching module.

## Example 1: Basic Repository Analysis

Running the analysis script on the entire project:

```bash
# From the project root
python pattern_matching/run_codomyrmex_analysis.py
```

The output will be stored in `output/codomyrmex_analysis/`.

## Example 2: Analyzing a Specific Module

Modify the script to target a specific module:

```python
# In pattern_matching/run_codomyrmex_analysis.py
# Find the MODULE_DIRS list and modify it:
MODULE_DIRS = [
    "data_visualization",  # Only analyze this module
]
```

Then run the script as usual:

```bash
python pattern_matching/run_codomyrmex_analysis.py
```

## Example 3: Using as a Library

You can import and use the analysis functions in your own scripts:

```python
from pattern_matching.run_codomyrmex_analysis import analyze_repository_path

# Define custom configuration
custom_config = {
    "text_search_queries": ["FIXME", "HACK"],
    "files_to_summarize_count": 2,
    "run_code_summarization": False,  # Disable LLM-based summarization
    "run_dependency_analysis": True,
}

# Run analysis on a specific repository with custom settings
result = analyze_repository_path(
    "/path/to/repository", 
    "custom_analysis_output",
    custom_config
)

print(f"Analysis completed. Results in: {result['output_path']}")
```

## Example 4: Visualizing Dependency Graphs

After running the analysis, you can visualize dependency graphs using Graphviz:

```bash
# Install Graphviz if not already installed
# Ubuntu: sudo apt-get install graphviz
# macOS: brew install graphviz

# Generate a PNG visualization from the DOT file
dot -Tpng output/codomyrmex_analysis/module_name/dependency_graph.dot -o dependency_graph.png

# View the generated image
xdg-open dependency_graph.png  # on Linux
open dependency_graph.png      # on macOS
```

## Common Pitfalls & Troubleshooting

- **Issue**: Analysis fails with an error about missing API keys.
  - **Solution**: Set up your environment variables properly by copying `.env.example` to `.env` and adding your API keys.

- **Issue**: Dependency analysis produces empty graphs.
  - **Solution**: Ensure the target repositories contain Python files with actual import statements.

- **Issue**: Code summarization fails or produces poor results.
  - **Solution**: Check your OpenAI API key and ensure your code files aren't too large (>25K characters). 
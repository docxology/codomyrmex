---
sidebar_label: "Getting Started Tutorial"
title: "Getting Started with Pattern Matching"
---

# Getting Started with Pattern Matching

This tutorial will guide you through using the Pattern Matching module's `run_codomyrmex_analysis.py` script to analyze a codebase.

## Prerequisites

Before you begin, ensure you have:

1. The Codomyrmex project cloned locally
2. Environment variables set up (particularly API keys if using LLM-based features)
3. Python 3.9+ installed

## Script Overview

The `run_codomyrmex_analysis.py` script performs several types of analysis on a codebase:

- Repository structure indexing
- Dependency analysis
- Text pattern searching (TODOs, FIXMEs, etc.)
- Code summarization (using LLMs)
- Docstring indexing and searching
- Symbol extraction and usage analysis
- Chunking examples for context handling

## Step 1: Set Up Environment Variables

If you haven't already set up environment variables, do so now:

```bash
# From the project root
cp .env.example .env
```

Edit the `.env` file to include your API keys if needed (for OpenAI features):

```
OPENAI_API_KEY=your_api_key_here
```

## Step 2: Running the Analysis

The simplest way to run the analysis is to execute the script from the project root:

```bash
python pattern_matching/run_codomyrmex_analysis.py
```

This will:
1. Analyze all configured module directories
2. Store results in the `output/codomyrmex_analysis/` directory

## Step 3: Reviewing Analysis Results

After running the script, navigate to the `output/codomyrmex_analysis/` directory to see the results:

```bash
ls -la output/codomyrmex_analysis/
```

For each module, you'll find a subdirectory with various analysis files:

- `repository_index.json`: Information about the repository structure
- `text_search_results.json`: Results of text pattern searches
- `dependency_graph.dot`: Dependency graph (can be visualized with Graphviz)
- `symbol_usages.json`: Symbol reference analysis
- Various other analysis outputs depending on configuration

## Step 4: Customizing the Analysis

To customize the analysis, you can modify the `ANALYSIS_CONFIG` dictionary in the script:

```python
ANALYSIS_CONFIG = {
    "text_search_queries": ["TODO", "FIXME", "NOTE"],  # Change search terms
    "files_to_summarize_count": 3,  # Summarize more files
    "run_code_summarization": False,  # Disable specific features
    # ... other settings
}
```

Key configuration options:
- `text_search_queries`: List of text patterns to search for
- `symbols_to_find_usages`: List of symbols to track usages for
- Various boolean flags to enable/disable analysis stages

## Step 5: Understanding the Output

### Repository Index

The repository index (`repository_index.json`) contains metadata about files in the codebase:

```json
{
  "files": [
    {
      "path": "example_file.py",
      "size": 1024,
      "is_binary": false,
      "last_modified": "2023-07-15T10:30:00Z"
    },
    // ...more files
  ]
}
```

### Text Search Results

The `text_search_results.json` file shows where specific text patterns occur:

```json
{
  "TODO": [
    {
      "file": "example_file.py",
      "line": 42,
      "content": "# TODO: Implement this feature"
    },
    // ...more results
  ]
}
```

## Advanced Usage

For more advanced usage, you can:

1. Import the analysis functions in your own scripts:
   ```python
   from pattern_matching.run_codomyrmex_analysis import analyze_repository_path
   
   analyze_repository_path(
     "/path/to/repo", 
     "custom_output_dir",
     custom_config_dict
   )
   ```

2. Modify the script to focus on specific modules:
   ```python
   MODULE_DIRS = [
       "your_specific_module",
   ]
   ```

3. Integrate with other Codomyrmex modules like Data Visualization to create insights from your analysis data.

## Troubleshooting

If you encounter issues:

- Check that all required dependencies are installed
- Verify your API keys are set correctly in the `.env` file
- Ensure Python path includes the project root directory

For LLM-related functionality, make sure you have:
- A valid OpenAI API key
- Internet connectivity for API calls

## Next Steps

After completing this tutorial, you can explore:
- Creating custom analysis configurations for different projects
- Building on the analysis results to generate insights
- Integrating with other Codomyrmex modules 
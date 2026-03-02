# Git Visualization -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Git repository visualization engine producing both PNG charts (via matplotlib) and Mermaid text diagrams. Integrates with `git_operations` for live repository data or operates on supplied sample data for testing.

## Architecture

Central class `GitVisualizer` with multiple visualization methods, each supporting either live repository data (via `git_operations`) or pre-built data dicts. Uses `MermaidDiagramGenerator` for text-based diagrams and `matplotlib` for raster output.

```
GitVisualizer()
  +-- visualize_git_tree_png(repo_path, branches, commits) -> bool
  +-- visualize_git_tree_mermaid(repo_path, branches, commits) -> str
  +-- visualize_commit_activity_png(repo_path, commits) -> bool
  +-- visualize_repository_summary_png(repo_path, repo_data) -> bool
  +-- create_comprehensive_git_report(repo_path, output_dir) -> dict[str, bool]

Convenience functions:
  +-- visualize_git_repository(repo_path, output_dir) -> dict[str, bool]
  +-- create_git_tree_png(...) -> bool
  +-- create_git_tree_mermaid(...) -> str
```

## Key Classes

### `GitVisualizer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `visualize_git_tree_png` | `repository_path, branches, commits, title, output_path, max_commits` | `bool` | Branch-lane scatter plot with commit points and hash labels |
| `visualize_git_tree_mermaid` | `repository_path, branches, commits, title, output_path` | `str` | Mermaid gitGraph diagram via `MermaidDiagramGenerator` |
| `visualize_commit_activity_png` | `repository_path, commits, title, output_path, days_back` | `bool` | Daily commit count bar chart with statistics overlay |
| `visualize_repository_summary_png` | `repository_path, repo_data, title, output_path` | `bool` | 6-panel dashboard: status pie, timeline, contributors, branch info, commit words, activity heatmap |
| `create_comprehensive_git_report` | `repository_path, output_dir, report_name` | `dict[str, bool]` | Generate all visualizations plus README summary; returns success map |

### Internal Helper Methods

| Method | Purpose |
|--------|---------|
| `_get_branch_color` | Map branch name patterns (main, develop, feature, hotfix) to hex colors |
| `_generate_sample_commits` | Create sample commit data for demo/testing |
| `_get_repository_structure` | Walk top-level directories for structure diagrams |
| `_plot_repository_status` | Pie chart subplot for clean/modified/untracked status |
| `_plot_commit_timeline` | Line chart subplot of recent commits |
| `_plot_author_contributions` | Horizontal bar chart of top 5 contributors |
| `_plot_activity_heatmap` | Week-by-day heatmap of commit activity |

## Dependencies

- **Internal**: `data_visualization.charts.plot_utils` (aesthetics, save), `data_visualization.mermaid` (Mermaid generation), `git_operations.core.git` (optional, for live repo data)
- **External**: `matplotlib` (required for PNG output)

## Constraints

- `git_operations` is optional; if unavailable, methods fall back to sample data or provided dicts.
- PNG output requires a non-interactive matplotlib backend; `plt.show()` only works in GUI environments.
- Mermaid output requires the `MermaidDiagramGenerator` from the sibling mermaid submodule.
- Repository structure scan is limited to 2 directory levels to avoid excessive traversal.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- All visualization methods catch generic `Exception`, log at ERROR with traceback, and return `False` or empty string.
- Permission errors during directory scanning are caught and logged at debug level.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md)
- Parent: [data_visualization](../README.md)

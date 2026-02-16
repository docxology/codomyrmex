# Codomyrmex MCP Tool Usage Examples

This guide provides practical examples for using the newly exposed Codomyrmex MCP tools.

## 📊 Data Visualization

### Line Plot

Create a line plot for time-series data or trends.

```python
# Simple usage
trusted_call_tool(
    "codomyrmex.create_line_plot",
    x_data=[1, 2, 3, 4, 5],
    y_data=[10, 15, 13, 18, 20],
    title="Growth Trend",
    x_label="Time (Days)",
    y_label="Users",
    output_path="docs/images/growth_trend.png"
)

# Multiple lines
trusted_call_tool(
    "codomyrmex.create_line_plot",
    x_data=[1, 2, 3, 4],
    y_data=[[10, 20, 30, 40], [15, 25, 35, 45]],
    line_labels=["Model A", "Model B"],
    title="Model Comparison",
    output_path="docs/images/comparison.png"
)
```

### Bar Chart

Compare categories or quantities.

```python
trusted_call_tool(
    "codomyrmex.create_bar_chart",
    categories=["Q1", "Q2", "Q3", "Q4"],
    values=[120, 150, 180, 200],
    title="Quarterly Revenue",
    horizontal=False,
    bar_color="skyblue",
    output_path="docs/images/revenue.png"
)
```

### Pie Chart

Show parts of a whole.

```python
trusted_call_tool(
    "codomyrmex.create_pie_chart",
    labels=["Engineering", "Sales", "Marketing", "HR"],
    sizes=[40, 30, 20, 10],
    title="Department Budget",
    explode=[0.1, 0, 0, 0],  # Highlight Engineering
    output_path="docs/images/budget.png"
)
```

## 🌳 Git Diagrams

Visualize repository state and history.

### Access Branch Diagram

Show the relationship between branches.

```python
trusted_call_tool(
    "codomyrmex.create_git_branch_diagram",
    title="Current Branch State",
    output_path="docs/start_state.mmd"
)
```

### Workflow Diagram

Visualize the CI/CD or development workflow.

```python
trusted_call_tool(
    "codomyrmex.create_git_workflow_diagram",
    title="Feature Development Flow",
    output_path="docs/workflow.mmd"
)
```

### Repo Structure

Visualize the file system structure.

```python
trusted_call_tool(
    "codomyrmex.create_repository_structure_diagram",
    title="Codomyrmex Architecture",
    output_path="docs/architecture.mmd"
)
```

## 🔧 Git Operations

Manage the Git repository programmatically.

### Initialize & Clone

```python
# Initialize
trusted_call_tool(
    "codomyrmex.initialize_git_repository",
    path="/path/to/new/project"
)

# Clone
trusted_call_tool(
    "codomyrmex.clone_repository",
    url="https://github.com/user/repo.git",
    destination="/path/to/local"
)
```

### Branch Management

```python
# Create and switch
trusted_call_tool("codomyrmex.create_branch", branch_name="feature/new-ui")

# Switch existing
trusted_call_tool("codomyrmex.switch_branch", branch_name="main")
```

### Commit & Push

```python
# Commit
trusted_call_tool(
    "codomyrmex.commit_changes",
    message="feat(ui): add new dashboard layout"
)

# Push
trusted_call_tool("codomyrmex.push_changes")
```

## 🖥️ Terminal & Code Execution

### Ascii Art

Add flair to CLI output.

```python
trusted_call_tool(
    "codomyrmex.create_ascii_art",
    text="Codomyrmex",
    style="block"
)
```

### Secure Execution

Run code in a sandboxed Docker container.

```python
trusted_call_tool(
    "codomyrmex.execute_code",
    language="python",
    code="print(sum(range(100)))"
)
```

## 🔍 Analysis & Documentation

### Static Analysis

```python
# Analyze single file
trusted_call_tool(
    "codomyrmex.analyze_file",
    file_path="src/main.py",
    analysis_types=["security", "quality"]
)

# Analyze project
trusted_call_tool(
    "codomyrmex.analyze_project",
    target_paths=["src/"],
    analysis_types=["security"]
)
```

### Auto-Documentation

```python
trusted_call_tool(
    "codomyrmex.generate_documentation",
    module_name="data_visualization"
)
```

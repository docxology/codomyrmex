# Codomyrmex Agents -- src/codomyrmex/data_visualization/mermaid

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Two complementary Mermaid diagram systems: (1) programmatic builders in `__init__.py` for flowcharts, sequence diagrams, and class diagrams using a fluent API, and (2) `MermaidDiagramGenerator` in `mermaid_generator.py` for Git-oriented visualizations (branch diagrams, workflow flowcharts, repo structure graphs, commit timelines) with `@mcp_tool` auto-discovery.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `MermaidDiagram` | Base class with `render()` and `to_markdown()` |
| `__init__.py` | `Flowchart` | Fluent builder: `add_node()`, `add_link()`, `add_subgraph()` |
| `__init__.py` | `SequenceDiagram` | Builder: `add_participant()`, `add_message()`, `add_note()`, `add_loop()` |
| `__init__.py` | `ClassDiagram` | Builder: `add_class()`, `add_relationship()` |
| `__init__.py` | `DiagramType`, `FlowDirection`, `NodeShape`, `LinkStyle` | Enums for diagram types, directions, shapes, and link styles |
| `__init__.py` | `Node`, `Link` | Dataclasses for flowchart nodes and links |
| `__init__.py` | `create_flowchart()`, `create_sequence_diagram()`, `create_class_diagram()` | Factory functions |
| `mermaid_generator.py` | `MermaidDiagramGenerator` | Git-focused generator with 9 diagram type handlers |
| `mermaid_generator.py` | `create_git_branch_diagram()` | `@mcp_tool` -- Git branch gitgraph |
| `mermaid_generator.py` | `create_git_workflow_diagram()` | `@mcp_tool` -- Git workflow flowchart |
| `mermaid_generator.py` | `create_repository_structure_diagram()` | `@mcp_tool` -- Repo structure graph |
| `mermaid_generator.py` | `create_commit_timeline_diagram()` | `@mcp_tool` -- Commit timeline |

## Operating Contracts

- All builders return `self` for method chaining (fluent API).
- `render()` produces valid Mermaid markdown syntax; `to_markdown()` wraps it in a fenced code block.
- `MermaidDiagramGenerator` accepts optional data; when data is empty, it falls back to a representative default diagram.
- Convenience functions decorated with `@mcp_tool()` are auto-discovered by the MCP bridge.
- `_save_mermaid_content()` creates parent directories and writes UTF-8 `.mmd` files.

## Integration Points

- **Depends on**: `logging_monitoring`, `model_context_protocol.decorators` (`@mcp_tool`), Python stdlib (`json`, `os`, `pathlib`)
- **Used by**: `data_visualization.plots.mermaid` (wraps `Flowchart`), Git analysis modules for visual output

## Navigation

- **Parent**: [data_visualization](../README.md)
- **Root**: [Root](../../../../README.md)

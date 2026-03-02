# Mermaid -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Two Mermaid diagram generation systems: programmatic builders (`Flowchart`, `SequenceDiagram`, `ClassDiagram`) using a fluent API with typed enums for shapes and link styles, and a Git-focused `MermaidDiagramGenerator` with four `@mcp_tool`-decorated convenience functions for branch diagrams, workflow flowcharts, repo structure graphs, and commit timelines.

## Architecture

```
MermaidDiagram (base)
  ├── Flowchart        -- add_node, add_link, add_subgraph
  ├── SequenceDiagram  -- add_participant, add_message, add_note, add_loop
  └── ClassDiagram     -- add_class, add_relationship

MermaidDiagramGenerator (mermaid_generator.py)
  ├── create_git_branch_diagram    (@mcp_tool)
  ├── create_git_workflow_diagram  (@mcp_tool)
  ├── create_repository_structure_diagram (@mcp_tool)
  └── create_commit_timeline_diagram (@mcp_tool)
```

## Key Classes

### `Flowchart`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_node` | `node_id, label, shape=RECTANGLE, style=None` | `self` | Add a node with shape from `NodeShape` enum |
| `add_link` | `source, target, label=None, style=SOLID` | `self` | Add a link with style from `LinkStyle` enum |
| `add_subgraph` | `subgraph_id, title, node_ids` | `self` | Group nodes into a subgraph |
| `render` | -- | `str` | Mermaid flowchart syntax |

### `SequenceDiagram`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_participant` | `alias, label=None, actor=False` | `self` | Add participant or actor |
| `add_message` | `sender, receiver, message, arrow_type="->>"` | `self` | Add message between participants |
| `add_note` | `text, position="right of", participant=""` | `self` | Add a note |
| `add_loop` | `label, messages: list[tuple]` | `self` | Add a loop block |

### `ClassDiagram`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_class` | `name, attributes=None, methods=None` | `self` | Add class with members |
| `add_relationship` | `class1, class2, relationship="-->", label=None` | `self` | Add relationship |

### Enums

| Enum | Values | Description |
|------|--------|-------------|
| `DiagramType` | FLOWCHART, SEQUENCE, CLASS, STATE, ER, GANTT, PIE, MINDMAP, TIMELINE, JOURNEY | Mermaid diagram type headers |
| `FlowDirection` | TD, TB, BT, LR, RL | Flowchart direction |
| `NodeShape` | RECTANGLE, ROUND, STADIUM, SUBROUTINE, CYLINDER, CIRCLE, ASYMMETRIC, RHOMBUS, HEXAGON, PARALLELOGRAM, TRAPEZOID | 11 node shapes |
| `LinkStyle` | SOLID, DOTTED, THICK, INVISIBLE | 4 link styles |

### `MermaidDiagramGenerator`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_git_branch_diagram` | `branches, commits, title, output_path` | `str` | Gitgraph from branch/commit data |
| `create_git_workflow_diagram` | `workflow_steps, title, output_path` | `str` | Flowchart from workflow steps |
| `create_repository_structure_diagram` | `repo_structure, title, output_path` | `str` | Graph from directory dict |
| `create_commit_timeline_diagram` | `commits, title, output_path` | `str` | Timeline from commit list (max 10) |

## Dependencies

- **Internal**: `logging_monitoring`, `model_context_protocol.decorators`
- **External**: None (pure string generation)

## Constraints

- `Node.render()` escapes double quotes to single quotes in labels.
- `MermaidDiagramGenerator` limits branch diagrams to 3 commits per branch and timelines to 10 commits.
- When data is empty/None, generators produce representative default diagrams.
- Zero-mock: all output is real Mermaid syntax; `NotImplementedError` for unimplemented paths.

## Error Handling

- `_save_mermaid_content()` catches all exceptions, logs error, returns `False`.
- File icon lookup in `_get_file_icon()` falls back to a generic document icon for unknown extensions.

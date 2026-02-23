# data_visualization/mermaid

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Mermaid diagram generation utilities. Provides a programmatic builder API for creating Mermaid diagrams including flowcharts, sequence diagrams, and class diagrams with full control over nodes, links, subgraphs, participants, and relationships.

## Key Exports

### Enums

- **`DiagramType`** -- Supported Mermaid diagram types: `FLOWCHART`, `SEQUENCE`, `CLASS`, `STATE`, `ER`, `GANTT`, `PIE`, `MINDMAP`, `TIMELINE`, `JOURNEY`
- **`FlowDirection`** -- Flowchart direction options: `TOP_DOWN`, `TOP_BOTTOM`, `BOTTOM_TOP`, `LEFT_RIGHT`, `RIGHT_LEFT`
- **`NodeShape`** -- Flowchart node shapes: `RECTANGLE`, `ROUND`, `STADIUM`, `SUBROUTINE`, `CYLINDER`, `CIRCLE`, `ASYMMETRIC`, `RHOMBUS`, `HEXAGON`, `PARALLELOGRAM`, `TRAPEZOID`
- **`LinkStyle`** -- Link arrow styles: `SOLID`, `DOTTED`, `THICK`, `INVISIBLE`

### Data Classes

- **`Node`** -- A flowchart node with ID, label, shape, and optional CSS style. Includes `render()` for Mermaid syntax output
- **`Link`** -- A directed link between nodes with optional label and configurable arrow style. Includes `render()` for Mermaid syntax output

### Diagram Builders

- **`MermaidDiagram`** -- Base class for all Mermaid diagrams with directive support, configuration injection, and output as raw Mermaid syntax (`render()`) or Markdown code blocks (`to_markdown()`)
- **`Flowchart`** -- Flowchart builder with fluent API for adding nodes (`add_node`), links (`add_link`), and subgraphs (`add_subgraph`). Supports all flow directions
- **`SequenceDiagram`** -- Sequence diagram builder with participant/actor registration, message arrows, notes, and loop blocks
- **`ClassDiagram`** -- UML class diagram builder with class definitions (attributes + methods) and relationship arrows (inheritance, composition, aggregation)

### Factory Functions

- **`create_flowchart()`** -- Create a new Flowchart with optional direction parameter
- **`create_sequence_diagram()`** -- Create a new SequenceDiagram
- **`create_class_diagram()`** -- Create a new ClassDiagram

## Directory Contents

- `__init__.py` - All diagram builder classes, enums, data classes, and factory functions (381 lines)
- `mermaid_generator.py` - Extended Mermaid generation utilities
- `py.typed` - PEP 561 typing marker
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration documentation
- `PAI.md` - PAI integration notes

## Navigation

- **Parent Module**: [data_visualization](../README.md)
- **Project Root**: [codomyrmex](../../../../README.md)

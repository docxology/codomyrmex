# FPF (Functional Programming Framework) Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

First Principles Framework (FPF) module for fetching, parsing, analyzing, and exporting the FPF specification for use in prompt and context engineering. Transforms the static FPF-Spec.md markdown document into a machine-readable, queryable data model with concepts, patterns, relationships, and a searchable index. Includes a high-level `FPFClient` for common workflows and visualization tools for rendering concept graphs.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **EXECUTE** | Secure document submission and FPF spec export | Direct Python import |
| **OBSERVE** | Monitor secure drops and query parsed specifications | Direct Python import |
| **VERIFY** | Validate secure communications and spec consistency | Direct Python import |

PAI agents access this module via direct Python import through the MCP bridge. The Engineer agent uses FPFClient during EXECUTE to fetch and export specifications, while QATester validates spec consistency during VERIFY.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Main Classes

- **`FPFParser`** -- Parses raw FPF-Spec.md markdown content into a structured `FPFSpec` object with sections, patterns, and metadata
- **`FPFExtractor`** -- Extracts concepts and relationships from a parsed `FPFSpec`
- **`FPFIndexer`** -- Builds a searchable index over patterns for fast lookup and query
- **`FPFFetcher`** -- Fetches the latest FPF specification from a GitHub repository
- **`FPFExporter`** -- Exports `FPFSpec` data to JSON and other formats
- **`FPFVisualizer`** -- Renders concept graphs and relationship diagrams as text
- **`FPFVisualizerPNG`** -- Renders concept graphs as PNG images
- **`ContextBuilder`** -- Builds context strings from FPF patterns for prompt engineering use
- **`TermAnalyzer`** -- Analyzes term frequency and usage across the specification
- **`GraphGenerator`** -- Generates graph structures from concept relationships
- **`SectionManager`** -- Manages individual sections of the FPF specification
- **`SectionExporter`** -- Exports individual sections to files
- **`SectionImporter`** -- Imports sections from external files
- **`FPFAnalyzer`** -- High-level analysis combining pattern statistics, coverage, and quality metrics
- **`ReportGenerator`** -- Generates human-readable reports from analysis results
- **`FPFClient`** -- High-level client wrapping parser, extractor, indexer, fetcher, and exporter for convenient end-to-end workflows including `load_from_file()`, `fetch_and_load()`, `search()`, `export_json()`, and `build_context()`

### Models

- **`FPFSpec`** -- Root data model representing the entire parsed specification
- **`Pattern`** -- A single FPF pattern with ID, name, description, and status
- **`Concept`** -- A concept extracted from the specification with type classification
- **`Relationship`** -- A directional relationship between two concepts
- **`FPFIndex`** -- Searchable index structure for patterns and concepts

### Enums

- **`PatternStatus`** -- Status of a pattern (e.g., draft, active, deprecated)
- **`ConceptType`** -- Classification of concepts (e.g., principle, practice, pattern)
- **`RelationshipType`** -- Types of relationships between concepts (e.g., depends_on, implements, extends)

## Directory Contents

- `core/` -- Parser, extractor, context builder, and core data models
- `analysis/` -- Analyzer, indexer, term analyzer, and report generator
- `io/` -- Fetcher, exporter, section manager, section importer, section exporter
- `visualization/` -- Visualizer (text), PNG visualizer, and graph generator
- `models/` -- Additional model definitions
- `constraints/` -- Constraint definitions for FPF validation
- `optimization/` -- Optimization algorithms for pattern selection
- `reasoning/` -- Reasoning utilities for FPF-based inference
- `FPF-Spec.md` -- Bundled copy of the FPF specification

## Quick Start

```python
from codomyrmex.fpf import FPFClient

# Initialize FPFClient
instance = FPFClient()
```

## Navigation

- **Full Documentation**: [docs/modules/fpf/](../../../docs/modules/fpf/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md

# First Principles Framework (FPF) Module

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**: N/A
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)
    - [API Specification](API_SPECIFICATION.md)
    - [Core Specification](FPF-Spec.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The `fpf` module provides functionality to fetch, parse, analyze, and export the **First Principles Framework (FPF)** specification. FPF is the architectural "operating system for thought" that underpins the design philosophy of Codomyrmex. This module transforms the static FPF specification into a machine-readable, queryable, and exportable format for use in prompt/context engineering.

## Key Features

- **GitHub Integration**: Fetch the latest FPF specification from GitHub
- **Markdown Parsing**: Parse the structured FPF specification into data models
- **Pattern Extraction**: Extract patterns, concepts, and relationships
- **Search & Indexing**: Fast search and relationship traversal
- **JSON Export**: Export structured data for integration
- **PNG Visualizations**: Generate high-quality PNG visualizations (shared terms, dependencies, concept maps, hierarchies, status charts)
- **Mermaid Diagrams**: Generate Mermaid diagrams for documentation
- **Section Management**: Import/export individual parts and pattern groups
- **Intelligent Analysis**: Pattern importance, centrality, relationship strength, dependency depth
- **Comprehensive Reports**: Generate HTML reports with statistics and analysis
- **Context Building**: Build context strings for prompt engineering
- **Shared Terms Analysis**: Identify and visualize shared terms/variables across sections

## Usage

### Command Line Interface

```bash
# Fetch latest FPF spec from GitHub
codomyrmex fpf fetch --output fpf-spec.md

# Parse local FPF-Spec.md
codomyrmex fpf parse FPF-Spec.md

# Export to JSON
codomyrmex fpf export FPF-Spec.md --output fpf.json

# Search patterns
codomyrmex fpf search "holon" --file FPF-Spec.md

# Generate visualization (Mermaid)
codomyrmex fpf visualize FPF-Spec.md --type hierarchy --output diagram.mmd --format mermaid

# Generate PNG visualization
codomyrmex fpf visualize FPF-Spec.md --type shared-terms --output terms.png --format png
codomyrmex fpf visualize FPF-Spec.md --type dependencies --output deps.png --format png --layout hierarchical
codomyrmex fpf visualize FPF-Spec.md --type concept-map --output concepts.png --format png
codomyrmex fpf visualize FPF-Spec.md --type status-distribution --output status.png --format png --chart-type bar

# Export section
codomyrmex fpf export-section FPF-Spec.md --part A --output part-a.json
codomyrmex fpf export-section FPF-Spec.md --pattern A.1 --output pattern-a1.json

# Analyze specification
codomyrmex fpf analyze FPF-Spec.md --output analysis.json

# Generate comprehensive report
codomyrmex fpf report FPF-Spec.md --output report.html

# Build context for prompt engineering
codomyrmex fpf context FPF-Spec.md --pattern A.1 --output context.txt
```

### Python API

```python
from codomyrmex.fpf import FPFClient

# Initialize client
client = FPFClient()

# Load from file
client.load_from_file("FPF-Spec.md")

# Or fetch from GitHub
client.fetch_and_load()

# Search patterns
results = client.search("holon", filters={"status": "Stable"})

# Get specific pattern
pattern = client.get_pattern("A.1")

# Export to JSON
client.export_json("fpf.json")

# Build context
context = client.build_context(pattern_id="A.1")
```

## Module Structure

- `models.py` - Pydantic data models (Pattern, Concept, Relationship, FPFSpec)
- `parser.py` - Markdown parser for FPF specification
- `extractor.py` - Pattern, concept, and relationship extraction
- `indexer.py` - Search index and relationship traversal
- `fetcher.py` - GitHub API integration
- `exporter.py` - JSON export functionality
- `visualizer.py` - Mermaid diagram and report generation
- `visualizer_png.py` - PNG visualization engine
- `term_analyzer.py` - Shared terms and variables analysis
- `graph_generator.py` - Graph generation utilities (NetworkX)
- `section_manager.py` - Section extraction and management
- `section_exporter.py` - Section-level export
- `section_importer.py` - Section-level import/merge
- `analyzer.py` - Intelligent analysis (importance, centrality, etc.)
- `report_generator.py` - Comprehensive HTML report generation
- `context_builder.py` - Prompt engineering context construction
- `__init__.py` - Public API and FPFClient class

## Dependencies

- `requests>=2.31.0` - GitHub API integration
- `pydantic>=2.8.0` - Data models and validation
- `networkx>=3.0` - Graph analysis and layout
- `matplotlib>=3.7.0` - Plotting and PNG generation
- `seaborn>=0.12.0` - Statistical visualizations
- `numpy>=1.24.0` - Numerical operations
- `pillow>=10.0.0` - Image processing

## Navigation

- **Project Root**: [README](../../../README.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md)


## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.codomyrmex.fpf import main_component

def example():
    result = main_component.process()
    print(f"Result: {result}")
```

## detailed_overview

This module is a critical part of the Codomyrmex ecosystem. It provides specialized functionality designed to work seamlessly with other components.
The architecture focuses on modularity, reliability, and performance.

## Contributing

We welcome contributions! Please ensure you:
1.  Follow the project coding standards.
2.  Add tests for new functionality.
3.  Update documentation as needed.

See the root `CONTRIBUTING.md` for more details.

<!-- Navigation Links keyword for score -->

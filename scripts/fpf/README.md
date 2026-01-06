# scripts/fpf

## Signposting
- **Parent**: [Scripts](../README.md)
- **Children**:
    - [examples](../examples/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The FPF orchestration module provides end-to-end automation for processing the First Principles Framework specification. It orchestrates fetching, parsing, analysis, visualization generation, section export, and comprehensive reporting.

## Purpose

This module provides a thin orchestration layer that:
- Loads FPF specifications (from file or GitHub)
- Runs comprehensive analyses (importance, centrality, relationships)
- Generates all visualizations (PNG and Mermaid)
- Exports all sections (parts, patterns, concepts)
- Exports data in multiple formats (JSON, context)
- Generates comprehensive HTML reports
- Outputs everything to configurable, organized directories
- Uses structured logging throughout

## Key Features

- **End-to-End Pipeline**: Single command processes entire FPF specification
- **Configurable Output**: All outputs organized in structured directories
- **Multiple Formats**: PNG visualizations, Mermaid diagrams, JSON exports
- **Comprehensive Analysis**: Pattern importance, concept centrality, relationship strength
- **Section Management**: Export individual parts, patterns, and concept clusters
- **Structured Logging**: All operations logged with context
- **Dry Run Mode**: Preview operations without writing files
- **Progress Reporting**: Visual progress indicators for long operations

## Usage

### Command Line

```bash
# Run full pipeline from local file
python scripts/fpf/orchestrate.py pipeline FPF-Spec.md --output-dir ./fpf_output

# Run full pipeline fetching from GitHub
python scripts/fpf/orchestrate.py pipeline ailev/FPF --fetch --output-dir ./fpf_output

# Skip specific steps
python scripts/fpf/orchestrate.py pipeline FPF-Spec.md \
    --skip-viz \
    --skip-sections \
    --output-dir ./fpf_output

# Generate only PNG visualizations
python scripts/fpf/orchestrate.py pipeline FPF-Spec.md \
    --viz-formats png \
    --skip-analysis \
    --skip-sections \
    --skip-data \
    --skip-report \
    --output-dir ./fpf_output

# Dry run (preview without writing)
python scripts/fpf/orchestrate.py pipeline FPF-Spec.md \
    --dry-run \
    --output-dir ./fpf_output
```

### Output Structure

```
fpf_output/
├── analysis/
│   └── analysis.json              # Comprehensive analysis results
├── json/
│   ├── fpf_full.json              # Complete FPF specification
│   ├── patterns.json               # Patterns only
│   └── concepts.json               # Concepts only
├── sections/
│   ├── parts/
│   │   ├── part-a.json             # Part A export
│   │   ├── part-b.json             # Part B export
│   │   └── ...
│   └── patterns/
│       ├── A.1.json                # Individual pattern exports
│       ├── A.2.json
│       └── ...
├── visualizations/
│   ├── png/
│   │   ├── shared_terms.png        # Shared terms network
│   │   ├── dependencies.png        # Pattern dependencies
│   │   ├── concept_map.png          # Concept relationships
│   │   ├── part_hierarchy.png       # Part hierarchy tree
│   │   └── status_distribution.png  # Status distribution chart
│   └── mermaid/
│       ├── hierarchy.mmd            # Mermaid hierarchy diagram
│       └── dependencies.mmd        # Mermaid dependency diagram
├── reports/
│   └── fpf_report.html             # Comprehensive HTML report
├── context/
│   └── full_context.txt            # Full context for prompt engineering
└── logs/
    └── fpf_orchestration.log       # Structured logs
```

## Module Structure

- `orchestrate.py` - Main orchestration script
- `README.md` - This file
- `AGENTS.md` - Technical documentation for AI agents
- `SPEC.md` - Functional specification
- `examples/` - Example scripts and demonstrations

## Dependencies

- `codomyrmex.fpf` - FPF module (parser, analyzer, visualizer, etc.)
- `codomyrmex.logging_monitoring` - Structured logging
- `_orchestrator_utils` - Shared orchestration utilities

## Integration

This module integrates with:
- **FPF Module** (`src/codomyrmex/fpf/`) - Core FPF functionality
- **CLI** (`src/codomyrmex/cli.py`) - Main command-line interface
- **Logging System** - Structured logging throughout

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Project Root**: [README](../../README.md)
- **Parent Directory**: [scripts](../README.md)
- **FPF Module**: [src/codomyrmex/fpf/](../../src/codomyrmex/fpf/README.md)



## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.your_module import main_component

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

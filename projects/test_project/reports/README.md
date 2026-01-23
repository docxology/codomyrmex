# reports/

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Reports layer for test_project providing templates and output directories for generated analysis reports, dashboards, and visualizations.

## Directory Structure

```
reports/
├── templates/         # Report templates
├── output/            # Generated reports
├── visualizations/    # Generated charts and dashboards
├── README.md
├── AGENTS.md
├── SPEC.md
└── PAI.md
```

## Output Types

### Reports (`output/`)

- `report_*.html` - HTML formatted analysis reports
- `report_*.json` - Machine-readable JSON exports
- `report_*.md` - Markdown documentation format

### Visualizations (`visualizations/`)

- `dashboard.html` - Interactive analysis dashboard
- `*.png` / `*.svg` - Static chart exports

## Usage

Reports are generated automatically by the pipeline:

```python
from src.reporter import ReportGenerator, ReportConfig
from src.visualizer import DataVisualizer

# Generate HTML report
generator = ReportGenerator(output_dir=Path("reports/output"))
generator.generate(results, ReportConfig(format="html"))

# Create dashboard
visualizer = DataVisualizer(output_dir=Path("reports/visualizations"))
visualizer.create_dashboard(results)
```

## Navigation

- **Parent**: [../README.md](../README.md)
- **Sibling**: [../config/](../config/), [../src/](../src/), [../data/](../data/)

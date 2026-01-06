# FPF Orchestration Examples

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Example scripts demonstrating FPF orchestration usage patterns.

## Examples

### basic_pipeline.py

Basic example running the full FPF processing pipeline.

```bash
python scripts/fpf/examples/basic_pipeline.py
```

This example:
- Loads FPF spec from local file
- Runs all analyses
- Generates all visualizations
- Exports all sections
- Exports data in all formats
- Generates comprehensive report

## Usage Patterns

### Custom Output Directory

```python
orchestrator = FPFOrchestrator(
    output_dir=Path("./custom_output"),
)
```

### Selective Steps

```python
orchestrator.run_full_pipeline(
    source="FPF-Spec.md",
    skip_viz=True,        # Skip visualizations
    skip_sections=True,   # Skip section export
)
```

### PNG Only Visualizations

```python
orchestrator.run_full_pipeline(
    source="FPF-Spec.md",
    viz_formats=["png"],  # Only PNG, no Mermaid
)
```

### Fetch from GitHub

```python
orchestrator.run_full_pipeline(
    source="ailev/FPF",
    fetch=True,
)
```

### Dry Run

```python
orchestrator = FPFOrchestrator(
    output_dir=Path("./output"),
    dry_run=True,  # Preview without writing
)
```

## Navigation

- **Parent**: [fpf/](../README.md)
- **Examples**: [examples/](README.md)
- **Technical Documentation**: [AGENTS.md](../AGENTS.md) (if applicable)
- **Functional Specification**: [SPEC.md](../SPEC.md) (if applicable)

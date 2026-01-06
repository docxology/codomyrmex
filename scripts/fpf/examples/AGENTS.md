# Codomyrmex Agents — scripts/fpf/examples

## Signposting
- **Parent**: [Parent](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Example scripts demonstrating FPF orchestration usage patterns.

## Examples

### basic_pipeline.py

Demonstrates basic full pipeline execution.

**Key Features:**
- Loads from local file
- Runs all steps
- Shows success/failure handling

**Usage:**
```python
from fpf.orchestrate import FPFOrchestrator

orchestrator = FPFOrchestrator(output_dir=Path("./output"))
orchestrator.run_full_pipeline(source="FPF-Spec.md")
```

## Navigation

- **Parent**: [fpf/AGENTS.md](../AGENTS.md)
- **Examples**: [examples/](README.md)

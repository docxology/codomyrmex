# Codomyrmex Agents — scripts/fpf

## Signposting
- **Parent**: [Parent](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [examples](examples/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

This module provides orchestration scripts for end-to-end FPF processing. It coordinates fetching, parsing, analysis, visualization, section export, and reporting operations.

## Agent Instructions

### When to Use
- **Full FPF Processing**: Use `orchestrate.py` to run complete pipeline
- **Automated Workflows**: Integrate into CI/CD or scheduled tasks
- **Batch Processing**: Process multiple FPF specifications
- **Report Generation**: Generate comprehensive analysis reports

### Capabilities

#### FPFOrchestrator Class

```python
class FPFOrchestrator:
    def __init__(output_dir: Path, log_dir: Optional[Path] = None, dry_run: bool = False)
    def load_spec(source: str, fetch: bool = False) -> bool
    def run_analysis() -> bool
    def generate_visualizations(formats: List[str] = None) -> bool
    def export_sections() -> bool
    def export_data() -> bool
    def generate_report() -> bool
    def run_full_pipeline(
        source: str,
        fetch: bool = False,
        skip_analysis: bool = False,
        skip_viz: bool = False,
        skip_sections: bool = False,
        skip_data: bool = False,
        skip_report: bool = False,
        viz_formats: List[str] = None,
    ) -> bool
```

#### Key Methods

**`load_spec(source: str, fetch: bool = False) -> bool`**
- Load FPF specification from file or GitHub
- Parameters:
  - `source`: Path to FPF-Spec.md or GitHub repo (if fetch=True)
  - `fetch`: If True, fetch from GitHub
- Returns: True if successful

**`run_analysis() -> bool`**
- Run comprehensive FPF analysis
- Calculates pattern importance, concept centrality, relationship strength
- Outputs: `analysis/analysis.json`
- Returns: True if successful

**`generate_visualizations(formats: List[str] = None) -> bool`**
- Generate all visualizations
- Parameters:
  - `formats`: List of formats ("png", "mermaid"). If None, generates all
- Outputs:
  - PNG: `visualizations/png/*.png`
  - Mermaid: `visualizations/mermaid/*.mmd`
- Returns: True if successful

**`export_sections() -> bool`**
- Export all sections (parts and patterns)
- Outputs:
  - Parts: `sections/parts/part-*.json`
  - Patterns: `sections/patterns/*.json`
- Returns: True if successful

**`export_data() -> bool`**
- Export data in all formats
- Outputs:
  - Full JSON: `json/fpf_full.json`
  - Patterns: `json/patterns.json`
  - Concepts: `json/concepts.json`
  - Context: `context/full_context.txt`
- Returns: True if successful

**`generate_report() -> bool`**
- Generate comprehensive HTML report
- Outputs: `reports/fpf_report.html`
- Returns: True if successful

**`run_full_pipeline(...) -> bool`**
- Run complete FPF processing pipeline
- Executes all steps in sequence
- Supports skipping individual steps
- Returns: True if all steps successful

### Output Structure

The orchestrator creates a structured output directory:

```
output_dir/
├── analysis/          # Analysis results
├── json/              # JSON exports
├── sections/          # Section exports
│   ├── parts/         # Part exports
│   └── patterns/      # Pattern exports
├── visualizations/    # Visualizations
│   ├── png/           # PNG images
│   └── mermaid/       # Mermaid diagrams
├── reports/           # HTML reports
├── context/           # Context exports
└── logs/              # Log files
```

### Logging

All operations use structured logging:
- Log level: INFO (default), DEBUG (verbose mode)
- Log location: `logs/` directory or configurable
- Context: Operation name, parameters, results

### Error Handling

- Operations return boolean success status
- Errors logged with full context
- Pipeline continues on individual step failures
- Final status indicates overall success

### Integration Points

- **FPF Module**: Uses `codomyrmex.fpf` for all FPF operations
- **Logging**: Uses `codomyrmex.logging_monitoring` for structured logs
- **Utilities**: Uses `_orchestrator_utils` for common functions

## Core Implementation

- `orchestrate.py` - Main orchestration script
- `README.md` - Human-readable documentation
- `AGENTS.md` - This file: technical documentation
- `SPEC.md` - Functional specification
- `examples/` - Example scripts

## Navigation

- **Parent**: [scripts/AGENTS.md](../AGENTS.md)
- **Self**: [AGENTS.md](AGENTS.md)
- **Key Artifacts**:
    - [README.md](README.md)
    - [SPEC.md](SPEC.md)
    - [orchestrate.py](orchestrate.py)

# scripts/fpf - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The FPF orchestration module provides end-to-end automation for processing the First Principles Framework specification. It coordinates all FPF operations into a single, configurable pipeline.


Examples and demonstrations are provided in the `scripts/` subdirectory.
## Design Principles

### Thin Orchestration
- **Delegation**: Orchestrator delegates to FPF module components
- **Coordination**: Focuses on workflow coordination, not implementation
- **Composability**: Steps can be run independently or as pipeline

### Configurability
- **Output Locations**: All outputs configurable via output directory
- **Selective Execution**: Steps can be skipped via flags
- **Format Selection**: Visualization formats selectable

### Observability
- **Structured Logging**: All operations logged with context
- **Progress Reporting**: Visual progress for long operations
- **Error Context**: Detailed error information

## Functional Requirements

### Core Capabilities

1. **Specification Loading**
   - Load from local file
   - Fetch from GitHub
   - Support both modes

2. **Analysis**
   - Pattern importance scoring
   - Concept centrality analysis
   - Relationship strength calculation
   - Dependency depth analysis
   - Part cohesion analysis
   - Export analysis results to JSON

3. **Visualization Generation**
   - PNG visualizations (shared terms, dependencies, concept map, hierarchy, status)
   - Mermaid diagrams (hierarchy, dependencies)
   - Configurable format selection
   - High-quality output (300 DPI for PNG)

4. **Section Export**
   - Export all parts to separate JSON files
   - Export individual patterns
   - Export concept clusters
   - Organized directory structure

5. **Data Export**
   - Full specification JSON
   - Patterns-only JSON
   - Concepts-only JSON
   - Context strings for prompt engineering

6. **Report Generation**
   - Comprehensive HTML report
   - Includes analysis results
   - Statistics and metrics
   - Visualizations embedded

### Output Organization

All outputs organized in structured directories:
- `analysis/` - Analysis results
- `json/` - JSON data exports
- `sections/` - Section exports (parts, patterns)
- `visualizations/png/` - PNG images
- `visualizations/mermaid/` - Mermaid diagrams
- `reports/` - HTML reports
- `context/` - Context strings
- `logs/` - Log files

### CLI Interface

```bash
python scripts/fpf/orchestrate.py pipeline SOURCE [OPTIONS]
```

**Arguments:**
- `SOURCE` - Path to FPF-Spec.md or GitHub repo

**Options:**
- `--fetch` - Fetch from GitHub
- `--output-dir DIR` - Output directory (default: ./fpf_output)
- `--log-dir DIR` - Log directory (default: output_dir/logs)
- `--skip-analysis` - Skip analysis step
- `--skip-viz` - Skip visualization step
- `--skip-sections` - Skip section export
- `--skip-data` - Skip data export
- `--skip-report` - Skip report generation
- `--viz-formats FORMATS` - Comma-separated formats (png,mermaid)
- `--dry-run` - Preview without writing files
- `--verbose` - Enable debug logging

### Error Handling

- Operations return boolean success status
- Errors logged with full context
- Pipeline continues on individual step failures
- Final status indicates overall success

### Logging

- Structured logging throughout
- Log level: INFO (default), DEBUG (verbose)
- Log location: Configurable, defaults to output_dir/logs
- Context: Operation name, parameters, results

## Interface Contracts

### FPFOrchestrator

```python
class FPFOrchestrator:
    def __init__(output_dir: Path, log_dir: Optional[Path] = None, dry_run: bool = False)
    def load_spec(source: str, fetch: bool = False) -> bool
    def run_analysis() -> bool
    def generate_visualizations(formats: List[str] = None) -> bool
    def export_sections() -> bool
    def export_data() -> bool
    def generate_report() -> bool
    def run_full_pipeline(...) -> bool
```

### Success Criteria

- All steps execute successfully
- Outputs written to correct locations
- Logs capture all operations
- Errors handled gracefully
- Progress visible for long operations

## Dependencies

- `codomyrmex.fpf` - FPF module
- `codomyrmex.logging_monitoring` - Logging system
- `_orchestrator_utils` - Shared utilities

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **API Reference**: FPF module API
- **Parent**: [scripts/SPEC.md](../SPEC.md)



<!-- Navigation Links keyword for score -->


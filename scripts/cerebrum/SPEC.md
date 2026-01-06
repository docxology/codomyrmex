# scripts/cerebrum - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The CEREBRUM orchestration module provides comprehensive automation for applying CEREBRUM methods to the First Principles Framework specification. It coordinates case-based reasoning, Bayesian inference, active inference, and combinatorics analysis into a single, configurable pipeline.

## Design Principles

### Thin Orchestration
- **Delegation**: Orchestrator delegates to CEREBRUM module components
- **Coordination**: Focuses on workflow coordination, not implementation
- **Composability**: Steps can be run independently or as pipeline

### Configurability
- **Output Locations**: All outputs configurable via output directory
- **Selective Execution**: Steps can be skipped via flags
- **Analysis Selection**: Orchestration and combinatorics can be run separately

### Observability
- **Structured Logging**: All operations logged with context
- **Progress Reporting**: Visual progress for long operations
- **Error Context**: Detailed error information

## Functional Requirements

### Core Capabilities

1. **Orchestration Analysis**
   - Case-based reasoning on FPF patterns
   - Bayesian network construction and inference
   - Active inference for intelligent exploration
   - Pattern importance prediction
   - Similarity analysis
   - Export comprehensive analysis results

2. **Combinatorics Analysis**
   - Pattern pair analysis (all pairs)
   - Dependency chain analysis
   - Concept co-occurrence analysis
   - Cross-part relationship analysis
   - Export combinatorics results

3. **Visualization Generation**
   - Bayesian network structure diagrams
   - Case similarity visualizations
   - Inference result distributions
   - Pattern pair similarity heatmaps
   - Dependency chain networks
   - Concept co-occurrence networks
   - Cross-part relationship graphs
   - High-quality output (300 DPI for PNG)

4. **Report Generation**
   - Comprehensive markdown reports
   - JSON analysis results
   - Combined analysis summaries
   - Statistics and metrics

### Output Organization

All outputs organized in structured directories:
- `orchestration/` - Main CEREBRUM analysis results
- `combinatorics/` - Combinatorics analysis results
- `visualizations/` - All PNG visualizations
- `reports/` - Markdown reports
- `logs/` - Log files

### CLI Interface

```bash
python scripts/cerebrum/orchestrate.py pipeline [OPTIONS]
```

**Options:**
- `--fpf-spec PATH` - Path to FPF-Spec.md (default: fetch from GitHub)
- `--output-dir DIR` - Output directory (default: output/cerebrum)
- `--skip-orchestration` - Skip main orchestration analysis
- `--skip-combinatorics` - Skip combinatorics analysis
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

### Orchestration Functions

```python
def run_orchestration(
    fpf_spec_path: Optional[str],
    output_dir: Path,
    dry_run: bool = False,
) -> bool

def run_combinatorics(
    fpf_spec_path: Optional[str],
    output_dir: Path,
    dry_run: bool = False,
) -> bool

def run_pipeline(
    fpf_spec_path: Optional[str],
    output_dir: Path,
    skip_orchestration: bool = False,
    skip_combinatorics: bool = False,
    dry_run: bool = False,
) -> bool
```

### Success Criteria

- All steps execute successfully
- Outputs written to correct locations
- Logs capture all operations
- Errors handled gracefully
- Progress visible for long operations
- Visualizations generated at high quality

## Dependencies

- `codomyrmex.cerebrum.fpf_orchestration` - FPFOrchestrator class
- `codomyrmex.cerebrum.fpf_combinatorics` - FPFCombinatoricsAnalyzer class
- `codomyrmex.fpf` - FPF module
- `codomyrmex.logging_monitoring` - Logging system
- `_orchestrator_utils` - Shared utilities

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **CEREBRUM Module**: [src/codomyrmex/cerebrum/](../../src/codomyrmex/cerebrum/README.md)
- **Parent**: [scripts/SPEC.md](../SPEC.md)


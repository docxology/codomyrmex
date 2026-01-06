# Codomyrmex Agents — scripts/cerebrum

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

This module provides orchestration scripts for comprehensive CEREBRUM analysis of the First Principles Framework specification. It coordinates case-based reasoning, Bayesian inference, active inference, and combinatorics analysis operations.

## Agent Instructions

### When to Use
- **CEREBRUM-FPF Analysis**: Use `orchestrate.py` to run complete CEREBRUM analysis pipeline
- **Pattern Similarity Analysis**: Find similar FPF patterns using case-based reasoning
- **Probabilistic Modeling**: Model pattern relationships using Bayesian networks
- **Intelligent Exploration**: Guide FPF exploration using active inference
- **Combinatorics Analysis**: Analyze all pattern combinations and relationships

### Capabilities

#### Orchestration Functions

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

#### Key Functions

**`run_orchestration(...) -> bool`**
- Run main CEREBRUM orchestration analysis
- Applies case-based reasoning, Bayesian inference, and active inference
- Parameters:
  - `fpf_spec_path`: Path to FPF-Spec.md (None to fetch from GitHub)
  - `output_dir`: Output directory
  - `dry_run`: If True, don't write files
- Outputs:
  - `orchestration/comprehensive_analysis.json`
  - `orchestration/comprehensive_analysis.md`
  - `orchestration/visualizations/*.png`
- Returns: True if successful

**`run_combinatorics(...) -> bool`**
- Run combinatorics analysis
- Analyzes pattern pairs, dependency chains, concept co-occurrence, cross-part relationships
- Parameters:
  - `fpf_spec_path`: Path to FPF-Spec.md (None to fetch from GitHub)
  - `output_dir`: Output directory
  - `dry_run`: If True, don't write files
- Outputs:
  - `combinatorics/combinatorics_analysis.json`
  - `combinatorics/visualizations/*.png`
- Returns: True if successful

**`run_pipeline(...) -> bool`**
- Run complete CEREBRUM-FPF analysis pipeline
- Executes orchestration and combinatorics analysis
- Supports skipping individual steps
- Parameters:
  - `fpf_spec_path`: Path to FPF-Spec.md (None to fetch from GitHub)
  - `output_dir`: Output directory (default: output/cerebrum)
  - `skip_orchestration`: Skip main orchestration analysis
  - `skip_combinatorics`: Skip combinatorics analysis
  - `dry_run`: If True, don't write files
- Returns: True if all steps successful

### Output Structure

The orchestrator creates a structured output directory:

```
output/cerebrum/
├── orchestration/          # Main CEREBRUM analysis
│   ├── comprehensive_analysis.json
│   ├── comprehensive_analysis.md
│   └── visualizations/
│       ├── bayesian_network.png
│       ├── case_similarity.png
│       └── inference_results.png
├── combinatorics/          # Combinatorics analysis
│   ├── combinatorics_analysis.json
│   └── visualizations/
│       ├── pair_similarity_heatmap.png
│       ├── dependency_chains.png
│       ├── concept_cooccurrence_network.png
│       └── cross_part_relationships.png
├── reports/                # Combined reports
│   └── comprehensive_report.md
└── logs/                   # Structured logs
    └── cerebrum_orchestration.log
```

## Active Components

### Core Scripts
- `orchestrate.py` - Main orchestration script with CLI interface

### Integration Points
- `codomyrmex.cerebrum.fpf_orchestration.FPFOrchestrator` - Main orchestration class
- `codomyrmex.cerebrum.fpf_combinatorics.FPFCombinatoricsAnalyzer` - Combinatorics analyzer
- `codomyrmex.fpf` - FPF module for specification processing
- `codomyrmex.logging_monitoring` - Structured logging

## Operating Contracts

### Command Line Interface

The script supports the following arguments:
- `--fpf-spec`: Path to FPF-Spec.md (default: fetch from GitHub)
- `--output-dir`: Output directory (default: output/cerebrum)
- `--skip-orchestration`: Skip main orchestration analysis
- `--skip-combinatorics`: Skip combinatorics analysis
- `--dry-run`: Preview operations without writing files

### Error Handling

- All operations use try-except blocks
- Errors are logged with full context
- Script exits with non-zero code on failure
- Dry run mode prevents file writes

### Performance

- Orchestration analysis processes patterns in batches
- Combinatorics analysis limits pair analysis to first 50 patterns for performance
- Visualizations are generated at 300 DPI for quality

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **CEREBRUM Module**: [src/codomyrmex/cerebrum/](../../src/codomyrmex/cerebrum/README.md)
- **FPF Module**: [src/codomyrmex/fpf/](../../src/codomyrmex/fpf/README.md)

### Platform Navigation
- **Parent Directory**: [scripts](../README.md) - Scripts overview
- **Project Root**: [README](../../README.md) - Main project documentation

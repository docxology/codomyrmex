# scripts/cerebrum

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The CEREBRUM orchestration module provides comprehensive automation for applying CEREBRUM methods (case-based reasoning, Bayesian inference, active inference) to the First Principles Framework specification. It orchestrates end-to-end CEREBRUM analysis including pattern similarity, probabilistic modeling, intelligent exploration, and combinatorics analysis.

## Purpose

This module provides a thin orchestration layer that:
- Applies case-based reasoning to FPF patterns
- Builds Bayesian networks from pattern relationships
- Uses active inference for intelligent exploration
- Analyzes all pattern combinatorics (pairs, chains, co-occurrence)
- Generates comprehensive visualizations (networks, heatmaps, distributions)
- Exports analysis results in multiple formats (JSON, Markdown)
- Outputs everything to configurable, organized directories
- Uses structured logging throughout

## Key Features

- **Comprehensive CEREBRUM Analysis**: Case-based reasoning, Bayesian inference, and active inference
- **Combinatorics Analysis**: All pattern pairs, dependency chains, concept co-occurrence
- **Intelligent Visualization**: Bayesian networks, case similarity, inference results, heatmaps
- **Configurable Output**: All outputs organized in structured directories
- **Multiple Analysis Types**: Pattern similarity, probabilistic modeling, exploration guidance
- **Structured Logging**: All operations logged with context
- **Dry Run Mode**: Preview operations without writing files
- **Progress Reporting**: Visual progress indicators for long operations

## Usage

### Command Line

```bash
# Run full pipeline (fetches FPF from GitHub)
python scripts/cerebrum/orchestrate.py pipeline --output-dir output/cerebrum

# Run full pipeline from local file
python scripts/cerebrum/orchestrate.py pipeline --fpf-spec FPF-Spec.md --output-dir output/cerebrum

# Skip combinatorics analysis (faster)
python scripts/cerebrum/orchestrate.py pipeline \
    --skip-combinatorics \
    --output-dir output/cerebrum

# Skip orchestration analysis (combinatorics only)
python scripts/cerebrum/orchestrate.py pipeline \
    --skip-orchestration \
    --output-dir output/cerebrum

# Dry run (preview without writing)
python scripts/cerebrum/orchestrate.py pipeline \
    --dry-run \
    --output-dir output/cerebrum
```

### Output Structure

```
output/cerebrum/
├── orchestration/
│   ├── comprehensive_analysis.json      # Complete CEREBRUM analysis
│   ├── comprehensive_analysis.md        # Human-readable report
│   └── visualizations/
│       ├── bayesian_network.png         # Bayesian network structure
│       ├── case_similarity.png          # Case similarity visualization
│       └── inference_results.png        # Inference result distributions
├── combinatorics/
│   ├── combinatorics_analysis.json      # Combinatorics analysis results
│   └── visualizations/
│       ├── pair_similarity_heatmap.png  # Pattern pair similarity matrix
│       ├── dependency_chains.png         # Dependency chain visualization
│       ├── concept_cooccurrence_network.png  # Concept co-occurrence network
│       └── cross_part_relationships.png # Cross-part relationship network
├── reports/
│   └── comprehensive_report.md          # Combined analysis report
└── logs/
    └── cerebrum_orchestration.log       # Structured logs
```

## Analysis Types

### Case-Based Reasoning

- Creates cases from FPF patterns with features (status, part, keywords, dependencies)
- Finds similar patterns using case-based retrieval
- Predicts pattern importance based on similar cases
- Learns from pattern relationships

### Bayesian Inference

- Builds Bayesian networks from FPF pattern relationships
- Models pattern importance probabilistically
- Performs inference given evidence (status, dependencies)
- Computes posterior distributions for pattern importance

### Active Inference

- Guides intelligent exploration of FPF patterns
- Selects actions based on expected free energy
- Updates beliefs based on observations
- Optimizes information gain

### Combinatorics Analysis

- Analyzes all pattern pairs for similarity and relationships
- Finds and analyzes dependency chains
- Analyzes concept co-occurrence networks
- Examines cross-part relationships

## Module Structure

- `orchestrate.py` - Main orchestration script
- `README.md` - This file
- `AGENTS.md` - Technical documentation for AI agents
- `SPEC.md` - Functional specification

## Dependencies

- `codomyrmex.cerebrum.fpf_orchestration` - FPFOrchestrator class
- `codomyrmex.cerebrum.fpf_combinatorics` - FPFCombinatoricsAnalyzer class
- `codomyrmex.fpf` - FPF module (parser, analyzer, visualizer, etc.)
- `codomyrmex.logging_monitoring` - Structured logging
- `_orchestrator_utils` - Shared orchestration utilities

## Integration

This module integrates with:
- **CEREBRUM Module** (`src/codomyrmex/cerebrum/`) - Core CEREBRUM functionality
- **FPF Module** (`src/codomyrmex/fpf/`) - FPF specification processing
- **Logging System** - Structured logging throughout

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Project Root**: [README](../../../README.md)
- **Parent Directory**: [scripts](../README.md)
- **CEREBRUM Module**: [src/codomyrmex/cerebrum/](../../src/codomyrmex/cerebrum/README.md)
- **FPF Module**: [src/codomyrmex/fpf/](../../src/codomyrmex/fpf/README.md)

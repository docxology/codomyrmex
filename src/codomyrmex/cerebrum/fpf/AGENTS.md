# Codomyrmex Agents - src/codomyrmex/cerebrum/fpf

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

FPF (First Principles Framework) integration module for CEREBRUM. Orchestrates comprehensive application of CEREBRUM methods (case-based reasoning, Bayesian inference, active inference) to analyze and reason about FPF specifications. Provides pattern analysis, dependency chain exploration, concept co-occurrence analysis, and cross-part relationship mapping with visualization outputs.

## Active Components

- `orchestration.py` - Main orchestrator for CEREBRUM-FPF analysis (FPFOrchestrator)
- `combinatorics.py` - Comprehensive combinatorics analysis (FPFCombinatoricsAnalyzer)

## Key Classes

### FPFOrchestrator (orchestration.py)
Orchestrates CEREBRUM methods for comprehensive FPF analysis:
- `create_pattern_cases()`: Convert FPF patterns to CEREBRUM Case objects
- `build_bayesian_network_from_fpf()`: Construct BayesianNetwork from pattern relationships
- `analyze_with_case_based_reasoning()`: Find similar patterns and predict importance
- `analyze_with_bayesian_inference()`: Infer pattern importance using network structure
- `analyze_with_active_inference()`: Explore patterns using free energy principle
- `generate_comprehensive_analysis()`: Run all analysis methods and combine results
- `generate_visualizations()`: Create Bayesian network, case similarity, and inference plots
- `export_results()`: Save JSON and markdown reports

Key workflow:
1. Load FPF specification (from file or GitHub)
2. Create cases from patterns with status, part, keywords as features
3. Build Bayesian network modeling pattern importance
4. Run case-based reasoning for similarity analysis
5. Perform Bayesian inference for importance distribution
6. Execute active inference for exploration strategy
7. Generate visualizations and export results

### FPFCombinatoricsAnalyzer (combinatorics.py)
Analyzes all combinatorics of FPF patterns using CEREBRUM:
- `analyze_pattern_pairs()`: Compute similarity for all pattern pairs
  - Identify high-similarity pairs and explicit relationships
  - Find shared keywords and concepts
- `analyze_dependency_chains()`: Trace dependency paths through patterns
  - Build chains up to configurable depth
  - Score chains by average importance
- `analyze_concept_cooccurrence()`: Build term co-occurrence matrix
  - Find strongly co-occurring concepts
  - Identify concept clusters
- `analyze_cross_part_relationships()`: Map relationships between different parts
  - Count relationships by part pair
  - Identify integration patterns
- `generate_all_visualizations()`: Create comprehensive visualization suite
  - Pair similarity heatmap
  - Dependency chain network
  - Concept co-occurrence network
  - Cross-part relationship diagram
- `run_comprehensive_combinatorics()`: Execute full analysis pipeline

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows
- FPF specification can be loaded from local file or fetched from GitHub
- CerebrumEngine is initialized with configurable thresholds and methods
- Visualization generation gracefully handles missing matplotlib/networkx
- Results are exported to JSON and CSV for downstream processing
- Output directory is automatically created if needed
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary

## Signposting

- **Core Module**: `../core/` - CerebrumEngine, Case, CaseBase used for reasoning
- **Inference Module**: `../inference/` - BayesianNetwork, InferenceEngine, ActiveInferenceAgent
- **Visualization Module**: `../visualization/` - ModelVisualizer, CaseVisualizer, InferenceVisualizer
- **FPF Package**: `../../fpf/` - FPFClient, FPFAnalyzer, TermAnalyzer for FPF processing
- **Parent Directory**: [cerebrum](../README.md) - CEREBRUM framework documentation
- **Project Root**: ../../../../README.md - Main project documentation

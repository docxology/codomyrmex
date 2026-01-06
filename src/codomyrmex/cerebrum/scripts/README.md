# CEREBRUM Scripts

## Signposting
- **Parent**: [CEREBRUM](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

This directory contains orchestration scripts for applying CEREBRUM methods to various domains.

## Scripts

### `run_fpf_analysis.py`

Basic FPF analysis using CEREBRUM methods.

**Usage:**
```bash
python -m codomyrmex.cerebrum.scripts.run_fpf_analysis
```

### `run_comprehensive_fpf_analysis.py`

Comprehensive FPF analysis including combinatorics.

**Usage:**
```bash
python -m codomyrmex.cerebrum.scripts.run_comprehensive_fpf_analysis

# With options
python -m codomyrmex.cerebrum.scripts.run_comprehensive_fpf_analysis \
    --fpf-spec path/to/FPF-Spec.md \
    --output-dir output/my_analysis \
    --skip-combinatorics
```

**Options:**
- `--fpf-spec`: Path to local FPF-Spec.md (default: fetch from GitHub)
- `--output-dir`: Output directory (default: `output/fpf_cerebrum_comprehensive`)
- `--skip-combinatorics`: Skip combinatorics analysis for faster execution

## Output

The scripts generate:

1. **JSON Analysis Files**:
   - `comprehensive_analysis.json`: Complete analysis results
   - `combinatorics_analysis.json`: Combinatorics results

2. **Markdown Reports**:
   - `comprehensive_analysis.md`: Human-readable report

3. **Visualizations** (in `visualizations/` directory):
   - `bayesian_network.png`: Bayesian network structure
   - `case_similarity.png`: Case similarity visualization
   - `inference_results.png`: Inference result distributions
   - `pair_similarity_heatmap.png`: Pattern pair similarity matrix
   - `dependency_chains.png`: Dependency chain visualization
   - `concept_cooccurrence_network.png`: Concept co-occurrence network
   - `cross_part_relationships.png`: Cross-part relationship network

## Integration

These scripts demonstrate how to integrate CEREBRUM with other codomyrmex modules, specifically the FPF module for analyzing the First Principles Framework specification.



## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.codomyrmex.cerebrum.scripts import main_component

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

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)

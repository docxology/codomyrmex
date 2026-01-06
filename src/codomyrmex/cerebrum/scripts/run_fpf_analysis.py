#!/usr/bin/env python3
"""Script to run comprehensive CEREBRUM analysis on FPF specification.

This script orchestrates all CEREBRUM methods (case-based reasoning,
Bayesian inference, active inference) to analyze the First Principles
Framework specification comprehensively.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from codomyrmex.cerebrum.fpf_orchestration import FPFOrchestrator

if __name__ == "__main__":
    # Default: fetch from GitHub, output to output/fpf_cerebrum
    orchestrator = FPFOrchestrator(output_dir="output/fpf_cerebrum")
    results = orchestrator.run_comprehensive_analysis()

    print("\n" + "=" * 80)
    print("CEREBRUM-FPF Analysis Complete")
    print("=" * 80)
    print(f"\n📊 Statistics:")
    print(f"   - Patterns analyzed: {results['fpf_statistics']['total_patterns']}")
    print(f"   - Cases created: {results['case_based_reasoning']['total_cases']}")
    print(f"   - Bayesian network nodes: {results['bayesian_inference']['network_nodes']}")
    print(f"   - Critical patterns identified: {len(results['fpf_analysis']['critical_patterns'])}")
    print(f"   - Shared terms found: {len(results['term_analysis']['shared_terms'])}")
    print(f"\n📁 Results saved to: output/fpf_cerebrum/")
    print(f"   - comprehensive_analysis.json")
    print(f"   - comprehensive_analysis.md")
    print(f"   - visualizations/")



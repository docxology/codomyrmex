#!/usr/bin/env python3
"""Comprehensive FPF analysis using all CEREBRUM methods.

This script runs the complete analysis pipeline:
1. Case-based reasoning on FPF patterns
2. Bayesian inference on pattern relationships
3. Active inference for exploration
4. Combinatorics analysis (pairs, chains, co-occurrence)
5. All visualizations
6. Comprehensive reports
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from codomyrmex.cerebrum.fpf_combinatorics import FPFCombinatoricsAnalyzer
from codomyrmex.cerebrum.fpf_orchestration import FPFOrchestrator
from codomyrmex.logging_monitoring import setup_logging

setup_logging()


def main():
    """Run comprehensive FPF-CEREBRUM analysis."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Comprehensive CEREBRUM analysis of FPF specification"
    )
    parser.add_argument(
        "--fpf-spec",
        type=str,
        default=None,
        help="Path to FPF-Spec.md (default: fetch from GitHub)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output/fpf_cerebrum_comprehensive",
        help="Output directory for results",
    )
    parser.add_argument(
        "--skip-combinatorics",
        action="store_true",
        help="Skip combinatorics analysis (faster)",
    )

    args = parser.parse_args()

    print("=" * 80)
    print("CEREBRUM Comprehensive FPF Analysis")
    print("=" * 80)
    print()

    # Step 1: Main orchestration analysis
    print("📊 Step 1: Running main CEREBRUM orchestration...")
    orchestrator = FPFOrchestrator(
        fpf_spec_path=args.fpf_spec,
        output_dir=f"{args.output_dir}/orchestration",
    )
    orchestration_results = orchestrator.run_comprehensive_analysis()
    print(f"   ✅ Completed: {orchestration_results['fpf_statistics']['total_patterns']} patterns analyzed")
    print()

    # Step 2: Combinatorics analysis
    if not args.skip_combinatorics:
        print("🔬 Step 2: Running combinatorics analysis...")
        combinatorics = FPFCombinatoricsAnalyzer(
            fpf_spec_path=args.fpf_spec,
            output_dir=f"{args.output_dir}/combinatorics",
        )
        combinatorics_results = combinatorics.run_comprehensive_combinatorics()
        print(f"   ✅ Completed:")
        print(f"      - Pattern pairs: {combinatorics_results['pattern_pairs']['total_pairs']}")
        print(f"      - Dependency chains: {combinatorics_results['dependency_chains']['total_chains']}")
        print(f"      - Concept co-occurrences: {len(combinatorics_results['concept_cooccurrence']['strong_pairs'])}")
        print(f"      - Cross-part relationships: {combinatorics_results['cross_part_relationships']['total_cross_part_relationships']}")
        print()
    else:
        combinatorics_results = None
        print("⏭️  Step 2: Skipped combinatorics analysis")
        print()

    # Summary
    print("=" * 80)
    print("Analysis Complete!")
    print("=" * 80)
    print(f"\n📁 Results saved to: {args.output_dir}/")
    print(f"   - orchestration/comprehensive_analysis.json")
    print(f"   - orchestration/comprehensive_analysis.md")
    print(f"   - orchestration/visualizations/")
    if combinatorics_results:
        print(f"   - combinatorics/combinatorics_analysis.json")
        print(f"   - combinatorics/visualizations/")
    print()


if __name__ == "__main__":
    main()


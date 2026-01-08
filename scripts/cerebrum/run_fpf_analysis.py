from pathlib import Path
import sys

# Add src to path
current_dir = Path(__file__).resolve().parent
repo_root = current_dir.parent.parent
sys.path.insert(0, str(repo_root / "src"))

try:
    from codomyrmex.cerebrum.fpf_orchestration import FPFOrchestrator
except ImportError:
    print("Error: Could not import FPFOrchestrator from codomyrmex.cerebrum.fpf_orchestration")
    sys.exit(1)


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

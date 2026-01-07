#!/usr/bin/env python3
"""
Basic FPF Pipeline Example

Demonstrates basic usage of FPF orchestration.
"""

from pathlib import Path
import sys

# Add parent directories to path to find codomyrmex modules
script_dir = Path(__file__).resolve().parent
# Navigate up to find project root (scripts/fpf/examples -> scripts/fpf -> scripts -> root)
project_root = script_dir.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "scripts"))

from fpf.orchestrate import FPFOrchestrator


def main():
    """Run basic FPF pipeline."""
    # Initialize orchestrator
    orchestrator = FPFOrchestrator(
        output_dir=Path("./fpf_output_example"),
        dry_run=False,
    )

    # Resolve spec path relative to project root
    spec_path = project_root / "src/codomyrmex/fpf/FPF-Spec.md"
    
    # Run full pipeline
    success = orchestrator.run_full_pipeline(
        source=str(spec_path),
        fetch=False,
        viz_formats=["png", "mermaid"],
    )

    if success:
        print("✅ Pipeline completed successfully!")
        print(f"📁 Outputs saved to: {orchestrator.output_dir}")
    else:
        print("❌ Pipeline completed with errors")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())



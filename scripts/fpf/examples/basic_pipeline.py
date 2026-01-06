#!/usr/bin/env python3
"""
Basic FPF Pipeline Example

Demonstrates basic usage of FPF orchestration.
"""

from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fpf.orchestrate import FPFOrchestrator


def main():
    """Run basic FPF pipeline."""
    # Initialize orchestrator
    orchestrator = FPFOrchestrator(
        output_dir=Path("./fpf_output_example"),
        dry_run=False,
    )

    # Run full pipeline
    success = orchestrator.run_full_pipeline(
        source="../../src/codomyrmex/fpf/FPF-Spec.md",
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


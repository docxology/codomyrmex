#!/usr/bin/env python3
"""
CEREBRUM-FPF Orchestration Script

Thin orchestrator script providing CLI access to CEREBRUM-FPF integration functionality.
Performs comprehensive CEREBRUM analysis on FPF specification: case-based reasoning,
Bayesian inference, active inference, and combinatorics analysis.

See also: src/codomyrmex/cerebrum/fpf_orchestration.py for core implementation
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add project root and src to path for imports
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import shared utilities
# Import shared utilities
from codomyrmex.utils.cli_helpers import (
    format_output,
    print_error,
    print_section,
    print_success,
    ProgressReporter,
    add_common_arguments,
    validate_dry_run,
)

# Import CEREBRUM-FPF modules
from codomyrmex.cerebrum.fpf_orchestration import FPFOrchestrator
from codomyrmex.cerebrum.fpf_combinatorics import FPFCombinatoricsAnalyzer

logger = get_logger(__name__)


def run_orchestration(
    fpf_spec_path: Optional[str],
    output_dir: Path,
    dry_run: bool = False,
) -> bool:
    """Run main CEREBRUM orchestration analysis.

    Args:
        fpf_spec_path: Path to FPF-Spec.md (None to fetch from GitHub)
        output_dir: Output directory
        dry_run: If True, don't write files

    Returns:
        True if successful
    """
    try:
        print_section("CEREBRUM Orchestration Analysis")
        logger.info("Starting CEREBRUM orchestration analysis")

        if dry_run:
            print_success("DRY RUN: Would run orchestration analysis")
            return True

        logger.info("Running orchestration analysis (not dry-run)")

        orchestrator = FPFOrchestrator(
            fpf_spec_path=fpf_spec_path,
            output_dir=str(output_dir / "orchestration"),
        )

        results = orchestrator.run_comprehensive_analysis()

        print_success(
            f"Orchestration complete: {results['fpf_statistics']['total_patterns']} patterns analyzed"
        )
        logger.info(f"Orchestration analysis complete: {len(results)} result keys")
        return True

    except Exception as e:
        logger.exception("Failed to run orchestration analysis")
        print_error("Failed to run orchestration analysis", exception=e)
        return False


def run_combinatorics(
    fpf_spec_path: Optional[str],
    output_dir: Path,
    dry_run: bool = False,
) -> bool:
    """Run combinatorics analysis.

    Args:
        fpf_spec_path: Path to FPF-Spec.md (None to fetch from GitHub)
        output_dir: Output directory
        dry_run: If True, don't write files

    Returns:
        True if successful
    """
    try:
        print_section("Combinatorics Analysis")
        logger.info("Starting combinatorics analysis")

        if dry_run:
            print_success("DRY RUN: Would run combinatorics analysis")
            return True

        combinatorics = FPFCombinatoricsAnalyzer(
            fpf_spec_path=fpf_spec_path,
            output_dir=str(output_dir / "combinatorics"),
        )

        results = combinatorics.run_comprehensive_combinatorics()

        print_success(
            f"Combinatorics complete: {results['pattern_pairs']['total_pairs']} pairs analyzed"
        )
        logger.info(f"Combinatorics analysis complete: {len(results)} result keys")
        return True

    except Exception as e:
        logger.exception("Failed to run combinatorics analysis")
        print_error("Failed to run combinatorics analysis", exception=e)
        return False


def run_pipeline(
    fpf_spec_path: Optional[str],
    output_dir: Path,
    skip_orchestration: bool = False,
    skip_combinatorics: bool = False,
    dry_run: bool = False,
) -> bool:
    """Run complete CEREBRUM-FPF analysis pipeline.

    Args:
        fpf_spec_path: Path to FPF-Spec.md (None to fetch from GitHub)
        output_dir: Output directory
        skip_orchestration: Skip main orchestration analysis
        skip_combinatorics: Skip combinatorics analysis
        dry_run: If True, don't write files

    Returns:
        True if successful
    """
    try:
        print_section("CEREBRUM-FPF Analysis Pipeline")
        logger.info("Starting CEREBRUM-FPF analysis pipeline")

        # Create output directory structure
        if not dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "orchestration").mkdir(exist_ok=True)
            (output_dir / "combinatorics").mkdir(exist_ok=True)
            (output_dir / "visualizations").mkdir(exist_ok=True)
            (output_dir / "reports").mkdir(exist_ok=True)
            (output_dir / "logs").mkdir(exist_ok=True)

        success = True

        # Run orchestration
        if not skip_orchestration:
            success = run_orchestration(fpf_spec_path, output_dir, dry_run) and success
        else:
            print_section("Skipping orchestration analysis")

        # Run combinatorics
        if not skip_combinatorics:
            success = run_combinatorics(fpf_spec_path, output_dir, dry_run) and success
        else:
            print_section("Skipping combinatorics analysis")

        if success:
            print_section("Pipeline Complete")
            print_success(f"All outputs saved to: {output_dir}")
            logger.info(f"Pipeline complete: {output_dir}")
        else:
            print_error("Pipeline completed with errors")

        return success

    except Exception as e:
        logger.exception("Failed to run pipeline")
        print_error("Failed to run pipeline", exception=e)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CEREBRUM-FPF orchestration script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Add common arguments
    add_common_arguments(parser)

    # CEREBRUM-specific arguments
    parser.add_argument(
        "--fpf-spec",
        type=str,
        default=None,
        help="Path to FPF-Spec.md (default: fetch from GitHub)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output/cerebrum",
        help="Output directory (default: output/cerebrum)",
    )
    parser.add_argument(
        "--skip-orchestration",
        action="store_true",
        help="Skip main orchestration analysis",
    )
    parser.add_argument(
        "--skip-combinatorics",
        action="store_true",
        help="Skip combinatorics analysis",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging()

    # Get dry run flag
    dry_run = getattr(args, 'dry_run', False)

    # Convert output directory to Path
    output_dir = Path(args.output_dir).resolve()

    # Run pipeline
    success = run_pipeline(
        fpf_spec_path=args.fpf_spec,
        output_dir=output_dir,
        skip_orchestration=args.skip_orchestration,
        skip_combinatorics=args.skip_combinatorics,
        dry_run=dry_run,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

